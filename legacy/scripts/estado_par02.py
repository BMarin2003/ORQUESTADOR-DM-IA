"""
Consulta rápida de estado — Par 02 (real).
Muestra current_turn real de las dos campañas (G2 y G1) para saber
EXACTAMENTE dónde quedó cada una antes de reanudar, y cuántos turnos
--turnos hay que pasarle al resume para no pasarse de 1400.

Uso: python scripts/estado_par02.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

OBJETIVO = 1400

CAMPANAS = {
    "Par02 G2 (monolítico)": "5653d917-4744-43e3-90ba-8190a22a126c",
    "Par02 G1 (multiagente)": "84eb6728-52d3-434c-924c-2c21b6099c92",
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
            continue
        cid_, title, turn, created = row
        restantes = OBJETIVO - turn
        print(f"{etiqueta}: turno {turn} / {OBJETIVO} -- \"{title}\" "
              f"(creada {created})")
        if restantes > 0:
            print(f"  -> para reanudar SIN pasarse de {OBJETIVO}, usar --turnos {restantes}")
        else:
            print(f"  -> YA ALCANZÓ O SUPERÓ el objetivo de {OBJETIVO} "
                  f"(excedente: {-restantes}). No reanudar sin decidir qué hacer con el excedente.")
