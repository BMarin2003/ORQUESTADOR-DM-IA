"""
Piezas compartidas del instrumento EXPLORATORIO «CL-2 recall semántico» (cl2_recall_semantico).

Qué mide: de los cambios de estado que la base registró (los MISMOS eventos que Jericho-QA:
Campaña.deltas_narrables() con el mismo filtro de reporte_validacion.jericho_qa_recall), qué
fracción aparece reflejada en la narración de su ventana (turno del delta y el siguiente), pero
reconociendo PARÁFRASIS: en vez de buscar un lexema («muert…», «desconf…»), compara por similitud
coseno la oración-consulta del evento («Yenna ha desaparecido.») con cada oración de la ventana.

Cómo decide sin umbral arbitrario: nulo por permutación EXACTO y determinista. Para cada evento
se calcula la misma puntuación (máxima similitud de una oración de la ventana con la consulta) en
TODAS las ventanas de 2 turnos de la misma campaña que estén a más de EXCLUSION turnos del evento.
El evento se da por reconocido si su ventana real supera el percentil 95 de ese nulo. Por
construcción, una ventana elegida al azar se «reconoce» como mucho ~5 % de las veces: esa es la
tasa de falsos positivos de referencia (a diferencia de Jericho, cuyo azar hubo que medirlo
después: 12.9 % global, 17-19 % en npc.affinity). Como el nulo sale de la MISMA campaña, también
absorbe la diferencia de longitud de turno entre G1 y G2 (más oraciones -> máximo más alto en la
ventana real y en el nulo por igual).

Dónde vive: en la tabla ADITIVA medicion_oraciones (migrations/002_medicion_semantica.sql), columna
vector(1024) de pgvector, con el mismo bge-m3 «versión FIJA» que el esquema prevé para sus tablas
vectoriales. Un fragmento = una oración de la narración NORMALIZADA (normalizar_turno) de los turnos
1..1400. No se usa narrative_chunks: es de la capa de generación (los brazos nunca la leyeron y así
sigue) y su índice HNSW es aproximado. El estado sigue siendo relacional: los filtros (campaña, turno,
evento) son columnas exactas y el vector solo ordena por parecido. Búsqueda EXACTA y determinista:
max() + GROUP BY sobre las filas de la campaña (índice B-tree), sin índice aproximado.

Alcance (no se cambia): instrumento de medición sobre el corpus ya generado. No toca la
generación, no regenera campañas y no compara gestores de memoria. Clasificación: EXPLORATORIO
hasta que pase su propia prueba A2 (sensibilidad_semantico.py).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import reporte_validacion as RV   # noqa: E402  (orquestador/reporte_validacion.py: _KEYWORDS_*, _banda_afinidad -- importadas, nunca duplicadas)

# ---------------------------------------------------------------- parámetros fijados ANTES de correr
MODELO = "BAAI/bge-m3"          # el mismo que nombra migrations/001_schema.sql para las tablas vectoriales
DIM = 1024                      # = vector(1024) del esquema
HASTA = 1400                    # diseño: 1 400 turnos por campaña
DESDE = 1                       # turno 0 = lore; se excluye
VENTANA = 1                     # igual que jericho_qa_recall(ventana=1): turno del delta y el siguiente
EXCLUSION = 5                   # el nulo no usa ventanas a <= 5 turnos del evento (mismo criterio que el diagnóstico de Jericho)
CUANTIL = 0.95                  # reconocido <=> puntuación real > percentil 95 del nulo de su campaña
MIN_PALABRAS = 2                # fragmentos de 1 palabra («—¿Y?») no son oraciones
VERSION_DIVISOR = "regex-v1"    # se registra en el manifiesto; si cambia, hay que re-embeber

TABLA = "medicion_oraciones"
MIGRACION = RAIZ / "migrations" / "002_medicion_semantica.sql"
SALIDA_DATOS = RAIZ / "datos_v2" / "semantico"
SALIDA_DOCS = RAIZ / "docs" / "reportes" / "semantico"
MANIFIESTO = SALIDA_DOCS / "manifiesto_embeddings.json"

# ---------------------------------------------------------------- oraciones
_CORTE = re.compile(r"(?<=[.!?…»\"])\s+|\n+")


def dividir_oraciones(texto):
    """Oraciones de un turno, en orden. Regla fija y determinista (sin modelo): corta tras . ! ? … »
    o comillas seguidos de espacio, y en saltos de línea. Descarta fragmentos de menos de
    MIN_PALABRAS palabras."""
    piezas = (p.strip() for p in _CORTE.split(texto or ""))
    return [p for p in piezas if len(p.split()) >= MIN_PALABRAS]


# ---------------------------------------------------------------- eventos (el MISMO conjunto que Jericho-QA)
def evento_desde_delta(d):
    """Traduce una fila de Campaña.deltas_narrables() al evento narrable que evalúa Jericho-QA, con
    EXACTAMENTE su filtro (npc.status / quest.status con vocabulario distintivo; npc.affinity solo si
    cruza de banda; 'alive', 'active', 'unknown' y la banda 'neutral' excluidos). None si Jericho lo
    excluye. test_semantico.py comprueba que el conteo coincide con RV.jericho_qa_recall."""
    campo = f"{d['entity_type']}.{d['field_name']}"
    nombre = d.get("entity_name") or "?"
    if campo == "npc.status":
        estado = str(d["new_value"]).strip('"').lower()
        claves = RV._KEYWORDS_NPC_STATUS.get(estado)
    elif campo == "quest.status":
        estado = str(d["new_value"]).strip('"').lower()
        claves = RV._KEYWORDS_QUEST_STATUS.get(estado)
    elif campo == "npc.affinity":
        try:
            estado = RV._banda_afinidad(d["new_value"])
        except (TypeError, ValueError):
            return None
        if d.get("old_value") is not None:
            try:
                if RV._banda_afinidad(d["old_value"]) == estado:
                    return None
            except (TypeError, ValueError):
                pass
        claves = RV._KEYWORDS_AFINIDAD_BANDA.get(estado)
    else:
        return None
    if not claves:
        return None
    return {"turno": int(d["turn_id"]), "campo": campo, "estado": estado, "entidad": nombre, "delta": d}


# ---------------------------------------------------------------- consulta (lo que se busca en la ventana)
# Oraciones declarativas neutras. No son las de los refuerzos de Jericho ni las paráfrasis de la A2.
_CONSULTA = {
    ("npc.status", "dead"): "{n} ha muerto.",
    ("npc.status", "missing"): "{n} ha desaparecido.",
    ("npc.status", "captured"): "{n} ha sido capturado.",
    ("quest.status", "completed"): "La misión «{n}» se ha completado.",
    ("quest.status", "failed"): "La misión «{n}» ha fracasado.",
    ("quest.status", "abandoned"): "La misión «{n}» ha sido abandonada.",
    ("npc.affinity", "hostile"): "{n} se ha vuelto hostil contigo.",
    ("npc.affinity", "wary"): "{n} ahora desconfía de ti.",
    ("npc.affinity", "cold"): "{n} se ha vuelto frío y distante contigo.",
    ("npc.affinity", "cordial"): "{n} ahora te trata con cordialidad.",
    ("npc.affinity", "loyal"): "{n} ahora te es leal.",
    ("npc.affinity", "devoted"): "{n} ahora te es completamente devoto.",
}


def consulta(ev):
    return _CONSULTA[(ev["campo"], ev["estado"])].format(n=ev["entidad"])


# ---------------------------------------------------------------- vectores
def vec_literal(v):
    """Texto que pgvector acepta como vector: '[0.0123457,-0.5,...]' (7 cifras significativas)."""
    return "[" + ",".join(f"{float(x):.7g}" for x in v) + "]"


class Embedder:
    """bge-m3 (denso) vía sentence-transformers, vectores normalizados (coseno = producto punto).
    Se carga una sola vez. `revision` fija el commit exacto del modelo en Hugging Face: la primera
    corrida lo registra en el manifiesto y las siguientes lo exigen (ver revision_fijada())."""

    def __init__(self, revision=None, dispositivo="cpu", lote=64):
        from sentence_transformers import SentenceTransformer   # import tardío: los tests no lo necesitan
        self.revision = revision
        self.lote = lote
        self.modelo = SentenceTransformer(MODELO, revision=revision, device=dispositivo)
        if self.modelo.get_sentence_embedding_dimension() != DIM:
            raise RuntimeError(f"{MODELO} devuelve {self.modelo.get_sentence_embedding_dimension()} dimensiones, el esquema espera {DIM}")

    def __call__(self, textos):
        if not textos:
            return np.zeros((0, DIM), dtype=np.float32)
        return np.asarray(self.modelo.encode(list(textos), batch_size=self.lote, normalize_embeddings=True,
                                             convert_to_numpy=True, show_progress_bar=False), dtype=np.float32)


def revision_fijada():
    """Commit del modelo registrado por embeber_corpus.py (None si todavía no se embebió nada)."""
    if MANIFIESTO.exists():
        return json.loads(MANIFIESTO.read_text(encoding="utf-8")).get("revision")
    return None


def resolver_revision():
    """Commit actual de BAAI/bge-m3 en Hugging Face (solo la primera vez; luego manda el manifiesto)."""
    try:
        from huggingface_hub import model_info
        return model_info(MODELO).sha
    except Exception as e:   # sin red o sin huggingface_hub: se detiene, no se adivina
        raise RuntimeError(f"No se pudo resolver el commit de {MODELO} ({e}). Pásalo con --revision.") from e


# ---------------------------------------------------------------- consultas a pgvector (búsqueda EXACTA)
SQL_MAX_POR_TURNO = """
SELECT turn_id, max(1 - (embedding <=> %s::vector)) AS s
  FROM medicion_oraciones
 WHERE campaign_id = %s AND turn_id BETWEEN %s AND %s
 GROUP BY turn_id
