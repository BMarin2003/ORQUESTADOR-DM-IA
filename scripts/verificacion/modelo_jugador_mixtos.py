"""Para las campañas con dos modelos de jugador en sus logs: qué modelo corrió en qué tramo de turnos.

Cada log de reanudación anota el turno real en su sección «turno»; se toma el primer y el último turno
que el log muestra, para saber qué rango de la campaña generó cada modelo.

    $env:PYTHONUTF8="1"; py scripts/verificacion/modelo_jugador_mixtos.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MIXTOS = ("ee613cb4", "fc6c19b0", "b7a090cf", "0bc0b20b", "fbe6d980", "d8bf034a")
RE_JUG = re.compile(r"jugador:\*\*\s*`([^`]+)`")
RE_TURNO = re.compile(r"turno:\*\*\s*(\d+)")
RE_CONTADOR = re.compile(r"\bturno (\d+)\s*/\s*1400\b|\[turno (\d+)\]", re.I)

for pref in MIXTOS:
    for ruta in sorted((RAIZ / "logs").rglob(f"*_{pref}_turnos_*.md")):
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        jug = RE_JUG.search(texto[:2000])
        ini = RE_TURNO.search(texto[:2000])
        n_turnos = texto.count("### [1]")
        print(f"{pref} · {ruta.name}\n    jugador: {jug.group(1) if jug else '?'} · turno inicial: "
              f"{ini.group(1) if ini else '?'} · turnos en el log: {n_turnos}")
