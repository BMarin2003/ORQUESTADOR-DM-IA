"""¿Sobrevive H1f a la precisión baja de persona2? Análisis de sensibilidad (solo lectura).

Tasa por campaña = % de turnos 1-1400 con hallazgo primario de persona2 (datos_v2/persona2, columna `primaria`).
Se multiplica cada tasa por la precisión del detector en su brazo y se repite el contraste pareado:
  - puntual: precisión estimada por brazo (E4, el evaluador externo que pasó el control de calidad)
  - peor caso para H1f: G1 con el límite SUPERIOR de su IC95 y G2 con el límite INFERIOR del suyo

    $env:PYTHONUTF8="1"; py scripts/verificacion/h1f_sensibilidad_precision.py
"""
import csv
from pathlib import Path

from scipy.stats import wilcoxon

RAIZ = Path(__file__).resolve().parents[2]
ESCENARIOS = {
    "sin corrección": (1.0, 1.0),
    "puntual E4 estricto (G1 0.429, G2 0.286)": (0.429, 0.286),
    "peor caso IC95 E4 (G1 0.674, G2 0.153)": (0.674, 0.153),
}


def tasa(par, brazo):
    with open(RAIZ / "datos_v2" / "persona2" / f"par{par}_{brazo}.csv", encoding="utf-8-sig", newline="") as f:
        # misma definición que consolidar.py (tabla de la tesis): media de `primaria` en turnos fuera del desarrollo del detector
        filas = [r for r in csv.DictReader(f) if int(r["turn_id"]) <= 1400 and int(r["en_desarrollo"] or 0) == 0]
    return 100 * sum(float(r["primaria"] or 0) for r in filas) / len(filas)


def main():
    pares = [f"{p:02d}" for p in range(1, 28)]
    t = {(p, b): tasa(p, b) for p in pares for b in ("G1", "G2")}
    g1 = sorted(t[(p, "G1")] for p in pares)
    g2 = sorted(t[(p, "G2")] for p in pares)
    print(f"mediana sin corregir: G1 {g1[13]:.2f} %  G2 {g2[13]:.2f} %")
    for nombre, (f1, f2) in ESCENARIOS.items():
        d = [t[(p, "G1")] * f1 - t[(p, "G2")] * f2 for p in pares]
        g1_menor = sum(x < 0 for x in d)
        p = wilcoxon(d, alternative="less").pvalue
        m1 = sorted(t[(q, "G1")] * f1 for q in pares)[13]
        m2 = sorted(t[(q, "G2")] * f2 for q in pares)[13]
        print(f"{nombre}: medianas G1 {m1:.2f} % / G2 {m2:.2f} % · G1 < G2 en {g1_menor}/27 pares · Wilcoxon unilateral p = {p:.2g}")


if __name__ == "__main__":
    main()
