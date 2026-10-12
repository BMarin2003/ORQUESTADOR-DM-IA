"""
PAQUETE DE RESULTADOS para el capítulo 6 de la tesis, con el formato del capítulo (una sección por objetivo específico), sobre las 27 parejas y texto
normalizado. Salidas:
  docs/resultados/resultados_tesis.md          tablas descriptivas (G2), normalidad, comparaciones pareadas y resumen por hipótesis, más la ficha de instrumentos
  docs/resultados/por_campana_largo.csv        una fila por campaña e instrumento (para cualquier prueba adicional)
  docs/resultados/por_pareja_ancho.csv         una fila por pareja, columnas <instrumento>__G1 y <instrumento>__G2
Descriptivo y post hoc en lo que corrige instrumentos. NO decide las hipótesis: entrega las pruebas y su dirección. El uso propuesto de cada instrumento en la
docimasia (confirmatorio / exploratorio / no usar) es una PROPUESTA basada en la validación disponible.
    PYTHONUTF8=1 py scripts/reporte_v2/consolidar.py && PYTHONUTF8=1 py scripts/reporte_v2/resultados_tesis.py
"""
import csv
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats as sps

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
import comparar_v1_v2 as cmp        # noqa: E402
import consolidar as CO             # noqa: E402
import estadistica as est           # noqa: E402
import pares as _pares              # noqa: E402

SALIDA = RAIZ / "docs" / "resultados"
SEMILLA, B = 20260920, 10000
PCT = {"cr1", "cl2_pnj_inactivo_actua", "cr2_nombres_no_reconocidos", "p2_primaria", "p2_volicion", "p2_cognicion", "p2_emocion", "p2_habla", "p2_secundaria",
       "rep_frases", "nolatin"}

