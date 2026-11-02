"""
Acceso de SOLO LECTURA a la base y reconstrucción del `Contexto` de un turno
real, tal como lo veía el motor al generarlo (vertical_slice.py, paso 1):

  * entidades: las de Campaña.entidades() en ese momento (created_at_turn <
    turno; objetos = con portador o creados en los 20 turnos previos);
  * estado de PNJ: estado histórico = valor inicial + deltas npc.status de
    state_deltas con turn_id < turno (los del propio turno se escriben DESPUÉS
    de verificar);
  * escena_anterior = dm_output del turno anterior; tiradas = dados.resolver_turno
    con la misma semilla del motor (campaña, turno, habilidad) sobre el texto
    del jugador guardado en player_buffer.

La conexión se abre con read_only=True: la base rechaza cualquier escritura.
"""
import json
import random
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
for _p in (RAIZ / "motor" / "orquestador", RAIZ / "motor" / "jugador", RAIZ / "experimento" / "scripts", AQUI):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import psycopg                      # noqa: E402
from psycopg.rows import dict_row   # noqa: E402

import dados                        # noqa: E402
import db as bd                     # noqa: E402
import instrumentos_texto as it     # noqa: E402

VENTANA_ITEMS = 20          # Campaña.entidades(ventana_items=20)


def abrir_conexion():
    """Conexión de solo lectura (SELECT únicamente)."""
    c = psycopg.connect(bd.DSN, row_factory=dict_row)
    c.read_only = True
    return c


# ---------------------------------------------------------------- muestreo
def cargar_pares():
    """Lee los ids de campaña G1/G2 de las parejas de los dos lotes (Par07-17 = v1, Par18-27 = v2) desde docs/ids_par*.json."""
    pares = []
    for fichero, lote in (("docs/ids_par07-17.json", "v1"), ("docs/ids_par18-27.json", "v2")):
        for e in json.loads((RAIZ / fichero).read_text(encoding="utf-8")):
            pares.append({"par": e["par"], "lote": lote, "lugar": e.get("lugar"),
                          "campaign_g1": e["campaign_g1"], "campaign_g2": e["campaign_g2"]})
    return pares


