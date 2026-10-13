#!/usr/bin/env python3
"""
Une las bitacoras por corrida de cada campania Par 07-17 (datos/logs/par_NN_real_g?_*.md, una por
arranque/reanudacion) en UN archivo cronologico por campania, y mueve los fragmentos
originales (.md + .log + .err) a datos/logs/par07-17/_fragmentos/. No borra nada. Solo Par 07-17.

Correr DESPUES de que el supervisor termine (si no, se mueve un archivo que aun se escribe).
Uso: python experimento/scripts/organizar_logs_par07-17.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
LOGS = RAIZ / "datos" / "logs"
# Uso: organizar_logs_par07-17.py [ids.json] [carpeta]   (Par 18-27: docs/ids_par18-27.json par18-27)
IDS = sys.argv[1] if len(sys.argv) > 1 else "docs/ids_par07-17.json"
DEST = LOGS / (sys.argv[2] if len(sys.argv) > 2 else "par07-17")
FRAG = DEST / "_fragmentos"
CAB = re.compile(r"^## Turno (\d+) — ", re.M)
COMPLETO = re.compile(r"^### \[\d+\] ESTADO DESPUÉS", re.M)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def orden(p):
    """Clave de orden cronológico de un log: (fecha, hora) del arranque, tomada del nombre."""
    return p.stem.rsplit("_", 2)[-2:]      # (fecha, hora) del arranque


def main():
    """Une los fragmentos de log de cada campaña en una bitácora completa ordenada cronológicamente y mueve los originales a la carpeta de fragmentos."""
    FRAG.mkdir(parents=True, exist_ok=True)
    for e in json.loads((RAIZ / IDS).read_text(encoding="utf-8")):
        for brazo, k in (("g2", "campaign_g2"), ("g1", "campaign_g1")):
            marca = e[k][:8]
            mds = sorted(LOGS.glob(f"par_{e['par']}_real_{brazo}_*_{marca}_turnos_*.md"), key=orden)
            sueltos = list(LOGS.glob(f"par{e['par']}_{brazo}_*.log")) + list(LOGS.glob(f"par{e['par']}_{brazo}_*.log.err"))
            if not mds and not sueltos:
                continue
            util = [m for m in mds if m.stat().st_size]
            salida = DEST / f"par{e['par']}_{brazo}_{e['lugar'].lower().replace(' ', '_')}_bitacora_completa.md"
            with salida.open("w", encoding="utf-8") as out:
                out.write(f"# Bitácora completa · Par {e['par']} {brazo.upper()} · {e['lugar']}\n\n"
                          f"Campaña `{e[k]}`. {len(util)} corrida(s) unidas en orden cronológico; "
                          f"cada turno completo aparece una sola vez, el interrumpido (si lo hay) "
                          f"figura al final de su fragmento y se rehace en el siguiente.\n\n")
                for i, m in enumerate(util, 1):
                    txt = m.read_text(encoding="utf-8", errors="replace")
                    turnos = [int(x) for x in CAB.findall(txt)]
                    hechos = len(COMPLETO.findall(txt))
                    rango = f"{turnos[0]}–{turnos[-1]}" if turnos else "sin turnos"
                    out.write(f"\n\n<!-- ═══ FRAGMENTO {i}/{len(util)} · {m.name} · turnos {rango} · "
                              f"{hechos} completos, {len(turnos) - hechos} interrumpido(s) ═══ -->\n\n")
                    out.write(txt)
            for f in mds + sueltos:
                shutil.move(str(f), FRAG / f.name)
            print(f"Par{e['par']} {brazo.upper()}: {len(util)} fragmento(s) útiles de {len(mds)} .md "
                  f"+ {len(sueltos)} .log/.err -> {salida.name} ({salida.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
