"""
respuesta_accion.py -- CR-2a: ¿la respuesta del DM está anclada en la acción ESPECÍFICA del
jugador en ese turno?

Instrumento DETERMINISTA (sin LLM, sin red, solo lemas de spaCy). Definición operacional en
docs/research/a4bc_diseno_instrumentos.md, sección 2.2; expectativas pre-especificadas en
matriz_a4bc.py (hash en el documento).

  * A = lemas de contenido (NOUN/VERB/ADJ, sin stopwords) de la acción del jugador sin etiquetas
    de tirada; R = lemas de contenido de prosa(dm_output) del MISMO turno.
  * crudo = coeficiente de Ochiai |A ∩ R| / sqrt(|A|·|R|) (normaliza por longitud).
  * Calibración: nulo por permutación restringida = la MISMA R emparejada con acciones de otros
    turnos de la misma campaña (|Δturno| > 2, banda de longitud de A). z = (crudo − media)/max(sd,
    0,01); percentil con rangos medios; p_perm = (1 + #{nulo ≥ obs})/(1 + m) (Phipson & Smyth 2010).
  * Acción degenerada: solo etiqueta de tirada -> no computable; solo diálogo -> se calcula y se
    marca; < 3 lemas (en A o en R) -> «insuficiente» (None).

Límite: similitud LÉXICA; no ve sinónimos, paráfrasis, anáfora ni negación, y hereda los errores
del etiquetador de spaCy (verbos de 2.ª persona).
"""
import hashlib
import math
import random
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

import lemas_es as le   # noqa: E402

RE_TAG = re.compile(r"\{[^}]*\}")
_RE_DIALOGO = re.compile(r'"[^"]*"|“[^”]*”|«[^»]*»|^[ \t]*[—–-][^\n]*', re.M)
MIN_LEMAS = 3
FRAC_BANDA = 0.15
MIN_BANDA = 40
MAX_NULO = 150
RADIO_EXCLUSION = 2
PISO_SD = 0.01


# ---------------------------------------------------------------- la acción del jugador
def texto_accion(x):
    """Texto de la acción sin etiquetas de tirada. `x` = str o player_buffer [{"pc","text"}]."""
    if isinstance(x, (list, tuple)):
        x = "\n".join((e.get("text", "") if isinstance(e, dict) else str(e)) for e in x)
    return RE_TAG.sub(" ", x or "").strip()


def clasificar_accion(x):
    """'solo_tag' | 'solo_dialogo' | 'mixta' | 'accion'."""
    t = texto_accion(x)
    if not t:
        return "solo_tag"
    resto = _RE_DIALOGO.sub(" ", t)
    if not re.search(r"\w", resto):
        return "solo_dialogo"
    return "mixta" if _RE_DIALOGO.search(t) else "accion"


def lemas_accion(x):
    """(lemas, clase) de la acción."""
    clase = clasificar_accion(x)
    if clase == "solo_tag":
        return frozenset(), clase
    return le.lemas(texto_accion(x)), clase


