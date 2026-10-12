"""
Consulta rápida de estado — Par 04, 05 y 06 (real), las seis campañas
afectadas por el incidente del .env / DMIA_MODELO_JUGADOR y, en el caso
de Par 05 G2, también por el bug de location.state fuera de dominio.

Muestra current_turn real de las seis campañas para saber EXACTAMENTE
dónde quedó cada una antes de reanudar, y cuántos turnos --turnos hay
que pasarle al resume para no pasarse de 1400.

Uso: python scripts/estado_par04_05_06.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

OBJETIVO = 1400

CAMPANAS = {
    "Par04 G2 (monolítico) · Caleta Lumbre":  "fc6c19b0-49a6-4abb-ad44-b12de9438828",
    "Par04 G1 (multiagente) · Caleta Lumbre": "ee613cb4-c84c-4c69-b276-bbf97e0cbbc6",
    "Par05 G2 (monolítico) · Vado Cabrero":   "0bc0b20b-0dba-454d-a32e-94fbeb24dddf",
    "Par05 G1 (multiagente) · Vado Cabrero":  "b7a090cf-032e-4a87-be01-e03fa88a9917",
    "Par06 G2 (monolítico) · Poza Seca":      "d8bf034a-bcc9-4a12-999e-490be27c8a2e",
    "Par06 G1 (multiagente) · Poza Seca":     "fbe6d980-964f-455c-89d9-96d34d9653fe",
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
        print(f"{etiqueta}: turno {turn} / {OBJETIVO} -- \"{title}\"")
        if restantes > 0:
            print(f"  -> para reanudar SIN pasarse de {OBJETIVO}, usar --turnos {restantes}")
        else:
            print(f"  -> YA ALCANZÓ O SUPERÓ el objetivo de {OBJETIVO} "
                  f"(excedente: {-restantes}). No reanudar sin decidir qué hacer con el excedente.")
