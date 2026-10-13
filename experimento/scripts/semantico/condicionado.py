"""
cl2_recall_semantico_v2: el MISMO instrumento de comun.py con el nulo CONDICIONADO por mención de la entidad.

Por qué existe: la A2 de la v1 (sensibilidad_semantico.py) falló en SC2: insertar una oración que solo
NOMBRA a la entidad, sin cambio de estado, encendía el reconocimiento. La literatura lo predice: en los
sentence transformers la similitud coseno la dominan los participantes nominales compartidos
(Nikolaev y Padó, EACL 2023). La v1 comparaba «ventana del evento» contra «cualquier ventana de la campaña»,
y la mayoría de esas ventanas no nombran a la entidad: el nombre solo ya bastaba para superar el P95.

Qué cambia (y nada más):
  * Solo cuentan las oraciones que MENCIONAN a la entidad (regla de alias de abajo), tanto en la ventana
    real como en el nulo. La pregunta pasa de «¿esta ventana se parece al cambio?» a «entre las oraciones que
    hablan de esta entidad, ¿las de la ventana del evento hablan del cambio más que las de cualquier otro
    momento de la campaña?». La mención queda igualada en ambos lados.
  * Una ventana real sin ninguna mención = no reconocido (la narración no nombró a la entidad).
  * Un evento es evaluable solo si su nulo condicionado tiene al menos 20 ventanas (mismo mínimo que la v1).
Todo lo demás es idéntico a la v1 y se importa de comun.py sin tocarlo: eventos, consultas, VENTANA,
EXCLUSION, CUANTIL, búsqueda EXACTA en pgvector (sin índice aproximado), solo lectura.

Regla de alias (fijada antes de correr):
  * Texto normalizado: minúsculas, sin tildes ni diéresis, ñ -> n (lo mismo en SQL con translate()).
  * PNJ: cada palabra del nombre que empiece con mayúscula, tenga al menos 4 letras y no sea un artículo o
    preposición («Yenna Roldós» -> yenna | roldos). Si no hay ninguna («El hombre de los harapos»), el nombre
    completo como frase.
  * Misiones: el título completo como frase.
  * Coincidencia por palabra completa (\\m...\\M en PostgreSQL, \\b...\\b en Python).
"""
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comun as C   # noqa: E402

MIN_NULO = 20
STOP = {"el", "la", "los", "las", "de", "del", "y", "un", "una", "al", "en", "con", "por", "para"}
_DESDE_SQL, _HACIA_SQL = "áéíóúüñàèìòùâêîôû", "aeiouunaeiouaeiou"
NORM_SQL = f"translate(lower(content), '{_DESDE_SQL}', '{_HACIA_SQL}')"


def normalizar(texto):
    """Pasa a minúsculas y quita acentos (NFKD), para comparar menciones sin depender de la ortografía."""
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    return "".join(ch for ch in t if not unicodedata.combining(ch))


def alias(nombre, campo):
    """Lista de alias normalizados de la entidad (ver regla en el docstring del módulo)."""
    if campo.startswith("npc"):
        palabras = re.findall(r"[^\W\d_]+", nombre or "")
        propias = sorted({normalizar(w) for w in palabras
                          if w[:1].isupper() and len(w) >= 4 and normalizar(w) not in STOP})
        if propias:
            return propias
    frase = re.sub(r"\s+", " ", normalizar(nombre)).strip(" «»\"'")
    return [frase] if frase else []


def _escapar(a):
    """Escapa los metacaracteres de regex de un alias para usarlo literal en un patrón."""
    return re.sub(r"([.^$*+?()\[\]{}|\\])", r"\\\1", a)


def patron_sql(nombre, campo):
    """Expresión regular ARE de PostgreSQL (palabra completa) para usar contra NORM_SQL."""
    al = alias(nombre, campo)
    return r"\m(" + "|".join(_escapar(a) for a in al) + r")\M" if al else None


def menciona(oracion, nombre, campo):
    """Lo mismo en Python, para decidir si una oración INSERTADA por la A2 cuenta como mención."""
    al = alias(nombre, campo)
    if not al:
        return False
    return re.search(r"\b(" + "|".join(re.escape(a) for a in al) + r")\b", normalizar(oracion)) is not None


SQL_MAX_POR_TURNO_MENCION = f"""
SELECT turn_id, max(1 - (embedding <=> %s::vector)) AS s
  FROM medicion_oraciones
 WHERE campaign_id = %s AND turn_id BETWEEN %s AND %s AND {NORM_SQL} ~ %s
 GROUP BY turn_id
"""


def max_por_turno_mencion(conn, campaign_id, q, patron, desde=None, hasta=None):
    """{turn_id: máxima similitud coseno entre q y las oraciones de ese turno QUE MENCIONAN a la entidad}.
    Búsqueda exacta (sin índice aproximado). Turnos sin mención no aparecen."""
    if not patron:
        return {}
    filas = conn.execute(SQL_MAX_POR_TURNO_MENCION,
                         (C.vec_literal(q), campaign_id, desde or C.DESDE, hasta or C.HASTA, patron)).fetchall()
    return {int(f["turn_id"]): float(f["s"]) for f in filas}


def evaluar(s_turno, ev, reemplazo=None):
    """Decisión v2 de un evento. None = no evaluable (nulo condicionado con menos de MIN_NULO ventanas).
    `reemplazo` sustituye SOLO las puntuaciones de la ventana real (perturbaciones de la A2); el nulo sale
    siempre de la campaña sin tocar. Ventana real sin mención -> reconocido False, margen None."""
    t = ev["turno"]
    nul = C.nulo(s_turno, t)
    if nul.size < MIN_NULO:
        return None
    ventana = dict(s_turno)
    if reemplazo is not None:
        for u in range(t, t + C.VENTANA + 1):
            ventana.pop(u, None)
        ventana.update(reemplazo)
    real = C.puntuacion_ventana(ventana, t)
    if real is None:
        return {"s_real": None, "q95": float(np.quantile(nul, C.CUANTIL)), "margen": None, "z": None,
                "p_emp": None, "reconocido": False, "n_nulo": int(nul.size)}
    return C.decidir(real, nul)
