"""
Prueba de tendencia de Page (1963) para H1a-H1c como hipotesis de degradacion (7 bloques de 200
turnos, n=27 campanas G2, unilateral). Implementada a mano (sin scipy), mismo criterio que el resto
del proyecto (wilson/cohen/holm/fleiss duplicados a proposito -- ver experimento/scripts/sensibilidad/estadistica.py
y experimento/scripts/reporte_v2/resultados_tesis.py:wilcoxon_uni, cuyo algoritmo se replica aqui para el
Wilcoxon bloque1-vs-bloque7 sin depender de todo ese modulo fuera de linea).

Formulas (Page 1963; Siegel & Castellan 1988, "Nonparametric Statistics for the Behavioral
Sciences", cap. 7):
  Dentro de cada fila (campana), se rankean los k bloques 1..k (rango medio en empates).
  R_j = suma de rangos de la columna j sobre las n filas.
  H1 "decrece" (degradacion, ej. CR-2a/MATTR donde mayor=mejor): se espera bloque1 > ... > bloquek,
  asi que se pesa la columna j (0-indexada, orden TEMPORAL real) con w_j = k-1-j (bloque1 pesa k-1,
  bloquek pesa 0). Esto es la formula estandar de Page (pesos 1..k sobre el orden PREDICHO creciente)
  desplazada en una constante -1 por indexar desde 0 en vez de 1; L' = L_estandar - n*k*(k+1)/2, un
  corrimiento constante que se compensa en E[L] mas abajo y no afecta Var[L] (invariante a corrimientos).
  H1 "crece" (degradacion, ej. cl2_pnj_inactivo_actua/persona2 donde MENOR=mejor -- son tasas de
  error): mismos rangos, pesos w_j = j (bloque1 pesa 0, bloquek pesa k-1).
  L = suma_j w_j * R_j.
  E[L] = n*k*(k+1)^2/4 - n*k*(k+1)/2   Var[L] = n*k^2*(k+1)*(k^2-1)/144
  z = (L - E[L] - 0.5) / sqrt(Var[L])   (correccion de continuidad, cola derecha)
  p = 1 - Phi(z)
  Verificado con datos de juguete antes de tocar datos reales (ver _autotest): caso perfectamente
  degradante -> p~0; calibracion bajo H0 con n=27,k=7 (3000 simulaciones) -> ~5% de p<0.05.
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent  # raiz del repo (experimento/scripts/reporte_v2 -> ..)
K = 7


def fi(x):
    """Convierte a float; None si el valor es vacio o no numerico."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- Page (1963)
def _rango_fila(valores):
    """Rangos 1..k de una fila de valores, con rango medio en empates (base de la prueba de Page)."""
    orden = sorted(range(len(valores)), key=lambda i: valores[i])
    rangos = [0.0] * len(valores)
    i = 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and valores[orden[j + 1]] == valores[orden[i]]:
            j += 1
        prom = (i + 1 + j + 1) / 2
        for t in range(i, j + 1):
            rangos[orden[t]] = prom
        i = j + 1
    return rangos


