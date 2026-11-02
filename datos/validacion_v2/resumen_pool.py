import collections
import csv
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = list(csv.DictReader(open(Path(__file__).resolve().parent / "pool_pnj.csv", encoding="utf-8")))
si = [r for r in R if r["refinado"] == "1"]
inter = 0
for r in si:
    ina = {x.split("|")[0] for x in r["inactivos"].split(";")}
    if ina & set(r["pnj_detector"].split(";")):
        inter += 1
no_menc = [r for r in R if r["refinado"] == "0" and r["mencionados"]]
no_nomenc = [r for r in R if r["refinado"] == "0" and not r["mencionados"]]
print("elegibles", len(R), "| detector Si", len(si), "| de ellos el sujeto es un PNJ inactivo:", inter)
print("detector No con inactivo mencionado:", len(no_menc), "| detector No sin mencion:", len(no_nomenc))
print("Si por campaña:", collections.Counter((r["par"], r["brazo"]) for r in si).most_common())
print("No-mencionado por brazo:", collections.Counter(r["brazo"] for r in no_menc))
print("No-sin-mencion por brazo:", collections.Counter(r["brazo"] for r in no_nomenc))
