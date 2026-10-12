"""
Estadística del arnés de sensibilidad (sin scipy: solo math + numpy).

Todas las reglas de decisión son convenciones publicadas, fijadas ANTES de ver
resultados:
  * Wilson (1927) para proporciones; Newcombe (1998, método 10) para la
    diferencia de proporciones PAREADAS con intervalo de Wilson.
  * McNemar exacta (binomial bilateral sobre los pares discordantes).
  * Numéricos: diferencia pareada (después - antes), mediana con IC bootstrap
    percentil al 95 %, prueba de signos exacta (para el p-valor), delta de
    Cliff. Umbral de efecto: |delta| >= 0.147 (Romano et al., 2006: por debajo
    es «despreciable»).
  * Holm (1979) sobre las comparaciones confirmatorias (las de dirección
    pre-especificada) y, aparte, sobre los controles «sin cambio».
"""
import math

import numpy as np

ALFA = 0.05
UMBRAL_DELTA = 0.147     # Romano, Kromrey, Coraggio & Skowronek (2006): |d| < 0.147 = despreciable
N_MIN = 10               # menos pares válidos -> «no aplica»


def wilson(k, n, z=1.959964):
    """Intervalo de Wilson al 95 % para k éxitos de n."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centro - mitad), min(1.0, centro + mitad)


def contar_pareado(antes, despues):
    """Tabla 2x2 pareada: a=1→1, b=1→0, c=0→1, d=0→0 (antes→después)."""
    t = {"a": 0, "b": 0, "c": 0, "d": 0}
    for x, y in zip(antes, despues):
        t["a" if (x and y) else "b" if x else "c" if y else "d"] += 1
    return t


def newcombe_pareado(a, b, c, d, z=1.959964):
    """Diferencia (después - antes) de proporciones pareadas e IC de Newcombe
    (1998, método 10, con corrección de la correlación phi)."""
    n = a + b + c + d
    if n == 0:
        return 0.0, -1.0, 1.0
    p1, p2 = (a + b) / n, (a + c) / n           # antes, después
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    A = (a + b) * (c + d) * (a + c) * (b + d)
    if A == 0:
        phi = 0.0
    else:
        C = a * d - b * c
        C = C - n / 2 if C > n / 2 else 0.0 if C >= 0 else C
        phi = C / math.sqrt(A)
    D = p2 - p1
    x1, y1 = p2 - l2, u1 - p1
    x2, y2 = u2 - p2, p1 - l1
    lo = D - math.sqrt(max(0.0, x1 * x1 + y1 * y1 - 2 * phi * x1 * y1))
    hi = D + math.sqrt(max(0.0, x2 * x2 + y2 * y2 - 2 * phi * x2 * y2))
    return D, max(-1.0, lo), min(1.0, hi)


def _binom_bilateral(n, k):
    if n == 0:
        return 1.0
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def mcnemar_exacta(b, c):
    """p bilateral exacta de McNemar (binomial 0.5 sobre los pares discordantes)."""
    return _binom_bilateral(b + c, min(b, c))


def prueba_signos(diffs):
    """Prueba de signos exacta bilateral (descarta ceros)."""
    pos = sum(1 for x in diffs if x > 0)
    neg = sum(1 for x in diffs if x < 0)
    return _binom_bilateral(pos + neg, min(pos, neg))


def holm(pvals):
    """p ajustados por Holm-Bonferroni, en el orden original."""
    m = len(pvals)
    orden = sorted(range(m), key=lambda i: pvals[i])
    ajustados = [0.0] * m
    previo = 0.0
    for rango, i in enumerate(orden):
        previo = max(previo, min(1.0, (m - rango) * pvals[i]))
        ajustados[i] = previo
    return ajustados


def cliff_delta(x, y):
    """delta de Cliff (dominancia entre dos muestras): P(x>y) - P(x<y)."""
    x = np.asarray(x, dtype=float)[:, None]
    y = np.asarray(y, dtype=float)[None, :]
    if x.size == 0 or y.size == 0:
        return 0.0
    return float(np.sign(x - y).mean())


def delta_pareado(diffs):
    """delta de Cliff de las diferencias pareadas contra 0: (n(+) - n(-)) / n."""
    if not len(diffs):
        return 0.0
    pos = sum(1 for x in diffs if x > 0)
    neg = sum(1 for x in diffs if x < 0)
    return (pos - neg) / len(diffs)


def ic_bootstrap_mediana(diffs, semilla=0, B=10000, alfa=ALFA):
    """IC bootstrap percentil de la mediana de las diferencias pareadas."""
    d = np.asarray(diffs, dtype=float)
    if d.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(semilla)
    idx = rng.integers(0, d.size, size=(B, d.size))
    med = np.median(d[idx], axis=1)
    lo, hi = np.percentile(med, [100 * alfa / 2, 100 * (1 - alfa / 2)])
    return float(lo), float(hi)


def direccion_numerica(p_aj, delta, alfa=ALFA, umbral=UMBRAL_DELTA):
    """Dirección observada de un numérico: exige significancia (p ajustado) Y efecto no despreciable."""
    if p_aj < alfa and abs(delta) >= umbral:
        return "sube" if delta > 0 else "baja"
    return "sin_cambio"


def direccion_booleana(p_aj, b, c, alfa=ALFA):
    """b = 1→0 (deja de marcar), c = 0→1 (empieza a marcar)."""
    if p_aj < alfa:
        return "se_dispara" if c > b else "baja"
    return "sin_cambio"


def veredicto(esperado, observado, n, n_min=N_MIN):
    """responde / no responde / dirección opuesta / cambio inesperado / no aplica."""
    if n < n_min:
        return "no aplica"
    if esperado == "sin_cambio":
        return "responde" if observado == "sin_cambio" else "cambio inesperado"
    if observado == esperado:
        return "responde"
    if observado == "sin_cambio":
        return "no responde"
    return "dirección opuesta"
