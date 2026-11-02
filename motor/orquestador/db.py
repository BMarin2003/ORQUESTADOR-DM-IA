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
import time
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

try:
    from dotenv import load_dotenv
    # Busca .env subiendo desde este archivo (motor/orquestador/db.py -> raíz del
    # proyecto), no desde el cwd del que invoque el script -- así funciona
    # igual sea "python crear_campana_real_g1.py" desde la raíz o
    # "python motor/orquestador/vertical_slice_g1.py" desde donde sea.
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except ImportError:
    # python-dotenv no instalado: se sigue pudiendo forzar DATABASE_URL a
    # mano por variable de entorno, como antes. No es un error fatal.
    pass

DSN = os.environ.get(
    "DATABASE_URL",
    "host=127.0.0.1 port=5432 dbname=dmia_dev user=postgres "
    "password=dev_only_change_me")

# Escala del reloj del mundo (ver Campaña.sincronizar_dia): 1 día de juego cada
# N turnos. 1400 turnos = 70 días. Es una convención de campaña, no tiempo
# narrado: los fixtures deben calibrar `threshold`/`rate_per_game_day` contra
# esto (experimento/scripts/validar_fixtures_real.py avisa si un reloj no encaja).
TURNOS_POR_DIA = 20


class Campaña:
    """Acceso a una campaña en Postgres: cada método abre su conexión y fija el tenant (RLS) solo para esa transacción."""
    def __init__(self, campaign_id, dsn=None):
        """Guarda el id de campaña y el DSN (por defecto `DSN`); el tenant se resuelve en la primera transacción."""
        self.campaign_id = campaign_id
        self.dsn = dsn or DSN
        self._tenant = None

    def _conn(self):
        """Abre una conexión nueva (sin pool) con hasta 6 intentos y backoff de 0.5 a 8 s ante `OperationalError`."""
        # Bug encontrado en Par 07-17 (2026-09-18, 17:17): cada método abre
        # una conexión TCP nueva (sin pool) y, con 22 corridas en paralelo,
        # Windows agotó puertos efímeros una vez en 5 h -> "connection
        # failed ... Address already in use (10048)" tumbó Par09 G2. Es
        # transitorio: reintento corto (0.5..8 s) antes de propagar.
        for intento in range(6):
            try:
                return psycopg.connect(self.dsn, row_factory=dict_row)
            except psycopg.OperationalError:
                if intento == 5:
                    raise
                time.sleep(0.5 * 2 ** intento)

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
        """Fila de `campaigns` con título, arquitectura, tono, día de juego y turno actual."""
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

    def contexto_escena(self, npcs_presentes=(), eventos_reloj=None):
        """Lo que la base sabe y el turno no dice.

        Es lo que subió el recall del extractor de 33% a 60% en el sondeo 4.
        Aquí se construye desde Postgres, no desde los fixtures.

        `eventos_reloj`: salida de eventos_reloj_turno(turn_id_anterior) --
        opcional, compartido con G2 (MUN-1/2, ver avanzar_relojes()). Si
        se pasa y no está vacío, aparece como hecho consumado que hay que
        narrar, no como algo a decidir.
        """
        with self._conn() as c:
            self._tx(c)
            partes = []

            if eventos_reloj:
                lin = ["  algo que ya ocurrió y aún no se ha narrado:"]
                for ev in eventos_reloj:
                    # Bug encontrado en la octava pasada (ver "QM - Respaldo
                    # bibliografico instrumentos deterministicos.md", punto
                    # 11): acá se buscaba la clave "descripcion" dentro de
                    # on_fire_event, que NUNCA existe en el fixture real
                    # (experimento/fixtures/world.json usa headline/scope/consequence) --
                    # el DM solo veía el fallback `agenda`, sin la consecuencia
                    # rica que el diseño de fixtures preveía. Corregido acá:
                    # headline (qué pasó) + consequence (qué resultó) son las
                    # dos claves narrables; scope es un tag interno de
                    # ubicación, no texto para el DM. Se preserva el fallback
                    # a `agenda` para cualquier on_fire_event vacío o con
                    # forma distinta (defensivo, no se asume una única forma).
                    ofe = ev.get("on_fire_event") or {}
                    partes_detalle = [ofe[k] for k in ("headline", "consequence")
                                      if ofe.get(k)]
                    detalle = " — ".join(partes_detalle) if partes_detalle \
                              else ev.get("agenda")
                    lin.append(f"    - {ev['faccion']} · {ev['agenda']}: {detalle}")
                partes.append("\n".join(lin))

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
        """Estado de un PNJ por nombre (status, afinidad y su banda, hechos conocidos, secretos revelados); None si no existe."""
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

    def get_persona(self, nombre, turn_id):
        """Ficha completa del Actor de G1 (motor/dm/prompt_actor_g1.md): los
        cuatro ejes de personalidad ESTABLE (warmth/candor/principle/
        boldness), los rasgos ricos (traits/internal_contradiction/taboos/
        voice_notes/stated_desire/actual_need/fear), su IBF, y SOLO lo que
        el propio PNJ puede saber a este punto -- conocimiento aprendido
        hasta turn_id (npc_knowledge.learned_at_turn <= turn_id) y sus
        secretos CON contenido (a diferencia de contexto_escena_narrador(),
        que se lo oculta al Narrador a propósito: la asimetría de
        información -- solo el Actor conoce el secreto -- es justo lo que
        el diseño de G1 existe para poder medir).

        Devuelve None si el nombre no tiene fila en npcs -- quien llama
        decide qué hacer (normalmente: saltar ese PNJ y marcarlo en
        `faltantes` para el Narrador, igual que un fallo de red)."""
        with self._conn() as c:
            self._tx(c)
            npc = c.execute("""
                SELECT id, name, species, social_role, appearance, status,
                       warmth, candor, principle, boldness,
                       traits, internal_contradiction, taboos, voice_notes,
                       stated_desire, actual_need, fear
                  FROM npcs WHERE campaign_id=%s AND name=%s""",
                            (self.campaign_id, nombre)).fetchone()
            if not npc:
                return None
            ibf = c.execute("""
                SELECT ideal_text, ideal_tags, bond_text, bond_strength,
                       flaw_text, flaw_tags, flaw_exploit
                  FROM npc_ibf WHERE npc_id=%s""", (npc["id"],)).fetchone()
            conocimiento = c.execute("""
                SELECT fact, learned_at_turn, source FROM npc_knowledge
                 WHERE npc_id=%s AND learned_at_turn <= %s
                 ORDER BY learned_at_turn""", (npc["id"], turn_id)).fetchall()
            secretos = c.execute("""
                SELECT content, reveal_condition, revealed_at_turn
                  FROM npc_secrets WHERE npc_id=%s""", (npc["id"],)).fetchall()
            disp = c.execute("""
                SELECT round(affinity,1) AS affinity,
                       disposition_band(affinity) AS banda
                  FROM npc_disposition
                 WHERE npc_id=%s AND pc_id IS NULL""", (npc["id"],)).fetchone()
        return {"npc": npc, "ibf": ibf, "conocimiento": conocimiento,
                "secretos": secretos, "disposicion": disp}

    def hp_pj(self, nombre):
        """hp_current/hp_max reales del PJ (tabla characters), para el
        chequeo CL-2 de HP-vs-narración (ver FIREBALL, Hit Point Reasoning).
        None si el nombre no tiene fila en characters -- puede pasar en
        datos de desarrollo donde personajes_jugadores.json y los fixtures
        de characters no coinciden todavía; el chequeo se omite, no falla.
        """
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT hp_current, hp_max FROM characters
                 WHERE campaign_id=%s AND name=%s""",
                             (self.campaign_id, nombre)).fetchone()

    def campos_mutables(self, entity_type):
        """Lista blanca real (tabla mutable_fields), no la copia de
        contrato.json que usa el extractor -- CL-1 compara contra la
        fuente de verdad de la base, no contra el contrato del LLM."""
        with self._conn() as c:
            self._tx(c)
            filas = c.execute(
                "SELECT field_name FROM mutable_fields WHERE entity_type=%s",
                (entity_type,)).fetchall()
        return {f["field_name"] for f in filas}

    # --------------------------------------------------------------- escribir

    def registrar_turno(self, turn_id, buffer, dm_output, gate_passed,
                        router_modo=None, router_last_npc=None):
        """
        router_modo / router_last_npc: NULL en G2 (el Router no existe en
        ese brazo). En G1 son lo que motor/orquestador/router.py necesita leer
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

    def registrar_validacion(self, turn_id, architecture, campos):
        """Una fila en turn_validation por turno (ver motor/migrations/001_schema.sql
        y 'QM - Respaldo bibliografico instrumentos deterministicos.md' para
        la justificación de cada columna por tier de confianza).

        `campos`: dict con las claves que existan de las columnas
        cr1_*/cl1_*/cl2_*/qn1_*/qn2_*/cr2_nombres_no_reconocidos/raw_flags;
        las que falten quedan en su DEFAULT (false / NULL / '{}'). Requiere
        que turn_log ya tenga la fila (campaign_id, turn_id) -- FK
        compuesta -- así que se llama DESPUÉS de registrar_turno, nunca en
        modo --seco.
        """
        columnas = list(campos.keys())
        placeholders = ", ".join(["%s"] * len(columnas))
        nombres = ", ".join(columnas)
        valores = [campos[k] for k in columnas]
        with self._conn() as c:
            self._tx(c)
            c.execute(f"""
                INSERT INTO turn_validation
                    (tenant_id, campaign_id, turn_id, architecture, {nombres})
                VALUES (%s, %s, %s, %s, {placeholders})""",
                      [self._tenant, self.campaign_id, turn_id, architecture]
                      + valores)
            c.commit()

    def historial_router(self, ventana=2):
        """
        Lo que motor/orquestador/router.py necesita para clasificar_turno():
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
        """UUID de la entidad por tipo y nombre en esta campaña, o None. `tipo` se normaliza a minúsculas; un tipo desconocido lanza KeyError."""
        # El casing de `tipo` no siempre viene controlado: el contrato del
        # extractor sí fuerza minúsculas, pero el prompt de Mundo (G1) no
        # -- se vio en producción un delta con entity_type="NPC" en vez de
        # "npc", que tumbaba esto con KeyError. Normalizar aquí, en el
        # único punto de entrada, cubre a cualquier llamador presente o
        # futuro sin tener que confiar en que cada prompt sea disciplinado.
        tabla = {"npc": ("npcs", "name"), "location": ("locations", "name"),
                 "faction": ("factions", "name"), "quest": ("quests", "title"),
                 "character": ("characters", "name")}[tipo.strip().lower()]
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
        """Delega en `resolve_event()` de SQL: el modelo solo clasifica el evento y las magnitudes (afinidad, confianza, respeto) salen de la base, moduladas por la personalidad del PNJ."""
        with self._conn() as c:
            self._tx(c)
            return c.execute(
                "SELECT * FROM resolve_event(%s, %s::event_kind)",
                (npc_id, event_kind)).fetchone()

    def propagar(self, entity_type, entity_id, field, value, turn_id, witnessed):
        """Delega en `propagate_from_delta()`: recorre entity_relations y devuelve los eventos de facción derivados; sin `witnessed` verdadero no propaga."""
        with self._conn() as c:
            self._tx(c)
            r = c.execute("""
                SELECT * FROM propagate_from_delta(%s,%s::entity_type,%s,%s,
                                                   %s::jsonb,%s,%s)""",
                          (self.campaign_id, entity_type, entity_id, field,
                           json.dumps(value), turn_id, witnessed)).fetchall()
            c.commit()
            return r
    # ------------------------------------------------------------------
    # Agente del Mundo (§5.4). Igual que historial_router(), estos métodos
    # existen porque el Mundo mecánico necesita leer/escribir cosas que el
    # modelo de datos entidad+delta no cubre directamente:
    #   - avanzar_relojes: envoltura de advance_clocks(), ya escribe
    #     progress/fired_at_turn directamente (es la propia función SQL la
    #     que decide, no una extracción del modelo -- fuente 'clock').
    #   - fijar_lugar: `description_canonical` y `observed_at_turn` NO
    #     están en mutable_fields (solo `detail` sí, como enum). Son
    #     campos de acompañamiento del mismo evento de "congelar boceto"
    #     (MUN-5/6), no hechos extraídos que necesiten evidencia -- se
    #     escriben directo, igual que turn_log en registrar_turno(). El
    #     campo `detail` en cambio SÍ pasa por apply_delta porque SÍ está
    #     en la lista blanca.
    #   - semillas_sin_ubicar / plantar_semilla: session_seeds no es un
    #     entity_type (mirar el enum), es tabla de planificación de sesión,
    #     no de estado de mundo -- fuera del alcance de apply_delta por
    #     diseño, no por descuido.
    # ------------------------------------------------------------------

    def avanzar_relojes(self, game_days, turn_id):
        """MUN-1/MUN-2: avanza faction_clocks con tiempo de juego y
        devuelve los que dispararon ESTE turno. El Mundo (LLM) no decide
        si un reloj dispara -- eso ya es verdad en la base cuando esta
        función retorna. Su trabajo es narrar/plantar consecuencia del
        evento devuelto, no juzgar si ocurrió.

        COMPARTIDO entre G1 y G2 (2026-09-07) -- igual que dados.py: es
        aritmética/umbral, no memoria narrativa, así que darle este
        resultado a los dos brazos no contamina la comparación (mismo
        principio que ya regía para las tiradas). Lo que SÍ se queda
        exclusivo de G1 es el congelado de lugares (locations.detail) --
        ahí la consistencia de memoria ES parte de lo que la tesis mide,
        decisión tomada explícitamente el 2026-09-07."""
        with self._conn() as c:
            self._tx(c)
            r = c.execute(
                "SELECT * FROM advance_clocks(%s, %s, %s)",
                (self.campaign_id, game_days, turn_id)).fetchall()
            c.commit()
            return r

    def sincronizar_dia(self, turn_id, turnos_por_dia=None):
        """Reloj del mundo DETERMINISTA (2026-09-19, para Par 18+).

        En Par01-17 los relojes de facción nunca dispararon: solo avanzaban si
        el extractor emitía world.game_day, y en ~30 000 turnos no lo emitió
        ni una vez. Aquí el día de juego sale del número de turno
        (día = turno // TURNOS_POR_DIA), sin LLM, igual en G1 y en G2.

        Idempotente y a prueba de caídas: si `game_day` ya está al día no hace
        nada; si un turno anterior se perdió el tick, el siguiente lo recupera
        (avanza `día - game_day` días de golpe). El delta (fuente 'clock') y
        el avance de relojes van en UNA transacción: no puede quedar el día
        avanzado sin que los relojes lo sepan. Devuelve los relojes disparados
        en este turno (mismas columnas que avanzar_relojes)."""
        turnos_por_dia = turnos_por_dia or TURNOS_POR_DIA
        with self._conn() as c:
            self._tx(c)
            actual = c.execute("SELECT game_day FROM campaigns WHERE id=%s",
                               (self.campaign_id,)).fetchone()["game_day"]
            dia = turn_id // turnos_por_dia
            if dia <= actual:
                return []
            c.execute("""
                SELECT apply_delta(%s,'world'::entity_type,NULL,'game_day',
                                   %s::jsonb,%s,'clock'::delta_source,%s)""",
                      (self.campaign_id, json.dumps(dia), turn_id,
                       f"reloj determinista: día {dia} "
                       f"(1 día cada {turnos_por_dia} turnos)"))
            r = c.execute("SELECT * FROM advance_clocks(%s, %s, %s)",
                          (self.campaign_id, dia - actual, turn_id)).fetchall()
            c.commit()
            return r

    def eventos_reloj_turno(self, turn_id):
        """Relojes que dispararon EXACTAMENTE en `turn_id` -- se usa para
        pasarle al turno SIGUIENTE (turn_id+1) lo que aún no se ha
        narrado: avanzar_relojes() corre después de escribir (paso 8),
        así que la única oportunidad de narrar la consecuencia es al
        abrir el turno de después. Compartido con G2 por la misma razón
        que avanzar_relojes()."""
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT f.name AS faccion, c.agenda, c.on_fire_event
                  FROM faction_clocks c JOIN factions f ON f.id = c.faction_id
                 WHERE c.campaign_id=%s AND c.fired_at_turn=%s""",
                             (self.campaign_id, turn_id)).fetchall()

    def turnos_narracion(self):
        """turn_id + dm_output de toda la campaña, en orden. Usado por
        reporte_validacion.py para reconstruir el camino de ubicaciones
        REALIZADAS (no el espacio completo de posibilidades, que no
        existe en un sistema de texto libre) -- ver "Deep Research,
        Twine/Symmetry" en la nota de respaldo bibliográfico."""
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT turn_id, dm_output FROM turn_log
                 WHERE campaign_id=%s AND dm_output IS NOT NULL
                 ORDER BY turn_id""", (self.campaign_id,)).fetchall()

    def relojes_disparados(self):
        """Todos los faction_clocks que ya dispararon en esta campaña
        (fired_at_turn no nulo), ordenados por turno de disparo. A
        diferencia de eventos_reloj_turno() (un turno puntual, usado en
        tiempo real por el Mundo), este trae el historial completo para
        el chequeo longitudinal de reporte_validacion.py: ¿la narración
        reconoció el evento en los turnos siguientes al disparo?"""
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT f.name AS faccion, c.agenda, c.on_fire_event,
                       c.fired_at_turn
                  FROM faction_clocks c JOIN factions f ON f.id = c.faction_id
                 WHERE c.campaign_id=%s AND c.fired_at_turn IS NOT NULL
                 ORDER BY c.fired_at_turn""", (self.campaign_id,)).fetchall()

    def deltas_narrables(self):
        """Tripletas ground-truth para el chequeo Jericho-QA State Graph
        (reporte_validacion.py, sección 5): cada fila de state_deltas para
        npc.status, npc.affinity y quest.status, con el nombre de la
        entidad ya resuelto (evita que reporte_validacion.py tenga que
        conocer el esquema de npcs/quests). Estos tres campos se eligieron
        porque son los únicos con un vocabulario de salida lo bastante
        cerrado (enum, o numérico traducible a banda) como para construir
        un detector léxico honesto en español -- a diferencia de, por
        ejemplo, location.detail o character.inventory, donde el texto
        libre hace imposible un chequeo determinístico sin un extractor de
        tripletas real (NLP entrenado), que está fuera de alcance.

        `source` se devuelve para que el reporte pueda, si hace falta más
        adelante, distinguir deltas 'mechanical' (relojes, no requieren
        narración inmediata) de 'extracted' (si el Árbitro/Mundo lo
        escribió, se espera que el Narrador lo refleje).

        `old_value` se devuelve para que el reporte pueda filtrar
        npc.affinity a solo CRUCES de banda (ver jericho_qa_recall() en
        reporte_validacion.py) -- exigir que cada delta individual se
        narre por separado es una vara injusta cuando varios eventos
        pequeños seguidos caen en la misma banda de disposición sin
        cruzarla; eso no es la narración ignorando el cambio, es que no
        había cambio de banda que narrar."""
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT d.turn_id, d.entity_type::text AS entity_type,
                       d.field_name, d.old_value, d.new_value,
                       d.source::text AS source,
                       COALESCE(n.name, q.title) AS entity_name
                  FROM state_deltas d
                  LEFT JOIN npcs   n ON d.entity_type='npc'   AND n.id = d.entity_id
                  LEFT JOIN quests q ON d.entity_type='quest' AND q.id = d.entity_id
                 WHERE d.campaign_id=%s
                   AND (d.entity_type='npc'   AND d.field_name IN ('status','affinity')
                        OR d.entity_type='quest' AND d.field_name='status')
                 ORDER BY d.turn_id""", (self.campaign_id,)).fetchall()

    def lugar_estado(self, location_id):
        """Lo que motor/orquestador/mundo.py necesita para decidir MUN-4/5/6/7:
        si el lugar ya está congelado (`observed`/`full`, repetir
        `description_canonical` tal cual) o sigue en `sketch` (el LLM
        genera boceto nuevo)."""
        with self._conn() as c:
            self._tx(c)
            return c.execute("""
                SELECT id, kind, detail, description_canonical, observed_at_turn
                  FROM locations WHERE id=%s AND campaign_id=%s""",
                             (location_id, self.campaign_id)).fetchone()

    def fijar_lugar(self, location_id, description_canonical, turn_id,
                     detail="observed"):
        """Congela el detalle de un lugar la primera vez que el jugador
        pregunta algo concreto (MUN-5). A partir de aquí, `lugar_estado()`
        devuelve SIEMPRE este texto para este lugar (MUN-6) -- nunca se
        vuelve a llamar al LLM para redescribirlo, salvo que algo cambie
        de verdad en el mundo (eso sí es un delta nuevo, no un re-fijado)."""
        with self._conn() as c:
            self._tx(c)
            self.aplicar("location", location_id, "detail", detail, turn_id,
                          source="mechanical")
            c.execute("""
                UPDATE locations
                   SET description_canonical=%s, observed_at_turn=%s
                 WHERE id=%s AND campaign_id=%s""",
                      (description_canonical, turn_id, location_id,
                       self.campaign_id))
            c.commit()

    def semillas_sin_ubicar(self, session_id=None, limite=5):
        """MUN-3: semillas SIN ubicación, listas para plantarse donde el
        grupo esté. Se listan las más antiguas primero (FIFO) -- no hay
        orden narrativo correcto, pero sí hay uno injusto: dejar una
        semilla enterrada para siempre porque siempre se prioriza otra."""
        with self._conn() as c:
            self._tx(c)
            if session_id:
                return c.execute("""
                    SELECT id, kind, content FROM session_seeds
                     WHERE campaign_id=%s AND session_id=%s
                       AND location_id IS NULL AND planted_at_turn IS NULL
                     ORDER BY id LIMIT %s""",
                                 (self.campaign_id, session_id, limite)).fetchall()
            return c.execute("""
                SELECT id, kind, content FROM session_seeds
                 WHERE campaign_id=%s
                   AND location_id IS NULL AND planted_at_turn IS NULL
                 ORDER BY id LIMIT %s""",
                             (self.campaign_id, limite)).fetchall()

    def plantar_semilla(self, seed_id, location_id, turn_id):
        """Planta una semilla donde el grupo esté AHORA -- nunca al revés
        (el grupo nunca es empujado hacia donde estaba la semilla)."""
        with self._conn() as c:
            self._tx(c)
            c.execute("""
                UPDATE session_seeds
                   SET location_id=%s, planted_at_turn=%s
                 WHERE id=%s AND campaign_id=%s""",
                      (location_id, turn_id, seed_id, self.campaign_id))
            c.commit()
