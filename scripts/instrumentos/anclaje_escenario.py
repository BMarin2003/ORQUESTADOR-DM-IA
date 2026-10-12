"""
anclaje_escenario.py -- CR-2b: ¿la narración está anclada en el escenario de la campaña (lore, lugares,
facciones, PNJ) y no en otro?

Instrumento DETERMINISTA (sin LLM, sin red). Definición operacional en
docs/research/a4bc_diseno_instrumentos.md, sección 2.3; expectativas en matriz_a4bc.py.

  * Referencia del escenario = lore (turno 0) + campos descriptivos de world_parNN.json y
    personas_parNN.json (sin campos de autoría ni ocultos).
  * Vector = TF-IDF sobre lemas (spaCy es_core_news_sm) con tf sublineal (1 + ln tf) e
    idf(t) = ln((1+N)/(1+df)) + 1, df = nº de las N=42 campañas cuya narración contiene el lema
    (los términos genéricos pesan ~1; los del escenario, ~4). Salida = coseno con la referencia.
  * Variante «con» (NOUN/VERB/ADJ/PROPN) y variante «sn» (sin nombres propios ni lemas de los
    nombres del escenario: evita el atajo de mencionar nombres).
  * Por turno (cos_turno) y por ventana de k=8 turnos (suma de conteos por turno: invariante al
    orden de los turnos).

Límite: mide vocabulario compartido con la referencia, no «arraigo» en sentido pleno; no distingue
deriva de evolución legítima del mundo.
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

import lemas_es as le   # noqa: E402

VARIANTES = ("con", "sn")
K_VENTANA = 8
_POS = {"con": le.POS_CON_NOMBRES, "sn": le.POS_CONTENIDO}


# ---------------------------------------------------------------- fixtures del escenario
def cargar_fixtures(par):
    """Lee world_parNN.json y personas_parNN.json de fixtures/real para el par indicado; devuelve (world, personas)."""
    d = RAIZ / "fixtures" / "real"
    w = json.loads((d / f"world_par{par}.json").read_text(encoding="utf-8"))
    p = json.loads((d / f"personas_par{par}.json").read_text(encoding="utf-8"))
    return w, p


def _pnj(personas):
    """Entradas de `personas` que son PNJ (dict con nombre)."""
    return [v for v in personas.values() if isinstance(v, dict) and v.get("name")]


def nombres_escenario(world, personas):
    """Nombres propios: localizaciones, facciones, PNJ y PJ (no los títulos de misión)."""
    n = [x["name"] for x in world.get("locations", []) if x.get("name")]
    n += [x["name"] for x in world.get("factions", []) if x.get("name")]
    n += [v["name"] for v in _pnj(personas)]
    n += [x["name"] for x in world.get("characters", []) if x.get("name")]
    return list(dict.fromkeys(n))


def _textos(*xs):
    """Aplana a una lista los textos no vacíos de los argumentos, que pueden ser str o secuencias de str."""
    out = []
    for x in xs:
        if isinstance(x, str) and x.strip():
            out.append(x)
        elif isinstance(x, (list, tuple)):
            out += [y for y in x if isinstance(y, str) and y.strip()]
    return out


def texto_referencia(lore, world, personas):
    """Lore + descripciones (ver docstring del módulo). Excluye _arquetipo, _nota, voice_notes,
    secrets, knowledge y todo campo numérico."""
    piezas = [lore or ""]
    for x in world.get("locations", []):
        piezas += _textos(x.get("name"), x.get("description_canonical"), x.get("sketch_text"),
                          [v for v in (x.get("culture_overrides") or {}).values() if isinstance(v, str)])
    for x in world.get("factions", []):
        piezas += _textos(x.get("name"), x.get("description"))
    for x in world.get("quests", []):
        piezas += _textos(x.get("title"), x.get("description"))
    for x in world.get("clocks", []):
        piezas += _textos(x.get("agenda"))
    for v in _pnj(personas):
        piezas += _textos(v.get("name"), v.get("species"), v.get("social_role"), v.get("appearance"),
                          v.get("internal_contradiction"), v.get("traits"), v.get("taboos"))
    return "\n".join(piezas)


def lemas_nombres(nombres):
    """Claves de las palabras de los nombres propios (y sus lemas de spaCy)."""
    out = set()
    for n in nombres:
        for w in n.split():
            k = le.clave(w)
            if k:
                out.add(k)
        out |= {k for k, _ in le.tokens(n)}
    return frozenset(out)


class Escenario:
    """Referencia de un par: tokens del lore + descripciones y lemas de sus nombres propios."""

    def __init__(self, par, tokens_ref, nombres_lemas, nombres=()):
        """Guarda la referencia del par como tuplas/frozenset inmutables."""
        self.par = par
        self.tokens_ref = tuple(tokens_ref)
        self.nombres_lemas = frozenset(nombres_lemas)
        self.nombres = tuple(nombres)

    @classmethod
    def de_fixtures(cls, par, lore, world, personas):
        """Construye la referencia a partir del lore y los fixtures world/personas del par."""
        nombres = nombres_escenario(world, personas)
        return cls(par, le.tokens(texto_referencia(lore, world, personas)), lemas_nombres(nombres), nombres)

    @classmethod
    def de_textos(cls, par, lore, nombres):
        """Construye la referencia solo con lore y lista de nombres (sin fixtures), p. ej. para pruebas."""
        return cls(par, le.tokens(lore + "\n" + "\n".join(nombres)), lemas_nombres(nombres), nombres)


# ---------------------------------------------------------------- modelo TF-IDF (idf de las 42 campañas)
def _filtro(variante, escenario):
    """Devuelve (POS admitidos, lemas excluidos) de la variante; solo «sn» excluye los nombres del escenario."""
    return _POS[variante], (escenario.nombres_lemas if variante == "sn" else None)


class ModeloAnclaje:
    """Modelo TF-IDF del anclaje: df por variante sobre las N campañas y vectores de referencia cacheados por (par, variante)."""
    def __init__(self, df, n_docs):
        """Guarda df por variante y nº de documentos; la caché de vectores de referencia empieza vacía."""
        self.df = df                      # {"con": Counter, "sn": Counter}
        self.n_docs = n_docs
        self._ref = {}

    @classmethod
    def desde_campanas(cls, campanas):
        """campanas = [{"nombres": frozenset de lemas de nombres del par, "turnos": [tokens por turno]}].
        df(t) = nº de campañas en cuya narración aparece t (sn: sin los nombres de su propio par)."""
        df = {"con": Counter(), "sn": Counter()}
        for c in campanas:
            con, sn = set(), set()
            for toks in c["turnos"]:
                con |= le.filtrar(toks, _POS["con"])
                sn |= le.filtrar(toks, _POS["sn"], c["nombres"])
            df["con"].update(con)
            df["sn"].update(sn)
        return cls(df, len(campanas))

    def idf(self, variante, t):
        """idf suavizado ln((1+N)/(1+df)) + 1; un término ausente de todas las campañas pesa el máximo."""
        return math.log((1 + self.n_docs) / (1 + self.df[variante].get(t, 0))) + 1.0

    def vector(self, variante, conteo):
        """Vector TF-IDF disperso con tf sublineal (1 + ln c) a partir de un conteo de lemas."""
        return {t: (1.0 + math.log(c)) * self.idf(variante, t) for t, c in conteo.items() if c > 0}

    def vector_ref(self, escenario, variante):
        """Vector TF-IDF de la referencia del escenario; se calcula una vez por (par, variante)."""
        k = (escenario.par, variante)
        if k not in self._ref:
            pos, excl = _filtro(variante, escenario)
            self._ref[k] = self.vector(variante, le.contar_tokens(escenario.tokens_ref, pos, excl))
        return self._ref[k]


def _coseno(a, b):
    """Coseno entre dos vectores dispersos; 0.0 si alguno está vacío o no comparten términos."""
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a, b = b, a
    num = sum(w * b.get(t, 0.0) for t, w in a.items())
    if num == 0.0:
        return 0.0
    return num / (math.sqrt(sum(w * w for w in a.values())) * math.sqrt(sum(w * w for w in b.values())))


def conteo_ventana(lista_tokens, variante, escenario):
    """Suma de los conteos de lemas de varios turnos (el orden no importa)."""
    pos, excl = _filtro(variante, escenario)
    total = Counter()
    for toks in lista_tokens:
        total.update(le.contar_tokens(toks, pos, excl))
    return total


def cos_tokens(modelo, escenario, lista_tokens, variante="con"):
    """Coseno entre la referencia del escenario y el vector de la ventana formada por `lista_tokens`."""
    v = modelo.vector(variante, conteo_ventana(lista_tokens, variante, escenario))
    return _coseno(v, modelo.vector_ref(escenario, variante))


def cos_turno(modelo, escenario, texto, variante="con"):
    """Coseno de un solo turno (texto) contra la referencia del escenario."""
    return cos_tokens(modelo, escenario, [le.tokens(texto)], variante)


def cos_ventana(modelo, escenario, textos, variante="con"):
    """Coseno de una ventana de turnos (lista de textos) contra la referencia; invariante al orden de los turnos."""
    return cos_tokens(modelo, escenario, [le.tokens(t) for t in textos], variante)


def identificar(modelo, escenarios, lista_tokens, variante="con"):
    """(par con mayor coseno, {par: coseno}) entre las referencias `escenarios` = {par: Escenario}."""
    cos = {p: cos_tokens(modelo, e, lista_tokens, variante) for p, e in escenarios.items()}
    return max(cos, key=cos.get), cos


def serie_rodante(modelo, escenario, tokens_por_turno, variante="con", k=K_VENTANA):
    """Coseno de la ventana móvil de k turnos que termina en cada turno i >= k-1 (len - k + 1 valores)."""
    pos, excl = _filtro(variante, escenario)
    cuentas = [le.contar_tokens(t, pos, excl) for t in tokens_por_turno]
    ref = modelo.vector_ref(escenario, variante)
    acum, out = Counter(), []
    for i, c in enumerate(cuentas):
        acum.update(c)
        if i >= k:
            acum.subtract(cuentas[i - k])
            acum = +acum
        if i >= k - 1:
            out.append(_coseno(modelo.vector(variante, acum), ref))
    return out


# ---------------------------------------------------------------- enchufe al arnés
def _f_turno(variante):
    """Fábrica de la función de ámbito «turno» del arnés para la variante dada."""
    return lambda texto, ctx: cos_turno(ctx.modelo, ctx.escenario, texto, variante)


def _f_ventana(variante):
    """Fábrica de la función de ámbito «ventana» del arnés para la variante dada."""
    return lambda textos, ctx: cos_ventana(ctx.modelo, ctx.escenario, textos, variante)


def registrar_en_arnes():
    """Registra cr2b_cos_turno[_sn] (turno) y cr2b_cos_ventana8[_sn] (ventana). Idempotente. El
    contexto debe ser un contexto_a4bc.ContextoA4bc (con .escenario y .modelo)."""
    import contexto_a4bc  # noqa: F401
    import instrumentos_texto as it
    defs = [("cr2b_cos_turno", _f_turno("con"), "turno"), ("cr2b_cos_turno_sn", _f_turno("sn"), "turno"),
            ("cr2b_cos_ventana8", _f_ventana("con"), "ventana"), ("cr2b_cos_ventana8_sn", _f_ventana("sn"), "ventana")]
    for nombre, f, ambito in defs:
        if nombre not in it.INSTRUMENTOS:
            it.registrar_instrumento(nombre, f, "num", ambito=ambito)
    return [n for n, _, _ in defs]
