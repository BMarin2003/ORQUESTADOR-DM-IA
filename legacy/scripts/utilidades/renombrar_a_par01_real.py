"""
Renombra las campañas "Par 04" a "Par 01 (real)" en la base de datos.

Contexto: "Par 04" fue un nombre provisional puesto al momento de crearlas
(seguía la numeración de los 3 pilotos previos). En realidad esta es la
primera pareja del CORPUS REAL (con el juego completo de herramientas
deterministas activo desde el inicio), no una cuarta muestra piloto -- así
que le corresponde su propia numeración, empezando en 1. Se deja explícito
"(real)" en el título para no confundirla con los campaign_id de "Par 01"
del piloto (ef4e900a / 7b7a3cd5), que se quedan como están.

Solo cambia el título. No toca current_turn, turn_log, ni ningún otro dato.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

RENOMBRES = {
    "e9bef82d-8b7a-41e9-8cb6-8e6af542e514":
        "Par 01 (real) · G2 (Monolítico) · Puerto Salazón",
    "68a5896f-e7bb-4479-8403-a8403cf80838":
        "Par 01 (real) · G1 (Multiagente) · Puerto Salazón",
}

with psycopg.connect(db.DSN) as conn:
    for cid, nuevo_titulo in RENOMBRES.items():
        antes = conn.execute(
            "SELECT title FROM campaigns WHERE id = %s", (cid,)
        ).fetchone()
        if antes is None:
            print(f"NO ENCONTRADA: {cid}")
            continue
        conn.execute(
            "UPDATE campaigns SET title = %s WHERE id = %s",
            (nuevo_titulo, cid),
        )
        print(f"{cid}:")
        print(f"  antes:   {antes[0]}")
        print(f"  ahora:   {nuevo_titulo}")
    conn.commit()

print("\nListo. Confirmado con COMMIT.")