# uso propuesto en la docimasia: (categoría, motivo). Basado en A2 (sensibilidad), A4b/c y los hallazgos documentados; es una PROPUESTA.
CONF, COND, EXPL, NOUSAR = "Confirmatorio", "Confirmatorio condicionado", "Exploratorio", "Descriptivo / no usar"
USO = {
    "grammaticality_lt": (NOUSAR, "techo ≈ 0.999: no discrimina"),
    "cr1": (NOUSAR, "baja precisión (ignora la negación); tasas ≈ 0.1 %"),
    "nolatin": (EXPL, "medida simple; sin prueba de sensibilidad"),
    "cr2a_z": (CONF, "instrumento nuevo, matriz a4bc-2 (25 de 26 celdas direccionales)"),
    "cr2a_crudo": (EXPL, "complementa a z; misma evaluación a4bc-2"),
    "cr2b_cos_v8": (EXPL, "no distingue deriva de evolución legítima del mundo; idf depende del conjunto de campañas"),
    "cr2b_cos_v8_sn": (EXPL, "casi plano: la señal la sostienen los nombres"),
    "cr2_entidad_grafo_densidad": (NOUSAR, "A2: insensible a otro escenario"),
    "cr2_nombres_no_reconocidos": (EXPL, "no separa nombres inventados de PNJ legítimos nuevos"),
    "cr2_n_nombres_no_reconocidos": (EXPL, "ídem"),
    "papalampidi_C": (EXPL, "proxy de identidad; solo controles en A2"),
    "papalampidi_V": (EXPL, "proxy; no mide voz ni motivaciones"),
    "ecr": (NOUSAR, "saturado (≈ 1)"),
    "jericho_recall": (EXPL, "A2 mecánico 80/80 (léxico exacto insertado y quitado); frente al azar: 25.9 % real vs 12.9 %, con +21 a +25 pp en npc.status y solo +2 a +4.5 pp en npc.affinity (55 % de los eventos)"),
    "relojes_reconocidos": (NOUSAR, "A2 mecánico 23/23, pero 88.3 % real frente a 89.8 % por azar: el vocabulario (palabras funcionales y texto del evento) reconoce casi cualquier ventana; solo Par18-27 (10 parejas)"),
    "cl2_pnj_inactivo_actua": (EXPL, "mide mención, no acción; precisión sin auditar"),
    "pnj_refinado": (EXPL, "solo ve nombres de una palabra"),
    "cl2_lugar_jaccard_similarity": (EXPL, "continuidad léxica, no de eventos"),
    "bucles_ciclos": (NOUSAR, "A2: no reacciona a permutar turnos"),
    "t_pnj": (EXPL, "mide mención; censurado en 1 401"),
    "qn1_ttr": (EXPL, "respondió en A2, pero por turno depende de la longitud (G1 158 vs G2 116 palabras): la diferencia se invierte a igual longitud; ver ttr100, MTLD y MATTR"),
    "qn1_ngram_repeticion": (EXPL, "respondió en A2, pero por turno crece con la longitud del turno: la diferencia se invierte a 100 palabras; ver ngram100"),
    "qn1_legibilidad_fh": (NOUSAR, "complejidad, sin sentido de mejora"),
    "grafo_lema": (NOUSAR, "A2: insensible a otro escenario"),
    "rep_frases": (EXPL, "medida simple; sin prueba de sensibilidad"),
    "ttr100": (EXPL, "control de longitud del TTR por turno; sin prueba de sensibilidad"),
    "ngram100": (EXPL, "control de longitud de la repetición por turno; sin prueba de sensibilidad"),
    "frac_100": (NOUSAR, "descriptivo: fracción de turnos que entra al control"),
    "mtld_campana": (EXPL, "complementa a TTR; no depende de la longitud; A2 (extensión): control P9 sin sesgo significativo (Holm 0.17 en G1, 1.0 en G2; G1 +2.0 de mediana, δ 0.43); sin celda que detecte un defecto real"),
    "mattr_campana": (EXPL, "complementa a TTR; no depende de la longitud; A2 (extensión): control P9 sin sesgo (Holm 0.73 en G1, 1.0 en G2); sin celda que detecte un defecto real"),
    "palabras_turno": (NOUSAR, "descriptivo: longitud del turno (confusor del TTR y de los bigramas por turno)"),
    "qn1_sz": (NOUSAR, "complementa a Fernández-Huerta (no lo reemplaza); A2 (extensión): invariante exacto ante P6, incumple P11a en G2 igual que FH (artefacto de formato); sin celda confirmatoria posible para legibilidad"),
    "sd_ttr": (EXPL, "medida simple"),
    "sd_fh": (EXPL, "medida simple"),
    "n_npc": (NOUSAR, "proxy descriptivo; G1 tiene un agente extra que crea entidades"),
    "n_misiones": (NOUSAR, "casi constante (2 por campaña, sembradas)"),
    "p2_primaria": (COND, "detector congelado v2b; precisión sin auditar (fase posterior)"),
    "p2_volicion": (COND, "ídem"), "p2_cognicion": (COND, "ídem"), "p2_emocion": (COND, "ídem"), "p2_habla": (COND, "ídem"),
    "p2_secundaria": (EXPL, "experimental"),
    "seg_turno": (NOUSAR, "operativo, fuera de la rúbrica"),
}
FAMILIAS = {"H1d (coherencia reactiva)": ("CR-1", "CR-2"), "H1e (coherencia longitudinal)": ("CL-1", "CL-2"), "H1f (calidad narrativa emergente)": ("QN-1", "QN-2")}


