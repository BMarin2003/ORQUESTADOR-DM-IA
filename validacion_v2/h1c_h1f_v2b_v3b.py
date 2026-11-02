"""H1c (Page, 7 bloques de 200 turnos, G2) y H1f (Wilcoxon exacto pareado G1-G2) con persona2 v2b y v3b.
Tasa = % de turnos 2-1400 válidos y fuera de desarrollo con al menos un hallazgo primario."""
import csv
import sys
from pathlib import Path
import numpy as np
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts" / "reporte_v2")); sys.path.insert(0, str(RAIZ / "scripts" / "sensibilidad"))
import pares as _pares  # noqa: E402


def tasas(carpeta, par, brazo):
    with open(RAIZ / "datos_v2" / carpeta / f"par{par}_{brazo}.csv", newline="", encoding="utf-8") as fh:
        f = [r for r in csv.DictReader(fh) if 2 <= int(r["turn_id"]) <= 1400 and r["en_desarrollo"] == "0"]
    tot = 100 * np.mean([int(r["primaria"]) for r in f])
    bl = [100 * np.mean([int(r["primaria"]) for r in f if b * 200 < int(r["turn_id"]) <= (b + 1) * 200] or [np.nan]) for b in range(7)]
    return tot, bl


def rb(d):
    d = np.array([x for x in d if x != 0]); r = stats.rankdata(np.abs(d))
    return (r[d > 0].sum() - r[d < 0].sum()) / r.sum() if len(d) else float("nan")


for carpeta in ("persona2", "persona2_v3b"):
    g1, g2, bl2 = [], [], []
    for p in _pares.todos():
        a, _ = tasas(carpeta, p["par"], "G1"); b, bl = tasas(carpeta, p["par"], "G2")
        g1.append(a); g2.append(b); bl2.append(bl)
    d = np.array(g1) - np.array(g2)
    w = stats.wilcoxon(d, alternative="less", zero_method="wilcox", method="auto")
    w2 = stats.wilcoxon(d, alternative="two-sided", zero_method="wilcox", method="auto")
    B = np.array(bl2); ok = ~np.isnan(B).any(axis=1)
    pg = stats.page_trend_test(B[ok])
    print(f"== {carpeta}: Mdn G1 {np.median(g1):.2f} % | Mdn G2 {np.median(g2):.2f} % | pares con dif. no nula {int((d != 0).sum())}")
    print(f"   H1f Wilcoxon p unilateral (G1 < G2) = {w.pvalue:.4g} | bilateral = {w2.pvalue:.4g} | r = {rb(d):+.2f}")
    print(f"   H1c Page (aumento B1->B7) L = {pg.statistic:.0f}, p = {pg.pvalue:.4g} | mediana B1 {np.median(B[:,0]):.2f} % -> B7 {np.median(B[:,6]):.2f} %")
