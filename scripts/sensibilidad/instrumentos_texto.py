"""
Envoltorios de los instrumentos deterministas sobre TEXTO ARBITRARIO.

Ningún instrumento toca la base de datos: todo lo que el original leía de
Postgres (nombre del PJ, entidades, estado de PNJ, HP, tiradas, escena
anterior) llega en un `Contexto` explícito. La lógica es la del motor:

  * Se IMPORTAN (sin efectos secundarios más allá de reconfigurar stdout) las
    funciones puras de orquestador/vertical_slice.py: jaccard_palabras,
    fernandez_huerta, entidades_conocidas, entidad_grafo_densidad (idénticas
    en vertical_slice_g1.py: lo comprueba test_sensibilidad.py) y las post-hoc
    de orquestador/reporte_validacion.py: grammaticality_lt,
    grafo_lema_densidad, entity_coreference_rate, coherencia_entidad_C,
    consistencia_atributos_V, detector_bucles, pnj_inactivo_refinado.
  * Las comprobaciones del paso «VERIFICACIÓN» (paso 5 de vertical_slice.py,
    paso 9 de vertical_slice_g1.py) viven dentro de `_cuerpo_principal` y no
    son importables: se REPLICAN aquí citando las líneas de vertical_slice.py.
    `PATRONES_REPLICADOS` lista los literales copiados; un test comprueba que
    siguen apareciendo en los dos scripts (guarda de deriva).

Enchufe para detectores nuevos (p. ej. los de 2.ª persona):

    registrar_instrumento("nombre", funcion, "bool" | "num", ambito="turno")

con `funcion(texto, ctx) -> valor` (ambito="turno") o
`funcion(textos, ctx) -> valor` (ambito="ventana").
"""
import dataclasses
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (RAIZ / "orquestador", RAIZ / "jugador", RAIZ / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import reporte_validacion as _rv   # noqa: E402
import vertical_slice as _vs       # noqa: E402


# ---------------------------------------------------------------- contexto
@dataclass
class Contexto:
    """Todo lo que el motor leía de la base para verificar UN turno."""
    pj_nombre: str
    entidades: list                       # [{"tipo","nombre"}] como Campaña.entidades()
    estados_pnj: dict                     # nombre de PNJ -> status (alive/dead/missing/captured)
    hp_current: Optional[int] = None
    hp_max: Optional[int] = None
    tiradas: list = field(default_factory=list)   # dicts de dados.tirar()
    escena_anterior: str = ""             # dm_output del turno anterior
    nombres_pj: Optional[set] = None      # nombres_pj_conocidos (todos los PJ)
    previas: frozenset = frozenset()      # entidades ya mencionadas en turnos previos
    brazo: str = "G2"                     # "G1" | "G2"
    _cache: dict = field(default_factory=dict, init=False, repr=False, compare=False)

    @property
    def nombres_pj_conocidos(self):
        return self.nombres_pj if self.nombres_pj is not None else {self.pj_nombre}

    @property
    def conocidos(self):
        """vertical_slice.entidades_conocidas (L482): vocabulario de la campaña."""
        if "conocidos" not in self._cache:
            self._cache["conocidos"] = _vs.entidades_conocidas(self.entidades, self.pj_nombre)
        return self._cache["conocidos"]

    def copia(self, **cambios):
        return dataclasses.replace(self, **cambios)


# ---------------------------------------------------------------- registro
@dataclass
class Instrumento:
    nombre: str
    funcion: Callable
    tipo: str          # "bool" | "num"
    ambito: str        # "turno" | "ventana"


INSTRUMENTOS: dict = {}


def registrar_instrumento(nombre, funcion, tipo, ambito="turno"):
    if tipo not in ("bool", "num"):
        raise ValueError(f"tipo debe ser 'bool' o 'num', no {tipo!r}")
    if ambito not in ("turno", "ventana"):
        raise ValueError(f"ambito debe ser 'turno' o 'ventana', no {ambito!r}")
    if nombre in INSTRUMENTOS:
        raise ValueError(f"instrumento ya registrado: {nombre}")
    INSTRUMENTOS[nombre] = Instrumento(nombre, funcion, tipo, ambito)


def calcular(texto, ctx, nombres=None):
    """Valores de los instrumentos de ámbito turno sobre `texto`."""
    return {n: i.funcion(texto, ctx) for n, i in INSTRUMENTOS.items()
            if i.ambito == "turno" and (nombres is None or n in nombres)}


def calcular_ventana(textos, ctx, nombres=None):
    """Valores de los instrumentos de ámbito ventana sobre una lista de textos."""
    return {n: i.funcion(textos, ctx) for n, i in INSTRUMENTOS.items()
            if i.ambito == "ventana" and (nombres is None or n in nombres)}


# ------------------------------------------------- literales replicados (guarda de deriva)
# Cada cadena aparece tal cual en vertical_slice.py Y en vertical_slice_g1.py.
PATRONES_REPLICADOS = [
    r"\[[^\]]{20,}\]",                                   # vertical_slice.py L621
    r"tirada de \w+ necesaria|resuelvo la|como DM|",      # L624
    r"seg[úu]n las reglas|no obstante,? al haber",        # L625
    r"logras|consigues|aciertas|lo convences",            # L633
    r"(piensa|siente|decide|comprende)",                  # L641
    r"(ataca|golpea|convence|",                           # L653
    r"esquiva|salta|derriba|desarma)",                    # L654
    r"(muere|cae muerto|fallece|",                        # L680
    r"pierde la vida)",                                   # L681
    r'"Ella", "Él", "Sargento", "Vado", "Ceniza"}',       # L815
    r"""set(".!?¿¡—\n\"'")""",                            # L821
    r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b",                    # L823
]

_RE_META = re.compile(r"\[[^\]]{20,}\]")
_RE_REGLAS = re.compile(r"\b(tirada de \w+ necesaria|resuelvo la|como DM|"
                        r"seg[úu]n las reglas|no obstante,? al haber)\b", re.I)
_RE_EXITO = re.compile(r"\b(logras|consigues|aciertas|lo convences)\b", re.I)
_STOP_MAYUS = {"El", "La", "Los", "Las", "Un", "Una", "Unos", "Unas",
               "Cuando", "Si", "Pero", "Y", "Aunque", "Tras", "Al",
               "Ella", "Él", "Sargento", "Vado", "Ceniza"}
_LIMITES = set(".!?¿¡—\n\"'")


# ---------------------------------------------------- booleanos (paso 5 del motor)
def meta_comentario(texto, ctx):                                   # vertical_slice.py L621
    return bool(_RE_META.search(texto))


def comenta_reglas(texto, ctx):                                    # L624-626
    return bool(_RE_REGLAS.search(texto))


def cr1_veredicto_contradice_narracion(texto, ctx):                # L632-638
    return any(t["pifia"] and _RE_EXITO.search(texto) for t in ctx.tiradas)


def qn2_pj_piensa_narrado(texto, ctx):                             # L641-643
    return bool(re.search(rf"\b{re.escape(ctx.pj_nombre)}\s+(piensa|siente|decide|comprende)",
                          texto, re.I))


def qn2_pj_accion_revisar(texto, ctx):                             # L653-655
    m = re.search(rf"\b{re.escape(ctx.pj_nombre)}\s+(ataca|golpea|convence|"
                  r"esquiva|salta|derriba|desarma)\b", texto, re.I)
    return bool(m and not ctx.tiradas)


def cl2_pnj_inactivo_actua(texto, ctx):                            # L661-673
    for e in ctx.entidades:
        if (e["tipo"] != "npc" or e["nombre"] not in texto
                or e["nombre"] in ctx.nombres_pj_conocidos):
            continue
        estado = ctx.estados_pnj.get(e["nombre"])
        if estado and estado != "alive":
            return True
    return False


def cl2_pc_hp_contradice_narracion(texto, ctx):                    # L677-687
    if ctx.hp_current is None:
        return False
    narra_muerte = re.search(rf"\b{re.escape(ctx.pj_nombre)}\s+(muere|cae muerto|fallece|"
                             r"pierde la vida)\b", texto, re.I)
    return bool(narra_muerte and ctx.hp_current > 0)


def nombres_no_reconocidos(texto, ctx):                            # L813-833
    no_reconocidos = set()
    for m in re.finditer(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b", texto):
        palabra = m.group(0)
        if palabra in ctx.conocidos or palabra in _STOP_MAYUS:
            continue
        prefijo = texto[:m.start()].rstrip()
        if prefijo and prefijo[-1] in _LIMITES:
            continue
        if not prefijo:
            continue
        no_reconocidos.add(palabra)
    return sorted(no_reconocidos)


def cr2_nombres_no_reconocidos(texto, ctx):
    return bool(nombres_no_reconocidos(texto, ctx))


def cr2_n_nombres_no_reconocidos(texto, ctx):
    return len(nombres_no_reconocidos(texto, ctx))


# ---------------------------------------------------- numéricos (L693-702)
def cl2_lugar_jaccard_similarity(texto, ctx):
    return round(_vs.jaccard_palabras(ctx.escena_anterior, texto), 3)


def cr2_entidad_grafo_densidad(texto, ctx):
    return _vs.entidad_grafo_densidad(texto, ctx.conocidos)


def _palabras(texto):
    return re.findall(r"\w+", texto.lower())


def qn1_ttr(texto, ctx):
    p = _palabras(texto)
    return round(len(set(p)) / len(p), 3) if p else None


def qn1_ngram_repeticion(texto, ctx):
    p = _palabras(texto)
    bigramas = list(zip(p, p[1:]))
    return round(1 - len(set(bigramas)) / len(bigramas), 3) if bigramas else None


def qn1_legibilidad_fh(texto, ctx):
    return _vs.fernandez_huerta(texto)


def szigriszt_pazos(texto):
    """Índice de perspicuidad de Szigriszt-Pazos (1993), base de la escala INFLESZ (Barrio-Cantalejo et al., 2008): P = 206.835 - 62.3*(sílabas/palabra) - (palabras/frase).
    Mismas palabras, frases y sílabas que _vs.fernandez_huerta. Solo capa de análisis: NO está en el motor ni en turn_validation."""
    palabras = re.findall(r"[a-záéíóúñü]+", texto.lower())
    frases = [f for f in re.split(r"[.!?]+", texto) if f.strip()]
    if not palabras or not frases:
        return None
    silabas = sum(_vs.contar_silabas_es(p) for p in palabras)
    return round(206.835 - 62.3 * (silabas / len(palabras)) - len(palabras) / len(frases), 2)


def qn1_legibilidad_sz(texto, ctx):
    return szigriszt_pazos(texto)


# Diversidad léxica independiente de la longitud (complementa a qn1_ttr, que se deja igual). Pensadas para texto de bloque o campaña, no de un turno.
def mtld(palabras, umbral=0.72):
    """MTLD bidireccional (McCarthy & Jarvis, 2010): longitud media de los tramos en que el TTR acumulado se mantiene por encima de `umbral`.
    `palabras` ya tokenizado (_palabras). None con menos de 10 palabras; con TTR siempre por encima del umbral (sin ningún factor) devuelve len(palabras)."""
    if len(palabras) < 10:
        return None

    def pase(secuencia):
        factores, tipos, n = 0.0, set(), 0
        for w in secuencia:
            tipos.add(w)
            n += 1
            if len(tipos) / n <= umbral:
                factores += 1
                tipos, n = set(), 0
        if n > 0:
            factores += min((1 - len(tipos) / n) / (1 - umbral), 1.0)     # factor parcial
        return len(secuencia) / factores if factores > 0 else len(secuencia)

    return round((pase(palabras) + pase(palabras[::-1])) / 2, 2)


def mattr(palabras, ventana=50):
    """MATTR (Covington & McFall, 2010): TTR de una ventana móvil de `ventana` palabras, promediado. Conteo incremental: O(n), mismo resultado que rehacer el set por ventana."""
    n = len(palabras)
    if n == 0:
        return None
    if n < ventana:
        return round(len(set(palabras)) / n, 3)
    cuenta = {}
    for w in palabras[:ventana]:
        cuenta[w] = cuenta.get(w, 0) + 1
    tipos, suma = len(cuenta), len(cuenta)
    for i in range(ventana, n):
        sale = palabras[i - ventana]
        cuenta[sale] -= 1
        if cuenta[sale] == 0:
            tipos -= 1
        entra = palabras[i]
        if cuenta.get(entra, 0) == 0:
            tipos += 1
        cuenta[entra] = cuenta.get(entra, 0) + 1
        suma += tipos
    return round(suma / ((n - ventana + 1) * ventana), 3)


# ---------------------------------------------------- post-hoc (reporte_validacion.py)
_LT_CACHE_PATH = AQUI / "_cache" / "lt_cache.json"
_lt_memoria: Optional[dict] = None


def _lt_cargar():
    global _lt_memoria
    if _lt_memoria is None:
        try:
            _lt_memoria = json.loads(_LT_CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _lt_memoria = {}
    return _lt_memoria


def guardar_cache_lt():
    """Vuelca la caché de LanguageTool a disco (es lento: se reutiliza entre corridas)."""
    if _lt_memoria is None:
        return
    _LT_CACHE_PATH.parent.mkdir(exist_ok=True)
    _LT_CACHE_PATH.write_text(json.dumps(_lt_memoria), encoding="utf-8")


def grammaticality_lt(texto, ctx):
    """Roemmele & Gordon vía LanguageTool (reporte_validacion.grammaticality_lt), con caché."""
    cache = _lt_cargar()
    k = hashlib.sha1(texto.encode("utf-8")).hexdigest()
    if k not in cache:
        tool = _rv._herramienta_lt()
        if tool is None:
            raise RuntimeError("LanguageTool no disponible")
        cache[k] = _rv.grammaticality_lt(texto, tool)
    return cache[k]


_LEMAS: dict = {}


def _lemas_conocidos(ctx, nlp):
    """reporte_validacion.reporte_grafo_lema L930-934."""
    clave = tuple(sorted(e["nombre"] for e in ctx.entidades))
    if clave not in _LEMAS:
        lemas = set()
        for e in ctx.entidades:
            for tok in nlp(e["nombre"]):
                if len(tok.lemma_) >= 3:
                    lemas.add(tok.lemma_.lower())
        _LEMAS[clave] = lemas
    return _LEMAS[clave]


def grafo_lema_densidad(texto, ctx):
    nlp = _rv._modelo_grafo()
    if nlp is None:
        raise RuntimeError("spaCy es_core_news_sm no disponible")
    return _rv.grafo_lema_densidad(texto, _lemas_conocidos(ctx, nlp), nlp)


def entidades_mencionadas(texto, entidades):
    """reporte_validacion.entity_coreference_rate L755-764: conjunto de entidades
    de la campaña mencionadas en `texto` (nombre completo o palabra de 3+ letras,
    por subcadena)."""
    nombres = {e["nombre"] for e in entidades}
    mencionadas = set()
    for nombre in nombres:
        tokens = [nombre] + [p for p in nombre.split() if len(p) >= 3]
        if any(tok and tok in texto for tok in tokens):
            mencionadas.add(nombre)
    return mencionadas


def entity_coreference_rate(texto, ctx):
    """Roemmele & Gordon, por turno (L765-772): fracción de las entidades
    mencionadas que ya estaban en `ctx.previas`. None si no menciona ninguna."""
    m = entidades_mencionadas(texto, ctx.entidades)
    if not m:
        return None
    return sum(1 for n in m if n in ctx.previas) / len(m)


def cl2_pnj_inactivo_refinado(texto, ctx):
    """reporte_validacion.pnj_inactivo_refinado (sección 9): ¿algún PNJ inactivo
    aparece como sujeto sintáctico (nsubj) de su oración? Requiere que el
    detector crudo ya dispare (así se usa en el reporte)."""
    if not cl2_pnj_inactivo_actua(texto, ctx):
        return False
    inactivos = [e for e in ctx.entidades
                 if e["tipo"] == "npc" and e["nombre"] not in ctx.nombres_pj_conocidos
                 and ctx.estados_pnj.get(e["nombre"], "alive") != "alive"]
    r = _rv.pnj_inactivo_refinado([{"turn_id": 0, "cl2_pnj_inactivo_actua": True}],
                                  {0: texto}, inactivos)
    if r is None:
        raise RuntimeError("spaCy es_core_news_sm no disponible")
    return len(r["actuando"]) > 0


# ---------------------------------------------------- ventanas
def _turnos(textos):
    return [{"turn_id": i, "dm_output": t} for i, t in enumerate(textos)]


def ventana_jaccard_medio(textos, ctx):
    """Media de cl2_lugar_jaccard_similarity de cada turno contra el anterior de
    la ventana (el primero contra ctx.escena_anterior)."""
    previos = [ctx.escena_anterior] + list(textos[:-1])
    vals = [_vs.jaccard_palabras(a, b) for a, b in zip(previos, textos)]
    return sum(vals) / len(vals) if vals else None


def ventana_entity_coreference_medio(textos, ctx):
    return _rv.entity_coreference_rate(_turnos(textos), ctx.entidades)["promedio"]


def ventana_coherencia_C(textos, ctx):
    return _rv.coherencia_entidad_C(_turnos(textos), ctx.entidades)[0]


def ventana_consistencia_V(textos, ctx):
    return _rv.consistencia_atributos_V(_turnos(textos), ctx.entidades)[0]


def _bucles(textos, ctx):
    ubic = [e for e in ctx.entidades if e["tipo"] == "location"]
    return _rv.detector_bucles(_turnos(textos), ubic)


def ventana_bucles_visitas(textos, ctx):
    return _bucles(textos, ctx)["num_visitas"]


def ventana_bucles_ciclos(textos, ctx):
    return len(_bucles(textos, ctx)["ciclos"])


def ventana_mtld(textos, ctx):
    return mtld(_palabras(" ".join(textos)))


def ventana_mattr(textos, ctx):
    return mattr(_palabras(" ".join(textos)))


# ---------------------------------------------------- catálogo por defecto
for _n, _f, _t in [
    ("meta_comentario", meta_comentario, "bool"),
    ("comenta_reglas", comenta_reglas, "bool"),
    ("cr1_veredicto_contradice_narracion", cr1_veredicto_contradice_narracion, "bool"),
    ("qn2_pj_piensa_narrado", qn2_pj_piensa_narrado, "bool"),
    ("qn2_pj_accion_revisar", qn2_pj_accion_revisar, "bool"),
    ("cl2_pnj_inactivo_actua", cl2_pnj_inactivo_actua, "bool"),
    ("cl2_pc_hp_contradice_narracion", cl2_pc_hp_contradice_narracion, "bool"),
    ("cr2_nombres_no_reconocidos", cr2_nombres_no_reconocidos, "bool"),
    ("cl2_pnj_inactivo_refinado", cl2_pnj_inactivo_refinado, "bool"),
    ("cl2_lugar_jaccard_similarity", cl2_lugar_jaccard_similarity, "num"),
    ("cr2_entidad_grafo_densidad", cr2_entidad_grafo_densidad, "num"),
    ("qn1_ttr", qn1_ttr, "num"),
    ("qn1_ngram_repeticion", qn1_ngram_repeticion, "num"),
    ("qn1_legibilidad_fh", qn1_legibilidad_fh, "num"),
    ("qn1_legibilidad_sz", qn1_legibilidad_sz, "num"),
    ("cr2_n_nombres_no_reconocidos", cr2_n_nombres_no_reconocidos, "num"),
    ("grammaticality_lt", grammaticality_lt, "num"),
    ("grafo_lema_densidad", grafo_lema_densidad, "num"),
    ("entity_coreference_rate", entity_coreference_rate, "num"),
]:
    registrar_instrumento(_n, _f, _t)

for _n, _f in [
    ("ventana_jaccard_medio", ventana_jaccard_medio),
    ("ventana_entity_coreference_medio", ventana_entity_coreference_medio),
    ("ventana_coherencia_C", ventana_coherencia_C),
    ("ventana_consistencia_V", ventana_consistencia_V),
    ("ventana_bucles_visitas", ventana_bucles_visitas),
    ("ventana_bucles_ciclos", ventana_bucles_ciclos),
    ("ventana_mtld", ventana_mtld),
    ("ventana_mattr", ventana_mattr),
]:
    registrar_instrumento(_n, _f, "num", ambito="ventana")

# No aplica sobre texto: depende de los deltas que propone el extractor, no de la narración.
NO_APLICABLES_TEXTO = {"cl1_campo_inmutable_alterado"}