def wilcoxon_uni(d):
    """Wilcoxon de rangos con signo EXACTO (condicional a empates, rangos medios, ceros descartados): p bilateral y las dos unilaterales (H1: d>0 / H1: d<0)."""
    d = np.asarray(d, dtype=float)
    d = d[d != 0]
    n = int(d.size)
    if n == 0:
        return {"n": 0, "W_mas": 0.0, "p_bi": 1.0, "p_mas": 1.0, "p_menos": 1.0}
    r = cmp._rangos_medios(np.abs(d))
    r2 = np.rint(2 * r).astype(int)
    total = int(r2.sum())
    cuenta = [0] * (total + 1)
    cuenta[0] = 1
    for x in r2:
        x = int(x)
        for s in range(total, x - 1, -1):
            cuenta[s] += cuenta[s - x]
    obs = int(r2[d > 0].sum())
    ge = sum(cuenta[obs:])                     # P(W+ >= obs)
    le = sum(cuenta[:obs + 1])                 # P(W+ <= obs)
    bi = sum(c for s, c in enumerate(cuenta) if abs(2 * s - total) >= abs(2 * obs - total))
    den = 2 ** n
    return {"n": n, "W_mas": float(r[d > 0].sum()), "p_bi": min(1.0, bi / den), "p_mas": ge / den, "p_menos": le / den}


def resumen(x):
    """Estadísticos descriptivos de un vector: n, mediana, cuartiles (interpolación lineal), RIQ, mínimo, máximo, media y DE."""
    x = np.asarray(x, dtype=float)
    q1, m, q3 = np.percentile(x, [25, 50, 75])
    return {"n": int(x.size), "mdn": float(m), "q1": float(q1), "q3": float(q3), "riq": float(q3 - q1), "min": float(x.min()), "max": float(x.max()),
            "media": float(x.mean()), "de": float(x.std(ddof=1)) if x.size > 1 else 0.0}


def sw(x):
    """Shapiro-Wilk (W, p); (None, None) si hay menos de 3 datos o todos son iguales."""
    x = np.asarray(x, dtype=float)
    if x.size < 3 or np.ptp(x) == 0:
        return (None, None)
    w, p = sps.shapiro(x)
    return (float(w), float(p))


def f(clave, v, d=None):
    """Formatea un valor del instrumento `clave`: porcentaje si está en `PCT`, si no con sus decimales de `CO_DEC`; «—» si es None."""
    if v is None:
        return "—"
    if clave in PCT:
        return f"{100 * v:.2f} %"
    dd = CO_DEC.get(clave, 3)
    return f"{v:.{dd}f}"


CO_DEC = {"qn1_sz": 1, "ttr100": 4, "ngram100": 4, "frac_100": 3, "mtld_campana": 1, "mattr_campana": 3, "palabras_turno": 0, "grammaticality_lt": 4, "cr2a_z": 2, "cr2a_crudo": 3, "cr2b_cos_v8": 3, "cr2b_cos_v8_sn": 3, "papalampidi_C": 2, "papalampidi_V": 3, "ecr": 3, "jericho_recall": 2,
          "relojes_reconocidos": 2, "pnj_refinado": 2, "qn1_ttr": 3, "qn1_ngram_repeticion": 3, "qn1_legibilidad_fh": 1, "sd_ttr": 4, "sd_fh": 2, "n_npc": 1, "n_misiones": 1,
          "t_pnj": 0, "seg_turno": 1, "cl2_lugar_jaccard_similarity": 3, "cr2_entidad_grafo_densidad": 3, "cr2_n_nombres_no_reconocidos": 3, "grafo_lema": 3, "bucles_ciclos": 2}


def inflesz_banda(v):
    """Escala INFLESZ (Barrio-Cantalejo et al., 2008) sobre un valor de Szigriszt-Pazos. Solo para leer el resultado; no filtra nada."""
    if v is None:
        return None
    for tope, nombre in ((40, "muy difícil"), (55, "algo difícil"), (65, "normal"), (80, "bastante fácil")):
        if v < tope:
            return nombre
    return "muy fácil"


def banda(c, v):
    """Banda INFLESZ entre paréntesis, solo para la legibilidad Szigriszt-Pazos (`qn1_sz`); cadena vacía en otro caso."""
    return f" ({inflesz_banda(v)})" if c == "qn1_sz" and v is not None else ""


def fp(p):
    """Formatea un p-valor: «<0.0001» si es menor, si no 4 decimales; «—» si es None."""
    return "—" if p is None else ("<0.0001" if p < 1e-4 else f"{p:.4f}")


