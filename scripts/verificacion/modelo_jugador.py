"""Qué modelo usó el agente jugador en cada campaña del corpus, según las cabeceras de los logs.

Solo lectura. Cruza el prefijo de 8 caracteres del campaign_id en el nombre del log con la tabla
campaigns (solo las 54 campañas con current_turn >= 1400).

    $env:PYTHONUTF8="1"; py scripts/verificacion/modelo_jugador.py
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "orquestador"))
from db import DSN  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

RE_ID = re.compile(r"_([0-9a-f]{8})_turnos_")
RE_JUG = re.compile(r"jugador:\*\*\s*`([^`]+)`")
RE_DM = re.compile(r"DM:\*\*\s*`([^`]+)`")

modelos = defaultdict(lambda: {"jugador": set(), "dm": set(), "logs": 0})
for ruta in (RAIZ / "logs").rglob("*.md"):
    m = RE_ID.search(ruta.name)
    if not m:
        continue
    cab = ruta.read_text(encoding="utf-8", errors="replace")[:2000]
    x = modelos[m.group(1)]
    x["logs"] += 1
    for rx, k in ((RE_JUG, "jugador"), (RE_DM, "dm")):
        for v in rx.findall(cab):
            x[k].add(v)

with psycopg.connect(DSN, row_factory=dict_row) as c:
    camps = c.execute("SELECT id::text AS id, title, architecture FROM campaigns "
                      "WHERE current_turn >= 1400").fetchall()

filas = []
for cp in camps:
    par = re.search(r"Par (\d+)", cp["title"] or "")
    x = modelos.get(cp["id"][:8], {"jugador": set(), "dm": set(), "logs": 0})
    filas.append((int(par.group(1)) if par else 0, "G1" if cp["architecture"] == "mas" else "G2",
                  ", ".join(sorted(x["jugador"])) or "SIN LOG", ", ".join(sorted(x["dm"])) or "—", x["logs"]))
filas.sort()
print("| Par | Brazo | Jugador | DM | logs |\n|---|---|---|---|---|")
for f in filas:
    print(f"| {f[0]:02d} | {f[1]} | {f[2]} | {f[3]} | {f[4]} |")
resumen = defaultdict(list)
for f in filas:
    resumen[f[2]].append(f"{f[0]:02d}{f[1]}")
print("\nResumen por modelo del jugador:")
for k, v in resumen.items():
    print(f"  {k}: {len(v)} campañas")
