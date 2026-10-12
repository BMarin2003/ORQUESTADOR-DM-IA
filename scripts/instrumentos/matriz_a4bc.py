"""
MATRIZ DE EXPECTATIVAS PRE-ESPECIFICADA de A4b/c (instrumento x perturbación).

Escrita el 2026-09-20 ANTES de programar los instrumentos (respuesta_accion.py,
anclaje_escenario.py) y de correrlos sobre la muestra de evaluación. NO se edita tras ver
resultados: los cambios van en un apéndice fechado «post hoc» de
docs/research/a4bc_diseno_instrumentos.md. El hash SHA-256 (json ordenado) está registrado en ese
documento y en test_matriz_a4bc.py.

Vocabulario de direcciones = el del arnés (scripts/sensibilidad): "baja" | "sube" | "sin_cambio",
para poder pasar la tabla a correr_sensibilidad.evaluar sin traducir.

Cada celda:
  dir         dirección esperada (derivada de la DEFINICIÓN operacional del instrumento)
  min         magnitud mínima de |mediana de la diferencia pareada (después - antes)| para aprobar
              (None en «sin_cambio»); unidades: z para cr2a_z*, puntos de Ochiai para cr2a_crudo,
              puntos de coseno para cr2b_*
  exacto      True = invariante exacto por construcción: aprobado solo si TODAS las diferencias son 0
  descriptivo True = sin veredicto (se reporta, no se juzga)
  justificacion / criterio  texto
Criterio general de aprobación (ver documento): veredicto del arnés = «responde» (Holm p < 0,05 y
|delta de Cliff pareado| >= 0,147 en la dirección esperada; para «sin_cambio», ausencia de ambos)
Y, en celdas con dirección, |mediana de la diferencia| >= min.

Magnitudes mínimas: se fijan como la MITAD del efecto observado en una muestra de DESARROLLO
disjunta de la de evaluación (pares 07, 08, 10, 12, 15, 17, 18, 19, 22, 26, 27; la evaluación usa
los pares 09, 11, 13, 14, 16, 20, 21, 23, 24, 25). Ver el documento, apéndice de desarrollo.
"""
import copy
import hashlib
import json

FECHA = "2026-09-20"
VERSION = "a4bc-1"

_CRIT_ABAJO = ("Aprobado si el arnés da «responde» (baja, Holm p<0,05, |delta pareado|>=0,147) y "
               "la mediana de la diferencia pareada es <= -min.")
_CRIT_IGUAL = ("Aprobado si el arnés da «responde» en un control «sin cambio» (sin cambio "
               "significativo con efecto no despreciable). Un movimiento sistemático es un hallazgo.")
_CRIT_EXACTO = "Aprobado solo si la diferencia pareada es exactamente 0 en el 100 % de los pares."

