#!/usr/bin/env python3
"""
Imprime SOLO el current_turn (entero) de una campaña -- para que scripts de
PowerShell puedan calcular --turnos = 1400 - current_turn sin adivinar ni
hardcodear (regla del proyecto: nunca relanzar con --turnos 1400 fijo).

Uso: python scripts/current_turn.py <campaign_id>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

campaign_id = sys.argv[1]
with psycopg.connect(db.DSN) as c:
    row = c.execute("SELECT current_turn FROM campaigns WHERE id=%s",
                     (campaign_id,)).fetchone()
if row is None:
    sys.exit(f"Campaña {campaign_id} no encontrada")
print(row[0])