"""
# max() + GROUP BY sobre el B-tree (campaign_id, turn_id): recorrido exacto de las oraciones de la campaña.


def max_por_turno(conn, campaign_id, q):
    """{turn_id: máxima similitud coseno entre la consulta q y las oraciones de ese turno}."""
    filas = conn.execute(SQL_MAX_POR_TURNO, (vec_literal(q), campaign_id, DESDE, HASTA)).fetchall()
    return {int(f["turn_id"]): float(f["s"]) for f in filas}


# ---------------------------------------------------------------- decisión: ventana real vs nulo exacto
def puntuacion_ventana(s_turno, t):
    """Máxima similitud en la ventana [t, t+VENTANA]; None si la ventana no tiene oraciones."""
    vals = [s_turno[u] for u in range(t, t + VENTANA + 1) if u in s_turno]
    return max(vals) if vals else None


def nulo(s_turno, t):
    """Puntuaciones de TODAS las ventanas de la campaña a más de EXCLUSION turnos del evento
    (sin muestreo: determinista)."""
    out = []
    for u in sorted(s_turno):
        if abs(u - t) <= EXCLUSION + VENTANA:
            continue
        v = puntuacion_ventana(s_turno, u)
        if v is not None:
            out.append(v)
    return np.asarray(out, dtype=float)


def decidir(real, nul):
    """Veredicto y medidas continuas de un evento. margen = real - percentil 95 del nulo (>0 =
    reconocido); z = (real - media nulo) / desv. nulo; p_emp = (1 + #nulo >= real) / (1 + n)."""
    if real is None or nul.size < 20:
        return None
    q = float(np.quantile(nul, CUANTIL))
    sd = float(nul.std(ddof=1)) or 1e-9
    return {"s_real": real, "q95": q, "margen": real - q, "z": (real - float(nul.mean())) / sd,
            "p_emp": (1 + int((nul >= real).sum())) / (1 + nul.size), "reconocido": real > q, "n_nulo": int(nul.size)}


def evaluar_evento(s_turno, ev, s_turno_reemplazo=None):
    """Decisión de un evento. `s_turno_reemplazo` (opcional) sustituye SOLO las puntuaciones de su
    ventana real (lo usan las perturbaciones de la A2); el nulo sale siempre de la campaña sin tocar."""
    t = ev["turno"]
    ventana = dict(s_turno)
    if s_turno_reemplazo is not None:
        for u in range(t, t + VENTANA + 1):
            ventana.pop(u, None)
        ventana.update(s_turno_reemplazo)
    return decidir(puntuacion_ventana(ventana, t), nulo(s_turno, t))


def jericho_reconoce(ev, tpi):
    """Veredicto del instrumento léxico REAL (RV.jericho_qa_recall) para este mismo evento."""
    r = RV.jericho_qa_recall([ev["delta"]], tpi)
    return None if r["recall_global"] is None else r["recall_global"] == 1.0
