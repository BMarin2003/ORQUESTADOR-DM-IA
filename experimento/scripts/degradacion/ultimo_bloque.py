"""
¿Hay un quiebre al final? Análisis EXPLORATORIO del último bloque de 100 turnos (1301-1400).

NO es una docimasia nueva: H1a-H1c ya se contrastaron con Page sobre 7 bloques de 200. Esto responde
a una pregunta posterior ("¿la degradación empieza al final?") y se reporta como exploratorio, para
sustentar o descartar la recomendación de probar campañas más largas.

Tres lecturas por indicador y brazo (una campaña por par, n = 27):
  A. salto final:        b14 − media(b12, b13)                    (Wilcoxon bilateral, por brazo)
  B. fuera de tendencia: b14 − predicción OLS de b1..b13          (Wilcoxon bilateral, por brazo)
  C. dif-en-dif:         salto_G1 − salto_G2 dentro de cada par   (Wilcoxon bilateral)
Holm dentro de cada lectura sobre todos los indicadores (familia exploratoria).

Fuentes, solo lectura: datos/datos_v2/par*_G*.csv, datos/datos_v2/booleanos, datos/datos_v2/persona2 (por turno) y,
salvo --sin-cr2a, CR-2a(z) por turno recalculado con correr_a4bc/respuesta_accion (mismo código que
distribucion_a4bc_27.py, solo que sin promediar en ventanas de 200).

    $env:PYTHONUTF8="1"; py experimento/scripts/degradacion/ultimo_bloque.py [--sin-cr2a]
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

RAIZ = Path(__file__).resolve().parents[3]
D2 = RAIZ / "datos" / "datos_v2"
SALIDA = RAIZ / "docs" / "reportes" / "degradacion"
HASTA, TAM = 1400, 100
NB = HASTA // TAM  # 14

# indicador -> (archivo relativo a datos_v2, columna, sentido de "peor")
FUENTES = {
    "qn1_ttr": ("par{p}_{b}.csv", "qn1_ttr_v2", "baja"),
    "qn1_ngram_repeticion": ("par{p}_{b}.csv", "qn1_ngram_repeticion_v2", "sube"),
    "qn1_legibilidad_fh": ("par{p}_{b}.csv", "qn1_legibilidad_fh_v2", "?"),
    "cl2_lugar_jaccard": ("par{p}_{b}.csv", "cl2_lugar_jaccard_similarity_v2", "?"),
    "cr2_nombres_no_reconocidos": ("par{p}_{b}.csv", "cr2_n_nombres_no_reconocidos_v2", "sube"),
    "cr1_contradice_narracion": ("booleanos/par{p}_{b}.csv", "cr1_veredicto_contradice_narracion_v2", "sube"),
    "cl2_pnj_inactivo_actua": ("booleanos/par{p}_{b}.csv", "cl2_pnj_inactivo_actua_v2", "sube"),
    "qn2_persona2_primaria": ("persona2/par{p}_{b}.csv", "primaria", "sube"),
    "qn2_persona2_secundaria": ("persona2/par{p}_{b}.csv", "secundaria", "sube"),
}


def fnum(x):
    """Convierte a float; None si no es numérico o no es finito."""
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def bloques_de(serie):
    """{turno: valor} -> [media bloque 1..14] (None si el bloque no tiene datos)."""
    acc = defaultdict(list)
    for t, v in serie.items():
        if 1 <= t <= HASTA and v is not None:
            acc[(t - 1) // TAM + 1].append(v)
    return [float(np.mean(acc[k])) if acc[k] else None for k in range(1, NB + 1)]


def leer_por_turno():
    """{indicador: {(brazo, par): [14 bloques]}} desde los CSV por turno."""
    out = defaultdict(dict)
    for p in range(1, 28):
        par = f"{p:02d}"
        for b in ("G1", "G2"):
            cache = {}
            for ind, (patron, col, _) in FUENTES.items():
                ruta = D2 / patron.format(p=par, b=b)
                if ruta not in cache:
                    with open(ruta, encoding="utf-8-sig", newline="") as f:
                        cache[ruta] = list(csv.DictReader(f))
                serie = {int(r["turn_id"]): fnum(r.get(col)) for r in cache[ruta]}
                out[ind][(b, par)] = bloques_de(serie)
    return out


def leer_cr2a():
    """CR-2a(z) por turno con el mismo código que distribucion_a4bc_27.py."""
    aqui = RAIZ / "experimento" / "scripts" / "instrumentos"
    for q in (aqui, RAIZ / "experimento" / "scripts" / "reporte_v2", RAIZ / "experimento" / "scripts" / "sensibilidad", RAIZ / "experimento" / "scripts", RAIZ / "motor" / "orquestador"):
        if str(q) not in sys.path:
            sys.path.insert(0, str(q))
    import correr_a4bc as C
    import datos
    import distribucion_a4bc_27 as D
    import pares as _pares
    import respuesta_accion as ra
    conn = D.ConnRecortada(datos.abrir_conexion())
    camps, _ = C.cargar_campanas(conn, _pares.todos(), lambda s: print(s, flush=True))
    out = {}
    for c in camps.values():
        serie = {t: ra.medir(c.pool, t, None, tokens_respuesta=c.tokR[t])["z"] for t in sorted(c.tokR)}
        out[(c.brazo, f"{int(c.par):02d}")] = bloques_de(serie)
    return out


def holm(ps):
    """Ajuste de Holm-Bonferroni (monótono, tope 1.0) en el orden original de `ps`."""
    idx = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, m, prev = [None] * len(ps), len(ps), 0.0
    for r, i in enumerate(idx):
        prev = max(prev, min(1.0, (m - r) * ps[i]))
        adj[i] = prev
    return adj


def wil(d):
    """Wilcoxon bilateral (scipy) sobre las diferencias `d`, descartando None y ceros.

    Returns:
        (n efectivo, mediana, p, nº de positivas); con menos de 6 diferencias, (n, None, None, None).
    """
    d = [x for x in d if x is not None and abs(x) > 1e-12]
    if len(d) < 6:
        return len(d), None, None, None
    w = wilcoxon(d, alternative="two-sided")
    pos = sum(x > 0 for x in d)
    return len(d), float(np.median(d)), float(w.pvalue), pos


def salto(bl):
    """Lectura A: b14 − media(b12, b13); None si falta alguno de los tres bloques."""
    if None in (bl[11], bl[12], bl[13]):
        return None
    return bl[13] - (bl[11] + bl[12]) / 2


def fuera_tendencia(bl):
    """Lectura B: b14 menos su predicción por OLS lineal sobre b1..b13; None si hay menos de 8 bloques previos o falta b14."""
    xs = [k for k in range(13) if bl[k] is not None]
    if len(xs) < 8 or bl[13] is None:
        return None
    pend, inter = np.polyfit(xs, [bl[k] for k in xs], 1)
    return bl[13] - (inter + pend * 13)


def analizar(series):
    """Aplica las tres lecturas (A salto, B fuera de tendencia, C dif-en-dif G1−G2) por indicador y brazo.

    Holm se calcula dentro de cada lectura sobre todos los indicadores (familia exploratoria). No es una docimasia nueva.
    """
    filas = []
    for ind, dic in series.items():
        pares = sorted({p for _, p in dic})
        for lectura, fn in (("A_salto", salto), ("B_tendencia", fuera_tendencia)):
            for b in ("G1", "G2"):
                r = wil([fn(dic[(b, p)]) for p in pares if (b, p) in dic])
                filas.append({"indicador": ind, "lectura": lectura, "brazo": b, "r": r})
        dd = [salto(dic[("G1", p)]) - salto(dic[("G2", p)]) for p in pares
              if ("G1", p) in dic and ("G2", p) in dic and None not in (salto(dic[("G1", p)]), salto(dic[("G2", p)]))]
        filas.append({"indicador": ind, "lectura": "C_difendif", "brazo": "G1-G2", "r": wil(dd)})
    for lect in {f["lectura"] for f in filas}:
        grupo = [f for f in filas if f["lectura"] == lect and f["r"][2] is not None]
        for f, a in zip(grupo, holm([f["r"][2] for f in grupo])):
            f["p_holm"] = a
    return filas


def medias_bloque(series):
    """Media entre pares por bloque, para la figura/tabla descriptiva."""
    out = []
    for ind, dic in series.items():
        for b in ("G1", "G2"):
            vals = [dic[k] for k in dic if k[0] == b]
            for j in range(NB):
                xs = [v[j] for v in vals if v[j] is not None]
                out.append({"indicador": ind, "brazo": b, "bloque": j + 1,
                            "media": float(np.mean(xs)) if xs else None, "n": len(xs)})
    return out


SENTIDO = {k: v[2] for k, v in FUENTES.items()} | {"cr2a_z": "baja"}


def escribir(filas, medias):
    """Escribe `ultimo_bloque_medias.csv`, `ultimo_bloque_pruebas.csv` y `ultimo_bloque.md` en `docs/reportes/degradacion/`."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / "ultimo_bloque_medias.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["indicador", "brazo", "bloque", "media", "n"])
        w.writeheader()
        w.writerows(medias)
    with open(SALIDA / "ultimo_bloque_pruebas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["indicador", "sentido_peor", "lectura", "brazo", "n", "mediana", "positivos", "p", "p_holm"])
        for x in filas:
            n, med, p, pos = x["r"]
            w.writerow([x["indicador"], SENTIDO[x["indicador"]], x["lectura"], x["brazo"], n,
                        med, pos, p, x.get("p_holm")])
    lineas = ["# Último bloque (1301-1400): análisis exploratorio", "",
              "Bloques de 100 turnos; una campaña por par (n = 27 por brazo). Wilcoxon bilateral; Holm dentro de cada lectura.",
              "A = b14 − media(b12, b13); B = b14 − predicción OLS de b1..b13; C = salto G1 − salto G2 por par.", "",
              "| indicador | peor si | lectura | brazo | n | mediana | + | p | p Holm |", "|---|---|---|---|---|---|---|---|---|"]
    for x in filas:
        n, med, p, pos = x["r"]
        f = lambda v, d=4: "—" if v is None else f"{v:.{d}f}"  # noqa: E731
        lineas.append(f"| {x['indicador']} | {SENTIDO[x['indicador']]} | {x['lectura']} | {x['brazo']} | {n} | "
                      f"{f(med)} | {pos if pos is not None else '—'} | {f(p, 3)} | {f(x.get('p_holm'), 3)} |")
    (SALIDA / "ultimo_bloque.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    """Lee los indicadores por turno (CR-2a(z) salvo `--sin-cr2a`), corre `analizar`, escribe los resultados e imprime cada fila con la marca `p_holm<.05`."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    series = leer_por_turno()
    if "--sin-cr2a" not in sys.argv:
        series["cr2a_z"] = leer_cr2a()
    filas = analizar(series)
    escribir(filas, medias_bloque(series))
    for x in filas:
        n, med, p, pos = x["r"]
        marca = " <== p_holm<.05" if x.get("p_holm") is not None and x["p_holm"] < 0.05 else ""
        print(f"{x['indicador']:28s} {x['lectura']:12s} {x['brazo']:6s} n={n:2d} med={med if med is None else round(med, 4)!s:>9} "
              f"+={pos!s:>3} p={p if p is None else round(p, 3)!s:>6} holm={x.get('p_holm') if x.get('p_holm') is None else round(x['p_holm'], 3)!s:>6}{marca}")
    print(f"\nescrito en {SALIDA}")


if __name__ == "__main__":
    main()