def plan_muestra(pares, semilla=20260920, n_pares=10, n_por_par=15, n_ventanas_por_par=6,
                 k_ventana=8, ultimo_turno=1400):
    """Muestra reproducible: n_pares pares (mitad de cada lote), n_por_par turnos por
    par y brazo (los mismos ids en G1 y G2), y n_ventanas_por_par ventanas de k_ventana
    turnos consecutivos por par y brazo. Turno 0 (lore) y 1 (escena = lore) excluidos."""
    rng = random.Random(semilla)
    elegidos = []
    for lote in ("v1", "v2"):
        del_lote = [p for p in pares if p["lote"] == lote]
        elegidos += rng.sample(del_lote, n_pares // 2 if lote == "v1" else n_pares - n_pares // 2)
    elegidos.sort(key=lambda p: p["par"])
    turnos, ventanas = [], []
    for p in elegidos:
        ids = sorted(rng.sample(range(2, ultimo_turno + 1), n_por_par))
        starts = sorted(rng.randint(2, ultimo_turno - k_ventana + 1) for _ in range(n_ventanas_por_par))
        for brazo in ("G1", "G2"):
            cid = p["campaign_g1" if brazo == "G1" else "campaign_g2"]
            turnos += [{"par": p["par"], "lote": p["lote"], "brazo": brazo, "campaign_id": cid, "turn": t}
                       for t in ids]
            ventanas += [{"par": p["par"], "lote": p["lote"], "brazo": brazo, "campaign_id": cid,
                          "start": s, "k": k_ventana} for s in starts]
    return {"semilla": semilla, "pares": elegidos, "turnos": turnos, "ventanas": ventanas}


# ---------------------------------------------------------------- campaña
_PERSONAJES = None


def personajes():
    """Personajes jugadores de motor/jugador/personajes_jugadores.json, cargados una sola vez (caché de módulo)."""
    global _PERSONAJES
    if _PERSONAJES is None:
        _PERSONAJES = json.loads((RAIZ / "motor" / "jugador" / "personajes_jugadores.json")
                                 .read_text(encoding="utf-8"))["personajes"]
    return _PERSONAJES


class DatosCampana:
    """Todo lo de UNA campaña necesario para reconstruir contextos (una sola carga)."""

    def __init__(self, conn, campaign_id, brazo, par=None):
        """Carga con SELECT la campaña completa (turnos, entidades, historia de estado de PNJ y datos del PJ) para no volver a consultar la base.

        El PJ es el personaje de la campaña cuyo nombre figura en personajes_jugadores.json (si no, el primero).
        El HP es el ACTUAL: la base no guarda su historia."""
        self.campaign_id = str(campaign_id)
        self.brazo = brazo
        self.par = par
        self.turnos = {r["turn_id"]: r for r in conn.execute(
            "SELECT turn_id, player_buffer, dm_output FROM turn_log WHERE campaign_id=%s ORDER BY turn_id",
            (campaign_id,)).fetchall()}
        self._ents = conn.execute("""
            SELECT 'npc' AS tipo, name AS nombre, created_at_turn AS creado, NULL::uuid AS portador FROM npcs WHERE campaign_id=%(c)s
            UNION ALL SELECT 'location', name, created_at_turn, NULL FROM locations WHERE campaign_id=%(c)s
            UNION ALL SELECT 'faction', name, created_at_turn, NULL FROM factions WHERE campaign_id=%(c)s
            UNION ALL SELECT 'quest', title, created_at_turn, NULL FROM quests WHERE campaign_id=%(c)s
            UNION ALL SELECT 'character', name, 0, NULL FROM characters WHERE campaign_id=%(c)s
            UNION ALL SELECT 'item', name, created_at_turn, holder_id FROM items WHERE campaign_id=%(c)s
            ORDER BY 1, 2""", {"c": campaign_id}).fetchall()
        # estado de PNJ: valor inicial + historia de deltas npc.status
        ds = conn.execute("""
            SELECT n.name AS nombre, sd.turn_id, sd.old_value, sd.new_value
              FROM state_deltas sd JOIN npcs n ON n.id = sd.entity_id
             WHERE sd.campaign_id=%s AND sd.entity_type='npc' AND sd.field_name='status'
             ORDER BY sd.turn_id, sd.id""", (campaign_id,)).fetchall()
        self._estado = {}
        for d in ds:
            ini, hist = self._estado.setdefault(d["nombre"], ["alive", []])
            if not hist and d["old_value"] is not None:
                self._estado[d["nombre"]][0] = d["old_value"]
            self._estado[d["nombre"]][1].append((d["turn_id"], d["new_value"]))
        nombres_json = {p["nombre"]: p for p in personajes()}
        chars = conn.execute(
            "SELECT name, hp_current, hp_max FROM characters WHERE campaign_id=%s ORDER BY created_at",
            (campaign_id,)).fetchall()
        ch = next((c for c in chars if c["name"] in nombres_json), chars[0] if chars else None)
        self.pj_nombre = ch["name"] if ch else None
        self.hp_current = ch["hp_current"] if ch else None
        self.hp_max = ch["hp_max"] if ch else None
        self.pj = nombres_json.get(self.pj_nombre)
        self.nombres_pj = set(nombres_json)
        self._prefijos = None

    # -- texto
    def texto(self, t):
        """Salida del DM del turno `t` ('' si el turno no existe)."""
        r = self.turnos.get(t)
        return (r["dm_output"] or "") if r else ""

    def accion(self, t):
        """Acción del jugador del turno `t`: texto del primer elemento de player_buffer ('' si no hay)."""
        r = self.turnos.get(t)
        buf = (r or {}).get("player_buffer") or []
        return buf[0].get("text", "") if buf and isinstance(buf[0], dict) else ""

    # -- estado
    def estado_en(self, nombre, t):
        """Estado del PNJ al INICIO del turno t (deltas con turn_id < t)."""
        ini, hist = self._estado.get(nombre, ["alive", []])
        est = ini
        for turno, nuevo in hist:
            if turno < t:
                est = nuevo
        return est

    def _entidades_en(self, t):
        """Entidades visibles en el turno `t` para el gazetteer: creadas hasta el turno anterior.

        Los personajes siempre cuentan; los objetos solo si tienen portador o fueron creados en los últimos
        VENTANA_ITEMS turnos, igual que Campaña.entidades(ventana_items=20) del motor."""
        ult = t - 1                                   # entidades creadas hasta el turno anterior
        umbral_items = max(0, ult - VENTANA_ITEMS)
        visibles = []
        for e in self._ents:
            if e["tipo"] == "character":
                ok = True
            elif e["tipo"] == "item":
                ok = e["creado"] <= ult and (e["portador"] is not None or e["creado"] >= umbral_items)
            else:
                ok = e["creado"] <= ult
            if ok:
                visibles.append({"tipo": e["tipo"], "nombre": e["nombre"]})
        return visibles

    def _prefijo(self, t):
        """Entidades ya mencionadas en el texto de turnos anteriores a `t` (frozenset de menciones).

        Calcula de una vez el acumulado por turno la primera vez que se llama y lo guarda en caché."""
        if self._prefijos is None:
            todas = [{"tipo": e["tipo"], "nombre": e["nombre"]} for e in self._ents]
            acumulado, snap = set(), {}
            ultimo = max(self.turnos) if self.turnos else 0
            for i in range(1, ultimo + 2):
                snap[i] = frozenset(acumulado)        # menciones en turnos < i
                acumulado |= it.entidades_mencionadas(self.texto(i), todas)
            self._prefijos = snap
        return self._prefijos.get(t, frozenset())

    def tiradas(self, t):
        """Tiradas del turno `t`, recalculadas con motor/jugador/dados.py de HOY, no las que el motor guardó entonces.

        Devuelve [] si la acción no lleva marcas `{...}` o si la resolución falla. Diferencia legítima
        conocida: Par07-17 aún no tenía tiradas de combate."""
        accion = self.accion(t)
        if not accion or "{" not in accion:
            return []
        try:
            tabla = dados.tabla_pj(self.pj) if self.pj else None
            _, tiradas, _ = dados.resolver_turno(accion, self.campaign_id, t, tabla_modificadores=tabla)
        except Exception:
            return []
        return tiradas

    def contexto(self, t):
        """Reconstruye el Contexto de instrumentos_texto para el turno `t` con el estado de la campaña tal como estaba al inicio de ese turno (salvo HP del PJ y portadores de objetos, que son los actuales)."""
        ents = self._entidades_en(t)
        estados = {e["nombre"]: self.estado_en(e["nombre"], t) for e in ents if e["tipo"] == "npc"}
        nombres = {e["nombre"] for e in ents}
        return it.Contexto(
            pj_nombre=self.pj_nombre, entidades=ents, estados_pnj=estados,
            hp_current=self.hp_current, hp_max=self.hp_max, tiradas=self.tiradas(t),
            escena_anterior=self.texto(t - 1), nombres_pj=set(self.nombres_pj),
            previas=frozenset(self._prefijo(t) & nombres), brazo=self.brazo)


def guardado_en_turn_validation(conn, campaign_id, turn_ids):
    """Filas de turn_validation de esos turnos: {turn_id: fila}."""
    rs = conn.execute("SELECT * FROM turn_validation WHERE campaign_id=%s AND turn_id = ANY(%s)",
                      (campaign_id, list(turn_ids))).fetchall()
    return {r["turn_id"]: r for r in rs}