# ---------------------------------------------------------------- justificaciones por familia
_J = {
    "respuesta": {
        "X1_misma_campana_lejana":
            "La respuesta se sustituye por la de un turno de la MISMA campaña a 50 o más turnos. "
            "Por definición el puntaje mide el solapamiento de lemas de contenido con la acción de "
            "ESTE turno; la respuesta ajena comparte solo vocabulario genérico y del escenario, que "
            "el nulo (misma campaña) ya descuenta, así que el z cae hacia 0.",
        "X2_misma_campana_cercana":
            "Respuesta de un turno de la misma campaña a 3-10 turnos (misma escena). Comparte "
            "escenario y PNJ pero no las palabras de la acción concreta de este turno: el z debe bajar "
            "aunque quizá menos que con una respuesta lejana (continuidad de escena).",
        "P8":
            "Respuesta de otro PAR (otro escenario). Sin solapamiento específico con la acción; el "
            "solapamiento residual es vocabulario genérico que el nulo descuenta: el puntaje baja.",
        "P5":
            "Se añade una oración con dos nombres inventados. Los nombres propios no son lemas de "
            "contenido (solo NOUN/VERB/ADJ) y las palabras añadidas alargan R por igual en el "
            "observado y en el nulo (misma R): el z no debe moverse. En el crudo no se juzga (crece |R|).",
        "P6":
            "Se barajan las palabras en minúscula de ~30 % de las oraciones. El puntaje es una bolsa "
            "de lemas: en teoría invariante al orden. Riesgo conocido: el etiquetador de spaCy depende "
            "del contexto y puede cambiar el lema de algunas formas; se espera un efecto despreciable.",
        "C1_reorden_oraciones":
            "Se reordenan las oraciones de la narración (mismo contenido léxico). La bolsa de lemas "
            "es la misma salvo el contexto de etiquetado en las fronteras: invariante.",
        "C2_minusculas":
            "Todo el texto en minúsculas. El puntaje normaliza minúsculas en la clave; riesgo "
            "conocido: spaCy etiqueta distinto sin mayúscula inicial (nombres propios). Se espera "
            "efecto despreciable en NOUN/VERB/ADJ.",
        "C3_sin_tildes":
            "Se quitan las tildes de la respuesta. La clave del lema ya se normaliza sin tildes; "
            "riesgo conocido: spaCy lematiza distinto formas sin tilde. Se espera efecto despreciable.",
        "P11a_inyeccion":
            "Se inyectan etiquetas de formato de G1 y una línea mecánica en un texto de G2. El "
            "instrumento aplica prosa(texto, 'G1') antes de medir: la entrada tras la limpieza es "
            "idéntica, invariante exacto por construcción.",
        "P11b_eliminacion":
            "Se elimina el formato de G1 (prosa). El instrumento ya lo elimina: prosa es "
            "idempotente, invariante exacto por construcción.",
        "S1_sinonimos":
            "Sustitución por sinónimos de un diccionario mínimo escrito a mano. Una similitud LÉXICA "
            "no ve sinónimos: si se cambia un lema compartido con la acción, el solapamiento cae. "
            "Es el LÍMITE conocido del enfoque léxico; se cuantifica, sin veredicto (la cobertura "
            "del diccionario es pequeña y no está calibrada).",
    },
    "ventana_resp": {
        "P9":
            "Se permuta el orden de las 8 respuestas de la ventana dejando las acciones en su sitio: "
            "cada respuesta queda emparejada con la acción de OTRO turno de la ventana (misma escena). "
            "El z medio de la ventana baja como en X2.",
        "W1_ventana_otro_par":
            "Las 8 respuestas se sustituyen por 8 turnos consecutivos de otro par: sin solapamiento "
            "específico con las acciones; el z medio cae hacia 0.",
    },
    "anclaje_turno": {
        "P8":
            "Narración de un turno de OTRO par. El coseno TF-IDF con la referencia de ESTE escenario "
            "cae porque los lemas específicos (idf alto) ya no aparecen y aparecen los del otro "
            "escenario, que no están en la referencia.",
        "X1_misma_campana_lejana":
            "Narración de otro turno de la misma campaña (mismo escenario), a 50 o más turnos. El "
            "instrumento mide pertenencia al ESCENARIO, no al turno: en promedio no debe cambiar "
            "(la diferencia pareada es simétrica alrededor de 0).",
        "X2_misma_campana_cercana":
            "Narración de otro turno de la misma campaña a 3-10 turnos: mismo escenario, mismo "
            "vocabulario; diferencia pareada simétrica alrededor de 0.",
        "P5":
            "Se añade una oración con dos nombres inventados. En la variante con nombres los lemas "
            "nuevos (idf máximo, ausentes de la referencia) entran en el vector de la narración y "
            "aumentan su norma sin aumentar el producto escalar: el coseno baja por construcción. "
            "Es la parte (b) del constructo («sin introducir cosas ajenas»). Efecto pequeño.",
        "P6": "Barajar palabras en minúscula de ~30 % de oraciones. Bolsa de lemas: se espera invariancia "
              "(riesgo: el etiquetador depende del contexto). Efecto despreciable esperado.",
        "C1_reorden_oraciones":
            "Reordenar oraciones: misma bolsa de lemas; invariante salvo contexto de etiquetado.",
        "C2_minusculas":
            "Minúsculas: la clave se normaliza; riesgo conocido: los nombres propios en minúscula se "
            "etiquetan y lematizan distinto (p. ej. verbo inventado). Se espera efecto despreciable.",
        "C3_sin_tildes":
            "Sin tildes: la clave se normaliza; riesgo conocido: spaCy lematiza distinto las formas sin "
            "tilde. Se espera efecto despreciable.",
        "P11a_inyeccion":
            "Inyección de formato G1: el instrumento aplica prosa() antes de medir: invariante exacto.",
        "P11b_eliminacion":
            "Eliminación de formato G1: prosa idempotente: invariante exacto.",
    },
    "anclaje_turno_sn": {
        "P8":
            "Sin nombres propios ni lemas de nombres del escenario. Los lemas comunes específicos "
            "(niebla, cansancio, dique...) de la narración propia desaparecen con una narración ajena, "
            "así que el coseno baja, pero se espera MENOS que con nombres (el atajo de nombrar "
            "entidades queda excluido).",
        "X1_misma_campana_lejana": "Mismo escenario: diferencia pareada simétrica alrededor de 0.",
        "X2_misma_campana_cercana": "Mismo escenario: diferencia pareada simétrica alrededor de 0.",
        "P5":
            "Los nombres inventados se excluyen (nombre propio) y la variante ignora lemas de nombres: "
            "sin nombres propios en el vector, la oración añadida apenas cambia el coseno.",
        "P6": "Bolsa de lemas: invariante salvo contexto de etiquetado.",
        "C1_reorden_oraciones": "Bolsa de lemas: invariante salvo contexto de etiquetado.",
        "C2_minusculas": "Clave normalizada; riesgo de etiquetado sin mayúscula. Efecto despreciable esperado.",
        "C3_sin_tildes": "Clave normalizada; riesgo de lematizado sin tilde. Efecto despreciable esperado.",
        "P11a_inyeccion": "prosa() previa a la medición: invariante exacto.",
        "P11b_eliminacion": "prosa() idempotente: invariante exacto.",
    },
    "anclaje_ventana": {
        "P9":
            "Permutar el orden de los 8 turnos no cambia la suma de los conteos de lemas de la "
            "ventana (cada turno se lematiza por separado): el vector TF-IDF y su coseno son "
            "idénticos. Invariante exacto por construcción.",
        "W1_ventana_otro_par":
            "Ventana de 8 turnos de otro par: el coseno con la referencia de este escenario baja "
            "(los lemas específicos del otro escenario no están en la referencia).",
    },
    "anclaje_ventana_sn": {
        "P9": "Suma de conteos por turno: invariante exacto.",
        "W1_ventana_otro_par":
            "Ventana ajena sin nombres: baja, menos que con nombres (se excluye el atajo de nombrar).",
    },
}


