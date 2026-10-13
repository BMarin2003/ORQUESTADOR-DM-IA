"""
Informe consolidado G1 vs G2 de las 42 campañas de Par07-27, con TODOS los instrumentos sobre texto NORMALIZADO (v2), agrupados por dimensión de
la rúbrica, más el contador de avance hacia resultados documentables (docs/avance_resultados.json).

Lee: datos/datos_v2/par*_G?.csv (numéricos), datos/datos_v2/booleanos/, datos/datos_v2/persona2/, datos/datos_v2/campana/ (nivel de campaña) y la distribución de A4b/c
(docs/reportes/sensibilidad_a4bc_distribucion.csv). Unidad de análisis: la PAREJA (d = G1 − G2, n = 21) con los estadísticos de comparar_v1_v2.py
(Hodges-Lehmann, rank-biserial pareada con IC bootstrap sobre parejas, Wilcoxon exacto, Holm sobre toda la tabla). DESCRIPTIVO: no declara ganador;
es una corrección posterior (post hoc) igual para los dos brazos. Consistencia entre lotes: HL por separado en Par07-17 (11) y Par18-27 (10).

    PYTHONUTF8=1 py experimento/scripts/reporte_v2/consolidar.py [--B 10000]
"""
import argparse
import csv
import glob
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
for _p in (AQUI, RAIZ / "experimento" / "scripts", RAIZ / "experimento" / "scripts" / "sensibilidad", RAIZ / "motor" / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import comparar_v1_v2 as cmp        # noqa: E402
import estadistica as est           # noqa: E402
import recalcular as rc             # noqa: E402
import pares as _pares            # noqa: E402

D2 = RAIZ / "datos" / "datos_v2"
SALIDA = RAIZ / "docs" / "reportes" / "consolidado_v2.md"
SALIDA_CSV = RAIZ / "docs" / "reportes" / "consolidado_v2.csv"
AVANCE = RAIZ / "docs" / "avance_resultados.json"
A2_CSV = RAIZ / "docs" / "reportes" / "sensibilidad_baseline.csv"

# (clave, etiqueta, dimensión, fuente, campo, sentido, clave A2, nota de estado)
#   sentido: "↓" menos es mejor · "↑" más es mejor · "·" neutro (descriptivo)
T = [
    ("grammaticality_lt", "Gramaticalidad (LanguageTool, 1 de cada 10 turnos)", "CR-1", "num", "grammaticality_lt", "↑", "grammaticality_lt", "techo cercano a 1: discrimina poco"),
    ("cr1", "cr1: pifia narrada como éxito (% de turnos)", "CR-1", "bool", "cr1_veredicto_contradice_narracion", "↓", "cr1_veredicto_contradice_narracion", "baja precisión: ignora la negación («no logras»)"),
    ("cr2a_z", "CR-2a: respuesta a la acción específica (z)", "CR-2", "a4bc", "z", "↑", "a4bc", "instrumento nuevo, matriz a4bc-2"),
    ("cr2a_crudo", "CR-2a: solapamiento con la acción (crudo)", "CR-2", "a4bc", "crudo", "↑", "a4bc", "instrumento nuevo, matriz a4bc-2"),
    ("cr2b_cos_v8", "CR-2b: anclaje al escenario (coseno, ventana de 8)", "CR-2", "a4bc", "cos_v8", "↑", "a4bc", "no distingue deriva de evolución legítima del mundo"),
    ("cr2b_cos_v8_sn", "CR-2b: anclaje sin nombres propios (ventana de 8)", "CR-2", "a4bc", "cos_v8_sn", "↑", "a4bc", "casi plano: la señal la sostienen los nombres"),
    ("cr2_entidad_grafo_densidad", "Densidad del grafo de entidades", "CR-2", "num", "cr2_entidad_grafo_densidad", "·", "cr2_entidad_grafo_densidad", "insensible a otro escenario (P8)"),
    ("cr2_nombres_no_reconocidos", "Turnos con algún nombre no reconocido", "CR-2", "num", "cr2_nombres_no_reconocidos", "↓", "cr2_nombres_no_reconocidos", "v1 saturado en G1 por la línea mecánica"),
    ("cr2_n_nombres_no_reconocidos", "N.º de nombres no reconocidos por turno", "CR-2", "num", "cr2_n_nombres_no_reconocidos", "↓", "cr2_n_nombres_no_reconocidos", "no detecta nombres inventados por sí solo"),
    ("papalampidi_C", "Papalampidi C: coherencia de entidad", "CL-1", "camp", "papalampidi_C", "↑", "ventana_coherencia_C", "proxy de consistencia de personajes"),
    ("papalampidi_V", "Papalampidi V: consistencia de atributos", "CL-1", "camp", "papalampidi_V", "↑", "ventana_consistencia_V", "proxy; no mide voz ni motivaciones"),
    ("ecr", "Entity Coreference Rate", "CL-1", "camp", "ecr", "↑", "entity_coreference_rate", "saturado (≈ 1)"),
    ("jericho_recall", "Jericho: recall de cambios de estado narrados", "CL-2", "camp", "jericho_recall", "↑", None, "A2 mecánico 80/80; frente al azar discrimina en npc.status (+21 a +25 pp) y casi nada en npc.affinity (+2 a +4.5 pp)"),
    ("relojes_reconocidos", "Relojes: fracción reconocida en la narración", "CL-2", "camp", "relojes_reconocidos", "↑", None, "A2 mecánico 23/23, pero reconoce lo mismo por azar (88 % real frente a 90 %): no discrimina"),
    ("cl2_pnj_inactivo_actua", "PNJ inactivo mencionado (% de turnos)", "CL-2", "bool", "cl2_pnj_inactivo_actua", "↓", "cl2_pnj_inactivo_actua", "mide mención, no acción; precisión sin auditar"),
    ("pnj_refinado", "PNJ inactivo como sujeto (por 1 000 turnos)", "CL-2", "camp", "pnj_refinado_actuando", "↓", "cl2_pnj_inactivo_refinado", "solo ve nombres de una palabra"),
    ("cl2_lugar_jaccard_similarity", "Jaccard con la escena anterior", "CL-2", "num", "cl2_lugar_jaccard_similarity", "·", "cl2_lugar_jaccard_similarity", "continuidad léxica, no de eventos"),
    ("bucles_ciclos", "Bucles: ciclos de ubicaciones", "CL-2", "camp", "bucles_ciclos", "↓", "ventana_bucles_ciclos", "A2: no reacciona a permutar turnos"),
    ("qn1_ttr", "TTR (diversidad léxica)", "QN-1", "num", "qn1_ttr", "↑", "qn1_ttr", "por turno: depende de la longitud (ver MTLD, MATTR y el control a 100 palabras)"),
    ("qn1_ngram_repeticion", "Repetición de bigramas", "QN-1", "num", "qn1_ngram_repeticion", "↓", "qn1_ngram_repeticion", "por turno: depende de la longitud (ver el control a 100 palabras)"),
    ("qn1_legibilidad_fh", "Legibilidad Fernández-Huerta", "QN-1", "num", "qn1_legibilidad_fh", "·", "qn1_legibilidad_fh", "complejidad, no calidad"),
    ("grafo_lema", "Densidad del grafo por lema", "QN-1", "camp", "grafo_lema", "·", "grafo_lema_densidad", "insensible a otro escenario (P8)"),
    ("p2_primaria", "Usurpación mental o verbal del PJ (% de turnos)", "QN-2", "p2", "primaria", "↓", "persona2", "v2b congelado, léxico cerrado; precisión sin auditar (C2-C4)"),
    ("p2_volicion", "  · decisión", "QN-2", "p2", "VOLICION", "↓", "persona2", "ídem"),
    ("p2_cognicion", "  · pensamiento", "QN-2", "p2", "COGNICION", "↓", "persona2", "ídem"),
    ("p2_emocion", "  · emoción", "QN-2", "p2", "EMOCION", "↓", "persona2", "ídem"),
    ("p2_habla", "  · habla", "QN-2", "p2", "HABLA", "↓", "persona2", "ídem"),
    ("p2_secundaria", "Acción física no declarada (experimental, % de turnos)", "QN-2", "p2", "secundaria", "↓", "persona2", "experimental; equivalencia 70 % (A2)"),
    # medidas descriptivas adicionales (experimento/scripts/reporte_v2/medidas_cierre.py): sin prueba de sensibilidad
    ("rep_frases", "Frases idénticas repetidas ≥ 3 veces (% de turnos)", "QN-1", "cierre", "rep_frases", "↓", None, "medida simple, sin prueba A2; límite inferior de las fórmulas evasivas"),
    ("mtld_campana", "MTLD de la campaña (complementa al TTR; no depende de la longitud)", "QN-1", "cierre", "mtld_campana", "↑", None, "medida nueva sobre texto concatenado; sin prueba A2 con datos reales"),
    ("mattr_campana", "MATTR de la campaña, ventana de 50 (complementa al TTR)", "QN-1", "cierre", "mattr_campana", "↑", None, "medida nueva sobre texto concatenado; sin prueba A2 con datos reales"),
    ("ttr100", "TTR a 100 palabras (control de longitud del TTR por turno)", "QN-1", "cierre", "ttr100", "↑", None, "mismas 100 primeras palabras de cada turno con >= 100; sin prueba A2"),
    ("ngram100", "Repetición de bigramas a 100 palabras (control de longitud)", "QN-1", "cierre", "ngram100", "↓", None, "mismas 100 primeras palabras de cada turno con >= 100; sin prueba A2"),
    ("frac_100", "Turnos con ≥ 100 palabras (fracción que entra al control)", "QN-1", "cierre", "frac_100", "·", None, "descriptivo: el control excluye más turnos de G2 (más cortos)"),
    ("palabras_turno", "Palabras por turno (mediana)", "QN-1", "cierre", "palabras_turno", "·", None, "descriptivo: el TTR y la repetición de bigramas por turno dependen de la longitud del turno"),
    ("qn1_sz", "Szigriszt-Pazos (legibilidad; complementa a Fernández-Huerta)", "QN-1", "cierre", "sz_media", "·", None, "calculado del texto, no está en el motor; sin prueba A2; sin sentido de mejora"),
    ("sd_ttr", "Estabilidad de estilo: variación del TTR entre bloques", "QN-1", "cierre", "sd_ttr", "↓", None, "medida simple, sin prueba A2"),
    ("sd_fh", "Estabilidad de estilo: variación de Fernández-Huerta entre bloques", "QN-1", "cierre", "sd_fh", "↓", None, "medida simple, sin prueba A2"),
    ("n_npc", "PNJ registrados hasta el turno 1 400", "QN-1", "cierre", "n_npc", "·", None, "proxy de emergencia; G1 tiene un agente extra que también crea entidades"),
    ("n_misiones", "Misiones registradas hasta el turno 1 400", "QN-1", "cierre", "n_misiones", "·", None, "casi constante (2 por campaña, sembradas): el r no es informativo"),
    ("nolatin", "Turnos con caracteres de otro alfabeto o U+FFFD (%)", "CR-1", "cierre", "nolatin", "↓", None, "medida simple; detecta fallos de codificación e idioma"),
    ("t_pnj", "Turno de la primera mención de un PNJ no vivo (1 401 = nunca)", "CL-2", "cierre", "t_pnj", "↑", None, "mide mención, no acción; censurado en 1 401"),
    ("seg_turno", "Segundos por turno (mediana; proxy de latencia)", "OP", "cierre", "seg_turno", "↓", None, "incluye al jugador LLM y la extracción; corridas concurrentes"),
]


# ---------------------------------------------------------------- carga: {par: {"G1": v, "G2": v}} por instrumento
def carga(par, brazo, fuente, campo):
    """Valor v2 de un instrumento para una campaña (par, brazo); None si no hay dato.

    Args:
        fuente: origen de los datos: `num` (CSV numérico), `bool` (booleanos), `p2` (persona2, solo turnos fuera
            del desarrollo del detector), `camp` (JSON de campaña), `cierre`, `a4bc` (media de la matriz de sensibilidad).
        campo: columna o clave dentro de la fuente.

    Raises:
        ValueError: si `fuente` no existe.
    """
    if fuente == "num":
        ruta = D2 / rc.nombre_csv(par, brazo)
        return cmp.media_campana(rc.leer_csv(ruta), campo)["v2"] if ruta.exists() else None
    if fuente == "bool":
        ruta = D2 / "booleanos" / rc.nombre_csv(par, brazo)
        return cmp.media_campana(rc.leer_csv(ruta), campo)["v2"] if ruta.exists() else None
    if fuente == "p2":
        ruta = D2 / "persona2" / rc.nombre_csv(par, brazo)
        if not ruta.exists():
            return None
        v = [r[campo] for r in rc.leer_csv(ruta) if r["en_desarrollo"] == 0]      # solo turnos fuera del desarrollo del detector
        return float(np.mean(v)) if v else None
    if fuente == "camp":
        ruta = D2 / "campana" / f"par{par}_{brazo}.json"
        if not ruta.exists():
            return None
        d = json.loads(ruta.read_text(encoding="utf-8"))
        v = d["v2"]
        if campo == "relojes_reconocidos":
            return v["relojes_reconocidos"] / v["relojes_disparados"] if v["relojes_disparados"] else None
        if campo == "pnj_refinado_actuando":
            return None if v[campo] is None else 1000 * v[campo] / d["n_turnos"]
        return v.get(campo)
    if fuente == "cierre":
        r = _CIERRE.get((par, brazo))
        if r is None or r[campo] == "" and campo != "t_pnj":
            return None
        return 1401.0 if campo == "t_pnj" and r[campo] == "" else float(r[campo])
    if fuente == "a4bc":
        filas = [r for r in _A4BC if r["brazo"] == brazo and r["par"] == par]
        return float(np.mean([float(r[campo]) for r in filas])) if filas else None
    raise ValueError(fuente)


def cargar_cierre():
    """Indexa `datos/datos_v2/cierre/por_campana.csv` por (par, brazo); {} si no existe."""
    ruta = D2 / "cierre" / "por_campana.csv"
    if not ruta.exists():
        return {}
    with open(ruta, newline="", encoding="utf-8") as fh:
        return {(r["par"], r["brazo"]): r for r in csv.DictReader(fh)}


def cargar_a4bc():
    """Filas de la matriz de sensibilidad a4bc (versión de 27 parejas si existe, si no la anterior)."""
    ruta = RAIZ / "docs" / "reportes" / "sensibilidad_a4bc_distribucion_27.csv"
    if not ruta.exists():
        ruta = RAIZ / "docs" / "reportes" / "sensibilidad_a4bc_distribucion.csv"
    with open(ruta, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def a2_por_instrumento():
    """{clave A2: 'k/n'} con las celdas confirmatorias que respondieron (ambos brazos)."""
    out = {}
    if not A2_CSV.exists():
        return out
    with open(A2_CSV, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["familia"] == "confirmatoria":
                k = out.setdefault(r["instrumento"], [0, 0])
                k[1] += 1
                k[0] += r["veredicto"] == "responde"
    res = {k: f"{v[0]}/{v[1]}" for k, v in out.items()}
    res["a4bc"] = "25/26"          # sensibilidad_a4bc.csv: 25 de 26 direccionales aprobadas
    md = RAIZ / "docs" / "reportes" / "persona2_equivalencia.md"
    if md.exists():                # celdas aprobadas de persona2: DIR (recall inyectado) e INV (falsas alarmas)
        txt = md.read_text(encoding="utf-8")
        dir_, inv = txt.split("## INV")[0].split("## DIR")[1], txt.split("## INV")[1].split("## EXP")[0]
        c = lambda t: (t.count("**aprobada**"), t.count("**aprobada**") + t.count("**NO aprobada**"))
        res["persona2"] = f"DIR {c(dir_)[0]}/{c(dir_)[1]} · INV {c(inv)[0]}/{c(inv)[1]}"
    return res


# ---------------------------------------------------------------- estadística
def estadisticos(d, B, semilla):
    """Estadísticos pareados (`comparar_v1_v2._estadisticos`) de las diferencias `d` con índices bootstrap de `semilla`."""
    d = np.asarray(d, dtype=float)
    idx = cmp.indices_bootstrap(d.size, B, semilla)
    return cmp._estadisticos(d, idx)


def analizar(pares, B, semilla):
    """Calcula, por instrumento de la tabla `T`, medias, HL, r y p con Holm sobre las parejas con dato en ambos brazos.

    Un instrumento con menos de 5 parejas queda «sin datos suficientes» (sin estadísticos). También calcula el HL
    por lote (Par01-17 y Par18-27) y aplica Holm sobre toda la tabla.
    """
    filas = []
    for (clave, etiq, dim, fuente, campo, sentido, a2, nota) in T:
        vs = []
        for p in pares:
            g1, g2 = carga(p["par"], "G1", fuente, campo), carga(p["par"], "G2", fuente, campo)
            if g1 is not None and g2 is not None:
                vs.append((int(p["par"]), g1, g2))
        r = {"clave": clave, "etiqueta": etiq, "dimension": dim, "sentido": sentido, "a2": a2, "nota": nota, "n": len(vs)}
        if len(vs) >= 5:
            g1 = np.array([v[1] for v in vs]); g2 = np.array([v[2] for v in vs]); d = g1 - g2
            r.update(estadisticos(d, B, semilla))
            r.update(media_g1=float(g1.mean()), media_g2=float(g2.mean()))
            for nombre, cond in (("hl_lote1", lambda x: x <= 17), ("hl_lote2", lambda x: x >= 18)):
                sub = np.array([v[1] - v[2] for v in vs if cond(v[0])])
                r[nombre] = cmp.hodges_lehmann(sub) if sub.size >= 3 else None
        filas.append(r)
    con = [r for r in filas if "p" in r]
    for r, pa in zip(con, est.holm([r["p"] for r in con])):
        r["p_holm"] = pa
    return filas


# ---------------------------------------------------------------- avance
def avance():
    """Lee el JSON de avance y resuelve el estado de cada ítem.

    Los ítems con `auto` cuentan archivos que cumplen un patrón; los que tienen `depende` quedan pendientes mientras
    alguna dependencia (encadenada, hasta 3 pasadas) no esté hecha.

    Returns:
        (dict original, lista de ítems con estado y progreso).
    """
    d = json.loads(AVANCE.read_text(encoding="utf-8"))
    items = []
    for it in d["items"]:
        it = dict(it)
        if "auto" in it:
            n = len(glob.glob(str(RAIZ / it["auto"]["patron"])))
            it["progreso"] = f"{n}/{it['auto']['total']}"
            it["estado"] = "hecho" if n >= it["auto"]["total"] else "pendiente"
        items.append(it)
    hechos = {i["id"] for i in items if i["estado"] == "hecho"}
    for _ in range(3):                     # un ítem con 'depende' solo cuenta si TODAS sus dependencias están hechas (encadenadas)
        hechos = {i["id"] for i in items if i["estado"] == "hecho"}
        for it in items:
            if "depende" in it:
                faltan = [x for x in it["depende"] if x not in hechos]
                if faltan:                 # bloqueado hasta que sus dependencias estén hechas; si no, conserva su propio estado (un ítem tuyo no se marca solo)
                    it["estado"] = "pendiente"
                    it["progreso"] = "falta " + ", ".join(faltan)
    return d, items


def md_avance(d, items):
    """Sección Markdown «Avance hacia resultados documentables»: barra de la fase de resultados, avance por fase y por bloque, y tabla de ítems."""
    def barra(pct):
        """Barra de progreso de 20 caracteres para un porcentaje."""
        return "█" * round(pct / 5) + "░" * (20 - round(pct / 5))
    quien = lambda lst, q: sum(1 for i in lst if i["quien"] == q)
    cuenta = {}
    for clave, nombre in d["fases"]:
        ob = [i for i in items if i.get("fase") == clave and not i.get("opcional")]
        cuenta[clave] = (nombre, ob, [i for i in ob if i["estado"] == "hecho"])
    n0, ob0, h0 = cuenta["resultados"]
    falta0 = [i for i in ob0 if i["estado"] != "hecho"]
    pct = 100 * len(h0) / len(ob0)
    L = ["## Avance hacia resultados documentables en la tesis", "",
         f"**{n0}: {len(h0)} de {len(ob0)} ítems hechos ({pct:.0f} %)** `{barra(pct)}` · faltan {len(falta0)}"
         f" ({quien(falta0, 'claude')} míos, {quien(falta0, 'usuario')} tuyos, {quien(falta0, 'asesor')} del asesor)", "", d["umbral"], ""]
    for clave, nombre in d["fases"][1:]:
        _, ob, h = cuenta[clave]
        L.append(f"- {nombre}: {len(h)} de {len(ob)} hechos ({100 * len(h) / len(ob):.0f} %) · opcionales pendientes: {sum(1 for i in items if i.get('fase') == clave and i.get('opcional') and i['estado'] != 'hecho')}")
    L += ["", "| bloque | hechos | total | avance |", "|---|---|---|---|"]
    for b in dict.fromkeys(i["bloque"] for i in items if not i.get("opcional")):
        ob = [i for i in items if i["bloque"] == b and not i.get("opcional")]
        h = sum(1 for i in ob if i["estado"] == "hecho")
        L.append(f"| {b} | {h} | {len(ob)} | {100 * h / len(ob):.0f} % |")
    L += ["", "| id | estado | quién | ítem |", "|---|---|---|---|"]
    for i in items:
        marca = "hecho" if i["estado"] == "hecho" else "**pendiente**"
        extra = f" ({i['progreso']})" if i.get("progreso") else ""
        opc = " *(opcional)*" if i.get("opcional") else ""
        L.append(f"| {i['id']} | {marca}{extra} | {i['quien']} | {i['texto']}{opc} |")
    L.append("")
    return L


# ---------------------------------------------------------------- informe
def f(x, d=3):
    """Formatea con `d` cifras significativas; «—» si es None."""
    return "—" if x is None else f"{x:.{d}g}"


def commit():
    """Hash corto del commit actual; «?» si git no está disponible."""
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    except OSError:
        return "?"


def main():
    """Genera `consolidado_v2.md` y `consolidado_v2.csv`: tablas por lista de la rúbrica (CR, CL, QN, OP) con G1, G2, HL, r, p Holm, lotes y A2.

    Opciones: `--B` y `--semilla`. Descriptivo y post hoc; no declara ganador.
    """
    global _A4BC, _CIERRE
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--semilla", type=int, default=20260920)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _A4BC, _CIERRE = cargar_a4bc(), cargar_cierre()
    pares = _pares.todos()
    filas = analizar(pares, a.B, a.semilla)
    a2 = a2_por_instrumento()
    d, items = avance()
    n_camp = len(glob.glob(str(D2 / "campana" / "par*_G?.json")))
    n_par = len(pares)
    L = [f"# Informe consolidado G1 vs G2: {2 * n_par} campañas ({n_par} parejas), instrumentos sobre texto normalizado (v2)", "",
         f"Generado por `experimento/scripts/reporte_v2/consolidar.py` · commit `{commit()}` · semilla {a.semilla} · B = {a.B}. "
         "**Descriptivo: no declara ganador.** Corrección posterior (post hoc) del instrumento, igual para los dos brazos; pendiente del visto bueno del asesor (ítem C1).", ""]
    L += md_avance(d, items)
    L += ["## Cómo leer las tablas", "",
          "- Unidad de análisis: la **pareja** (" + str(n_par) + ": Par01-27). Cada valor es la media de la campaña (turnos ≥ 2; `persona2` solo sobre turnos que no se usaron para construir el detector).",
          "- **HL** = Hodges-Lehmann de la diferencia G1 − G2 entre parejas, con IC 95 % bootstrap sobre parejas; **r** = correlación rank-biserial pareada (−1 a +1; signo positivo = G1 mayor). **p Holm** = Wilcoxon exacto bilateral, corregido por Holm sobre TODA la tabla (referencia, no criterio de éxito).",
          "- **Lotes**: HL por separado en Par01-17 (17 parejas, motor sin avance de reloj) y Par18-27 (10, con reloj determinista, dados de combate y guardia de metamensajes); si el signo cambia, la diferencia no es estable entre lotes (los lotes difieren, p. ej., en la frecuencia de combate).",
          "- **Sentido**: ↓ menos es mejor, ↑ más es mejor, · neutro, según la definición del indicador en la rúbrica. No implica que el instrumento mida bien el constructo: mira la columna *Estado*.",
          "- **A2**: celdas confirmatorias de la prueba de sensibilidad en que el instrumento respondió como se pre-especificó (k/n; «—» = sin prueba).",
          f"- Instrumentos de campaña (Papalampidi, Jericho, ECR, relojes, bucles, grafo): {n_camp} de {2 * n_par} campañas recalculadas; los que dependen de ellos usan solo las parejas completas (columna *Parejas*).", ""]
    listas = (("Lista 1. Coherencia reactiva (CR-1 fluidez y sensatez; CR-2 arraigo contextual)", ("CR-1", "CR-2")),
              ("Lista 2. Coherencia longitudinal (CL-1 personajes; CL-2 eventos y estado del mundo)", ("CL-1", "CL-2")),
              ("Lista 3. Calidad narrativa emergente (QN-1 interés y creatividad, solo proxies léxicos; QN-2 no usurpar la agencia)", ("QN-1", "QN-2")),
              ("Medidas operativas (fuera de la rúbrica)", ("OP",)))
    for titulo, dims in listas:
        L += [f"## {titulo}", "", "| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) [IC 95 %] | r [IC] | p Holm | Lotes (01-17 / 18-27) | Parejas | A2 | Estado |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in [x for x in filas if x["dimension"] in dims]:
            if "p" not in r:
                L.append(f"| {r['dimension']} | {r['etiqueta']} | {r['sentido']} | — | — | sin datos suficientes | — | — | — | {r['n']} | {a2.get(r['a2'], '—') if r['a2'] else '—'} | {r['nota']} |")
                continue
            lotes = f"{f(r['hl_lote1'])} / {f(r['hl_lote2'])}" + ("" if r["hl_lote1"] is None or r["hl_lote2"] is None or (r["hl_lote1"] * r["hl_lote2"] >= 0) else " ⚠ signo")
            L.append(f"| {r['dimension']} | {r['etiqueta']} | {r['sentido']} | {f(r['media_g1'])} | {f(r['media_g2'])} | {f(r['hl'])} [{f(r['hl_ic'][0])}, {f(r['hl_ic'][1])}] | "
                     f"{r['rb']:+.2f} [{r['rb_ic'][0]:+.2f}, {r['rb_ic'][1]:+.2f}] | {f(r['p_holm'], 2)} | {lotes} | {r['n']} | {a2.get(r['a2'], '—') if r['a2'] else '—'} | {r['nota']} |")
        L.append("")
    L += ["## Trazabilidad", "",
          "- Detector `persona2` v2b congelado: hashes en `datos/validacion/persona2_congelado.sha256` (verificados antes de correr `recalcular_persona2.py`). Equivalencia por persona gramatical: `docs/reportes/persona2_equivalencia.md`.",
          "- Instrumentos nuevos CR-2a/CR-2b: matriz a4bc-2, SHA-256 `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744`; `docs/reportes/sensibilidad_a4bc.md`.",
          "- Línea base de sensibilidad: `docs/reportes/sensibilidad_baseline.md`. Numéricos: `docs/reportes/reporte_v2_formato_normalizado.md`. Booleanos: `docs/reportes/reporte_v2_booleanos.md`.",
          "- Datos por campaña: `datos/datos_v2/` (numéricos), `datos/datos_v2/booleanos/`, `datos/datos_v2/persona2/`, `datos/datos_v2/campana/`. Solo SELECT; sin LLM.", ""]
    SALIDA.write_text("\n".join(L), encoding="utf-8")
    campos = ["clave", "etiqueta", "dimension", "sentido", "n", "media_g1", "media_g2", "mediana", "hl", "rb", "p", "p_holm", "hl_lote1", "hl_lote2", "a2", "nota"]
    with open(SALIDA_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(campos)
        for r in filas:
            w.writerow([r.get(c, "") if c != "a2" else a2.get(r["a2"], "") if r["a2"] else "" for c in campos])
    print(f"informe: {SALIDA}")
    for r in filas:
        if "p" in r:
            print(f"  {r['clave']:32} n={r['n']:2} G1 {r['media_g1']:.4g}  G2 {r['media_g2']:.4g}  HL {r['hl']:+.3g}  r {r['rb']:+.2f}  pHolm {r['p_holm']:.3g}  lotes {f(r['hl_lote1'])}/{f(r['hl_lote2'])}")
        else:
            print(f"  {r['clave']:32} n={r['n']:2} sin datos suficientes")


_A4BC, _CIERRE = [], {}

if __name__ == "__main__":
    main()
