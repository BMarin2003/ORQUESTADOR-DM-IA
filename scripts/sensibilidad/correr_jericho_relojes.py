"""
A2 para dos instrumentos CL-2 que hoy no tienen prueba de sensibilidad: jericho_recall y
relojes_reconocidos (docs/cierre_brechas.md, fila CL-2: "heurística léxica; solo recall; sin
prueba A2" / "proxy de solapamiento léxico; sin prueba A2"). Esta es la brecha que deja H1e
(coherencia longitudinal) como indeterminada -- ver docs/triage-brechas-cierre-2026-09-21.md, B.

jericho_qa_recall() y relojes_no_reconocidos() (orquestador/reporte_validacion.py) NO operan
sobre un Contexto de UN turno como los instrumentos de scripts/sensibilidad/instrumentos_texto.py:
actúan sobre un EVENTO real (un delta narrable de Campaña.deltas_narrables() / un reloj de
Campaña.relojes_disparados()) y su ventana de evidencia (los turnos siguientes donde se busca el
vocabulario). Por eso este arnés es propio y no reutiliza correr_sensibilidad.py -- pero sigue las
MISMAS convenciones que el resto de scripts/sensibilidad/: expectativas fijadas y con hash SHA-256
ANTES de correr sobre datos reales, la línea base (sensibilidad_baseline.*) no se toca, y el
informe se escribe aparte (patrón de correr_extension_sz_mtld.py).

Perturbaciones (por EVENTO, no por turno; deterministas con semilla; SOLO LECTURA de la base --
toda la perturbación ocurre sobre str/dict en memoria, nunca se escribe en Postgres):

  JQ1  refuerzo léxico (Jericho)     delta narrable HOY no_reconocido -> inserta una oración que
                                     contiene el lexema EXACTO que jericho_qa_recall busca para
                                     ese estado (mismas tablas _KEYWORDS_*/_banda_afinidad de
                                     reporte_validacion.py, importadas aquí tal cual -- nunca se
                                     duplica la tabla, para que no pueda divergir del instrumento
                                     real) en el turno turn_id+ventana de su ventana de evidencia.
                                     ESPERADO: reconocido False -> True ("se_dispara")

  JQ2  supresión de evidencia        delta narrable HOY reconocido -> en su turno de evidencia
       (Jericho)                     REAL, quita la oración que contiene el lexema que lo hace
                                     reconocido; el resto del turno queda intacto.
                                     ESPERADO: reconocido True -> False ("se_apaga")

  RJ1  refuerzo léxico (relojes)     reloj disparado HOY no_reconocido -> inserta una oración con
                                     la facción o una palabra (>=4 letras) de su agenda en el
                                     primer turno de su ventana de evidencia (fired_at_turn+1).
                                     ESPERADO: reconocido False -> True ("se_dispara")

  RJ2  supresión de evidencia        reloj disparado HOY reconocido -> en su turno de evidencia
       (relojes)                     real, quita la oración con la palabra que lo hace reconocido.
                                     ESPERADO: reconocido True -> False ("se_apaga")

Límite pre-registrado (no se cambia tras ver resultados): los relojes de facción solo existen en
Par18-27 -- Par01-17 se generó con el motor sin avance de reloj (docs/cierre_brechas.md, nota
general). La muestra de RJ1/RJ2 se toma solo de esas 10 parejas / 20 campañas, y por tanto es más
pequeña que la de JQ1/JQ2.

SEGUNDA CORRIDA COMPLETA (2026-09-21): la primera dio RJ2 13/16; las 3 filas «sin_cambio» eran un error de la supresión (las claves con mayúscula, p. ej. «Acreedora», «Congreso» o el
nombre completo de la facción, no coincidían con la oración pasada a minúsculas). Se corrigió con re.I; el hash y las direcciones esperadas no cambian. La primera corrida se conserva en
docs/reportes/sensibilidad_jericho_relojes_corrida1_con_error.*.

REVISIÓN ANTES DE LA PRIMERA EJECUCIÓN (2026-09-21; las 4 perturbaciones, sus direcciones y el hash NO cambian): el script original nunca se había
ejecutado y se corrigió (1) `import bd` -> `import db as bd`; (2) JQ2/RJ2 quitan la evidencia en TODA la ventana del instrumento (Jericho: turno del delta y el
siguiente; relojes: disparo+1 y +2), no solo en el primer turno con coincidencia; (3) se trabaja sobre texto NORMALIZADO (normalizar_turno), como todo lo v2: en
G1 la línea mecánica contiene raíces de los léxicos («fall», «logr»); (4) el resultado «después» se calcula llamando a las funciones REALES
(RV.jericho_qa_recall / RV.relojes_no_reconocidos), no a una reimplementación, y al cargar se comprueba que la re-derivación coincide con ellas; (5) Jericho usa las 27 parejas
(pares.todos()) y los relojes solo Par18-27.
LÍMITE DE LO QUE PRUEBA: las cuatro perturbaciones comprueban la mecánica (que el instrumento lea la ventana correcta y que su veredicto dependa del léxico en ambos
sentidos). No prueban que un solapamiento léxico signifique que el evento fue narrado (falsos positivos por «muert…» de otra cosa): eso no se puede probar por perturbación.

ESTADO: escrito por Claude (asistente de IA) a partir de la lectura de reporte_validacion.py,
datos.py, perturbaciones.py y recalcular_campana.py -- NO se ha ejecutado todavía (esta sesión no
tiene acceso a la base de datos de Bryan). Antes de tratar sus resultados como válidos: correr
primero con --rapido (muestra de 3+3 y 2+2) como humo, revisar a mano 2-3 filas del CSV de salida
para confirmar que la oración insertada/la oración quitada son las que se esperaba, y solo después
correr la muestra completa.

    PYTHONUTF8=1 py scripts/sensibilidad/correr_jericho_relojes.py [--n-jericho 40] [--n-relojes 16] [--semilla 20260921] [--rapido]
"""
import argparse
import csv
import hashlib
import json
import random
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "reporte_v2", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                          # noqa: E402  (scripts/sensibilidad/datos.py -- cargar_pares)
import perturbaciones as pt           # noqa: E402  (reutiliza _partir_zona/_insertar_al_inicio_de_parrafo/_rearmar: misma zona «narrativa» que el resto de perturbaciones del arnés)
import db as bd                       # noqa: E402  (orquestador/db.py -- Campaña)
import pares as _pares                # noqa: E402  (scripts/reporte_v2/pares.py -- las 27 parejas)
from normalizacion import normalizar_turno   # noqa: E402  (scripts/reporte_v2/normalizacion.py)
import reporte_validacion as RV       # noqa: E402  (orquestador/reporte_validacion.py -- jericho_qa_recall, relojes_no_reconocidos, _KEYWORDS_*, _banda_afinidad, _texto_reloj: importadas tal cual, nunca duplicadas)

