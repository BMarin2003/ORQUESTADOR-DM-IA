"""Partición desarrollo / prueba de los 400 ítems A (persona2), estratificada por estrato x brazo.
Se congela ANTES de reajustar el detector: el conjunto de prueba no se inspecciona hasta congelar persona2 v4.
    PYTHONUTF8=1 py validacion_v2/particion_persona2.py
"""
import csv
import hashlib
import random
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SEMILLA = 20261105


def main():
    with open(AQUI / "clave.csv", newline="", encoding="utf-8") as fh:
        filas = [r for r in csv.DictReader(fh) if r["tipo"] == "persona2"]
    grupos = defaultdict(list)
    for r in filas:
        grupos[(r["estrato"], r["brazo"])].append(r["id"])
    rng = random.Random(SEMILLA)
    out = []
    for k in sorted(grupos):
        ids = sorted(grupos[k])
        rng.shuffle(ids)
        mitad = len(ids) // 2
        out += [(i, "desarrollo") for i in ids[:mitad]] + [(i, "prueba") for i in ids[mitad:]]
    out.sort()
    with open(AQUI / "particion_persona2.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "conjunto"])
        w.writerows(out)
    h = hashlib.sha256((AQUI / "particion_persona2.csv").read_bytes()).hexdigest()
    (AQUI / "particion_persona2.sha256").write_text(f"{h}  particion_persona2.csv\n", encoding="utf-8")
    print(sum(c == "desarrollo" for _, c in out), "desarrollo |", sum(c == "prueba" for _, c in out), "prueba |", h)


if __name__ == "__main__":
    main()