def ochiai(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / math.sqrt(len(a) * len(b))


# ---------------------------------------------------------------- pool de acciones de una campaña
class PoolAcciones:
    """Lemas y clase de la acción de cada turno de UNA campaña (el reservorio del nulo)."""

    def __init__(self, campana, lemas=None, clases=None):
        self.campana = str(campana)
        self.lemas = dict(lemas or {})
        self.clases = dict(clases or {})
        self.turnos = sorted(t for t, ls in self.lemas.items() if self._valida(t))

    def _valida(self, t):
        return self.clases.get(t) != "solo_tag" and len(self.lemas.get(t, ())) >= MIN_LEMAS

    @classmethod
    def desde_textos(cls, campana, acciones):
        """acciones = {turno: texto (str o player_buffer)}. Lematiza en lote."""
        turnos = sorted(acciones)
        clases = {t: clasificar_accion(acciones[t]) for t in turnos}
        toks = le.tokens_lote([texto_accion(acciones[t]) if clases[t] != "solo_tag" else "" for t in turnos])
        lemas = {t: le.filtrar(tk) for t, tk in zip(turnos, toks)}
        return cls(campana, lemas, clases)

    def agregar_turno(self, turno, accion):
        ls, clase = lemas_accion(accion)
        self.lemas[turno], self.clases[turno] = ls, clase
        self.turnos = sorted(t for t in self.lemas if self._valida(t))


def candidatos_nulo(pool, turno, n_lemas):
    """Turnos cuya acción se empareja con la respuesta del `turno` para formar el nulo."""
    cand = [x for x in pool.turnos if x != turno and abs(x - turno) > RADIO_EXCLUSION]
    tol = max(1, round(FRAC_BANDA * n_lemas))
    banda = [x for x in cand if abs(len(pool.lemas[x]) - n_lemas) <= tol]
    if len(banda) < MIN_BANDA:
        banda = sorted(cand, key=lambda x: (abs(len(pool.lemas[x]) - n_lemas), x))[:MIN_BANDA]
    if len(banda) > MAX_NULO:
        semilla = int(hashlib.sha1(f"{pool.campana}|{turno}".encode("utf-8")).hexdigest()[:8], 16)
        banda = random.Random(semilla).sample(banda, MAX_NULO)
    return sorted(banda)


# ---------------------------------------------------------------- medición
def _vacio(clase, nA=0, nR=0):
    return {"clase": clase, "crudo": None, "z": None, "percentil": None, "p_perm": None,
            "n_nulo": 0, "nA": nA, "nR": nR}


def medir(pool, turno, respuesta, accion=None, tokens_respuesta=None):
    """Puntaje de la `respuesta` (texto DM, con o sin formato G1) frente a la acción del `turno`.
    `accion` (str o player_buffer) sobrescribe la del pool. Devuelve un dict; z=None si no es
    computable. `tokens_respuesta` (tuplas (clave, POS) ya lematizadas) evita relematizar."""
    if accion is None:
        A, clase = pool.lemas.get(turno, frozenset()), pool.clases.get(turno, "solo_tag")
    else:
        A, clase = lemas_accion(accion)
    R = le.filtrar(tokens_respuesta) if tokens_respuesta is not None else le.lemas(respuesta)
    if clase == "solo_tag":
        return _vacio("solo_tag", 0, len(R))
    if len(A) < MIN_LEMAS or len(R) < MIN_LEMAS:
        return _vacio("insuficiente", len(A), len(R))
    crudo = ochiai(A, R)
    nulo = [ochiai(pool.lemas[x], R) for x in candidatos_nulo(pool, turno, len(A))]
    if not nulo:
        return {**_vacio("sin_nulo", len(A), len(R)), "crudo": crudo}
    m = len(nulo)
    media = sum(nulo) / m
    sd = math.sqrt(sum((v - media) ** 2 for v in nulo) / m)
    menores = sum(1 for v in nulo if v < crudo)
    iguales = sum(1 for v in nulo if v == crudo)
    return {"clase": clase, "crudo": crudo, "z": (crudo - media) / max(sd, PISO_SD),
            "percentil": (menores + 0.5 * iguales) / m,
            "p_perm": (1 + sum(1 for v in nulo if v >= crudo)) / (1 + m),
            "n_nulo": m, "nA": len(A), "nR": len(R)}


def medir_ventana(pool, inicio, textos):
    """Media de los z (no nulos) de las respuestas `textos` emparejadas con las acciones de los
    turnos inicio, inicio+1, ...; None si ninguno es computable."""
    zs = [r["z"] for j, t in enumerate(textos) for r in [medir(pool, inicio + j, t)] if r["z"] is not None]
    return sum(zs) / len(zs) if zs else None


# ---------------------------------------------------------------- enchufe al arnés
def _f_z(texto, ctx):
    return medir(ctx.pool, ctx.turno, texto)["z"]


def _f_crudo(texto, ctx):
    return medir(ctx.pool, ctx.turno, texto)["crudo"]


def _f_ventana(textos, ctx):
    return medir_ventana(ctx.pool, ctx.turno, textos)


def registrar_en_arnes():
    """Registra cr2a_z, cr2a_crudo (turno) y cr2a_z_ventana8 (ventana) en el arnés de sensibilidad
    (instrumentos_texto.registrar_instrumento). Idempotente. El contexto debe ser un
    contexto_a4bc.ContextoA4bc (con .pool y .turno)."""
    import contexto_a4bc  # noqa: F401  (asegura la ruta del arnés)
    import instrumentos_texto as it
    defs = [("cr2a_z", _f_z, "turno"), ("cr2a_crudo", _f_crudo, "turno"),
            ("cr2a_z_ventana8", _f_ventana, "ventana")]
    for nombre, f, ambito in defs:
        if nombre not in it.INSTRUMENTOS:
            it.registrar_instrumento(nombre, f, "num", ambito=ambito)
    return [n for n, _, _ in defs]
