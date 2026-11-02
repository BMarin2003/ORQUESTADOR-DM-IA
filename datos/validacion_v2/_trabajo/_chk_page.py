import csv, numpy as np
from scipy import stats
from pathlib import Path
R = Path(__file__).resolve().parent.parent
B = {}
for r in csv.DictReader(open(R / "datos_v2/cierre/bloques.csv", encoding="utf-8")):
    if r["indicador"] == "primaria" and r["brazo"] == "G2":
        B.setdefault(r["par"], {})[int(r["bloque"])] = float(r["valor"])
M = np.array([[B[p][b] for b in range(1, 8)] for p in sorted(B)])
n, k = M.shape
pg = stats.page_trend_test(M, method="asymptotic")
rho = 12 * pg.statistic / (n * k * (k * k - 1)) - 3 * (k + 1) / (k - 1)
d = M[:, 6] - M[:, 0]
w = stats.wilcoxon(d, alternative="greater", zero_method="wilcox")
dd = d[d != 0]; rk = stats.rankdata(np.abs(dd)); rb = (rk[dd > 0].sum() - rk[dd < 0].sum()) / rk.sum()
print(f"n={n} L={pg.statistic} p_page={pg.pvalue:.4f} rho_bar={rho:+.3f} | B7-B1 Wilcoxon p={w.pvalue:.4f} n_efect={len(dd)} r={rb:+.2f}")
print("medianas por bloque (%):", [round(100 * float(np.median(M[:, j])), 2) for j in range(k)])
