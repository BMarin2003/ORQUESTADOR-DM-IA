"""Tablas en crudo de QN-2 con persona2 v3b para el documento:
  OE3-9: G2 por campaña y bloque de 200 turnos (% de turnos), más el total de la campaña.
  OE6-4/OE6-5: G1 y G2 por par, total y por categoría (% de turnos).
Misma definición que el pipeline: turnos 2-1400 válidos, fuera de desarrollo; bloques de datos_v2/cierre/bloques.csv."""
import csv
import sys
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(R / "experimento" / "scripts" / "reporte_v2")); sys.path.insert(0, str(R / "experimento" / "scripts" / "sensibilidad"))
import pares as _pares  # noqa: E402

V3 = R / "datos" / "datos_v2" / "persona2_v3b"
CATS = ["primaria", "VOLICION", "COGNICION", "EMOCION", "HABLA"]


def tasa(par, brazo, col):
    with open(V3 / f"par{par}_{brazo}.csv", newline="", encoding="utf-8") as fh:
        f = [r for r in csv.DictReader(fh) if 2 <= int(r["turn_id"]) <= 1400 and r["en_desarrollo"] == "0"]
    return 100 * np.mean([int(r[col]) for r in f])


bl = {}
for r in csv.DictReader(open(R / "datos/datos_v2/cierre/bloques.csv", encoding="utf-8")):
    if r["indicador"] == "primaria" and r["brazo"] == "G2":
        bl.setdefault(r["par"], {})[int(r["bloque"])] = 100 * float(r["valor"])
pares = [p["par"] for p in _pares.todos()]
with open(R / "datos" / "validacion_v2" / "tabla_OE3-9_v3b.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["Par"] + [f"B{b}" for b in range(1, 8)] + ["Total"])
    for p in pares:
        w.writerow([p] + [f"{bl[p][b]:.2f}" for b in range(1, 8)] + [f"{tasa(p, 'G2', 'primaria'):.2f}"])
with open(R / "datos" / "validacion_v2" / "tabla_OE6-4_5_v3b.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Par"] + [f"{c} {b}" for c in ("Usurp. total", "Decisión", "Pensamiento", "Emoción", "Habla") for b in ("G1", "G2")])
    for p in pares:
        w.writerow([p] + [f"{tasa(p, b, c):.2f}" for c in CATS for b in ("G1", "G2")])
print("ok")
