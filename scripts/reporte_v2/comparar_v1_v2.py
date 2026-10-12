"""
Compara G1 vs G2 con los instrumentos numéricos ANTES (v1: texto crudo, guardado en turn_validation)
y DESPUÉS (v2: texto normalizado) de quitar el formato de G1. Lee los CSV de datos_v2/ (recalcular.py)
y escribe el informe docs/reportes/reporte_v2_formato_normalizado.md.

Unidad de análisis: la campaña (media de sus turnos 2-1400; el turno 1 se compara con el lore, no con
un turno del DM) y la PAREJA (par): diferencia d_par = media(G1) - media(G2), n = 21 parejas.
Estadísticos de las 21 diferencias: mediana, Hodges-Lehmann (mediana de los promedios de Walsh),
correlación rank-biserial pareada (Kerby 2014; ceros descartados, rangos medios) con IC bootstrap
percentil al 95 % remuestreando PAREJAS, y prueba de rangos con signo de Wilcoxon exacta (bilateral,
con empates por rangos medios) solo como referencia, con Holm sobre la familia de instrumentos
dentro de cada versión.

DESCRIPTIVO: no declara un «ganador». Es una corrección POSTERIOR (post hoc) del instrumento.

    PYTHONUTF8=1 py scripts/reporte_v2/comparar_v1_v2.py [--B 10000] [--semilla 20260920]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import estadistica as est          # noqa: E402  (scripts/sensibilidad/estadistica.py: Holm)
import recalcular as rc            # noqa: E402

DATOS = RAIZ / "datos_v2"
INFORME = RAIZ / "docs" / "reportes" / "reporte_v2_formato_normalizado.md"
ALFA = 0.05

ETIQUETA = {
    "qn1_ttr": "TTR (type/token)",
    "qn1_ngram_repeticion": "Repetición de bigramas",
    "qn1_legibilidad_fh": "Legibilidad Fernández-Huerta",
    "cl2_lugar_jaccard_similarity": "Jaccard con la escena anterior",
    "cr2_entidad_grafo_densidad": "Densidad del grafo de entidades",
    "cr2_n_nombres_no_reconocidos": "N.º de nombres no reconocidos",
    "cr2_nombres_no_reconocidos": "Turnos con algún nombre no reconocido",
    "grammaticality_lt": "Gramaticalidad (LanguageTool)",
}


# ---------------------------------------------------------------- estadística
def hodges_lehmann(d):
    """Estimador de Hodges-Lehmann de la posición: mediana de los promedios de Walsh (i <= j)."""
    d = np.asarray(d, dtype=float)
    if d.size == 0:
        return float("nan")
    i, j = np.triu_indices(d.size)
    return float(np.median((d[i] + d[j]) / 2.0))


def _rangos_medios(a):
    a = np.asarray(a, dtype=float)
    _, inv, cnt = np.unique(a, return_inverse=True, return_counts=True)
    fin = np.cumsum(cnt)
    ini = fin - cnt + 1
    return ((ini + fin) / 2.0)[inv]


def rank_biserial_pareada(d):
    """Correlación rank-biserial de muestras pareadas (Kerby 2014): (W+ - W-) / (W+ + W-),
    con rangos medios de |d| y las diferencias nulas descartadas. +1: todas positivas."""
    d = np.asarray(d, dtype=float)
    d = d[d != 0]
    if d.size == 0:
        return 0.0
    r = _rangos_medios(np.abs(d))
    wp, wm = r[d > 0].sum(), r[d < 0].sum()
    return float((wp - wm) / (wp + wm))


def wilcoxon_exacto(d):
    """Prueba de rangos con signo de Wilcoxon, p bilateral EXACTA (condicional a los empates:
    rangos medios; ceros descartados). Distribución de W+ por programación dinámica sobre rangos
    duplicados (enteros)."""
    d = np.asarray(d, dtype=float)
    d = d[d != 0]
    n = int(d.size)
    if n == 0:
        return {"p": 1.0, "W_mas": 0.0, "W_menos": 0.0, "n_efectivo": 0}
    r = _rangos_medios(np.abs(d))
    r2 = np.rint(2 * r).astype(int)                         # rangos duplicados: enteros
    total2 = int(r2.sum())
    cuenta = [0] * (total2 + 1)
    cuenta[0] = 1
    for x in r2:
        x = int(x)
        for s in range(total2, x - 1, -1):
            cuenta[s] += cuenta[s - x]
    obs = int(r2[d > 0].sum())
    desv_obs = abs(2 * obs - total2)
    ge = sum(c for s, c in enumerate(cuenta) if abs(2 * s - total2) >= desv_obs)
    return {"p": min(1.0, ge / 2 ** n), "W_mas": float(r[d > 0].sum()),
            "W_menos": float(r[d < 0].sum()), "n_efectivo": n}


def indices_bootstrap(n, B, semilla):
    return np.random.default_rng(semilla).integers(0, n, size=(B, n))


def ic_bootstrap_pares(d, estadistico, semilla=0, B=10000, alfa=ALFA, indices=None):
    """IC bootstrap percentil remuestreando PAREJAS (las diferencias) con reemplazo."""
    d = np.asarray(d, dtype=float)
    if d.size == 0:
        return float("nan"), float("nan")
    idx = indices if indices is not None else indices_bootstrap(d.size, B, semilla)
    vals = np.array([estadistico(d[i]) for i in idx])
    lo, hi = np.percentile(vals, [100 * alfa / 2, 100 * (1 - alfa / 2)])
    return float(lo), float(hi)


ORDEN_BANDERAS = ["signo", "desaparece", "tamaño", "aparece"]
TITULAR = {"signo": "cambia de signo", "desaparece": "desaparece",
           "tamaño": "cambia de tamaño (>50 %)", "aparece": "aparece"}


def _signo(x):
    return (x > 0) - (x < 0)


def clasificar_cambio(v1, v2):
    """Cómo cambia la conclusión G1-vs-G2 de un instrumento al normalizar. Entradas: dicts con `hl`
    (Hodges-Lehmann de G1-G2), `p_holm`. Banderas (no exclusivas salvo signo/tamaño):
      signo      HL de signo opuesto (ambos no nulos);
      desaparece significativo en v1 (Holm < 0.05) y no en v2;
      tamaño     mismo signo pero |HL_v2 - HL_v1| > 50 % de |HL_v1|;
      aparece    no significativo en v1 y sí en v2.
    `titular` = la primera por precedencia signo > desaparece > tamaño > aparece."""
    h1, h2 = v1["hl"], v2["hl"]
    s1, s2 = v1["p_holm"] < ALFA, v2["p_holm"] < ALFA
    banderas = []
    signo_opuesto = _signo(h1) * _signo(h2) < 0
    if signo_opuesto:
        banderas.append("signo")
    if s1 and not s2:
        banderas.append("desaparece")
    if not signo_opuesto and abs(h2 - h1) > 0.5 * abs(h1):
        banderas.append("tamaño")
    if s2 and not s1:
        banderas.append("aparece")
    titular = next((TITULAR[b] for b in ORDEN_BANDERAS if b in banderas), "sin cambio material")
    return {"banderas": banderas, "titular": titular, "signif_v1": s1, "signif_v2": s2}


# ---------------------------------------------------------------- datos
def media_campana(filas, instrumento, desde=2):
    """Media por campaña de v1 y v2 sobre los turnos >= `desde` donde AMBOS existen."""
    a, b = f"{instrumento}_v1", f"{instrumento}_v2"
    v1, v2 = [], []
    for f in filas:
        if f["turn_id"] < desde or f.get(a) is None or f.get(b) is None:
            continue
        v1.append(float(f[a]))
        v2.append(float(f[b]))
    if not v1:
        return {"v1": None, "v2": None, "n": 0}
    return {"v1": float(np.mean(v1)), "v2": float(np.mean(v2)), "n": len(v1)}


def _estadisticos(d, idx):
    d = np.asarray(d, dtype=float)
    w = wilcoxon_exacto(d)
    return {"n_pares": int(d.size), "n_efectivo": w["n_efectivo"],
            "mediana": float(np.median(d)), "hl": hodges_lehmann(d),
            "hl_ic": ic_bootstrap_pares(d, hodges_lehmann, indices=idx),
            "rb": rank_biserial_pareada(d),
            "rb_ic": ic_bootstrap_pares(d, rank_biserial_pareada, indices=idx),
            "W_mas": w["W_mas"], "W_menos": w["W_menos"], "p": w["p"]}


def analizar(directorio, pares, instrumentos=None, semilla=20260920, B=10000, desde=2):
    """Análisis completo a partir de los CSV de `directorio`. Devuelve un dict serializable."""
    directorio = Path(directorio)
    instrumentos = list(instrumentos or rc.INSTRUMENTOS)
    filas = {}
    for p in pares:
        for brazo in ("G1", "G2"):
            ruta = directorio / rc.nombre_csv(p["par"], brazo)
            if ruta.exists():
                filas[(p["par"], brazo)] = rc.leer_csv(ruta)
    out = {"semilla": semilla, "B": B, "desde_turno": desde, "instrumentos": {}, "por_campana": []}
    for instr in instrumentos:
        por_par = []
        for p in pares:
            if (p["par"], "G1") not in filas or (p["par"], "G2") not in filas:
                continue
            m1 = media_campana(filas[(p["par"], "G1")], instr, desde)
            m2 = media_campana(filas[(p["par"], "G2")], instr, desde)
            if m1["n"] == 0 or m2["n"] == 0:
                continue
            por_par.append({"par": p["par"], "G1": m1, "G2": m2})
            for brazo, m in (("G1", m1), ("G2", m2)):
                out["por_campana"].append({"par": p["par"], "brazo": brazo, "instrumento": instr,
                                           "v1": m["v1"], "v2": m["v2"], "n_turnos": m["n"]})
        if not por_par:
            continue
        r = {"n_pares": len(por_par)}
        diffs = {}
        idx_c = indices_bootstrap(len(por_par), B, semilla)     # mismas parejas remuestreadas en v1 y v2
        for v in ("v1", "v2"):
            g1 = np.array([x["G1"][v] for x in por_par])
            g2 = np.array([x["G2"][v] for x in por_par])
            d = g1 - g2
            diffs[v] = d
            r[v] = _estadisticos(d, idx_c)
            r[v].update(media_g1=float(g1.mean()), media_g2=float(g2.mean()),
                        sd_g1=float(g1.std(ddof=1)) if len(g1) > 1 else 0.0,
                        sd_g2=float(g2.std(ddof=1)) if len(g2) > 1 else 0.0,
                        diferencias=[float(x) for x in d], pares=[x["par"] for x in por_par])
        dr = np.array([rank_biserial_pareada(diffs["v2"][i]) - rank_biserial_pareada(diffs["v1"][i])
                       for i in idx_c])
        r["rb_cambio"] = float(r["v2"]["rb"] - r["v1"]["rb"])
        r["rb_cambio_ic"] = [float(x) for x in np.percentile(dr, [2.5, 97.5])]
        out["instrumentos"][instr] = r
    # Holm dentro de cada versión, sobre la familia de instrumentos analizados
    nombres = list(out["instrumentos"])
    for v in ("v1", "v2"):
        aj = est.holm([out["instrumentos"][i][v]["p"] for i in nombres])
        for i, pa in zip(nombres, aj):
            out["instrumentos"][i][v]["p_holm"] = pa
    for i in nombres:
        r = out["instrumentos"][i]
        r["cambio"] = clasificar_cambio(r["v1"], r["v2"])
    return out


# ---------------------------------------------------------------- informe
def _f(x, d=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:.{d}f}"


def _fp(p):
    return "—" if p is None else (f"{p:.2g}" if p < 0.001 else f"{p:.3f}")


def _ic(ic, d=2):
    return f"[{ic[0]:.{d}f}, {ic[1]:.{d}f}]"


def _cifras(x):
    """3 cifras significativas (para efectos en unidades muy distintas)."""
    if x is None:
        return "—"
    if x == 0:
        return "0"
    return f"{x:.3g}" if abs(x) < 1000 else f"{x:.0f}"


def _leer_json(nombre):
    ruta = DATOS / nombre
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, timeout=10).stdout.strip() or "?"
    except Exception:
        return "?"


def generar_informe(res, extras):
    R = res["instrumentos"]
    nombres = list(R)
    L = []
    w = L.append
    w("# Instrumentos numéricos recalculados sobre texto normalizado (v2) — G1 vs G2, Par07-27")
    w("")
    w(f"- Generado: {time.strftime('%Y-%m-%d %H:%M')} · commit `{_commit()}` (árbol de trabajo con cambios sin confirmar) · "
      f"semilla de bootstrap **{res['semilla']}** (B = {res['B']}, remuestreo de parejas)")
    w("- **DESCRIPTIVO y POST HOC.** Este informe corrige un artefacto de formato del *instrumento* y mide cuánto "
      "cambian las comparaciones G1-vs-G2; **no declara ningún ganador**. La corrección se decidió DESPUÉS de ver el "
      "hallazgo de sensibilidad (`docs/reportes/sensibilidad_baseline.md`, P11), no estaba pre-especificada. "
      "Las pruebas de Wilcoxon son solo referencia (n = 21 parejas; los turnos dentro de una campaña no son independientes).")
    w(f"- Datos: 42 campañas (21 parejas, Par07-27), turnos 1-1400 por campaña en `datos_v2/par<NN>_<G1|G2>.csv`; "
      f"las medias usan los turnos ≥ {res['desde_turno']} (el turno 1 se compara con el lore, no con un turno del DM, como en la línea base).")
    w("")
    # 1 ---------------------------------------------------------------
    w("## 1. El artefacto y su corrección")
    w("")
    w("G1 escribe cada turno como `narrativa / mecanica / presion` (etiquetas en líneas solas) más una línea de tirada "
      "(«Percepción: Éxito (10 vs CD 10)»); G2 nunca. `normalizar_turno(dm, brazo)` (`scripts/reporte_v2/normalizacion.py`) deja en G1 "
      "solo la prosa (narrativa + presion), quita el bloque `mecanica`, las etiquetas y cualquier línea de tirada suelta; en G2 "
      "(y en el lore, turno 0) es la identidad salvo `.strip()`. **No** modifica `prosa()` de `validacion_generar.py`.")
    w("")
    rs = extras.get("residuos")
    if rs:
        w(f"Residuos de formato medidos sobre **{rs['n_muestra']} turnos G1 reales** (muestra aleatoria con semilla {rs['semilla']} de los 21×1399 turnos 2-1400) "
          f"y, como confirmación, sobre la población completa de G1 ({rs['poblacion_g1']['n']} turnos):")
        w("")
        w("| texto | muestra: turnos con algún residuo | etiquetas | línea de tirada | encabezados | patrón «Habilidad: Éxito/Fallo (N vs CD M)» | JSON crudo | población: con algún residuo |")
        w("|---|---|---|---|---|---|---|---|")
        for k, etiq in (("crudo", "G1 crudo"), ("prosa (validacion_generar)", "G1 tras `prosa()`"),
                        ("normalizar_turno", "G1 tras `normalizar_turno`")):
            m = rs["muestra_g1"][k]
            pob = rs["poblacion_g1"].get(k)
            w(f"| {etiq} | {m['con_algun_residuo']}/{m['n']} ({m['fraccion_con_algun_residuo']:.2%}) | {m['etiquetas']} | {m['linea_tirada']} | "
              f"{m['encabezados']} | {m['patron_habilidad']} | {m['json_crudo']} | "
              + (f"{pob['con_algun_residuo']}/{pob['n']} ({pob['fraccion_con_algun_residuo']:.2%})" if pob else "—") + " |")
        g2 = rs["muestra_g2_crudo"]
        w("")
        w(f"G2 crudo (muestra de {g2['n']}): {g2['con_algun_residuo']} turnos con algún residuo. "
          f"`normalizar_turno` difiere de `prosa` en {rs['g1_difiere_de_prosa_muestra']} turnos de la muestra y "
          f"{rs['g1_difiere_de_prosa_poblacion']} de la población: **`prosa()` no era suficiente** porque solo reconoce las etiquetas "
          "en minúscula y sin adorno; deja `**narrativa**`/`**mecanica**` en negrita (sobre todo el Par 12), «Mecanica»/«Mecánica» capitalizadas (p. ej. Par 18, 21) y los 3 turnos "
          "en que el modelo devolvió el JSON crudo (Par 13, 17, 26). Decisión de diseño: el bloque `presion` se **conserva** (es prosa dirigida al jugador, "
          "como en `prosa()`, que se usó en la validación humana ciega); ver limitaciones.")
        pp = rs.get("residuos_prosa_por_par")
        if pp:
            w("")
            w("Turnos con residuo tras `prosa()` por pareja (población G1): " + ", ".join(f"Par {k}: {v}" for k, v in pp.items()) + ".")
    w("")
    # 2 ---------------------------------------------------------------
    w("## 2. Sanidad")
    w("")
    s2 = extras.get("sanidad_g2")
    if s2:
        n = max(r["n"] for r in s2.values())
        tot = sum(r["discrepancias"] for r in s2.values())
        w(f"**G2 (la normalización es la identidad): v2 = v1 en {n} turnos × {len(s2)} columnas → {tot} discrepancias.** "
          "(v1 = valor guardado por el motor en `turn_validation`; comparación a los decimales de cada columna; bandera y recuento exactos.)")
        w("")
        w("| instrumento | turnos comparados | discrepancias | máx. \\|v1 − v2\\| |")
        w("|---|---|---|---|")
        for k, r in s2.items():
            w(f"| `{k}` | {r['n']} | {r['discrepancias']} | {r['max_abs_dif']:.3g} |")
    else:
        w("_Falta `datos_v2/sanidad_g2.json` (ejecutar recalcular.py)._")
    c1 = extras.get("control_g1")
    if c1:
        n = max(r["n"] for r in c1.values())
        tot = sum(r["discrepancias"] for r in c1.values())
        w("")
        w(f"**Control en G1:** recalcular G1 sobre el texto CRUDO con el mismo contexto reconstruido reproduce v1 en {n} turnos × {len(c1)} columnas → {tot} discrepancias. "
          "Es decir, toda diferencia v1 → v2 en G1 se debe a la normalización del texto, no a la reconstrucción del contexto.")
    w("")
    # 3 ---------------------------------------------------------------
    w("## 3. Medias por brazo (media de las 21 campañas de cada brazo; entre paréntesis, la desviación típica entre campañas)")
    w("")
    w("| instrumento | G1 v1 | G2 v1 | G1 v2 | G2 v2 | Δ G1 (v2 − v1) | Δ G2 (v2 − v1) |")
    w("|---|---|---|---|---|---|---|")
    for i in nombres:
        r = R[i]
        w(f"| {ETIQUETA[i]} (`{i}`) | {_cifras(r['v1']['media_g1'])} ({_cifras(r['v1']['sd_g1'])}) | {_cifras(r['v1']['media_g2'])} ({_cifras(r['v1']['sd_g2'])}) | "
          f"{_cifras(r['v2']['media_g1'])} ({_cifras(r['v2']['sd_g1'])}) | {_cifras(r['v2']['media_g2'])} ({_cifras(r['v2']['sd_g2'])}) | "
          f"{_cifras(r['v2']['media_g1'] - r['v1']['media_g1'])} | {_cifras(r['v2']['media_g2'] - r['v1']['media_g2'])} |")
    w("")
    w("`cr2_nombres_no_reconocidos` es la proporción de turnos con al menos un nombre no reconocido; `grammaticality_lt` usa solo 1 de cada 10 turnos "
      "(los turnos múltiplos de 10) y su v1 es LanguageTool sobre el texto crudo recalculado aquí (no se guarda en `turn_validation`).")
    w("")
    # 4 ---------------------------------------------------------------
    w("## 4. Diferencia pareada G1 − G2 por pareja, antes (v1) y después (v2) de normalizar")
    w("")
    w("n = 21 parejas. HL = Hodges-Lehmann; r = correlación rank-biserial pareada (+1 = G1 > G2 en todas las parejas); IC bootstrap 95 % remuestreando parejas; "
      "p = Wilcoxon exacto bilateral; p Holm = ajustado sobre la familia de instrumentos dentro de cada versión.")
    w("")
    w("| instrumento | versión | mediana | HL [IC95] | r [IC95] | W+ / W− | p Wilcoxon | p Holm |")
    w("|---|---|---|---|---|---|---|---|")
    for i in nombres:
        for v in ("v1", "v2"):
            r = R[i][v]
            w(f"| `{i}` | {v} | {_cifras(r['mediana'])} | {_cifras(r['hl'])} [{_cifras(r['hl_ic'][0])}, {_cifras(r['hl_ic'][1])}] | "
              f"{r['rb']:+.2f} {_ic(r['rb_ic'])} | {r['W_mas']:.1f} / {r['W_menos']:.1f} | {_fp(r['p'])} | {_fp(r['p_holm'])} |")
    w("")
    # 5 ---------------------------------------------------------------
    w("## 5. ¿Qué conclusiones G1-vs-G2 cambian al normalizar?")
    w("")
    w("«Conclusión» de un instrumento = signo y tamaño de HL(G1 − G2) y si es significativa (Wilcoxon con Holm < 0,05). Reglas fijadas antes de mirar la tabla: "
      "**cambia de signo** (HL de signo opuesto); **desaparece** (significativa en v1 y no en v2); **cambia de tamaño** (mismo signo pero |HL v2 − HL v1| > 50 % de |HL v1|); "
      "**aparece** (no significativa en v1 y sí en v2). Δr = r(v2) − r(v1) con IC bootstrap (mismas parejas remuestreadas) como medida sin unidades del cambio.")
    w("")
    w("| instrumento | HL v1 → HL v2 | r v1 → r v2 | Δr [IC95] | significativa v1 → v2 (Holm) | resultado |")
    w("|---|---|---|---|---|---|")
    cuenta = {"cambia de signo": 0, "desaparece": 0, "cambia de tamaño (>50 %)": 0, "aparece": 0, "sin cambio material": 0}
    for i in nombres:
        r = R[i]
        c = r["cambio"]
        cuenta[c["titular"]] += 1
        otras = [TITULAR[b] for b in ORDEN_BANDERAS if b in c["banderas"] and TITULAR[b] != c["titular"]]
        extra = f" (además: {', '.join(otras)})" if otras else ""
        w(f"| `{i}` | {_cifras(r['v1']['hl'])} → {_cifras(r['v2']['hl'])} | {r['v1']['rb']:+.2f} → {r['v2']['rb']:+.2f} | "
          f"{r['rb_cambio']:+.2f} {_ic(r['rb_cambio_ic'])} | {'sí' if c['signif_v1'] else 'no'} → {'sí' if c['signif_v2'] else 'no'} | "
          f"**{c['titular']}**{extra} |")
    w("")
    n = len(nombres)
    n_sig = sum(1 for i in nombres if "signo" in R[i]["cambio"]["banderas"])
    n_des = sum(1 for i in nombres if "desaparece" in R[i]["cambio"]["banderas"])
    n_tam = sum(1 for i in nombres if "tamaño" in R[i]["cambio"]["banderas"])
    n_apa = sum(1 for i in nombres if "aparece" in R[i]["cambio"]["banderas"])
    w(f"**Resumen ({n} instrumentos):** {n_sig} cambian de signo; {n_des} pierden la significancia (desaparecen); {n_tam} cambian de tamaño en más de un 50 % con el mismo signo; "
      f"{n_apa} aparecen (no significativos antes, significativos después); {cuenta['sin cambio material']} sin cambio material. "
      f"(Una misma conclusión puede llevar varias banderas; la columna «resultado» muestra la de mayor precedencia: signo > desaparece > tamaño > aparece.)")
    w("")
    # 6 ---------------------------------------------------------------
    w("## 6. Diferencias por pareja (G1 − G2)")
    w("")
    pares = R[nombres[0]]["v1"]["pares"]
    w("| instrumento | versión | " + " | ".join(pares) + " |")
    w("|---|---|" + "---|" * len(pares))
    for i in nombres:
        for v in ("v1", "v2"):
            d = R[i][v]["diferencias"]
            w(f"| `{i}` | {v} | " + " | ".join(_cifras(x) for x in d) + " |")
    w("")
    # 7 ---------------------------------------------------------------
    manual = AQUI / "lectura_manual.md"
    if manual.exists():
        w(manual.read_text(encoding="utf-8").rstrip())
        w("")
    # 8 ---------------------------------------------------------------
    w("## Limitaciones y decisiones")
    w("")
    w("- Solo se corrige el **formato** (etiquetas, bloque de mecánica, línea de tirada, JSON crudo). Lo que sigue distinguiendo a G1 de G2 tras normalizar puede ser estilo genuino de la arquitectura "
      "**o** otros restos de forma que no se han normalizado (el bloque `presion` de G1 no existe en G2; la tipografía del diálogo, abajo). Esas diferencias **no se han ajustado**: se reportan tal cual.")
    tp = (extras.get("residuos") or {}).get("tipografia_dialogo")
    if tp:
        g1t, g2t = tp["G1_normalizado"], tp["G2"]
        w(f"- Tipografía del diálogo (población, turnos 2-1400; NO normalizada): turnos con línea que empieza por raya «—»: G1 {g1t['raya']:.1%} vs G2 {g2t['raya']:.1%}; "
          f"turnos con diálogo entre comillas rectas: G1 {g1t['comillas']:.1%} vs G2 {g2t['comillas']:.1%}. Los instrumentos tokenizan por `\\w+` (TTR, bigramas, Jaccard) o parten frases por `.!?` (FH, grafo), "
          "así que la puntuación afecta sobre todo a FH y al grafo; no se ha medido cuánto.")
    w("- `presion` se conserva como prosa (igual que en `prosa()` de la validación ciega). Si se considerara formato, las cifras de G1 v2 cambiarían; no se ha explorado.")
    w("- El contexto de cada turno (entidades vigentes, escena anterior) se reconstruye como en `scripts/sensibilidad/datos.py`; el control de sanidad muestra 0 discrepancias con el valor guardado en G1 (texto crudo) y en G2. La «escena anterior» del Jaccard en v2 es el turno previo también normalizado; el lore (turno 0) no se altera.")
    w("- La gramaticalidad (LanguageTool) solo se calcula en 1 de cada 10 turnos (turnos múltiplos de 10); v1 y v2 comparten esos turnos. La categoría TYPOS está excluida como en `reporte_validacion.py`.")
    w("- Estadística: n = 21 parejas de dos lotes de configuración (Par07-17 y Par18-27); el remuestreo de parejas ignora esa estructura de lotes. Wilcoxon exacto condicional a empates y con ceros descartados; el IC de r y de HL es percentil, no corregido. El criterio «> 50 %» es sobre HL en las unidades de cada instrumento y es inestable cuando |HL v1| es pequeño (véase el IC).")
    w("- La familia de Holm es el conjunto de instrumentos de este informe, por versión; no incluye otras comparaciones del proyecto.")
    t = extras.get("tiempos")
    if t:
        w("")
        w("## Tiempos de cada etapa")
        w("")
        w("| etapa | tiempo |")
        w("|---|---|")
        for k, v in t.items():
            w(f"| {k} | {v} |")
    return "\n".join(L) + "\n"


def escribir_csv_resumen(res, destino):
    import csv
    with open(destino / "resumen_por_campana.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["par", "brazo", "instrumento", "media_v1", "media_v2", "n_turnos"])
        for r in res["por_campana"]:
            w.writerow([r["par"], r["brazo"], r["instrumento"], repr(r["v1"]), repr(r["v2"]), r["n_turnos"]])
    with open(destino / "comparacion_pares.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["instrumento", "version", "par", "diferencia_g1_menos_g2"])
        for i, r in res["instrumentos"].items():
            for v in ("v1", "v2"):
                for par, d in zip(r[v]["pares"], r[v]["diferencias"]):
                    w.writerow([i, v, par, repr(d)])
    (destino / "comparacion_estadistica.json").write_text(
        json.dumps({k: v for k, v in res.items() if k != "por_campana"}, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--semilla", type=int, default=20260920)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import datos
    t0 = time.time()
    pares = datos.cargar_pares()
    res = analizar(DATOS, pares, semilla=args.semilla, B=args.B)
    escribir_csv_resumen(res, DATOS)
    extras = {"residuos": _leer_json("residuos_formato.json"), "sanidad_g2": _leer_json("sanidad_g2.json"),
              "control_g1": _leer_json("control_g1_crudo.json"), "tiempos": _leer_json("tiempos.json")}
    if extras["tiempos"] is not None:
        extras["tiempos"]["comparación estadística y generación del informe"] = f"{time.time() - t0:.0f} s"
    INFORME.write_text(generar_informe(res, extras), encoding="utf-8")
    print(f"informe: {INFORME} ({time.time() - t0:.1f} s)")
    for i, r in res["instrumentos"].items():
        c = r["cambio"]
        print(f"  {i:32} HL {r['v1']['hl']:+.4g} -> {r['v2']['hl']:+.4g}  r {r['v1']['rb']:+.2f} -> {r['v2']['rb']:+.2f}  "
              f"pHolm {r['v1']['p_holm']:.3g} -> {r['v2']['p_holm']:.3g}  {c['titular']}")


if __name__ == "__main__":
    main()
