"""
Capa de base de datos del orquestador.

Todo lo que el DM y el extractor necesitan saber sale de aquí, no de ficheros
JSON. Los sondeos leían los fixtures directamente; el instrumento real lee la
base, que es donde el estado evoluciona.

Regla dura: **cada transacción fija app.tenant_id con SET LOCAL**, nunca con
SET a nivel de sesión. Con pool de conexiones, un SET de sesión persiste y la
siguiente petición hereda el tenant de la anterior — fuga de datos entre
campañas.
"""

import json
import os

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get(
    "DATABASE_URL",
    "host=127.0.0.1 port=5433 dbname=dmia user=postgres")


class Campaña:
    def __init__(self, campaign_id, dsn=None):
        self.campaign_id = campaign_id
        self.dsn = dsn or DSN
        self._tenant = None

    def _conn(self):
        c = psycopg.connect(self.dsn, row_factory=dict_row)
        return c

    def _tx(self, conn):
        """Fija el tenant SOLO para esta transacción."""
        if self._tenant is None:
            r = conn.execute("SELECT tenant_id FROM campaigns WHERE id = %s",
                             (self.campaign_id,)).fetchone()
            if not r:
                raise RuntimeError(f"campaña {self.campaign_id} no existe")
            self._tenant = r["tenant_id"]
        # SET LOCAL no admite parámetros: hay que usar set_config().
        # El tercer argumento en true = ámbito de transacción, que es lo
        # que evita que el tenant se filtre a la siguiente petición del pool.
        conn.execute("SELECT set_config('app.tenant_id', %s, true)",
                     (str(self._tenant),))

    # ------------------------------------------------------------------ leer

    def cabecera(self):
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT id, title, architecture, profile, world_tone,
                       party_register, rules_visibility, game_day, current_turn,
                       content_boundaries, optional_mechanics
                  FROM campaigns WHERE id = %s""", (self.campaign_id,)).fetchone()

    def entidades(self, ventana_items=20):
        """La lista que el extractor recibe. Sin ella inventaría entidades.

        Los objetos se filtran: solo los que alguien tiene o los creados en
        los últimos `ventana_items` turnos. Si no, tras 700 turnos la lista
        llevaría cientos de objetos de decorado y ahogaría el prompt.
        """
        with self._conn() as c:
            self._tx(c)
            filas = c.execute("""
                SELECT 'npc' AS tipo, id, name AS nombre FROM npcs WHERE campaign_id=%(c)s
                UNION ALL SELECT 'location', id, name FROM locations WHERE campaign_id=%(c)s
                UNION ALL SELECT 'faction', id, name FROM factions WHERE campaign_id=%(c)s
                UNION ALL SELECT 'quest', id, title FROM quests WHERE campaign_id=%(c)s
                UNION ALL SELECT 'character', id, name FROM characters WHERE campaign_id=%(c)s
                UNION ALL SELECT 'item', id, name FROM items
                  WHERE campaign_id=%(c)s
                    AND (holder_id IS NOT NULL
                         OR created_at_turn >= %(t)s)
                ORDER BY 1, 3""",
                {"c": self.campaign_id,
                 "t": max(0, (self.cabecera() or {}).get("current_turn", 0)
                          - ventana_items)}).fetchall()
        return filas

    def contexto_escena(self, npcs_presentes=()):
        """Lo que la base sabe y el turno no dice.

        Es lo que subió el recall del extractor de 33% a 60% en el sondeo 4.
        Aquí se construye desde Postgres, no desde los fixtures.
        """
        with self._conn() as c:
            self._tx(c)
            partes = []

            if npcs_presentes:
                for n in npcs_presentes:
                    pnj = c.execute("""
                        SELECT n.id, n.name, i.bond_text, i.ideal_text, i.flaw_text
                          FROM npcs n LEFT JOIN npc_ibf i ON i.npc_id = n.id
                         WHERE n.campaign_id=%s AND n.name=%s""",
                                    (self.campaign_id, n)).fetchone()
                    if not pnj:
                        continue
                    lin = [f"  {pnj['name']}"]

                    vin = c.execute("""
                        SELECT b.target_type, COALESCE(l.name, f.name, q.title, n2.name) AS nombre
                          FROM npc_bond_targets b
                          LEFT JOIN locations  l  ON l.id  = b.target_id
                          LEFT JOIN factions   f  ON f.id  = b.target_id
                          LEFT JOIN quests     q  ON q.id  = b.target_id
                          LEFT JOIN npcs       n2 ON n2.id = b.target_id
                         WHERE b.npc_id = %s""", (pnj["id"],)).fetchall()
                    if vin:
                        lin.append("    aprecia y protegería: "
                                   + ", ".join(f"{v['nombre']}" for v in vin if v['nombre']))

                    sec = c.execute("""
                        SELECT content, reveal_condition FROM npc_secrets
                         WHERE npc_id=%s AND revealed_at_turn IS NULL""",
                                    (pnj["id"],)).fetchall()
                    for s in sec:
                        lin.append(f"    guarda este secreto: {s['content']}")

                    disp = c.execute("""
                        SELECT disposition_band(affinity) AS b FROM npc_disposition
                         WHERE npc_id=%s AND pc_id IS NULL""", (pnj["id"],)).fetchone()
                    if disp:
                        lin.append(f"    su disposición hacia el grupo: {disp['b']}")
                    partes.append("\n".join(lin))

            q = c.execute("""
                SELECT key_title, status, completion_condition FROM (
                  SELECT title AS key_title, status, completion_condition
                    FROM quests WHERE campaign_id=%s AND status IN ('unknown','active')
                ) s""", (self.campaign_id,)).fetchall()
            if q:
                lin = ["  objetivos abiertos:"]
                for x in q:
                    lin.append(f"    - {x['key_title']} [{x['status']}]")
                    if x["completion_condition"]:
                        lin.append(f"      se cierra cuando: {x['completion_condition']}")
                partes.append("\n".join(lin))

            f = c.execute("""SELECT name, knows_about_party FROM factions
                              WHERE campaign_id=%s""", (self.campaign_id,)).fetchall()
            if f:
                partes.append("  facciones:\n" + "\n".join(
                    f"    - {x['name']}"
                    + ("" if x["knows_about_party"] else " (aún no sabe del grupo)")
                    for x in f))

            prom = c.execute("""
                SELECT d.new_value ->> 'detail' AS texto, n.name AS pnj
                  FROM state_deltas d JOIN npcs n ON n.id = d.entity_id
                 WHERE d.campaign_id=%s AND d.field_name='promise_made'""",
                             (self.campaign_id,)).fetchall()
            if prom:
                partes.append("  compromisos del grupo aún abiertos:\n" + "\n".join(
                    f"    - {p['texto']} (con {p['pnj']})" for p in prom))

        if not partes:
            return ""
        return "\nLO QUE SABE LA BASE Y EL TURNO NO DICE\n" + "\n".join(partes) + "\n"

    def contexto_escena_narrador(self, npcs_presentes=()):
        """Como contexto_escena(), pero para el Narrador de G1.

        El Narrador no puede ver el contenido de un secreto no revelado: si
        lo ve, puede filtrarlo en la prosa aunque el Actor nunca lo haya
        dicho, y eso rompe la asimetria de informacion que el MAS existe
        para medir (solo el Actor la conoce, via get_persona). Por eso esta
        función reutiliza la misma consulta de contexto_escena() pero omite
        el bloque 'guarda este secreto'.

        Ojo si en el futuro se añade aquí una consulta de npc_knowledge:
        tendría que filtrarse a lo que ese PNJ concreto sabe, nunca al
        conocimiento agregado de la campaña — el mismo principio que ya
        aplica get_persona() para el Actor.
        """
        with self._conn() as c:
            self._tx(c)
            partes = []

            if npcs_presentes:
                for n in npcs_presentes:
                    pnj = c.execute("""
                        SELECT n.id, n.name, i.bond_text, i.ideal_text, i.flaw_text
                          FROM npcs n LEFT JOIN npc_ibf i ON i.npc_id = n.id
                         WHERE n.campaign_id=%s AND n.name=%s""",
                                    (self.campaign_id, n)).fetchone()
                    if not pnj:
                        continue
                    lin = [f"  {pnj['name']}"]

                    vin = c.execute("""
                        SELECT b.target_type, COALESCE(l.name, f.name, q.title, n2.name) AS nombre
                          FROM npc_bond_targets b
                          LEFT JOIN locations  l  ON l.id  = b.target_id
                          LEFT JOIN factions   f  ON f.id  = b.target_id
                          LEFT JOIN quests     q  ON q.id  = b.target_id
                          LEFT JOIN npcs       n2 ON n2.id = b.target_id
                         WHERE b.npc_id = %s""", (pnj["id"],)).fetchall()
                    if vin:
                        lin.append("    aprecia y protegería: "
                                   + ", ".join(f"{v['nombre']}" for v in vin if v['nombre']))

                    # A propósito NO se consulta npc_secrets aquí: es la
                    # diferencia con contexto_escena(). El Narrador no
                    # recibe contenido de secretos, revelados o no — lo
                    # revelado le llega, si acaso, como cita textual dentro
                    # del fragmento del Actor, nunca como dato de fondo.

                    disp = c.execute("""
                        SELECT disposition_band(affinity) AS b FROM npc_disposition
                         WHERE npc_id=%s AND pc_id IS NULL""", (pnj["id"],)).fetchone()
                    if disp:
                        lin.append(f"    su disposición hacia el grupo: {disp['b']}")
                    partes.append("\n".join(lin))

            q = c.execute("""
                SELECT key_title, status, completion_condition FROM (
                  SELECT title AS key_title, status, completion_condition
                    FROM quests WHERE campaign_id=%s AND status IN ('unknown','active')
                ) s""", (self.campaign_id,)).fetchall()
            if q:
                lin = ["  objetivos abiertos:"]
                for x in q:
                    lin.append(f"    - {x['key_title']} [{x['status']}]")
                    if x["completion_condition"]:
                        lin.append(f"      se cierra cuando: {x['completion_condition']}")
                partes.append("\n".join(lin))

            f = c.execute("""SELECT name, knows_about_party FROM factions
                              WHERE campaign_id=%s""", (self.campaign_id,)).fetchall()
            if f:
                partes.append("  facciones:\n" + "\n".join(
                    f"    - {x['name']}"
                    + ("" if x["knows_about_party"] else " (aún no sabe del grupo)")
                    for x in f))

            prom = c.execute("""
                SELECT d.new_value ->> 'detail' AS texto, n.name AS pnj
                  FROM state_deltas d JOIN npcs n ON n.id = d.entity_id
                 WHERE d.campaign_id=%s AND d.field_name='promise_made'""",
                             (self.campaign_id,)).fetchall()
            if prom:
                partes.append("  compromisos del grupo aún abiertos:\n" + "\n".join(
                    f"    - {p['texto']} (con {p['pnj']})" for p in prom))

        if not partes:
            return ""
        return "\nLO QUE SABE LA BASE Y EL TURNO NO DICE\n" + "\n".join(partes) + "\n"

    def escena_actual(self):
        """Último turno narrado, para que el DM sepa dónde está la escena."""
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT turn_id, dm_output, player_buffer, location_id
                  FROM turn_log WHERE campaign_id=%s
                 ORDER BY turn_id DESC LIMIT 1""", (self.campaign_id,)).fetchone()

    def estado_pnj(self, nombre):
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT n.name, n.status, round(d.affinity,1) AS affinity,
                       disposition_band(d.affinity) AS banda,
                       (SELECT count(*) FROM npc_knowledge k WHERE k.npc_id=n.id) AS hechos,
                       (SELECT count(*) FROM npc_secrets s
                         WHERE s.npc_id=n.id AND s.revealed_at_turn IS NOT NULL)
                         AS secretos_revelados
                  FROM npcs n LEFT JOIN npc_disposition d
                    ON d.npc_id=n.id AND d.pc_id IS NULL
                 WHERE n.campaign_id=%s AND n.name=%s""",
                             (self.campaign_id, nombre)).fetchone()

    # --------------------------------------------------------------- escribir

    def registrar_turno(self, turn_id, buffer, dm_output, gate_passed,
                        router_modo=None, router_last_npc=None):
        """
        router_modo / router_last_npc: NULL en G2 (el Router no existe en
        ese brazo). En G1 son lo que orquestador/router.py necesita leer
        de vuelta en el turno siguiente para clasificar_turno() — ver el
        aviso al final de ese archivo. router_last_npc es el id del PNJ,
        no el nombre (resolver con self.id_de("npc", nombre) antes de
        llamar aquí).
        """
        with self._conn() as c:
            self._tx(c)
            r = c.execute("""
                INSERT INTO turn_log (tenant_id, campaign_id, turn_id,
                                      player_buffer, dm_output, gate_passed,
                                      router_modo, router_last_npc)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                          (self._tenant, self.campaign_id, turn_id,
                           json.dumps(buffer), dm_output, gate_passed,
                           router_modo, router_last_npc)).fetchone()
            c.execute("UPDATE campaigns SET current_turn=%s WHERE id=%s",
                      (turn_id, self.campaign_id))
            c.commit()
            return r["id"]

    def historial_router(self, ventana=2):
        """
        Lo que orquestador/router.py necesita para clasificar_turno():
        el modo de los últimos `ventana` turnos (más reciente al final,
        tal como pide la firma de la función) y el nombre del último PNJ
        que intervino, buscando hacia atrás el primer turno con
        router_last_npc no nulo (no necesariamente el turno inmediatamente
        anterior: un turno ambiental de por medio no tuvo PNJ que hablara).
        Devuelve (historial_modos: tuple[str], ultimo_pnj_hablo: str|None).
        """
        with self._conn() as c:
            self._tx(c)
            filas = c.execute("""
                SELECT t.router_modo, n.name AS ultimo_pnj
                  FROM turn_log t
                  LEFT JOIN npcs n ON n.id = t.router_last_npc
                 WHERE t.campaign_id=%s
                 ORDER BY t.turn_id DESC
                 LIMIT %s""",
                              (self.campaign_id, max(ventana, 10))).fetchall()
        recientes = list(reversed(filas))
        historial_modos = tuple(f["router_modo"] for f in recientes[-ventana:]
                                if f["router_modo"] is not None)
        ultimo_pnj_hablo = next(
            (f["ultimo_pnj"] for f in reversed(recientes) if f["ultimo_pnj"]),
            None)
        return historial_modos, ultimo_pnj_hablo

    def id_de(self, tipo, nombre):
        tabla = {"npc": ("npcs", "name"), "location": ("locations", "name"),
                 "faction": ("factions", "name"), "quest": ("quests", "title"),
                 "character": ("characters", "name")}[tipo]
        with self._conn() as c:
            self._tx(c)
            r = c.execute(
                f"SELECT id FROM {tabla[0]} WHERE campaign_id=%s AND {tabla[1]}=%s",
                (self.campaign_id, nombre)).fetchone()
        return r["id"] if r else None

    def aplicar(self, entity_type, entity_id, field, value, turn_id,
                source, evidence=None):
        """Pasa por apply_delta. Si no pasó por aquí, no ocurrió."""
        with self._conn() as c:
            self._tx(c)
            r = c.execute("""
                SELECT apply_delta(%s,%s::entity_type,%s,%s,%s::jsonb,%s,
                                   %s::delta_source,%s) AS delta_id""",
                          (self.campaign_id, entity_type, entity_id, field,
                           json.dumps(value), turn_id, source, evidence)).fetchone()
            c.commit()
            return r["delta_id"]

    def crear(self, entity_type, nombre, turn_id, evidence,
              dentro_de=None, kind=None, descripcion=None):
        """Creación explícita. Idempotente por nombre y con evidencia
        obligatoria, igual que apply_delta."""
        with self._conn() as c:
            self._tx(c)
            r = c.execute("""
                SELECT * FROM create_entity(%s,%s::entity_type,%s,%s,%s,%s,%s,%s)""",
                          (self.campaign_id, entity_type, nombre, turn_id,
                           evidence, dentro_de, kind, descripcion)).fetchone()
            c.commit()
            return r

    def resolver_evento(self, npc_id, event_kind):
        with self._conn() as c:
            self._tx(c)
            return c.execute(
                "SELECT * FROM resolve_event(%s, %s::event_kind)",
                (npc_id, event_kind)).fetchone()

    def propagar(self, entity_type, entity_id, field, value, turn_id, witnessed):
        with self._conn() as c:
            self._tx(c)
            r = c.execute("""
                SELECT * FROM propagate_from_delta(%s,%s::entity_type,%s,%s,
                                                   %s::jsonb,%s,%s)""",
                          (self.campaign_id, entity_type, entity_id, field,
                           json.dumps(value), turn_id, witnessed)).fetchall()
            c.commit()
            return r