HASTA = 1400
SALIDA = RAIZ / "docs" / "reportes" / "sensibilidad_jericho_relojes"

EXPECTATIVAS = {
    "JQ1|jericho_recall": "se_dispara",
    "JQ2|jericho_recall": "se_apaga",
    "RJ1|relojes_reconocidos": "se_dispara",
    "RJ2|relojes_reconocidos": "se_apaga",
}
HASH = hashlib.sha256(json.dumps(EXPECTATIVAS, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


# ---------------------------------------------------------------- oraciones de refuerzo
# Cada oración CONTIENE el lexema exacto de la tabla correspondiente en reporte_validacion.py
# (verificado por _assert_oraciones_contienen_lexema() más abajo, que se corre antes de perturbar
# nada -- si una oración no contiene su lexema, el script se detiene ahí, no a mitad de la corrida).
_ORACION_NPC_STATUS = {
    "dead": "{n} yace muerto en el suelo, sin vida.",
    "missing": "Desde ese momento nadie ha vuelto a ver a {n}: ha desaparecido sin dejar rastro.",
    "captured": "{n} ha sido capturado y ahora es cautivo de sus enemigos.",
}
_ORACION_QUEST_STATUS = {
    "completed": "La misión queda completada.",
    "failed": "La misión termina en un fracaso total.",
    "abandoned": "Deciden abandonar la misión de una vez.",
}
_ORACION_AFINIDAD = {
    "hostile": "{n} se muestra abiertamente hostil hacia ti.",
    "wary": "{n} te mira ahora con evidente desconfianza.",
    "cold": "El trato de {n} contigo se ha vuelto frío y distante.",
    "cordial": "{n} te trata ahora de forma cordial y amable.",
    "loyal": "{n} te ha jurado lealtad y te es leal.",
    "devoted": "{n} te venera y te muestra una devoción incondicional.",
}


def _oracion_refuerzo(campo, estado, nombre_entidad):
    """Oración de refuerzo que contiene el lexema exacto que jericho_qa_recall busca para ese campo y estado (JQ1)."""
    n = nombre_entidad or "la persona"
    if campo == "npc.status":
        return _ORACION_NPC_STATUS[estado].format(n=n)
    if campo == "quest.status":
        return _ORACION_QUEST_STATUS[estado]
    if campo == "npc.affinity":
        return _ORACION_AFINIDAD[estado].format(n=n)
    raise ValueError(campo)


def _claves_de(campo, estado):
    """Claves léxicas que el instrumento real (tablas _KEYWORDS_* de reporte_validacion) busca para ese campo y estado."""
    if campo == "npc.status":
        return RV._KEYWORDS_NPC_STATUS[estado]
    if campo == "quest.status":
        return RV._KEYWORDS_QUEST_STATUS[estado]
    if campo == "npc.affinity":
        return RV._KEYWORDS_AFINIDAD_BANDA[estado]
    raise ValueError(campo)


def _assert_oraciones_contienen_lexema():
    """Se corre ANTES de tocar datos reales: si alguna oración de refuerzo no contiene ninguna de
    las claves que el instrumento real busca para ese estado, el diseño del A2 está mal y no debe
    correr (evita perturbar 40 campañas para descubrir el bug al final)."""
    tablas = (("npc.status", _ORACION_NPC_STATUS, RV._KEYWORDS_NPC_STATUS),
              ("quest.status", _ORACION_QUEST_STATUS, RV._KEYWORDS_QUEST_STATUS),
              ("npc.affinity", _ORACION_AFINIDAD, RV._KEYWORDS_AFINIDAD_BANDA))
    for campo, oraciones, claves in tablas:
        for estado, claves_estado in claves.items():
            if estado not in oraciones:
                continue
            oracion = oraciones[estado].format(n="Fulano").lower()
            if not any(k in oracion for k in claves_estado):
                raise AssertionError(f"la oración de refuerzo de {campo}/{estado} no contiene ninguna de sus claves {claves_estado}")


# ---------------------------------------------------------------- detalle por evento
# jericho_qa_recall()/relojes_no_reconocidos() solo agregan (recall global) o, para relojes,
# devuelven turno_evidencia pero no la clave que hizo match. Aquí se re-deriva el detalle turno a
# turno CON LA MISMA LÓGICA de reporte_validacion.py (mismas tablas, mismo orden de ventana), sin
# tocar ese archivo, para poder perturbar con precisión quirúrgica un único evento.
def _detalle_deltas(deltas, turnos_por_id, ventana=1):
    """Re-deriva turno a turno el detalle de cada delta narrable con la misma lógica y tablas de jericho_qa_recall.

    El instrumento real solo agrega (recall global); aquí se recupera qué clave hizo match y en qué turno
    de la ventana (turno del delta y los `ventana` siguientes) para poder perturbar un único evento.
    Omite deltas sin vocabulario o con afinidad que no cruza de banda."""
    out = []
    for d in deltas:
        campo = f"{d['entity_type']}.{d['field_name']}"
        if campo == "npc.affinity":
            try:
                banda = RV._banda_afinidad(d["new_value"])
            except (TypeError, ValueError):
                continue
            if d.get("old_value") is not None:
                try:
                    banda_previa = RV._banda_afinidad(d["old_value"])
                except (TypeError, ValueError):
                    banda_previa = None
                if banda_previa == banda:
                    continue
            estado, claves = banda, RV._KEYWORDS_AFINIDAD_BANDA.get(banda)
        elif campo in ("npc.status", "quest.status"):
            estado = str(d["new_value"]).strip('"').lower()
            claves = (RV._KEYWORDS_NPC_STATUS if campo == "npc.status" else RV._KEYWORDS_QUEST_STATUS).get(estado)
        else:
            continue
        if not claves:
            continue
        turno_match, clave_match = None, None
        for tid in range(d["turn_id"], d["turn_id"] + ventana + 1):
            texto = (turnos_por_id.get(tid) or "").lower()
            hit = next((k for k in claves if k in texto), None)
            if hit:
                turno_match, clave_match = tid, hit
                break
        out.append({"turn_id": d["turn_id"], "entidad": d["entity_name"], "campo": campo, "estado": estado,
                     "claves": claves, "reconocido": turno_match is not None,
                     "turno_match": turno_match, "clave_match": clave_match,
                     "turno_objetivo_refuerzo": d["turn_id"] + ventana,
                     "evento_crudo": d, "ventana_turnos": list(range(d["turn_id"], d["turn_id"] + ventana + 1))})
    return out


def _detalle_relojes(relojes, turnos_por_id, ventana=2):
    """Re-deriva el detalle de cada reloj disparado con la misma lógica de relojes_no_reconocidos.

    Busca el vocabulario del reloj (facción y palabras de su agenda) como palabra completa, sin
    distinguir mayúsculas, en los `ventana` turnos posteriores al disparo; devuelve también la clave que hizo match."""
    out = []
    for r in relojes:
        vocab = sorted(RV._texto_reloj(r))
        disparo = r["fired_at_turn"]
        turno_match, clave_match = None, None
        for tid in range(disparo + 1, disparo + 1 + ventana):
            texto = turnos_por_id.get(tid)
            if not texto:
                continue
            hit = next((p for p in vocab if re.search(rf"\b{re.escape(p)}\b", texto, re.I)), None)
            if hit:
                turno_match, clave_match = tid, hit
                break
        out.append({"faccion": r["faccion"], "agenda": r["agenda"], "disparo": disparo, "vocab": vocab,
                     "reconocido": turno_match is not None, "turno_match": turno_match, "clave_match": clave_match,
                     "turno_objetivo_refuerzo": disparo + 1,
                     "evento_crudo": r, "ventana_turnos": list(range(disparo + 1, disparo + 1 + ventana))})
    return out


# ---------------------------------------------------------------- perturbación de texto
def _insertar(texto, oracion, rng):
    """Inserta `oracion` al inicio de un párrafo de la zona narrativa, reutilizando la perturbación del arnés."""
    nuevo, _ = pt._insertar_al_inicio_de_parrafo(texto, oracion, rng)
    return nuevo


def _quitar_oracion_con(texto, claves, por_palabra):
    """Quita de la zona narrativa la(s) oración(es) que contienen alguna clave: substring (criterio
    de jericho_qa_recall, por_palabra=False) o \\bpalabra\\b (criterio de relojes_no_reconocidos,
    por_palabra=True). Devuelve (texto_nuevo, n_oraciones_quitadas)."""
    partes = pt._partir_zona(texto)
    piezas = re.split(r"(?<=[.!?])(\s+)", partes[2])
    idx = list(range(0, len(piezas), 2))

    def _match(oracion):
        """Indica si la oración contiene alguna clave: substring (Jericho) o palabra completa sin mayúsculas (relojes)."""
        low = oracion.lower()
        if por_palabra:
            return any(re.search(rf"\b{re.escape(k)}\b", oracion, re.I) for k in claves)      # re.I como relojes_no_reconocidos: las claves llevan mayúsculas (nombres de facción)
        return any(k in low for k in claves)

    quitadas = [i for i in idx if _match(piezas[i])]
    for i in quitadas:
        piezas[i] = ""
    return pt._rearmar(partes, "".join(piezas)), len(quitadas)


# ---------------------------------------------------------------- carga de campaña (mismo patrón que reporte_v2/recalcular_campana.py::procesar, sobre texto NORMALIZADO)
def _cargar_campana(cid, brazo):
    """Carga una campaña como la hace reporte_v2/recalcular_campana.py::procesar, sobre texto normalizado.

    Returns:
        (turnos normalizados por turn_id, relojes disparados, deltas narrables), todos hasta el turno HASTA."""
    camp = bd.Campaña(cid)
    turnos = [t for t in camp.turnos_narracion() if t["turn_id"] <= HASTA]
    relojes = [r for r in camp.relojes_disparados() if r["fired_at_turn"] <= HASTA]
    deltas = [d for d in camp.deltas_narrables() if d["turn_id"] <= HASTA]
    tpi = {t["turn_id"]: normalizar_turno(t["dm_output"], brazo) for t in turnos}
    return tpi, relojes, deltas


# ---------------------------------------------------------------- resultado con las funciones REALES del instrumento
def _real_jericho(delta, tpi):
    """True/False si el instrumento real reconoce ESE delta; None si no es evaluable (sin vocabulario o afinidad que no cruza banda)."""
    r = RV.jericho_qa_recall([delta], tpi)
    return None if r["recall_global"] is None else r["recall_global"] == 1.0


def _real_reloj(reloj, tpi):
    """Veredicto del instrumento real para un reloj sobre los turnos `tpi`."""
    return RV.relojes_no_reconocidos([reloj], tpi)[0]["reconocido"]


# ---------------------------------------------------------------- muestreo
def _candidatos(pares, rng, detalle, real, clave_evento, extra):
    """Reúne los eventos candidatos de las parejas y valida que la re-derivación coincida con el instrumento real.

    Returns:
        (no reconocidos, reconocidos), barajados con `rng`: candidatos a refuerzo y a supresión.

    Raises:
        AssertionError: si algún evento difiere entre la re-derivación y el instrumento real; no se perturba nada."""
    ok, no_ok, desajustes, evaluados = [], [], 0, 0
    for p in pares:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            tpi, relojes, deltas = _cargar_campana(p[k], brazo)
            for det in detalle(relojes if extra else deltas, tpi):
                if det["turno_objetivo_refuerzo"] not in tpi:                 # sin turno donde insertar
                    continue
                real_ok = real(det["evento_crudo"], tpi)
                if real_ok is None:
                    continue
                evaluados += 1
                if real_ok != det["reconocido"]:                                # la re-derivación no coincide con el instrumento real
                    desajustes += 1
                    continue
                det.update(par=p["par"], brazo=brazo, campaign_id=p[k], tpi=tpi)
                (ok if det["reconocido"] else no_ok).append(det)
    if desajustes:
        raise AssertionError(f"{desajustes} de {evaluados} eventos: la re-derivación de este script NO coincide con el instrumento real; no se perturba nada")
    rng.shuffle(ok)
    rng.shuffle(no_ok)
    return no_ok, ok


def _candidatos_jericho(pares, rng):
    """Candidatos Jericho (JQ1: hoy no reconocido, JQ2: hoy reconocido), sobre deltas narrables."""
    return _candidatos(pares, rng, _detalle_deltas, _real_jericho, "delta", False)       # (JQ1: hoy no reconocido, JQ2: hoy reconocido)


def _candidatos_relojes(pares_v2, rng):
    """Candidatos de relojes (RJ1: hoy no reconocido, RJ2: hoy reconocido), sobre relojes disparados."""
    return _candidatos(pares_v2, rng, _detalle_relojes, _real_reloj, "reloj", True)


# ---------------------------------------------------------------- quitar la evidencia de TODA la ventana
def _quitar_en_ventana(det, claves, por_palabra):
    """Quita la evidencia en TODOS los turnos de la ventana del instrumento, no solo en el primero con coincidencia.

    Returns:
        (turnos con la evidencia quitada, número de oraciones quitadas)."""
    tpi2, quitadas = dict(det["tpi"]), 0
    for t in det["ventana_turnos"]:
        if t in tpi2:
            tpi2[t], n = _quitar_oracion_con(tpi2[t], claves, por_palabra)
            quitadas += n
    return tpi2, quitadas


# ---------------------------------------------------------------- aplicar UNA perturbación (JQ1/RJ1: refuerzo; JQ2/RJ2: supresión)
def _base(pid, instrumento, det, evento):
    """Campos comunes de una fila de resultado (perturbación, instrumento, pareja, brazo, campaña y evento)."""
    return {"perturbacion": pid, "instrumento": instrumento, "par": det["par"], "brazo": det["brazo"], "campaign_id": det["campaign_id"], "evento": evento}


def _fila_jq1(det, rng):
    """JQ1: inserta la oración de refuerzo en el turno objetivo; confirmatoria si el delta pasa a reconocido ("se_dispara")."""
    oracion = _oracion_refuerzo(det["campo"], det["estado"], det["entidad"])
    t = det["turno_objetivo_refuerzo"]
    tpi2 = dict(det["tpi"])
    tpi2[t] = _insertar(det["tpi"][t], oracion, rng)
    despues = _real_jericho(det["evento_crudo"], tpi2)
    return dict(_base("JQ1", "jericho_recall", det, f"{det['campo']}={det['estado']}@{det['entidad']}"),
                turn_id=det["turn_id"], turno_editado=t, oracion_insertada=oracion, reconocido_antes=False, reconocido_despues=despues,
                resultado="se_dispara" if despues else "sin_cambio")


def _fila_jq2(det, rng):
    """JQ2: quita la evidencia léxica de la ventana; confirmatoria si el delta deja de reconocerse ("se_apaga")."""
    tpi2, n = _quitar_en_ventana(det, det["claves"], por_palabra=False)
    despues = _real_jericho(det["evento_crudo"], tpi2)
    return dict(_base("JQ2", "jericho_recall", det, f"{det['campo']}={det['estado']}@{det['entidad']}"),
                turn_id=det["turn_id"], turnos_editados=det["ventana_turnos"], oraciones_quitadas=n, clave_original=det["clave_match"],
                reconocido_antes=True, reconocido_despues=despues, resultado="se_apaga" if not despues else "sin_cambio")


def _fila_rj1(det, rng):
    """RJ1: inserta una oración con la facción o una palabra de su agenda en el primer turno de la ventana; confirmatoria si el reloj pasa a reconocido."""
    palabra = det["vocab"][0] if det["vocab"] else det["faccion"]
    oracion = "{n} recorre el lugar mientras se habla de \"{p}\" por todas partes.".format(n=det["faccion"], p=palabra)
    t = det["turno_objetivo_refuerzo"]
    tpi2 = dict(det["tpi"])
    tpi2[t] = _insertar(det["tpi"][t], oracion, rng)
    despues = _real_reloj(det["evento_crudo"], tpi2)
    return dict(_base("RJ1", "relojes_reconocidos", det, f"{det['faccion']}@{det['disparo']}"),
                disparo=det["disparo"], turno_editado=t, oracion_insertada=oracion, reconocido_antes=False, reconocido_despues=despues,
                resultado="se_dispara" if despues else "sin_cambio")


def _fila_rj2(det, rng):
    """RJ2: quita la evidencia léxica del reloj en su ventana; confirmatoria si deja de reconocerse ("se_apaga")."""
    tpi2, n = _quitar_en_ventana(det, det["vocab"], por_palabra=True)
    despues = _real_reloj(det["evento_crudo"], tpi2)
    return dict(_base("RJ2", "relojes_reconocidos", det, f"{det['faccion']}@{det['disparo']}"),
                disparo=det["disparo"], turnos_editados=det["ventana_turnos"], oraciones_quitadas=n, clave_original=det["clave_match"],
                reconocido_antes=True, reconocido_despues=despues, resultado="se_apaga" if not despues else "sin_cambio")


# ---------------------------------------------------------------- informe
def _tabla_md(filas):
    """Tabla Markdown por perturbación con n, filas confirmatorias (resultado distinto de sin_cambio) y su tasa."""
    L = ["| perturbación | instrumento | n | confirmatorias | tasa |", "|---|---|---|---|---|"]
    for pid in ("JQ1", "JQ2", "RJ1", "RJ2"):
        sub = [f for f in filas if f["perturbacion"] == pid]
        if not sub:
            L.append(f"| {pid} | — | 0 | — | sin datos (ver límite de relojes en Par01-17) |")
            continue
        conf = sum(1 for f in sub if f["resultado"] != "sin_cambio")
        L.append(f"| {pid} | {sub[0]['instrumento']} | {len(sub)} | {conf} | {conf / len(sub):.1%} |")
    return "\n".join(L)


def main():
    """Corre las cuatro perturbaciones (JQ1, JQ2, RJ1, RJ2) y escribe el CSV y el informe Markdown aparte de la línea base.

    Fija y publica el SHA-256 de las expectativas antes de tocar datos reales. Jericho usa las 27
    parejas; los relojes solo Par18-27. `--rapido` es la corrida de humo (3+3 y 2+2)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-jericho", type=int, default=40)
    ap.add_argument("--n-relojes", type=int, default=16)
    ap.add_argument("--semilla", type=int, default=20260921)
    ap.add_argument("--rapido", action="store_true", help="humo: 3+3 Jericho, 2+2 relojes")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    _assert_oraciones_contienen_lexema()
    print(f"SHA-256 de las expectativas (fijadas antes de correr): {HASH}", flush=True)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    (SALIDA.parent / "sensibilidad_jericho_relojes_expectativas.json").write_text(
        json.dumps({"sha256": HASH, "expectativas": EXPECTATIVAS}, indent=1, ensure_ascii=False), encoding="utf-8")

    n_j = 3 if a.rapido else a.n_jericho
    n_r = 2 if a.rapido else a.n_relojes
    rng = random.Random(a.semilla)

    pares = _pares.todos()                                          # 01-27 (Jericho: todas)
    pares_reloj = [p for p in pares if p["lote"] == "v2"]           # solo 18-27 (relojes)

    print(f"cargando candidatos Jericho ({len(pares)} parejas)...", flush=True)
    no_ok_j, ok_j = _candidatos_jericho(pares, rng)
    print(f"  {len(no_ok_j)} deltas no_reconocidos (candidatos JQ1), {len(ok_j)} reconocidos (candidatos JQ2)", flush=True)

    print(f"cargando candidatos relojes ({len(pares_reloj)} parejas, solo Par18-27)...", flush=True)
    no_ok_r, ok_r = _candidatos_relojes(pares_reloj, rng)
    print(f"  {len(no_ok_r)} relojes no_reconocidos (candidatos RJ1), {len(ok_r)} reconocidos (candidatos RJ2)", flush=True)

    filas = []
    for det in no_ok_j[:n_j]:
        filas.append(_fila_jq1(det, rng))
    for det in ok_j[:n_j]:
        filas.append(_fila_jq2(det, rng))
    for det in no_ok_r[:n_r]:
        filas.append(_fila_rj1(det, rng))
    for det in ok_r[:n_r]:
        filas.append(_fila_rj2(det, rng))

    if filas:
        campos = sorted({k for f in filas for k in f})
        with open(f"{SALIDA}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            w.writerows(filas)

    md = [f"# A2: Jericho recall y relojes reconocidos", "",
          f"SHA-256 de las expectativas (fijadas antes de correr): `{HASH}`", "",
          f"Semilla: {a.semilla}. n objetivo por perturbación: Jericho {n_j}, relojes {n_r}.", "",
          _tabla_md(filas), "",
          "Confirmatoria = el instrumento cambió en la dirección pre-especificada (JQ1/RJ1: reconocido False->True; "
          "JQ2/RJ2: reconocido True->False). «sin_cambio» = no confirmatoria: revisar la fila en el CSV "
          "(oración insertada/oraciones quitadas) antes de sacar conclusiones -- puede ser un fallo real del "
          "instrumento (la hipótesis que este A2 existe para probar) o un problema de la propia oración/plantilla.", "",
          "Límite: los relojes de facción solo existen en Par18-27 (Par01-17 sin avance de reloj); "
          "RJ1/RJ2 se muestrean solo de esas 10 parejas.", ""]
    SALIDA.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    print(f"escrito {SALIDA}.md y {SALIDA}.csv", flush=True)


if __name__ == "__main__":
    main()