def _Phi(z):
    """Funcion de distribucion normal estandar, via `math.erf`."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def page_L(matriz, direccion="decrece"):
    """matriz: lista de filas (una por campana), cada fila con k valores EN ORDEN TEMPORAL real
    (bloque1..bloquek). H1 'decrece' = degradacion monotona; H0 = no decrece (no arbitraria)."""
    n = len(matriz)
    k = len(matriz[0])
    assert all(len(f) == k for f in matriz), "todas las filas deben tener los mismos k bloques"
    rangos = [_rango_fila(f) for f in matriz]
    R = [sum(fila[j] for fila in rangos) for j in range(k)]
    pesos = [k - 1 - j for j in range(k)] if direccion == "decrece" else [j for j in range(k)]
    L = sum(pesos[j] * R[j] for j in range(k))
    EL = n * k * (k + 1) ** 2 / 4 - n * k * (k + 1) / 2  # ajustado al offset de pesos 0..k-1 (ver nota)
    VarL = n * k * k * (k + 1) * (k * k - 1) / 144
    if VarL <= 0:
        return {"L": L, "z": None, "p": None, "n": n, "k": k, "R": R}
    z = (L - EL - 0.5) / math.sqrt(VarL)
    p = max(0.0, min(1.0, 1 - _Phi(z)))
    return {"L": L, "EL": EL, "VarL": VarL, "z": z, "p": p, "n": n, "k": k, "R": R}


# ---------------------------------------------------------------- Wilcoxon exacto (bloque1 vs bloquek)
# Mismo algoritmo que experimento/scripts/reporte_v2/resultados_tesis.py:wilcoxon_uni -- duplicado a proposito
# (documentado) para no importar todo ese modulo (numpy) fuera de linea.
def _rangos_medios(valores_abs):
    """Rangos medios de `valores_abs` (alias de `_rango_fila`, para el Wilcoxon)."""
    return _rango_fila(valores_abs)


def wilcoxon_uni(d):
    """Wilcoxon de rangos con signo EXACTO sobre las diferencias `d` bloque1 - bloque7 (ceros descartados, empates por rango medio).

    Returns:
        Dict con n efectivo y los p-valores bilateral (`p_bi`), de cola superior (`p_mas`, H1 «b1 > b7») e
        inferior (`p_menos`, H1 «b1 < b7»), por programacion dinamica sobre rangos duplicados.
    """
    d = [x for x in d if x != 0]
    n = len(d)
    if n == 0:
        return {"n": 0, "p_bi": 1.0, "p_mas": 1.0, "p_menos": 1.0}
    r = _rangos_medios([abs(x) for x in d])
    r2 = [round(2 * x) for x in r]
    total = int(sum(r2))
    cuenta = [0] * (total + 1)
    cuenta[0] = 1
    for x in r2:
        x = int(x)
        for s in range(total, x - 1, -1):
            cuenta[s] += cuenta[s - x]
    obs = int(sum(r2[i] for i in range(n) if d[i] > 0))
    ge = sum(cuenta[obs:])
    le = sum(cuenta[:obs + 1])
    bi = sum(c for s, c in enumerate(cuenta) if abs(2 * s - total) >= abs(2 * obs - total))
    den = 2 ** n
    return {"n": n, "p_bi": min(1.0, bi / den), "p_mas": ge / den, "p_menos": le / den}


def holm(pvals):
    """Correccion de Holm-Bonferroni (p ajustados monotonos, tope 1.0) en el orden original de `pvals`."""
    m = len(pvals)
    orden = sorted(range(m), key=lambda i: pvals[i])
    ajustados = [0.0] * m
    previo = 0.0
    for rango, i in enumerate(orden):
        previo = max(previo, min(1.0, (m - rango) * pvals[i]))
        ajustados[i] = previo
    return ajustados


# ---------------------------------------------------------------- autoverificacion con datos de juguete
def _autotest():
    """Autoverificacion de `page_L` con datos de juguete antes de tocar datos reales.

    Comprueba que una degradacion perfecta da p < 0.001 y que, bajo H0 (n=27, k=7, 3000 simulaciones), la
    fraccion de p < 0.05 queda entre 3 % y 7 %.
    """
    import random
    rnd = random.Random(0)
    # 1) caso perfectamente degradante (bloque_j decreciente + ruido minimo): p debe ser ~0
    perfecto = [[7 - j + rnd.uniform(-0.05, 0.05) for j in range(7)] for _ in range(20)]
    r_perfecto = page_L(perfecto)
    assert r_perfecto["p"] < 0.001, r_perfecto
    # 2) calibracion bajo H0 (sin tendencia real, n=27 k=7 como los datos reales): la fraccion de
    # p simulados < 0.05 debe rondar 0.05 (si el z/p estuviera mal calculado, se veria sesgado aqui)
    n, k, trials = 27, 7, 3000
    bajo05 = sum(1 for _ in range(trials) if page_L([[rnd.random() for _ in range(k)] for _ in range(n)])["p"] < 0.05)
    frac = bajo05 / trials
    assert 0.03 < frac < 0.07, f"calibracion H0 fuera de rango: {frac} (esperado ~0.05)"
    print(f"  autotest Page OK: degradacion perfecta p={r_perfecto['p']:.2e} (z={r_perfecto['z']:.2f}); "
          f"calibracion H0 ({trials} sim., n={n} k={k}): {frac:.3%} de p<0.05 (esperado ~5%)")


# ---------------------------------------------------------------- carga de datos ya materializados
def leer(ruta):
    """Lee un CSV (utf-8-sig) como lista de dicts."""
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def matriz_g2(filas, col_par, col_bloque, col_valor, filtro=None):
    """{par: [v_bloque1..v_bloque7]} para brazo=G2, ordenado por par."""
    porpar = defaultdict(dict)
    for r in filas:
        if r.get("brazo") != "G2":
            continue
        if filtro and not filtro(r):
            continue
        v = fi(r[col_valor])
        if v is None:
            continue
        porpar[r[col_par]][int(r[col_bloque])] = v
    pares = sorted(p for p, b in porpar.items() if len(b) == K)
    incompletos = sorted(p for p, b in porpar.items() if len(b) != K)
    return pares, [[porpar[p][j] for j in range(1, K + 1)] for p in pares], incompletos


def main():
    """Corre la prueba de Page para H1a-H1c (degradacion por bloques de 200 turnos, n=27 campanas G2) y escribe `docs/reportes/degradacion_bloques.md`.

    Orden: autotest, carga de CR-2a/CL/MATTR/persona2 por bloque, Page unilateral y Wilcoxon bloque1-vs-7 en la
    direccion de H1 de cada instrumento (`DIRECCION`, tomada de `consolidar.py`), Holm dentro de H1b y de H1c, e
    informe con la lectura honesta (la nula «no degrada» se sostiene si los datos no la rechazan).
    `cl2_lugar_jaccard` no tiene sentido de mejora definido: se reporta aparte, bilateral.
    """
    print("Autoverificacion de la prueba de Page antes de tocar datos reales:")
    _autotest()
    print()

    a4bc = leer(RAIZ / "docs" / "reportes" / "sensibilidad_a4bc_distribucion_27.csv")
    bloques = leer(RAIZ / "datos" / "datos_v2" / "cierre" / "bloques.csv")
    ruta_rel = RAIZ / "datos" / "datos_v2" / "cierre" / "pnj_inactivo_relativizado.csv"
    relativizado = leer(ruta_rel) if ruta_rel.exists() else None

    resultados = {}

    # H1a -- CR-2a(z), ya viene agregado por bloque en sensibilidad_a4bc_distribucion_27.csv (ini/fin en vez de bloque 1..7)
    for r in a4bc:
        r["bloque"] = str((int(r["ini"]) - 1) // 200 + 1)
    pares_a, mat_a, inc_a = matriz_g2(a4bc, "par", "bloque", "z")
    resultados["H1a_cr2a_z"] = (pares_a, mat_a, inc_a)

    # H1b -- CL crudo (sin relativizar -- ver caveat en el reporte)
    pares_b1, mat_b1, inc_b1 = matriz_g2(bloques, "par", "bloque", "valor", lambda r: r["indicador"] == "cl2_lugar_jaccard_similarity")
    pares_b2, mat_b2, inc_b2 = matriz_g2(bloques, "par", "bloque", "valor", lambda r: r["indicador"] == "cl2_pnj_inactivo_actua")
    resultados["H1b_cl_lugar_jaccard"] = (pares_b1, mat_b1, inc_b1)
    resultados["H1b_cl_pnj_inactivo_crudo"] = (pares_b2, mat_b2, inc_b2)
    if relativizado is not None:
        # denominador = turnos con >=1 PNJ ya inactivo visible (ver relativizar_pnj_inactivo.py);
        # corrige el confusor de la version cruda (pendiente #1 del informe anterior)
        pares_b3, mat_b3, inc_b3 = matriz_g2(relativizado, "par", "bloque", "tasa_relativizada")
        resultados["H1b_cl_pnj_inactivo_relativizado"] = (pares_b3, mat_b3, inc_b3)

    # H1c -- MATTR (exploratorio) y persona2 primaria (confirmatorio condicionado a auditoria de Luis)
    pares_c1, mat_c1, inc_c1 = matriz_g2(bloques, "par", "bloque", "valor", lambda r: r["indicador"] == "mattr")
    pares_c2, mat_c2, inc_c2 = matriz_g2(bloques, "par", "bloque", "valor", lambda r: r["indicador"] == "primaria")
    resultados["H1c_mattr"] = (pares_c1, mat_c1, inc_c1)
    resultados["H1c_persona2_primaria"] = (pares_c2, mat_c2, inc_c2)

    # Direccion "mayor=mejor" por instrumento, tomada TAL CUAL de consolidar.py (columna sentido):
    #   cr2a_z ↑, mattr ↑  -> degradacion = DISMINUYE  (direccion='decrece')
    #   cl2_pnj_inactivo_actua ↓, p2_primaria ↓ (son tasas de ERROR) -> degradacion = AUMENTA (direccion='crece')
    #   cl2_lugar_jaccard_similarity '·' (consolidar.py: "sin sentido de mejora, solo bilateral") -> NO tiene
    #   una hipotesis de degradacion unilateral bien definida con la ficha actual; se reporta aparte, bilateral.
    DIRECCION = {
        "H1a_cr2a_z": "decrece",
        "H1c_mattr": "decrece",
        "H1b_cl_pnj_inactivo_crudo": "crece",
        "H1b_cl_pnj_inactivo_relativizado": "crece",
        "H1c_persona2_primaria": "crece",
    }

    print(f"{'instrumento':28s} {'n':>3s} {'incompletos':>11s} {'L':>10s} {'z':>7s} {'p unilateral':>13s}  {'Wilcoxon b1vs b7 (direccion H1)':>32s}  bloque1->bloque7 (mediana)")
    filas_reporte = []
    for nombre, (pares, mat, inc) in resultados.items():
        if len(mat) < 5:
            print(f"{nombre:28s}  -- insuficiente ({len(mat)} campanas completas) --  incompletos={inc}")
            continue
        if nombre not in DIRECCION:
            print(f"{nombre:28s}  -- sin direccion de mejora definida en la ficha ('·' en consolidar.py) -- se reporta abajo, bilateral")
            continue
        direccion = DIRECCION[nombre]
        res = page_L(mat, direccion=direccion)
        b1 = [fila[0] for fila in mat]
        b7 = [fila[6] for fila in mat]
        # d y p_wilcoxon en la direccion de H1 (degradacion): si direccion='decrece', H1 es b1>b7 (d=b1-b7>0, p_mas);
        # si direccion='crece', H1 es b7>b1 (d=b1-b7<0, p_menos).
        d = [x - y for x, y in zip(b1, b7)]
        wl = wilcoxon_uni(d)
        p_wilcoxon_h1 = wl["p_mas"] if direccion == "decrece" else wl["p_menos"]
        med_b1 = sorted(b1)[len(b1) // 2]
        med_b7 = sorted(b7)[len(b7) // 2]
        filas_reporte.append((nombre, res, wl, med_b1, med_b7))
        print(f"{nombre:28s} {res['n']:>3d} {len(inc):>11d} {res['L']:>10.1f} {res['z']:>7.2f} {res['p']:>13.4f}  "
              f"{p_wilcoxon_h1:>32.4f}  {med_b1:.3f} -> {med_b7:.3f}  ({direccion})")

    print()
    print("cl2_lugar_jaccard_similarity -- sin direccion 'mejor' en la ficha (bilateral), reportado descriptivamente:")
    for nombre in ("H1b_cl_lugar_jaccard",):
        pares, mat, inc = resultados[nombre]
        res_dec = page_L(mat, direccion="decrece")
        res_cre = page_L(mat, direccion="crece")
        print(f"  {nombre}: n={res_dec['n']}  p(disminuye)={res_dec['p']:.4f} (z={res_dec['z']:.2f})  "
              f"p(aumenta)={res_cre['p']:.4f} (z={res_cre['z']:.2f})  bilateral={2*min(res_dec['p'], res_cre['p']):.4f}")

    print()
    print("Holm dentro de H1c (mattr + persona2_primaria, las 2 confirmatorias/condicionadas de esa hipotesis):")
    claves_c = ["H1c_mattr", "H1c_persona2_primaria"]
    ps = [dict((n, r) for n, r, *_ in filas_reporte)[c]["p"] for c in claves_c if c in dict((n, r) for n, r, *_ in filas_reporte)]
    if len(ps) == 2:
        adj = holm(ps)
        for c, p, pa in zip(claves_c, ps, adj):
            print(f"  {c}: p={p:.4f} -> p_holm={pa:.4f}")

    b2_clave = "H1b_cl_pnj_inactivo_relativizado" if relativizado is not None else "H1b_cl_pnj_inactivo_crudo"
    print()
    print(f"Holm dentro de H1b (cl_lugar_jaccard + {b2_clave}):")
    claves_b = ["H1b_cl_lugar_jaccard", b2_clave]
    ps_b = [dict((n, r) for n, r, *_ in filas_reporte)[c]["p"] for c in claves_b if c in dict((n, r) for n, r, *_ in filas_reporte)]
    holm_b = {}
    if len(ps_b) == 2:
        adj = holm(ps_b)
        holm_b = dict(zip(claves_b, adj))
        for c, p, pa in zip(claves_b, ps_b, adj):
            print(f"  {c}: p={p:.4f} -> p_holm={pa:.4f}")

    # ---------- informe
    dicc = {n: (r, wl, med1, med7) for n, r, wl, med1, med7 in filas_reporte}
    holm_c = dict(zip(claves_c, holm(ps))) if len(ps) == 2 else {}
    lc = resultados["H1b_cl_lugar_jaccard"]
    res_dec = page_L(lc[1], direccion="decrece")
    res_cre = page_L(lc[1], direccion="crece")
    sig_alpha = 0.05

    L = ["# Prueba de tendencia de Page (1963) para H1a-H1c -- degradacion por bloques de 200 turnos",
         "",
         "Generado por `experimento/scripts/reporte_v2/page_test.py`. Fuente: `docs/reportes/sensibilidad_a4bc_distribucion_27.csv` "
         "(CR-2a por bloque, ya calculado el 2026-09-21), `datos/datos_v2/cierre/bloques.csv` (CL/MATTR/persona2 por bloque) y, "
         "cuando ya existe, `datos/datos_v2/cierre/pnj_inactivo_relativizado.csv` (generado por "
         "`experimento/scripts/reporte_v2/relativizar_pnj_inactivo.py`, que sí necesita acceso a la base de datos -- solo SELECT sobre "
         "`npcs`/`state_deltas`, sin LLM). H0 = 'no disminuye/no aumenta' (no arbitraria); H1 = degradacion monotona a lo "
         "largo de la campana G2 (7 bloques de 200 turnos, n=27). Prueba de Page unilateral + Wilcoxon exacto "
         "bloque1-vs-bloque7 como complemento.",
         "",
         "**Autoverificacion antes de correr sobre datos reales**: caso de juguete perfectamente degradante -> p~0; "
         "calibracion bajo H0 (3000 simulaciones, n=27 k=7) -> ~5% de p<0.05 (formula y signo confirmados, no solo revisados a ojo).",
         "",
         "## Resultado",
         "",
         "| Hipotesis / instrumento | direccion H1 | n | Page z | Page p (unilateral) | Wilcoxon p (bloque1 vs 7) | mediana bloque1 -> bloque7 |",
         "|---|---|---|---|---|---|---|"]
    filas_tabla = [("H1a_cr2a_z", "H1a -- CR-2a(z), confirmatorio"),
                   ("H1b_cl_pnj_inactivo_crudo", "H1b -- PNJ inactivo mencionado, CRUDO (sin relativizar; confundido, ver Lectura)")]
    if relativizado is not None:
        filas_tabla.append(("H1b_cl_pnj_inactivo_relativizado",
                            "H1b -- PNJ inactivo mencionado, RELATIVIZADO (denominador = turnos con >=1 PNJ ya inactivo)"))
    filas_tabla += [("H1c_mattr", "H1c -- MATTR, exploratorio"),
                    ("H1c_persona2_primaria", "H1c -- persona2 primaria, condicionado a auditoria")]
    resumen = []
    for nombre, etiqueta in filas_tabla:
        if nombre not in dicc:
            continue
        r, wl, med1, med7 = dicc[nombre]
        direccion = DIRECCION[nombre]
        p_w = wl["p_mas"] if direccion == "decrece" else wl["p_menos"]
        L.append(f"| {etiqueta} | {direccion} | {r['n']} | {r['z']:.2f} | {r['p']:.4f} | {p_w:.4f} | {med1:.3f} -> {med7:.3f} |")
        resumen.append((nombre, r["p"] < sig_alpha))
    n_sig = sum(1 for _, s in resumen if s)
    n_tot = len(resumen)

    L += ["",
          "`cl2_lugar_jaccard_similarity` no tiene direccion 'mejor' definida en la ficha (`consolidar.py`: '·', bilateral) -- "
          f"reportado aparte: p(disminuye)={res_dec['p']:.4f}, p(aumenta)={res_cre['p']:.4f}, bilateral={2*min(res_dec['p'], res_cre['p']):.4f} "
          "(sube significativamente -- lectura ambigua: mas continuidad lexica con la escena anterior, o mas repeticion/estancamiento; "
          "la propia ficha ya advierte que este instrumento 'no distingue deriva de evolucion legitima del mundo').",
          ""]
    if holm_c:
        L.append("**Holm dentro de H1c** (mattr + persona2_primaria): " + ", ".join(f"{c} p_holm={v:.4f}" for c, v in holm_c.items()))
        L.append("")
    if holm_b:
        L.append(f"**Holm dentro de H1b** (cl_lugar_jaccard + {b2_clave}): " + ", ".join(f"{c} p_holm={v:.4f}" for c, v in holm_b.items()))
        L.append("")

    L += ["## Lectura", "",
          f"Con los datos reales, **{n_tot - n_sig} de {n_tot} instrumentos NO muestran degradacion significativa** "
          "(mas `cl2_lugar_jaccard`, que no tiene direccion definida). El resultado crudo de `cl2_pnj_inactivo_actua` "
          "(sin relativizar) es justamente el indicador que la propia propuesta señalaba como el mas expuesto a un "
          "confusor: mas PNJ estan muertos/desaparecidos hacia el final de la campana, asi que la tasa de turnos que los "
          "narra como activos puede subir solo porque hay mas PNJ inactivos elegibles para el error, no porque el sistema "
          "degrade."]

    if "H1b_cl_pnj_inactivo_relativizado" in dicc:
        r_rel, wl_rel, med1_rel, med7_rel = dicc["H1b_cl_pnj_inactivo_relativizado"]
        direccion_rel = DIRECCION["H1b_cl_pnj_inactivo_relativizado"]
        p_w_rel = wl_rel["p_mas"] if direccion_rel == "decrece" else wl_rel["p_menos"]
        _, _, inc_rel = resultados["H1b_cl_pnj_inactivo_relativizado"]
        crudo_sig = dicc["H1b_cl_pnj_inactivo_crudo"][0]["p"] < sig_alpha
        rel_sig = r_rel["p"] < sig_alpha
        if crudo_sig and not rel_sig:
            lectura_rel = ("La significancia desaparece al relativizar por PNJ ya inactivos: consistente con que el "
                          "resultado crudo era el confusor sospechado, no degradacion real de la coherencia.")
        elif rel_sig:
            lectura_rel = ("Sigue significativo incluso relativizado por PNJ ya inactivos -- esto SI es evidencia mas "
                          "solida de degradacion real (no solo un artefacto del denominador).")
        else:
            lectura_rel = "Tampoco era significativo el crudo, asi que la relativizacion no cambia la conclusion aqui."
        L.append("")
        L.append(
            "**Version relativizada** (resuelve el pendiente #1 de la version anterior de este informe -- ver "
            "`experimento/scripts/reporte_v2/relativizar_pnj_inactivo.py` y `datos/datos_v2/cierre/pnj_inactivo_relativizado.csv`): "
            "denominador = turnos del bloque donde ya habia al menos un PNJ inactivo visible (reconstruido turno a turno "
            "desde `npcs`/`state_deltas`, la misma logica que usa el motor para `estados_pnj`), en vez de los 200 turnos "
            f"del bloque. Resultado: Page z={r_rel['z']:.2f} p={r_rel['p']:.4f} (Wilcoxon bloque1-vs-7 p={p_w_rel:.4f}; "
            f"mediana {med1_rel:.3f} -> {med7_rel:.3f}; n={r_rel['n']} campanas completas, {len(inc_rel)} excluidas por "
            f"tener algun bloque sin ningun PNJ inactivo todavia -- tipicamente el bloque 1). {lectura_rel}")
    else:
        L.append("")
        L.append(
            "**Este resultado crudo no se puede reportar como evidencia de degradacion hasta relativizarlo** "
            "(denominador = PNJ ya inactivos hasta ese bloque, no turnos totales del bloque) -- sigue pendiente correr "
            "`experimento/scripts/reporte_v2/relativizar_pnj_inactivo.py` con acceso a la base de datos (ver Pendiente #1 abajo).")

    if "H1c_persona2_primaria" in dicc:
        r_p2 = dicc["H1c_persona2_primaria"][0]
        p2_holm = holm_c.get("H1c_persona2_primaria")
        L.append("")
        L.append(
            f"`persona2_primaria` (p={r_p2['p']:.4f} sin corregir" +
            (f", p_holm={p2_holm:.4f}" if p2_holm is not None else "") +
            ") sugiere en el mejor de los casos una tendencia leve, y de todas formas sigue pendiente de una auditoria de "
            "precision con un evaluador EXTERNO (no el equipo investigador -- ver correccion en "
            "`claude/persona2-auditoria-IA-analisis.md`) para poder tratarse como confirmatorio.")

    L += ["",
          "**Conclusion honesta para el asesor**: la redefinicion de H1a-H1c como hipotesis de degradacion es tecnicamente "
          "solida (formula verificada, reutiliza instrumentos ya validados, resuelve el problema real del punto medio de "
          "Likert que ya estaba documentado en `resultados_tesis.py`), pero los datos, hasta ahora, no confirman de forma "
          "robusta la premisa de degradacion que motivo la propuesta. Es un hallazgo legitimo en si mismo (la nula 'no "
          "degrada' se sostiene en la mayoria de los instrumentos, con una H0 no arbitraria como pedia el diseño), pero "
          "cambia la narrativa: no es 'confirmamos que el sistema monolitico degrada', es 'probamos rigurosamente si "
          "degrada y, con esta instrumentacion, la evidencia es limitada'.",
          "",
          "## Pendiente antes de escribir el capitulo 6 con esto",
          ""]
    pendientes = []
    if "H1b_cl_pnj_inactivo_relativizado" not in dicc:
        pendientes.append("Definir y correr la version relativizada de `cl2_pnj_inactivo_actua` (denominador = PNJ ya "
                          "inactivos a esa altura de la campana) -- requiere acceso a la base de datos; el script ya "
                          "existe (`experimento/scripts/reporte_v2/relativizar_pnj_inactivo.py`), solo falta ejecutarlo y volver a "
                          "correr este informe.")
    else:
        pendientes.append("Version relativizada de `cl2_pnj_inactivo_actua`: **hecho** (ver arriba). Revisar con el "
                          "asesor si la lectura (confusor confirmado o degradacion real) es la que se reporta en el "
                          "capitulo 6.")
    pendientes.append("Cerrar la auditoria de precision de persona2 con un evaluador EXTERNO al equipo investigador "
                      "(Brecha 3) antes de tratar `persona2_primaria` como confirmatorio.")
    pendientes.append("Decidir con el asesor si `cl2_lugar_jaccard_similarity` entra a H1b con una direccion 'mejor' "
                      "definida, o se deja fuera del contraste inferencial y solo se describe.")
    pendientes.append("Confirmar la regla de decision de la hipotesis general (si H1a-c entran a la misma regla 'solo se "
                      "sostiene si a,b,c,d,e,f se sostienen' junto con H1d-f, y si Holm debe correr sobre esas 6 juntas en "
                      "vez de por hipotesis separada, que es como esta hoy).")
    L += [f"{i}. {t}" for i, t in enumerate(pendientes, 1)]

    destino = RAIZ / "docs" / "reportes"
    destino.mkdir(parents=True, exist_ok=True)
    ruta_salida = destino / "degradacion_bloques.md"
    ruta_salida.write_text("\n".join(L), encoding="utf-8")
    print(f"\n-> informe: {ruta_salida}")


if __name__ == "__main__":
    main()
