"""
Perturbaciones NUEVAS de A4b/c (no se edita scripts/sensibilidad/perturbaciones.py; se reutilizan
sus funciones para P5, P6, P8, P9 y P11):

  X1_misma_campana_lejana   respuesta de otro turno de la MISMA campaña a >= 50 turnos
  X2_misma_campana_cercana  ídem a 3-10 turnos (misma escena)
  C1_reorden_oraciones      reordena las oraciones de la narración (mismo contenido léxico)
  C2_minusculas             toda la narración en minúsculas
  C3_sin_tildes             quita las tildes (conserva la ñ)
  S1_sinonimos              sustituye palabras frecuentes por sinónimos (diccionario mínimo a mano)
  W1_ventana_otro_par       (ventana) sustituye 8 turnos por 8 turnos consecutivos de otro par

Firma como el arnés: aplicar(pid, texto, ctx, rng, donante=None) -> Resultado(texto, ctx, info).
Como en el arnés, las inserciones y transformaciones afectan SOLO a la zona «narrativa» (G1) y dejan
intactas las demás secciones. Solo cambian el texto de la respuesta: la acción y el escenario
quedan fijos.
"""
import random   # noqa: F401  (los rng llegan de fuera; se importa para los tipos en pruebas)
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_SENS = AQUI.parent / "sensibilidad"
for _p in (AQUI, _SENS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import perturbaciones as pt   # noqa: E402  (scripts/sensibilidad/perturbaciones.py)

# ---------------------------------------------------------------- diccionario de S1 (a mano)
SINONIMOS = {
    # sustantivos
    "paciente": "enfermo", "pacientes": "enfermos", "enfermo": "paciente", "enfermos": "pacientes",
    "miedo": "temor", "temor": "miedo", "camino": "sendero", "caminos": "senderos",
    "ruido": "sonido", "ruidos": "sonidos", "casa": "vivienda", "casas": "viviendas",
    "rostro": "semblante", "rostros": "semblantes", "herida": "lesión", "heridas": "lesiones",
    "tesoro": "riqueza", "habitación": "estancia", "habitaciones": "estancias", "sala": "salón",
    "silencio": "quietud", "oscuridad": "tinieblas", "aldea": "poblado", "guardia": "vigilante",
    "guardias": "vigilantes", "espada": "acero", "puerta": "portón", "puertas": "portones",
    # adjetivos
    "débil": "frágil", "débiles": "frágiles", "oscuro": "sombrío", "oscura": "sombría",
    "oscuros": "sombríos", "oscuras": "sombrías", "grande": "enorme", "grandes": "enormes",
    "pequeño": "diminuto", "pequeña": "diminuta", "antiguo": "vetusto", "antigua": "vetusta",
    "frío": "gélido", "fría": "gélida", "fríos": "gélidos", "frías": "gélidas",
    # verbos (formas frecuentes: 3.ª, 2.ª y 1.ª singular, gerundio)
    "mira": "observa", "miras": "observas", "miro": "observo", "mirando": "observando",
    "busca": "rastrea", "buscas": "rastreas", "busco": "rastreo", "buscando": "rastreando",
    "examina": "inspecciona", "examinas": "inspeccionas", "examino": "inspecciono",
    "examinando": "inspeccionando", "responde": "contesta", "respondes": "contestas",
    "susurra": "murmura", "susurras": "murmuras", "sigue": "prosigue", "sigues": "prosigues",
    "empieza": "comienza", "empiezas": "comienzas", "encuentra": "halla", "encuentras": "hallas",
    "entiende": "comprende", "entiendes": "comprendes", "ayuda": "auxilia", "ayudas": "auxilias",
}
_RE_SIN = re.compile(r"\b(" + "|".join(sorted(map(re.escape, SINONIMOS), key=len, reverse=True)) + r")\b",
                     re.I | re.U)
_TILDES = str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU")
_RE_ORACIONES = re.compile(r"(?<=[.!?])(\s+)")


# ---------------------------------------------------------------- donantes de la misma campaña
def elegir_donante_misma_campana(textos, turno, rng, dmin, dmax):
    """Turno donante de la misma campaña con dmin <= |Δturno| <= dmax (dmax None = sin tope) y texto no
    vacío. `textos` = {turno: texto DM}. Determinista dado `rng`."""
    cand = sorted(x for x, t in textos.items()
                  if x != turno and t and t.strip() and abs(x - turno) >= dmin and (dmax is None or abs(x - turno) <= dmax))
    if not cand:
        raise ValueError(f"sin donantes a distancia {dmin}-{dmax} del turno {turno}")
    return rng.choice(cand)


# ---------------------------------------------------------------- perturbaciones de turno
def _donante(texto, ctx, rng, donante=None):
    """X1/X2: sustituye la respuesta por la narración de otro turno de la misma campaña (`donante`); exige donante."""
    if donante is None:
        raise ValueError("requiere `donante` (narración de otro turno de la misma campaña)")
    return pt.Resultado(donante, ctx.copia(), {"donante_len": len(donante)})


def _c1(texto, ctx, rng, donante=None):
    """C1: permuta las oraciones de la zona narrativa (mismo contenido léxico); reintenta hasta 100 veces para que el orden cambie."""
    partes = pt._partir_zona(texto)
    piezas = _RE_ORACIONES.split(partes[2])          # [oración, sep, oración, ...]
    oraciones = piezas[0::2]
    perm = list(range(len(oraciones)))
    if len(set(oraciones)) >= 2:
        for _ in range(100):
            rng.shuffle(perm)
            if [oraciones[i] for i in perm] != oraciones:
                break
    for k, i in enumerate(perm):
        piezas[2 * k] = oraciones[i]
    return pt.Resultado(pt._rearmar(partes, "".join(piezas)), ctx.copia(), {"perm": perm})


def _c2(texto, ctx, rng, donante=None):
    """C2: pasa a minúsculas la zona narrativa."""
    partes = pt._partir_zona(texto)
    return pt.Resultado(pt._rearmar(partes, partes[2].lower()), ctx.copia(), {})


def _c3(texto, ctx, rng, donante=None):
    """C3: quita las tildes de la zona narrativa (conserva la ñ)."""
    partes = pt._partir_zona(texto)
    return pt.Resultado(pt._rearmar(partes, partes[2].translate(_TILDES)), ctx.copia(), {})


def _s1(texto, ctx, rng, donante=None):
    """S1: sustituye palabras frecuentes por sinónimos del diccionario mínimo y cuenta las sustituciones (límite léxico, solo descriptivo)."""
    partes = pt._partir_zona(texto)
    n = [0]

    def cambiar(m):
        """Reemplaza una coincidencia por su sinónimo conservando la mayúscula inicial y cuenta la sustitución."""
        n[0] += 1
        nuevo = SINONIMOS[m.group(0).lower()]
        return nuevo.capitalize() if m.group(0)[0].isupper() else nuevo

    core = _RE_SIN.sub(cambiar, partes[2])
    return pt.Resultado(pt._rearmar(partes, core), ctx.copia(), {"n_sustituciones": n[0]})


CATALOGO_A4BC = {
    "X1_misma_campana_lejana": _donante,
    "X2_misma_campana_cercana": _donante,
    "C1_reorden_oraciones": _c1,
    "C2_minusculas": _c2,
    "C3_sin_tildes": _c3,
    "S1_sinonimos": _s1,
}


def aplicar(pid, texto, ctx, rng, donante=None):
    """Despachador: perturbaciones nuevas (aquí) o del arnés (P5, P6, P8, P11a, P11b...)."""
    if pid in CATALOGO_A4BC:
        return CATALOGO_A4BC[pid](texto, ctx, rng, donante)
    return pt.perturbar(pid, texto, ctx, rng, donante=donante)


def elegible(pid, texto, ctx):
    """True si la perturbación es aplicable al turno; C1 exige >= 3 oraciones y las demás nuevas siempre aplican."""
    if pid == "C1_reorden_oraciones":
        return len(_RE_ORACIONES.split(pt._partir_zona(texto)[2])[0::2]) >= 3
    if pid in CATALOGO_A4BC:
        return True
    return pt.elegible(pid, texto, ctx)


# ---------------------------------------------------------------- perturbación de ventana
def perturbar_ventana_w1(textos, donantes):
    """W1_ventana_otro_par: las respuestas de la ventana pasan a ser `donantes` (mismo tamaño)."""
    if len(donantes) != len(textos):
        raise ValueError("W1 exige tantos donantes como turnos de la ventana")
    return pt.ResultadoVentana(list(donantes), {"origen": "otro par"})
