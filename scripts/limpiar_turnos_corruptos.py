"""
Deshace por completo el primer intento de la campaña real (turn_id
no-secuencial por el bug de vertical_slice.py -- ver "QM - Respaldo
bibliografico...", punto 19) Y el mundo sembrado, porque 259 turnos de
apply_delta() ya escribieron directo sobre columnas de npcs/npc_disposition
(afinidad, posiblemente status, secretos revelados, conocimiento) y revertir
cada campo a mano es más riesgoso que volver a sembrar limpio.

Deja intactos: la fila de `campaigns`, `campaign_members`, y el turno 0
(`turn_log` con el corpus de lore en `dm_output` -- nunca se tocó).
Borra: todo turn_log/turn_validation/deltas con turn_id > 0, y TODO el
mundo (locations, factions+clocks, quests, characters, npcs+subtablas).
Resetea current_turn y game_day a 0.

Después de correr esto, hay que volver a correr:
    python sembrar_mundo_real.py <campaign_id> <tenant_id> <user_id> pj_pj01

Uso: python limpiar_turnos_corruptos.py <campaign_id>
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db as bd
import psycopg


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    campaign_id = sys.argv[1]

    with psycopg.connect(bd.DSN, autocommit=False) as c:
        with c.cursor() as cur:
            cur.execute("SELECT tenant_id FROM campaigns WHERE id = %s",
                       (campaign_id,))
            row = cur.fetchone()
            if not row:
                sys.exit(f"No existe la campaña {campaign_id}")
            tenant_id = row[0]
            cur.execute("SELECT set_config('app.tenant_id', %s, true)",
                       (str(tenant_id),))

            cur.execute(
                "DELETE FROM turn_validation WHERE campaign_id = %s AND turn_id > 0",
                (campaign_id,))
            print(f"turn_validation borradas: {cur.rowcount}")

            cur.execute(
                "DELETE FROM state_deltas WHERE campaign_id = %s",
                (campaign_id,))
            print(f"state_deltas borrados: {cur.rowcount}")

            cur.execute(
                "DELETE FROM turn_log WHERE campaign_id = %s AND turn_id > 0",
                (campaign_id,))
            print(f"turn_log borrados (turno 0 -- el lore -- se conserva): {cur.rowcount}")

            # npcs cascada a npc_ibf/npc_bond_targets/npc_disposition/
            # npc_knowledge/npc_secrets (todas ON DELETE CASCADE).
            cur.execute("DELETE FROM npcs WHERE campaign_id = %s", (campaign_id,))
            print(f"npcs (+ subtablas en cascada) borrados: {cur.rowcount}")

            cur.execute("DELETE FROM characters WHERE campaign_id = %s", (campaign_id,))
            print(f"characters borrados: {cur.rowcount}")

            # factions cascada a faction_clocks.
            cur.execute("DELETE FROM factions WHERE campaign_id = %s", (campaign_id,))
            print(f"factions (+ relojes en cascada) borrados: {cur.rowcount}")

            cur.execute("DELETE FROM quests WHERE campaign_id = %s", (campaign_id,))
            print(f"quests borrados: {cur.rowcount}")

            cur.execute("DELETE FROM locations WHERE campaign_id = %s", (campaign_id,))
            print(f"locations borrados: {cur.rowcount}")

            cur.execute(
                "UPDATE campaigns SET current_turn = 0, game_day = 0 "
                "WHERE id = %s", (campaign_id,))
        c.commit()
    print("\nListo. Campaña limpia (turno 0 con el lore intacto, mundo "
          "vacío, current_turn=0). Ahora corré de nuevo:\n"
          f"  python sembrar_mundo_real.py {campaign_id} {tenant_id} <user_id> pj_pj01")


if __name__ == "__main__":
    main()
