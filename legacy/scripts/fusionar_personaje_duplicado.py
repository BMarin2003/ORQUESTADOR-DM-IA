"""
Fusiona dos filas 'characters' duplicadas (mismo nombre) que AMBAS
recibieron escritura real durante la partida -- caso más grave que un
simple duplicado sin usar: significa que las búsquedas por nombre
devolvieron una fila u otra de forma ambigua turno a turno, y el estado
real quedó repartido entre las dos. Ver bitácora QM punto 29.

Campos delta-ables de 'character' (mutable_fields, migrations/001_schema.sql):
  hp_current   numeric, 'último valor gana' -- la verdad es el valor del
               delta con turn_id MÁS ALTO entre las DOS filas.
  conditions   append (array, con dedup en apply_append) -- la verdad es
               la UNIÓN de lo que hoy tiene cada fila.
  inventory    append (array de {item, turno}, SIN dedup en apply_append)
               -- se concatenan ambas listas y se dedupean solo los pares
               (item, turno) exactamente iguales (una entrada añadida dos
               veces por el duplicado), preservando repeticiones legítimas
               de turnos distintos.

Se queda con la fila de menor `created_at` como destino (arbitrario, no
importa cuál -- los campos se sobreescriben con el estado reconstruido
de todas formas). TODOS los state_deltas que apuntaban a la fila borrada
se REAPUNTAN (UPDATE entity_id) a la fila destino -- no se pierde
historial. Todo en una transacción; sin --confirmar es dry-run.

Uso:
    python scripts\\fusionar_personaje_duplicado.py <campaign_id> "<nombre>"              (dry-run)
    python scripts\\fusionar_personaje_duplicado.py <campaign_id> "<nombre>" --confirmar  (aplica)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db as bd  # noqa: E402


def main():
    """Fusiona las dos filas 'characters' de un PJ duplicado por siembra doble: reconstruye el estado en la fila destino desde los deltas, reapunta los deltas de la sobrante y la borra.

    Sin --confirmar es dry-run; con él aplica todo en una transacción.
    """
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    campaign_id, nombre = sys.argv[1], sys.argv[2]
    confirmar = "--confirmar" in sys.argv[3:]
    camp = bd.Campaña(campaign_id)

    with camp._conn() as c:
        camp._tx(c)

        filas = c.execute(
            """SELECT id, created_at, hp_current, hp_max, conditions,
                      inventory FROM characters
                WHERE campaign_id=%s AND name=%s ORDER BY created_at""",
            (campaign_id, nombre)).fetchall()
        if len(filas) != 2:
            sys.exit(f"Se esperaban 2 filas 'characters' con nombre "
                      f"'{nombre}', hay {len(filas)}. Este script es solo "
                      f"para el caso de exactamente 2.")
        destino, sobra = filas[0], filas[1]
        print(f"Destino (se conserva, se sobreescribe con el estado "
              f"reconstruido): {destino['id']}")
        print(f"Sobra (se reapuntan sus deltas y se borra): {sobra['id']}\n")

        ambos_ids = [destino["id"], sobra["id"]]

        # ---- hp_current: el delta con turn_id más alto entre las 2 filas ----
        d = c.execute(
            """SELECT new_value, turn_id FROM state_deltas
                WHERE campaign_id=%s AND entity_type='character'
                  AND entity_id = ANY(%s) AND field_name='hp_current'
                ORDER BY turn_id DESC LIMIT 1""",
            (campaign_id, ambos_ids)).fetchone()
        if d:
            hp_final = d["new_value"]
            print(f"hp_current final (delta turno {d['turn_id']}): {hp_final}")
        else:
            hp_final = destino["hp_current"]
            print(f"hp_current sin deltas, se deja el de destino: {hp_final}")

        # ---- conditions: unión de ambas, preservando orden de aparición ----
        conditions_final = list(destino["conditions"] or [])
        for cond in (sobra["conditions"] or []):
            if cond not in conditions_final:
                conditions_final.append(cond)
        print(f"conditions final (unión, {len(conditions_final)} "
              f"item(s)): {conditions_final}")

        # ---- inventory: concatenar, dedup solo pares (item, turno) exactos ----
        inv_final = list(destino["inventory"] or [])
        vistos = {(i.get("item"), i.get("turno")) for i in inv_final}
        for it in (sobra["inventory"] or []):
            clave = (it.get("item"), it.get("turno"))
            if clave not in vistos:
                inv_final.append(it)
                vistos.add(clave)
        print(f"inventory final ({len(inv_final)} item(s)): {inv_final}\n")

        # ---- cuántos deltas se reapuntan ----
        n_reapuntar = c.execute(
            """SELECT COUNT(*) AS n FROM state_deltas
                WHERE campaign_id=%s AND entity_type='character'
                  AND entity_id=%s""",
            (campaign_id, sobra["id"])).fetchone()["n"]
        print(f"state_deltas a reapuntar de {sobra['id']} -> "
              f"{destino['id']}: {n_reapuntar}")

        if not confirmar:
            print("\n(dry-run -- vuelve a correr con --confirmar para aplicar)")
            return

        print("\nAplicando...")
        c.execute(
            """UPDATE characters SET hp_current=%s, conditions=%s,
                     inventory=%s WHERE id=%s""",
            (hp_final, conditions_final, json.dumps(inv_final),
             destino["id"]))
        c.execute(
            """UPDATE state_deltas SET entity_id=%s
                WHERE campaign_id=%s AND entity_type='character' AND entity_id=%s""",
            (destino["id"], campaign_id, sobra["id"]))
        c.execute("DELETE FROM characters WHERE id=%s", (sobra["id"],))
        c.commit()
        print("Listo -- fusionado.")


if __name__ == "__main__":
    main()
