"""
Barre `campaigns WHERE current_turn = 0` -- solo lee, no borra nada.

Por qué importa antes de Par 03: un stub vacío (campaña creada pero nunca
avanzada, remanente de un bug de siembra doble ya corregido -- ver
`f09ca142...` de Par 01 piloto) puede confundir cualquier lookup
automático de campañas por título. Antes de sembrar Par 03, conviene saber
cuántos quedan y decidir si se limpian o se dejan (documentados).

Uso: python scripts/barrer_stubs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

with psycopg.connect(db.DSN, row_factory=dict_row) as conn:
    filas = conn.execute(
        "SELECT id, title, architecture, created_at FROM campaigns "
        "WHERE current_turn = 0 ORDER BY created_at"
    ).fetchall()

if not filas:
    print("Ningún stub encontrado (current_turn = 0). Base limpia.")
else:
    print(f"{len(filas)} campaña(s) con current_turn = 0:\n")
    for f in filas:
        print(f"  {f['id']}  [{f['architecture'] or '?'}]  \"{f['title']}\"  "
              f"(creada {f['created_at']})")
    print("\nEsto es solo lectura -- no se borró nada. Si alguna es un stub "
          "real (siembra que falló a medias), decidir a mano si limpiarla "
          "o dejarla documentada como se hizo con f09ca142... de Par 01.")
