"""
Léxico común de los instrumentos A4b/c (respuesta_accion.py, anclaje_escenario.py).

Definición operacional (docs/research/a4bc_diseno_instrumentos.md, sección 2.1):
  1. limpiar(texto) = prosa(texto, "G1") de scripts/validacion_generar.py (quita las etiquetas de
     formato de G1 y el bloque «mecanica»; idempotente; en un texto sin etiquetas es solo strip()).
  2. spaCy es_core_news_sm con parser y ner desactivados.
  3. Unidad léxica: token con POS en el conjunto pedido, no stopword, lema = primera palabra del
     lema de spaCy, clave = minúsculas sin tildes, solo letras, longitud >= 3.

Todo es determinista (spaCy en CPU con versión fijada). Sin LLM, sin red, sin base de datos.
"""
import hashlib
import pickle
import sys
import unicodedata
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (RAIZ / "scripts", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from validacion_generar import prosa   # noqa: E402

POS_CONTENIDO = frozenset({"NOUN", "VERB", "ADJ"})
POS_CON_NOMBRES = POS_CONTENIDO | {"PROPN"}
_POS_TODOS = POS_CON_NOMBRES
DIR_CACHE = AQUI / "_cache"

_nlp = None


def modelo():
    """Carga perezosa (una vez por proceso) de es_core_news_sm con parser y ner desactivados."""
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("es_core_news_sm", disable=["parser", "ner"])
    return _nlp


def version_modelo():
    """Cadena spacy-X|es_core_news_sm-Y que identifica la versión usada; invalida la caché en disco."""
    import spacy
    return f"spacy-{spacy.__version__}|es_core_news_sm-{modelo().meta['version']}"


def limpiar(texto):
    """prosa(texto, 'G1'): idempotente; idéntica a prosa(texto, 'G2') si no hay etiquetas."""
    return prosa(texto or "", "G1")


def _sin_tildes(s):
    """Quita las marcas diacríticas (NFD sin categoría Mn)."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clave(lema):
    """Clave de comparación de un lema: primera palabra, minúsculas, sin tildes; None si no es
    alfabética o tiene menos de 3 letras."""
    partes = (lema or "").split()
    if not partes:
        return None
    k = _sin_tildes(partes[0]).lower()
    return k if len(k) >= 3 and k.isalpha() else None


def _extraer(doc):
    """Tupla de (clave, POS) de los tokens de contenido no stopword de un Doc de spaCy."""
    out = []
    for t in doc:
        if t.pos_ in _POS_TODOS and not t.is_stop:
            k = clave(t.lemma_)
            if k:
                out.append((k, t.pos_))
    return tuple(out)


_MEMO = {}          # texto limpio -> tokens (memoria de proceso; se vacía al pasar de 100 000 entradas)


def _memorizar(t, toks):
    """Guarda en la memoria de proceso; la vacía entera al llegar a 100 000 entradas para acotar el consumo."""
    if len(_MEMO) >= 100000:
        _MEMO.clear()
    _MEMO[t] = toks


def _tokens_limpio(texto_limpio):
    """Tokens de un texto ya limpio, con memoización; () si está vacío."""
    if not texto_limpio:
        return ()
    if texto_limpio not in _MEMO:
        _memorizar(texto_limpio, _extraer(modelo()(texto_limpio)))
    return _MEMO[texto_limpio]


def tokens(texto):
    """Tupla de (clave, POS) de los tokens de contenido (NOUN/VERB/ADJ/PROPN) del texto limpio."""
    return _tokens_limpio(limpiar(texto))


def tokens_lote(textos):
    """Igual que [tokens(t) for t in textos] pero con nlp.pipe (mucho más rápido)."""
    limpios = [limpiar(t) for t in textos]
    nuevos = {}
    pendientes = [t for t in dict.fromkeys(limpios) if t and t not in _MEMO]
    if pendientes:
        for t, doc in zip(pendientes, modelo().pipe(pendientes, batch_size=128)):
            nuevos[t] = _extraer(doc)
            _memorizar(t, nuevos[t])
    return [() if not t else (nuevos[t] if t in nuevos else _MEMO.get(t) or _tokens_limpio(t))
            for t in limpios]


def filtrar(toks, pos=POS_CONTENIDO, excluir=None):
    """Conjunto de claves de una tupla de tokens, por POS y con lista de exclusión."""
    return frozenset(k for k, p in toks if p in pos and (excluir is None or k not in excluir))


def contar_tokens(toks, pos=POS_CONTENIDO, excluir=None):
    """Conteo de claves de una tupla de tokens, filtrado por POS y lista de exclusión."""
    return Counter(k for k, p in toks if p in pos and (excluir is None or k not in excluir))


def lemas(texto, pos=POS_CONTENIDO, excluir=None):
    """Conjunto de lemas de contenido de un texto (tokens + filtrar)."""
    return filtrar(tokens(texto), pos, excluir)


def contar(texto, pos=POS_CONTENIDO, excluir=None):
    """Conteo de lemas de contenido de un texto (tokens + contar_tokens)."""
    return contar_tokens(tokens(texto), pos, excluir)


def tokens_lote_cacheado(nombre, textos, directorio=None):
    """tokens_lote con caché en disco (pickle) por `nombre`; se invalida si cambian los textos o la
    versión de spaCy/modelo. Devuelve una lista alineada con `textos`."""
    directorio = Path(directorio) if directorio else DIR_CACHE
    ruta = directorio / f"{nombre}.pkl"
    huella = hashlib.sha1(("\x00".join(textos) + "|" + version_modelo()).encode("utf-8")).hexdigest()
    if ruta.exists():
        try:
            d = pickle.loads(ruta.read_bytes())
            if d.get("huella") == huella:
                return d["tokens"]
        except Exception:
            pass
    toks = tokens_lote(textos)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(pickle.dumps({"huella": huella, "tokens": toks}))
    return toks