def _celda(dir_, min_, just, exacto=False, descriptivo=False, criterio=None):
    if criterio is None:
        criterio = _CRIT_EXACTO if exacto else (_CRIT_IGUAL if dir_ == "sin_cambio" else _CRIT_ABAJO)
    return {"dir": dir_, "min": min_, "exacto": exacto, "descriptivo": descriptivo,
            "justificacion": just, "criterio": criterio}


def _construir():
    c = {}
    # ---- cr2a_z (unidades: z del nulo por permutación)
    j = _J["respuesta"]
    z = {}
    for pid in ("X1_misma_campana_lejana", "X2_misma_campana_cercana", "P8"):
        z[pid] = _celda("baja", 1.0, j[pid])
    for pid in ("P5", "P6", "C1_reorden_oraciones", "C2_minusculas", "C3_sin_tildes"):
        z[pid] = _celda("sin_cambio", None, j[pid])
    for pid in ("P11a_inyeccion", "P11b_eliminacion"):
        z[pid] = _celda("sin_cambio", None, j[pid], exacto=True)
    z["S1_sinonimos"] = _celda("baja", 0.1, j["S1_sinonimos"], descriptivo=True,
                               criterio="Sin veredicto: se reporta la mediana y la fracción de turnos afectados.")
    c["cr2a_z"] = z
    # ---- cr2a_crudo (Ochiai)
    cr = {}
    for pid in ("X1_misma_campana_lejana", "X2_misma_campana_cercana", "P8"):
        cr[pid] = _celda("baja", 0.04, j[pid])
    for pid in ("P6", "C1_reorden_oraciones", "C2_minusculas", "C3_sin_tildes"):
        cr[pid] = _celda("sin_cambio", None, j[pid])
    for pid in ("P11a_inyeccion", "P11b_eliminacion"):
        cr[pid] = _celda("sin_cambio", None, j[pid], exacto=True)
    cr["S1_sinonimos"] = _celda("baja", 0.005, j["S1_sinonimos"], descriptivo=True,
                                criterio="Sin veredicto: se reporta la mediana y la fracción de turnos afectados.")
    c["cr2a_crudo"] = cr
    # ---- cr2a_z_ventana8 (media de z de 8 turnos)
    jv = _J["ventana_resp"]
    c["cr2a_z_ventana8"] = {"P9": _celda("baja", 1.0, jv["P9"]),
                            "W1_ventana_otro_par": _celda("baja", 1.0, jv["W1_ventana_otro_par"])}
    # ---- anclaje por turno
    for nombre, fam, m8, mp5 in (("cr2b_cos_turno", "anclaje_turno", 0.005, 0.0005),
                                 ("cr2b_cos_turno_sn", "anclaje_turno_sn", 0.001, None)):
        jt = _J[fam]
        d = {"P8": _celda("baja", m8, jt["P8"])}
        for pid in ("X1_misma_campana_lejana", "X2_misma_campana_cercana", "P6",
                    "C1_reorden_oraciones", "C2_minusculas", "C3_sin_tildes"):
            d[pid] = _celda("sin_cambio", None, jt[pid])
        d["P5"] = _celda("baja", mp5, jt["P5"]) if mp5 else _celda("sin_cambio", None, jt["P5"])
        for pid in ("P11a_inyeccion", "P11b_eliminacion"):
            d[pid] = _celda("sin_cambio", None, jt[pid], exacto=True)
        c[nombre] = d
    # ---- anclaje por ventana
    for nombre, fam, mw in (("cr2b_cos_ventana8", "anclaje_ventana", 0.01),
                            ("cr2b_cos_ventana8_sn", "anclaje_ventana_sn", 0.003)):
        jw = _J[fam]
        c[nombre] = {"P9": _celda("sin_cambio", None, jw["P9"], exacto=True),
                     "W1_ventana_otro_par": _celda("baja", mw, jw["W1_ventana_otro_par"])}
    return c


MATRIZ = {
    "version": VERSION,
    "fecha": FECHA,
    "regla_general": ("Aprobado = veredicto del arnés «responde» (Holm p<0,05 y |delta de Cliff pareado|>=0,147 "
                      "en la dirección esperada; «sin_cambio» = ninguno de los dos) Y, si hay dirección, "
                      "|mediana de la diferencia pareada| >= min. Celdas exactas: diferencia 0 en el 100 % de pares."),
    "celdas": _construir(),
}
_MATRIZ_INICIAL = copy.deepcopy(MATRIZ)


def hash_matriz(matriz=None):
    """SHA-256 del JSON ordenado de la matriz pre-especificada."""
    m = _MATRIZ_INICIAL if matriz is None else matriz
    return hashlib.sha256(json.dumps(m, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def esperado_arnes():
    """Tabla {perturbación: {instrumento: dirección}} para correr_sensibilidad.evaluar; las celdas
    descriptivas se omiten (el arnés las trata como «sin veredicto»)."""
    out = {}
    for instr, perts in MATRIZ["celdas"].items():
        for pid, cel in perts.items():
            if cel["descriptivo"]:
                continue
            out.setdefault(pid, {})[instr] = cel["dir"]
    return out
