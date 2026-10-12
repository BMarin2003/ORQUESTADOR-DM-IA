"""
Consulta rápida de estado — Par 04.
Muestra current_turn real de las dos campañas (G2 y G1) para reconciliar
contra el gasto reportado en DeepInfra.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

CAMPANAS = {
    "Par04 G2 (monolítico)": "e9bef82d-8b7a-41e9-8cb6-8e6af542e514",
    "Par04 G1 (multiagente)": "68a5896f-e7bb-4479-8403-a8403cf80838",
}

with psycopg.connect(db.DSN) as conn:
    for etiqueta, cid in CAMPANAS.items():
        row = conn.execute(
            "SELECT id, title, current_turn, created_at FROM campaigns "
            "WHERE id = %s",
            (cid,),
        ).fetchone()
        if row is None:
            print(f"{etiqueta}: NO ENCONTRADA ({cid})")
        else:
            cid_, title, turn, created = row
            print(f"{etiqueta}: turno {turn} / 1400 -- \"{title}\" "
                  f"(creada {created})")
