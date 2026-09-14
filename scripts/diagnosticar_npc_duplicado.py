"""
Diagnostica (sin borrar nada) filas duplicadas de un NPC por nombre dentro
de una campaña -- ver bitácora QM punto 29 (el guard contra NPCs duplicados
en vertical_slice_g1.py / vertical_slice.py solo comparaba contra los PJ,
no contra NPCs ya sembrados; ya está corregido para turnos futuros, este
script es para inspeccionar el daño ya hecho en campañas existentes antes
de decidir qué fila borrar).

Uso:
    python scripts\\diagnosticar_npc_duplicado.py <campaign_id> "<nombre npc>"

No modifica la base. Imprime, por cada fila con ese nombre en npcs: su id,
created_at_turn (0 = sembrada por sembrar_mundo_real.py, >0 = creada por el
extractor durante un turno -- casi siempre la duplicada es la de
created_at_turn > 0), y cuántas filas dependientes tiene en npc_ibf,
npc_disposition, npc_knowledge, npc_secrets, npc_bond_targets, y cuántos
state_deltas la referencian (estos últimos NO tienen FK a npcs -- si se
borra una fila referenciada, esos deltas quedan huérfanos pero no rompen
nada a nivel de base; se listan para decidir con esa información).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db as bd  # noqa: E402


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    campaign_id, nombre = sys.argv[1], sys.argv[2]
    camp = bd.Campaña(campaign_id)
    with camp._conn() as c:
        camp._tx(c)
        filas = c.execute(
            """SELECT id, name, status, created_at_turn, created_at,
                      appearance_count, is_persistent
                 FROM npcs WHERE campaign_id=%s AND name=%s
                ORDER BY created_at_turn""",
            (campaign_id, nombre)).fetchall()
        if not filas:
            sys.exit(f"No hay ninguna fila 'npcs' con nombre '{nombre}' "
                      f"en la campaña {campaign_id}.")
        print(f"{len(filas)} fila(s) de npcs con nombre '{nombre}':\n")
        for f in filas:
            print(f"  id={f['id']}")
            print(f"    created_at_turn={f['created_at_turn']}  "
                  f"created_at={f['created_at']}  status={f['status']}  "
                  f"appearance_count={f['appearance_count']}  "
                  f"is_persistent={f['is_persistent']}")
            ibf = c.execute("SELECT npc_id FROM npc_ibf WHERE npc_id=%s",
                             (f["id"],)).fetchone()
            disp = c.execute("SELECT COUNT(*) AS n FROM npc_disposition "
                              "WHERE npc_id=%s", (f["id"],)).fetchone()
            know = c.execute("SELECT COUNT(*) AS n FROM npc_knowledge "
                              "WHERE npc_id=%s", (f["id"],)).fetchone()
            sec = c.execute("SELECT COUNT(*) AS n FROM npc_secrets "
                             "WHERE npc_id=%s", (f["id"],)).fetchone()
            bonds = c.execute("SELECT COUNT(*) AS n FROM npc_bond_targets "
                               "WHERE npc_id=%s", (f["id"],)).fetchone()
            deltas = c.execute(
                "SELECT COUNT(*) AS n FROM state_deltas "
                "WHERE campaign_id=%s AND entity_type='npc' AND entity_id=%s",
                (campaign_id, f["id"])).fetchone()
            print(f"    npc_ibf: {'sí' if ibf else 'no'}  ·  "
                  f"npc_disposition: {disp['n']}  ·  "
                  f"npc_knowledge: {know['n']}  ·  "
                  f"npc_secrets: {sec['n']}  ·  "
                  f"npc_bond_targets: {bonds['n']}  ·  "
                  f"state_deltas que la referencian: {deltas['n']}\n")


if __name__ == "__main__":
    main()
