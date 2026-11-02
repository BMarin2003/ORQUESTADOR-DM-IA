"""
Siembra el mundo (lugares, facciones, relojes, misiones, el PJ activo y los
PNJ con IBF/disposición/conocimiento/secretos) para una campaña real ya
creada por crear_campana_real.py.

Por qué esto faltaba: crear_campana_real.py solo creó la fila de `campaigns`
y el turno 0 con el corpus de lore como texto narrativo. Pero el código
(entidades(), estado_pnj(), contexto_escena(), hp_pj()) no lee el lore en
prosa -- lee filas estructuradas en `locations`, `npcs`, `characters`,
`factions`, `quests`. Sin ellas, entidades() devuelve una lista vacía y
estado_pnj("Sargento Brea") devuelve None -- exactamente el
`TypeError: 'NoneType' object is not subscriptable` en vertical_slice.py
línea 307 (fallback en frío a "Sargento Brea" cuando no hay PNJ detectado
en escena).

Este script reproduce lo que experimento/fixtures/generar_seed.py hace para el
fixture, pero:
  - apunta a una campaña/tenant/usuario YA EXISTENTES (los que imprimió
    crear_campana_real.py), no crea tenant/campaña nuevos ni borra nada;
  - usa uuid4() al azar para cada fila en vez de uuid5 determinista por
    clave -- el esquema de generar_seed.py (uuid5 con namespace fijo +
    clave tipo "pj_pj01") generaría el MISMO id que ya existe en la
    campaña de experimento/fixtures/piloto, y `id` es PK global (no compuesta con
    campaign_id) -- chocaría;
  - solo inserta en `characters` el PJ activo de este par (Ilvard /
    pj_pj01), no los 30 de world.json -- entidades() no filtra por PJ, así
    que sembrar los 30 metería 29 personajes irrelevantes en cada lista de
    entidades que ve el extractor.

Uso:
    python sembrar_mundo_real.py <campaign_id> <tenant_id> <user_id> [pj_key] [world_file] [personas_file]
    (pj_key por defecto: pj_pj01, el arquetipo del par 1; world_file/personas_file
    por defecto: experimento/fixtures/world.json y experimento/fixtures/personas.json -- para pares con
    escenario propio, pasar los nombres de archivo específicos de ese par, p.ej.
    "world_par02.json" "personas_par02.json", ambos relativos a experimento/fixtures/)
"""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db as bd  # noqa: E402
import psycopg   # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent


def main():
    """Siembra en Postgres el mundo (lugares, facciones, misiones, PJ y PNJ) de una campaña real desde los fixtures world y personas, en una sola transacción.

    No debe correrse dos veces sobre la misma campaña: una siembra doble duplicó filas en Par02 G1 (punto 29 de la bitácora QM, ver comentario en el cuerpo).
    """
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    campaign_id, tenant_id, user_id = sys.argv[1:4]
    pj_key = sys.argv[4] if len(sys.argv) > 4 else "pj_pj01"
    world_file = sys.argv[5] if len(sys.argv) > 5 else "world.json"
    personas_file = sys.argv[6] if len(sys.argv) > 6 else "personas.json"
    world = json.loads((RAIZ / "experimento" / "fixtures" / world_file).read_text(encoding="utf-8"))
    personas = json.loads((RAIZ / "experimento" / "fixtures" / personas_file).read_text(encoding="utf-8"))

    keymap = {}  # world.json "key" -> uuid recién generado en esta corrida

    def new_id(key):
        """Genera un UUID nuevo y lo registra en keymap bajo la clave del fixture."""
        u = str(uuid.uuid4())
        keymap[key] = u
        return u

    with psycopg.connect(bd.DSN, autocommit=False) as c:
        with c.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, true)",
                       (tenant_id,))

            # Punto 29 (bitácora QM): este script no era idempotente -- si
            # se corría dos veces sobre la misma campaña (por ejemplo por
            # reflejo, sin fijarse en la salida de la corrida anterior),
            # sembraba un segundo set completo de lugares/facciones/
            # misiones/PJ/PNJ con ids nuevos, y las búsquedas por nombre en
            # el resto del sistema (WHERE campaign_id=... AND name=...)
            # empezaban a resolver de forma ambigua entre las dos copias.
            # Pasó en Par02 G1: el PJ Otto terminó con estado repartido
            # entre dos filas 'characters' distintas a mitad de partida.
            # Cortado aquí, antes de escribir nada: si la campaña ya tiene
            # CUALQUIER npc sembrado, se aborta.
            ya_sembrada = cur.execute(
                "SELECT COUNT(*) FROM npcs WHERE campaign_id=%s",
                (campaign_id,)).fetchone()[0]
            if ya_sembrada:
                sys.exit(
                    f"La campaña {campaign_id} ya tiene {ya_sembrada} "
                    f"NPC(s) sembrado(s) -- este script no es idempotente "
                    f"y NO se puede correr dos veces sobre la misma "
                    f"campaña sin duplicar todo el mundo. Si de verdad "
                    f"quieres re-sembrar desde cero, borra primero el "
                    f"mundo existente de esta campaña a mano.")

            # ---- lugares (padre antes que hijo, como generar_seed.py) ----
            done = set()
            pend = list(world["locations"])
            while pend:
                nxt = []
                for l in pend:
                    if l.get("parent") and l["parent"] not in done:
                        nxt.append(l)
                        continue
                    lid = new_id(l["key"])
                    cur.execute(
                        """INSERT INTO locations
                             (id, tenant_id, campaign_id, parent_id, kind, name,
                              detail, sketch_text, description_canonical,
                              culture_overrides, visibility)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (lid, tenant_id, campaign_id,
                         keymap.get(l.get("parent")), l["kind"], l["name"],
                         l.get("detail", "sketch"), l.get("sketch_text"),
                         l.get("description_canonical"),
                         json.dumps(l.get("culture_overrides", {})),
                         l.get("visibility", "party")))
                    done.add(l["key"])
                if len(nxt) == len(pend):
                    sys.exit("ciclo en la jerarquía de lugares")
                pend = nxt
            print(f"Lugares: {len(done)}")

            # ---- facciones + relojes ----
            for f in world["factions"]:
                fid = new_id(f["key"])
                cur.execute(
                    """INSERT INTO factions
                         (id, tenant_id, campaign_id, name, description,
                          seat_location_id, stance_party, knows_about_party)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (fid, tenant_id, campaign_id, f["name"], f.get("description"),
                     keymap.get(f.get("seat")), f.get("stance_party", 0),
                     f.get("knows_about_party", False)))
            for cl in world["clocks"]:
                cur.execute(
                    """INSERT INTO faction_clocks
                         (tenant_id, campaign_id, faction_id, agenda, progress,
                          threshold, rate_per_game_day, on_fire_event)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (tenant_id, campaign_id, keymap[cl["faction"]], cl["agenda"],
                     cl["progress"], cl["threshold"], cl["rate_per_game_day"],
                     json.dumps(cl["on_fire_event"])))
            print(f"Facciones: {len(world['factions'])}, relojes: {len(world['clocks'])}")

            # ---- misiones ----
            for qu in world["quests"]:
                cur.execute(
                    """INSERT INTO quests
                         (id, tenant_id, campaign_id, title, description, status,
                          next_step_known, visibility)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (new_id(qu["key"]), tenant_id, campaign_id, qu["title"],
                     qu.get("description"), qu["status"],
                     qu.get("next_step_known", False),
                     qu.get("visibility", "party")))
            print(f"Misiones: {len(world['quests'])}")

            # ---- el PJ activo de este par ----
            pj = next(ch for ch in world["characters"] if ch["key"] == pj_key)
            cur.execute(
                """INSERT INTO characters
                     (id, tenant_id, campaign_id, user_id, name, species,
                      hp_current, hp_max)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (new_id(pj["key"]), tenant_id, campaign_id, user_id, pj["name"],
                 pj.get("species"), pj["hp"], pj["hp_max"]))
            print(f"PJ activo sembrado: {pj['name']} ({pj_key})")

            # ---- PNJ con IBF/disposición/conocimiento/secretos ----
            for key, p in personas.items():
                if key.startswith("_"):
                    continue
                nid = new_id(key)
                per = p.get("personality", {})
                cur.execute(
                    """INSERT INTO npcs
                         (id, tenant_id, campaign_id, name, species, social_role,
                          appearance, status, location_id, warmth, candor,
                          principle, boldness, traits, internal_contradiction,
                          taboos, voice_notes, stated_desire, actual_need, fear)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (nid, tenant_id, campaign_id, p["name"], p.get("species"),
                     p.get("social_role"), p.get("appearance"),
                     p.get("status", "alive"), keymap.get(p.get("location")),
                     per.get("warmth", 0), per.get("candor", 0),
                     per.get("principle", 0), per.get("boldness", 0),
                     p.get("traits") or [], p.get("internal_contradiction"),
                     p.get("taboos") or [], p.get("voice_notes"),
                     p.get("stated_desire"), p.get("actual_need"), p.get("fear")))

                ibf = p.get("ibf") or {}
                cur.execute(
                    """INSERT INTO npc_ibf
                         (npc_id, tenant_id, ideal_text, ideal_tags, bond_text,
                          bond_strength, flaw_text, flaw_tags, flaw_exploit)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (nid, tenant_id, ibf.get("ideal_text"),
                     ibf.get("ideal_tags") or [], ibf.get("bond_text"),
                     ibf.get("bond_strength"), ibf.get("flaw_text"),
                     ibf.get("flaw_tags") or [], ibf.get("flaw_exploit")))

                for bt in ibf.get("bond_targets") or []:
                    cur.execute(
                        """INSERT INTO npc_bond_targets
                             (npc_id, tenant_id, target_type, target_id)
                           VALUES (%s,%s,%s,%s)""",
                        (nid, tenant_id, bt["type"], keymap[bt["key"]]))

                d = p.get("disposition", {})
                cur.execute(
                    """INSERT INTO npc_disposition
                         (npc_id, tenant_id, pc_id, affinity, trust, respect,
                          trust_ceiling, updated_at_turn)
                       VALUES (%s,%s,NULL,%s,%s,%s,%s,0)""",
                    (nid, tenant_id, d.get("affinity", 0), d.get("trust", 0),
                     d.get("respect", 0), d.get("trust_ceiling", 100)))

                for k in p.get("knowledge") or []:
                    cur.execute(
                        """INSERT INTO npc_knowledge
                             (npc_id, tenant_id, fact, learned_at_turn)
                           VALUES (%s,%s,%s,%s)""",
                        (nid, tenant_id, k["fact"], k["learned_at_turn"]))

                for s in p.get("secrets") or []:
                    cur.execute(
                        """INSERT INTO npc_secrets
                             (npc_id, tenant_id, content, reveal_condition,
                              visibility)
                           VALUES (%s,%s,%s,%s,%s)""",
                        (nid, tenant_id, s["content"], s["reveal_condition"],
                         s.get("visibility", "dm_only")))
            print(f"PNJ sembrados: {len(personas) - sum(1 for k in personas if k.startswith('_'))}")

        c.commit()
    print("\nListo. La campaña ya tiene lugares, facciones, misiones, "
          "el PJ activo y los PNJ con su IBF/disposición/conocimiento/secretos.")


if __name__ == "__main__":
    main()