def main():
    """Genera el paquete de resultados del capítulo 6: tablas descriptivas (G2), normalidad, comparaciones pareadas y resumen por hipótesis.

    Escribe `resultados_tesis.md`, `por_campana_largo.csv` y `por_pareja_ancho.csv` en `docs/resultados/`. Por
    instrumento calcula Wilcoxon exacto (bilateral y unilateral en cada dirección), HL con IC bootstrap y rank-biserial;
    Holm dentro de cada familia solo sobre los instrumentos confirmatorios/condicionados (`USO`). Es descriptivo: no decide las hipótesis.
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SALIDA.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    CO._A4BC, CO._CIERRE = CO.cargar_a4bc(), CO.cargar_cierre()
    pares = _pares.todos()
    a2 = CO.a2_por_instrumento()
    largo, datos_par = [], {}
    for (clave, etiq, dim, fuente, campo, sentido, clave_a2, nota) in CO.T:
        for p in pares:
            v = {b: CO.carga(p["par"], b, fuente, campo) for b in ("G1", "G2")}
            for b in ("G1", "G2"):
                if v[b] is not None:
                    largo.append({"par": p["par"], "lote": "Par18-27" if int(p["par"]) >= 18 else "Par01-17", "brazo": b, "clave": clave, "dimension": dim, "valor": v[b]})
            if v["G1"] is not None and v["G2"] is not None:
                datos_par.setdefault(clave, []).append((int(p["par"]), v["G1"], v["G2"]))
    with open(SALIDA / "por_campana_largo.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["par", "lote", "brazo", "clave", "dimension", "valor"]); w.writeheader(); w.writerows(largo)
    claves = [t[0] for t in CO.T]
    with open(SALIDA / "por_pareja_ancho.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["par", "lote"] + [f"{c}__{b}" for c in claves for b in ("G1", "G2")])
        for p in pares:
            fila = [p["par"], "Par18-27" if int(p["par"]) >= 18 else "Par01-17"]
            for c in claves:
                d = {x[0]: x for x in datos_par.get(c, [])}.get(int(p["par"]))
                fila += [d[1], d[2]] if d else ["", ""]
            w.writerow(fila)

    # ---------- estadísticos por instrumento
    E = {}
    for (clave, etiq, dim, fuente, campo, sentido, clave_a2, nota) in CO.T:
        vs = datos_par.get(clave, [])
        if len(vs) < 5:
            E[clave] = None
            continue
        g1 = np.array([v[1] for v in vs]); g2 = np.array([v[2] for v in vs]); d = g1 - g2
        wl = wilcoxon_uni(d)
        idx = cmp.indices_bootstrap(d.size, B, SEMILLA)
        hl_ic = cmp.ic_bootstrap_pares(d, cmp.hodges_lehmann, indices=idx)
        mejor = wl["p_mas"] if sentido == "↑" else wl["p_menos"] if sentido == "↓" else None      # p unilateral «G1 mejor»
        peor = wl["p_menos"] if sentido == "↑" else wl["p_mas"] if sentido == "↓" else None
        lote = lambda cond: (cmp.hodges_lehmann(np.array([v[1] - v[2] for v in vs if cond(v[0])])) if sum(1 for v in vs if cond(v[0])) >= 3 else None)
        h1, h2 = lote(lambda x: x <= 17), lote(lambda x: x >= 18)
        E[clave] = {"n": len(vs), "g1": resumen(g1), "g2": resumen(g2), "dif": resumen(d), "w1": sw(g1), "w2": sw(g2), "wd": sw(d), "wil": wl,
                    "hl": cmp.hodges_lehmann(d), "hl_ic": hl_ic, "rb": cmp.rank_biserial_pareada(d), "mejor": mejor, "peor": peor,
                    "lotes_signo": bool(h1 is not None and h2 is not None and h1 * h2 < 0)}
    for fam, dims in FAMILIAS.items():           # Holm dentro de la familia, sobre los instrumentos confirmatorios (p bilateral)
        cs = [t[0] for t in CO.T if t[2] in dims and E.get(t[0]) and USO[t[0]][0] in (CONF, COND)]
        for c, pa in zip(cs, est.holm([E[c]["wil"]["p_bi"] for c in cs])):
            E[c]["holm"] = pa

    # ---------- informe
    n_par = len(pares)
    L = ["# Paquete de resultados para el capítulo 6", "",
         f"Generado por `scripts/reporte_v2/resultados_tesis.py` el {time.strftime('%Y-%m-%d %H:%M')}. Muestra: **{n_par} parejas** (Par01-27; coincide con el N = 27 del diseño), {2 * n_par} campañas de 1 400 turnos, "
         "mismo modelo y mismo agente jugador en ambos brazos, medición 100 % determinista sobre texto normalizado (se quita el formato de G1). "
         "Descriptivo: **no decide las hipótesis**; entrega las pruebas y su dirección. El uso propuesto de cada instrumento en la docimasia es una propuesta basada en la validación disponible.", "",
         "**Cómo leer.** Cada valor es la media de la campaña (turnos 2-1 400; `persona2` solo sobre turnos que no se usaron para construir el detector); la unidad de análisis es la **pareja**, no el juicio de un evaluador. "
         "Cuartiles con interpolación lineal. Wilcoxon de rangos con signo **exacto** (condicional a empates, ceros descartados), con p bilateral y unilateral en cada dirección, como en el capítulo actual. "
         "**↕**: ↑ mayor es mejor, ↓ menor es mejor, · sin sentido de mejora (solo bilateral). «G1 mejor» = la dirección favorable a G1 según ↕. "
         "Holm: dentro de la familia de cada hipótesis, solo entre instrumentos confirmatorios. Shapiro-Wilk con SciPy.", "",
         "**Punto abierto para la docimasia.** Las hipótesis H1a-H1c ('superior a la media') se contrastaban con Wilcoxon de una muestra contra μ₀ = 4, el punto medio de la escala Likert. Los instrumentos deterministas **no tienen punto medio**, "
         "así que para OE-1 a OE-3 este paquete entrega los valores de G2 (y de G1) pero no un contraste contra μ₀; hay que decidir cómo se operacionaliza esa hipótesis. "
         "Además, el texto de Limitaciones del capítulo 2 aún dice que la calidad narrativa emergente se mitiga con la rúbrica sobre un bloque piloto; hay que reconciliarlo con el giro totalmente determinista.", ""]

    def fila_ficha(t):
        """Fila Markdown de la ficha del instrumento: dimensión, sentido, uso propuesto en la docimasia, celdas A2 y motivo."""
        clave, etiq, dim, fuente, campo, sentido, clave_a2, nota = t
        uso, motivo = USO[clave]
        return f"| {dim} | {etiq.strip()} | {sentido} | {uso} | {a2.get(clave_a2, '—') if clave_a2 else '—'} | {motivo}; {nota} |"

    L += ["## 0. Ficha de instrumentos (para documentar la metodología)", "",
          "| Indicador | Instrumento | ↕ | Uso propuesto | A2: confirmatorias que respondieron | Motivo y limitación |", "|---|---|---|---|---|---|"]
    L += [fila_ficha(t) for t in CO.T]
    L += ["", "A2 = prueba de sensibilidad por perturbación (`docs/reportes/sensibilidad_baseline.md`; CR-2a/CR-2b en `sensibilidad_a4bc.md`; persona2 en `persona2_equivalencia.md`). "
          "«—» = sin prueba. CR-2a/CR-2b y persona2 son instrumentos nuevos de esta tesis; persona2 está congelado (hashes en `validacion/persona2_congelado.sha256`).", ""]

    def tabla_desc(dims, brazo):
        """Tabla descriptiva de un brazo (n, cuartiles, RIQ, extremos, media y DE, Shapiro-Wilk) para las dimensiones `dims`."""
        L = [f"| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in CO.T:
            if t[2] not in dims or E.get(t[0]) is None:
                continue
            e = E[t[0]]; s = e[brazo.lower()]; w, p = e["w" + brazo[1]]
            c = t[0]
            L.append(f"| {t[2]} | {t[1].strip()} | {s['n']} | {f(c, s['mdn'])}{banda(c, s['mdn'])} | {f(c, s['q1'])} | {f(c, s['q3'])} | {f(c, s['riq'])} | {f(c, s['min'])} | {f(c, s['max'])} | {f(c, s['media'])} ({f(c, s['de'])}) | "
                     f"{'—' if w is None else f'{w:.4f}'} | {fp(p)} | {'—' if p is None else ('sí' if p > 0.05 else 'no')} |")
        return L

    secciones = [("OE-1", "Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico (G2)", ("CR-1", "CR-2")),
                 ("OE-2", "Evaluar la coherencia longitudinal a lo largo de las campañas generadas por el sistema monolítico (G2)", ("CL-1", "CL-2")),
                 ("OE-3", "Evaluar la calidad de la coherencia narrativa emergente en las campañas generadas por el sistema monolítico (G2)", ("QN-1", "QN-2"))]
    for i, (oid, tit, dims) in enumerate(secciones, 1):
        L += [f"## {i}. {oid}. {tit}", "", f"### Tabla {2 * i + 1}. Estadísticos descriptivos del sistema monolítico (G2), n = {n_par} campañas y prueba de normalidad de Shapiro-Wilk", ""]
        L += tabla_desc(dims, "G2")
        L += ["", "Mismos estadísticos del sistema multiagente (G1), como referencia para la comparación:", ""] + tabla_desc(dims, "G1") + [""]

    def tabla_comp(dims):
        """Tabla de comparación pareada G1 vs G2 para las dimensiones `dims`: medianas, HL con IC, Wilcoxon (bilateral y unilaterales), r, Holm y signo por lote."""
        L = ["| Indicador | Instrumento | ↕ | Uso | Mdn G1 (Q1–Q3) | Mdn G2 (Q1–Q3) | Mdn dif. | HL [IC 95 %] | W+ | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm | Shapiro dif. p | Lotes |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in CO.T:
            if t[2] not in dims or E.get(t[0]) is None:
                continue
            c, e, wl = t[0], E[t[0]], E[t[0]]["wil"]
            hl = e["hl"]
            hlt = f"{100 * hl:+.2f} pp [{100 * e['hl_ic'][0]:+.2f}, {100 * e['hl_ic'][1]:+.2f}]" if c in PCT else f"{hl:+.{CO_DEC.get(c, 3)}f} [{e['hl_ic'][0]:+.{CO_DEC.get(c, 3)}f}, {e['hl_ic'][1]:+.{CO_DEC.get(c, 3)}f}]"
            md = e["dif"]["mdn"]
            mdt = f"{100 * md:+.2f} pp" if c in PCT else f"{md:+.{CO_DEC.get(c, 3)}f}"
            g1, g2 = e["g1"], e["g2"]
            L.append(f"| {t[2]} | {t[1].strip()} | {t[5]} | {USO[c][0]} | {f(c, g1['mdn'])} ({f(c, g1['q1'])}–{f(c, g1['q3'])}) | {f(c, g2['mdn'])} ({f(c, g2['q1'])}–{f(c, g2['q3'])}) | {mdt} | {hlt} | "
                     f"{wl['W_mas']:.1f} | {wl['n']} | {fp(wl['p_bi'])} | {fp(e['mejor'])} | {fp(e['peor'])} | {e['rb']:+.2f} | {fp(e.get('holm'))} | {fp(e['wd'][1])} | {'⚠ signo distinto' if e['lotes_signo'] else 'consistente'} |")
        return L

    comp = [("OE-4", "Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura", "H1d (coherencia reactiva)"),
            ("OE-5", "Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas", "H1e (coherencia longitudinal)"),
            ("OE-6", "Comparar la calidad de la narrativa emergente producida por la arquitectura multiagente frente a la monolítica", "H1f (calidad narrativa emergente)")]
    for j, (oid, tit, fam) in enumerate(comp, 4):
        L += [f"## {j}. {oid}. {tit}", "", f"### Tabla {2 * j + 1}. Comparación pareada G1 − G2, {n_par} parejas ({fam})", ""] + tabla_comp(FAMILIAS[fam]) + [""]
        if oid == "OE-6":
            L += ["Medidas descriptivas adicionales (fuera de la rúbrica): tiempo por turno y proxies de emergencia.", ""] + tabla_comp(("OP",)) + [""]

    # ---------- resumen por hipótesis
    L += ["## 7. Resumen por hipótesis (dirección observada; no es la decisión de la docimasia)", "",
          "Cuenta de instrumentos por resultado, con p bilateral < 0.05 (sin corregir) y la dirección respecto de ↕. Solo instrumentos con sentido de mejora definido.", "",
          "| Hipótesis | Grupo de instrumentos | G1 mejor (p < 0.05) | G2 mejor (p < 0.05) | Sin diferencia significativa | Total |", "|---|---|---|---|---|---|"]
    for fam, dims in FAMILIAS.items():
        for etiqueta, usos in (("Confirmatorios y condicionados", (CONF, COND)), ("Exploratorios", (EXPL,))):
            a = b = c_ = 0
            for t in CO.T:
                if t[2] in dims and t[5] in ("↑", "↓") and E.get(t[0]) and USO[t[0]][0] in usos:
                    e = E[t[0]]
                    if e["wil"]["p_bi"] < 0.05:
                        if (e["mejor"] is not None and e["mejor"] < e["peor"]):
                            a += 1
                        else:
                            b += 1
                    else:
                        c_ += 1
            L.append(f"| {fam} | {etiqueta} | {a} | {b} | {c_} | {a + b + c_} |")
    L += ["", "Nota: un mismo constructo aparece con varios instrumentos correlacionados (por ejemplo, las cuatro categorías de `persona2` y su total); el conteo no equivale a hipótesis independientes.", "",
          "## 8. Advertencias", "",
          "- Los instrumentos miden proxies: no miden interés, creatividad ni voz del personaje. Los detectores con «precisión sin auditar» (persona2, PNJ inactivo) quedan condicionados a la auditoría posterior.",
          "- Par01-17 y Par18-27 se generaron con versiones distintas del motor (sin y con avance de reloj, dados de combate y guardia de metamensajes); la columna *Lotes* marca los cambios de signo.",
          "- G1 tiene un agente extra que crea entidades y un formato de salida distinto (normalizado aquí). Las diferencias por instrumento son entre sistemas completos, no una ablación.",
          "- Par02 G2 tiene 1 668 turnos en la base; se recorta a 1 400. En Par01-06 (G2), 42 de 8 400 turnos difieren en el recuento de nombres no reconocidos entre el valor guardado y el recalculado; sin efecto material.",
          "- Las medidas de repetición de frases, alfabetos, estabilidad de estilo, entidades registradas y tiempo por turno (`scripts/reporte_v2/medidas_cierre.py`) no tienen prueba de sensibilidad.", ""]
    (SALIDA / "resultados_tesis.md").write_text("\n".join(L), encoding="utf-8")
    print(f"escrito {SALIDA / 'resultados_tesis.md'} ({time.time() - t0:.0f} s)")
    # comprobación cruzada del Wilcoxon exacto propio contra SciPy (sin empates)
    rng = np.random.default_rng(1)
    for _ in range(50):
        d = rng.normal(0.3, 1, 20)
        mio = wilcoxon_uni(d)
        ref = sps.wilcoxon(d, method="exact", alternative="greater").pvalue
        ref2 = sps.wilcoxon(d, method="exact").pvalue
        assert abs(mio["p_mas"] - ref) < 1e-9 and abs(mio["p_bi"] - ref2) < 1e-9, (mio, ref, ref2)
    print("Wilcoxon exacto propio = SciPy en 50 casos aleatorios")


if __name__ == "__main__":
    main()
