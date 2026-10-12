#!/usr/bin/env python3
"""
Genera seed.sql a partir de los fixtures JSON.

Se genera en vez de escribirse a mano para que la base y los fixtures no
puedan divergir: si cambias world.json, regeneras y ya está.

Uso:  python3 generar_seed.py > seed.sql
      docker compose exec -T db psql -U postgres -d dmia_dev < seed.sql
"""

import json
import sys
import uuid
from pathlib import Path

# Windows usa cp1252 en stdout: cualquier carácter fuera de latin-1 (una
# flecha, una comilla tipográfica) mata el script. Y si muere antes de
# imprimir, el .sql anterior queda intacto y psql carga la versión vieja
# sin avisar de nada.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).parent
world = json.loads((BASE / "world.json").read_text(encoding="utf-8"))
personas = json.loads((BASE / "personas.json").read_text(encoding="utf-8"))

NS = uuid.UUID("00000000-0000-0000-0000-0000000000ff")


def uid(key):
    """UUID determinista por clave: regenerar el seed da los mismos ids."""
    return str(uuid.uuid5(NS, key))


def q(v):
    """Literal SQL para un valor Python: NULL, booleano, número, jsonb (dict/list) o texto con comillas escapadas."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def arr(items):
    """Literal SQL `ARRAY[...]::text[]` para una lista ('{}' si está vacía)."""
    if not items:
        return "'{}'"
    return "ARRAY[" + ",".join(q(i) for i in items) + "]::text[]"


T = uid("tenant")
U = uid("user")
C = uid("campaign")
out = []
w = out.append

w("-- GENERADO por generar_seed.py — no editar a mano.")
w("-- Regenerar tras cualquier cambio en world.json o personas.json.")
w("BEGIN;")
w("SET LOCAL row_security = off;")
w("")

w("-- Idempotente: borra la campaña de fixtures y la recrea.")
w(f"DELETE FROM campaigns WHERE id = {q(C)};")
w(f"DELETE FROM users     WHERE id = {q(U)};")
w(f"DELETE FROM tenants   WHERE id = {q(T)};")
w("")

w(f"INSERT INTO tenants (id, name) VALUES ({q(T)}, 'Fixtures');")
w(f"INSERT INTO users (id, tenant_id, email, display_name) VALUES "
  f"({q(U)}, {q(T)}, 'fixtures@local.dev', 'DM de pruebas');")

cp = world["campaign"]
w(f"""INSERT INTO campaigns (id, tenant_id, owner_id, title, architecture, profile,
  world_tone, party_register, rules_visibility, game_day, current_turn,
  content_boundaries)
 VALUES ({q(C)}, {q(T)}, {q(U)}, {q(cp['title'])}, 'monolithic', {q(cp['profile'])},
  {q(cp['world_tone'])}, {q(cp['party_register'])}, {cp['rules_visibility']},
  {cp['game_day']}, 0, {q(cp.get('content_boundaries', {}))});""")
w(f"INSERT INTO campaign_members (campaign_id, user_id, is_dm) VALUES ({q(C)}, {q(U)}, true);")
w("")

w("-- Lugares (orden de inserción respeta la jerarquía padre→hijo)")
done = set()
pend = list(world["locations"])
while pend:
    nxt = []
    for l in pend:
        if l.get("parent") and l["parent"] not in done:
            nxt.append(l)
            continue
        w(f"""INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ({q(uid(l['key']))}, {q(T)}, {q(C)},
  {q(uid(l['parent'])) if l.get('parent') else 'NULL'},
  {q(l['kind'])}::location_kind, {q(l['name'])},
  {q(l.get('detail','sketch'))}::detail_level, {q(l.get('sketch_text'))},
  {q(l.get('description_canonical'))}, {q(l.get('culture_overrides', {}))},
  {q(l.get('visibility','party'))}::visibility_level);""")
        done.add(l["key"])
    if len(nxt) == len(pend):
        raise SystemExit("ciclo en la jerarquía de lugares")
    pend = nxt
w("")

w("-- Facciones y relojes")
for f in world["factions"]:
    w(f"""INSERT INTO factions (id, tenant_id, campaign_id, name, description,
  seat_location_id, stance_party, knows_about_party)
 VALUES ({q(uid(f['key']))}, {q(T)}, {q(C)}, {q(f['name'])}, {q(f.get('description'))},
  {q(uid(f['seat'])) if f.get('seat') else 'NULL'}, {f.get('stance_party',0)},
  {q(f.get('knows_about_party', False))});""")

for c in world["clocks"]:
    w(f"""INSERT INTO faction_clocks (tenant_id, campaign_id, faction_id, agenda,
  progress, threshold, rate_per_game_day, on_fire_event)
 VALUES ({q(T)}, {q(C)}, {q(uid(c['faction']))}, {q(c['agenda'])},
  {c['progress']}, {c['threshold']}, {c['rate_per_game_day']}, {q(c['on_fire_event'])});""")
w("")

w("-- Misiones")
for qu in world["quests"]:
    w(f"""INSERT INTO quests (id, tenant_id, campaign_id, title, description, status,
  next_step_known, visibility)
 VALUES ({q(uid(qu['key']))}, {q(T)}, {q(C)}, {q(qu['title'])}, {q(qu.get('description'))},
  {q(qu['status'])}::quest_status, {q(qu.get('next_step_known', False))},
  {q(qu.get('visibility','party'))}::visibility_level);""")
w("")

w("-- Personajes jugadores")
for ch in world["characters"]:
    w(f"""INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ({q(uid(ch['key']))}, {q(T)}, {q(C)}, {q(U)}, {q(ch['name'])}, {q(ch['species'])},
  {ch['hp']}, {ch['hp_max']});""")
w("")

w("-- PNJ, persona, IBF, disposición, conocimiento y secretos")
for key, p in personas.items():
    if key.startswith("_"):
        continue
    nid = uid(key)
    per = p.get("personality", {})
    w(f"""INSERT INTO npcs (id, tenant_id, campaign_id, name, species, social_role,
  appearance, status, location_id, warmth, candor, principle, boldness,
  traits, internal_contradiction, taboos, voice_notes,
  stated_desire, actual_need, fear)
 VALUES ({q(nid)}, {q(T)}, {q(C)}, {q(p['name'])}, {q(p.get('species'))},
  {q(p.get('social_role'))}, {q(p.get('appearance'))},
  {q(p.get('status','alive'))}::npc_status,
  {q(uid(p['location'])) if p.get('location') else 'NULL'},
  {per.get('warmth',0)}, {per.get('candor',0)}, {per.get('principle',0)}, {per.get('boldness',0)},
  {arr(p.get('traits'))}, {q(p.get('internal_contradiction'))}, {arr(p.get('taboos'))},
  {q(p.get('voice_notes'))}, {q(p.get('stated_desire'))}, {q(p.get('actual_need'))},
  {q(p.get('fear'))});""")

    ibf = p.get("ibf") or {}
    w(f"""INSERT INTO npc_ibf (npc_id, tenant_id, ideal_text, ideal_tags, bond_text,
  bond_strength, flaw_text, flaw_tags, flaw_exploit)
 VALUES ({q(nid)}, {q(T)}, {q(ibf.get('ideal_text'))}, {arr(ibf.get('ideal_tags'))},
  {q(ibf.get('bond_text'))}, {ibf.get('bond_strength') or 'NULL'},
  {q(ibf.get('flaw_text'))}, {arr(ibf.get('flaw_tags'))}, {q(ibf.get('flaw_exploit'))});""")

    for bt in ibf.get("bond_targets") or []:
        w(f"""INSERT INTO npc_bond_targets (npc_id, tenant_id, target_type, target_id)
 VALUES ({q(nid)}, {q(T)}, {q(bt['type'])}::entity_type, {q(uid(bt['key']))});""")

    d = p.get("disposition", {})
    w(f"""INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, affinity, trust, respect,
  trust_ceiling, updated_at_turn)
 VALUES ({q(nid)}, {q(T)}, NULL, {d.get('affinity',0)}, {d.get('trust',0)},
  {d.get('respect',0)}, {d.get('trust_ceiling',100)}, 0);""")

    for k in p.get("knowledge") or []:
        w(f"""INSERT INTO npc_knowledge (npc_id, tenant_id, fact, learned_at_turn)
 VALUES ({q(nid)}, {q(T)}, {q(k['fact'])}, {k['learned_at_turn']});""")

    for s in p.get("secrets") or []:
        w(f"""INSERT INTO npc_secrets (npc_id, tenant_id, content, reveal_condition, visibility)
 VALUES ({q(nid)}, {q(T)}, {q(s['content'])}, {q(s['reveal_condition'])},
  {q(s.get('visibility','dm_only'))}::visibility_level);""")

w("")
w("COMMIT;")
w("")
w("-- Comprobación")
w("SELECT 'lugares' AS tabla, count(*) FROM locations")
w("UNION ALL SELECT 'pnj', count(*) FROM npcs")
w("UNION ALL SELECT 'disposiciones', count(*) FROM npc_disposition")
w("UNION ALL SELECT 'vinculos', count(*) FROM npc_bond_targets")
w("UNION ALL SELECT 'secretos', count(*) FROM npc_secrets")
w("UNION ALL SELECT 'relojes', count(*) FROM faction_clocks;")

print("\n".join(out))