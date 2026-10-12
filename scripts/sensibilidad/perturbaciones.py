"""
Catálogo de perturbaciones deterministas (con semilla) para el arnés de
sensibilidad, y la tabla ESPERADO de direcciones PRE-ESPECIFICADAS.

ESPERADO se escribió ANTES de correr el arnés sobre datos reales y NO se
ajusta después de ver resultados (ver docs/reportes/sensibilidad_baseline.md,
que imprime el hash de la tabla original). Criterio: la dirección esperada es
la que mostraría un instrumento VÁLIDO para el constructo que dice medir:

  * defecto real inyectado que el instrumento dice detectar -> "se_dispara"
    (booleanos) / "sube" / "baja" (numéricos);
  * cambio que no toca el constructo (control negativo, o invariante exacto
    por construcción: p. ej. barajar palabras no cambia el TTR) -> "sin_cambio".
  Los pares (perturbación, instrumento) que no aparecen aquí se calculan y se
  muestran como descriptivos, sin veredicto.

Perturbaciones de turno: perturbar(pid, texto, ctx, rng, donante=None)
   -> Resultado(texto, ctx, info)   (nunca muta texto ni ctx)
De ventana (P9):   perturbar_ventana(pid, textos, rng) -> ResultadoVentana

Los textos de G1 llevan etiquetas de formato («narrativa/mecanica/presion»):
las inserciones se hacen SIEMPRE dentro de la zona «narrativa» y dejan las
demás secciones intactas.
"""
import copy
import hashlib
import json
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import instrumentos_texto as it   # noqa: E402

from validacion_generar import ETIQ, prosa   # noqa: E402  (scripts/validacion_generar.py)


# ---------------------------------------------------------------- resultados
@dataclass
class Resultado:
    """Resultado de una perturbación de turno: texto nuevo, contexto (copia, posiblemente manipulado) e info de lo inyectado."""
    texto: str
    ctx: object
    info: dict = field(default_factory=dict)


@dataclass
class ResultadoVentana:
    """Resultado de una perturbación de ventana: textos reordenados e info (permutación aplicada)."""
    textos: list
    info: dict = field(default_factory=dict)


# ---------------------------------------------------------------- utilidades de texto
def _zona_narrativa(texto):
    """(ini, fin) de la zona de narración: todo el texto en G2; el primer
    bloque «narrativa» (sin la etiqueta) en G1."""
    ms = list(ETIQ.finditer(texto))
    if not ms:
        return 0, len(texto)
    for i, m in enumerate(ms):
        if m.group(1) == "narrativa":
            return m.end(), (ms[i + 1].start() if i + 1 < len(ms) else len(texto))
    return 0, len(texto)


def _partir_zona(texto):
    """-> (prefijo, lead, core, trail, sufijo) con texto == prefijo+lead+core+trail+sufijo."""
    ini, fin = _zona_narrativa(texto)
    zona = texto[ini:fin]
    core = zona.strip()
    lead = zona[:len(zona) - len(zona.lstrip())]
    trail = zona[len(zona.rstrip()):] if core else ""
    return texto[:ini], lead, core, trail, texto[fin:]


def _rearmar(partes, core):
    """Reconstruye el texto con un nuevo `core` de la zona narrativa, conservando prefijo, espacios y sufijo."""
    prefijo, lead, _, trail, sufijo = partes
    return prefijo + lead + core + trail + sufijo


def _insertar_al_inicio_de_parrafo(texto, oracion, rng):
    """Inserta `oracion + ' '` al inicio de un párrafo elegido al azar de la zona
    narrativa (así la oración añadida queda tras un salto de línea y nunca crea
    artefactos de capitalización con el detector de nombres). Devuelve
    (texto_nuevo, fragmento_insertado)."""
    partes = _partir_zona(texto)
    parrafos = partes[2].split("\n\n")
    i = rng.randrange(len(parrafos))
    fragmento = oracion + " "
    parrafos[i] = fragmento + parrafos[i]
    return _rearmar(partes, "\n\n".join(parrafos)), fragmento


# ---------------------------------------------------------------- plantillas
CATEGORIAS = ("decision", "pensamiento", "emocion", "habla", "accion")

PLANTILLAS_2P = {   # usurpación en 2.ª persona: el DM narra por el jugador (sin nombre)
    "decision": ["Decides que lo mejor es ceder y entregarles lo que piden sin discutir.",
                 "Resuelves quedarte donde estás y esperar a que el otro dé el primer paso.",
                 "Eliges callar y seguirlos hasta el fondo del pasillo.",
                 "Optas por no volver a preguntar y guardas la duda para más tarde."],
    "pensamiento": ["Piensas que todo esto es una trampa y que nadie te dirá la verdad.",
                    "Comprendes de golpe que has cometido un error irreparable.",
                    "Crees que todos aquí saben más de lo que aparentan.",
                    "Te dices que no puedes fiarte de nadie en este lugar."],
    "emocion": ["Sientes un miedo helado que te aprieta el pecho.",
                "Te invade una rabia sorda que apenas puedes contener.",
                "Te embarga una calma extraña, casi de resignación.",
                "Notas cómo la vergüenza te sube por el cuello."],
    "habla": ["Con voz temblorosa dices que aceptas el trato.",
              "Al final respondes en un susurro que no piensas irte todavía.",
              "Entonces murmuras una disculpa que nadie parece escuchar.",
              "Sin mirar a nadie susurras el nombre de tu madre.",
              "De pronto gritas que ya has tenido suficiente."],
    "accion": ["Sacas la daga y golpeas al guardia en el costado sin previo aviso.",
               "Saltas sobre la mesa y derribas al primero que se acerca.",
               "Golpeas la puerta con el hombro hasta que cede.",
               "Desarmas al guardia de un tirón y lo empujas contra la pared."],
}

PLANTILLAS_3P = {   # usurpación en 3.ª persona con el nombre del PJ ({n})
    "decision": ["{n} decide que lo mejor es ceder y entregarles lo que piden sin discutir.",
                 "{n} decide quedarse donde está y esperar a que el otro dé el primer paso.",
                 "{n} decide callar y seguirlos hasta el fondo del pasillo."],
    "pensamiento": ["{n} piensa que todo esto es una trampa y que nadie le dirá la verdad.",
                    "{n} comprende de golpe que ha cometido un error irreparable."],
    "emocion": ["{n} siente un miedo helado que le aprieta el pecho.",
                "{n} siente una rabia sorda que apenas puede contener."],
    "habla": ["{n} dice con voz temblorosa que acepta el trato.",
              "{n} responde en un susurro que no piensa irse todavía."],
    "accion": ["{n} ataca al guardia sin previo aviso.",
               "{n} golpea la puerta con el hombro hasta que cede.",
               "{n} salta sobre la mesa y derriba al primero que se acerca."],
}

PNJ_ACTUA = ["{n} desenvaina la espada y avanza hacia ti con paso firme.",
             "{n} cruza la sala a grandes zancadas y te corta el paso.",
             "{n} recoge las llaves del suelo y las guarda en su cinturón."]
PNJ_HABLA = ["{n} dice con voz grave: «no pienso repetirlo dos veces».",
             "{n} responde sin mirarte: «eso ya no importa».",
             "{n} susurra: «todavía estás a tiempo de marcharte»."]

MUERTE_2P = ["Mueres allí mismo, desangrado en el suelo, sin poder decir nada.",
             "Caes muerto en medio de la sala.",
             "Pierdes la vida entre los escombros.",
             "Falleces antes de que nadie pueda ayudarte."]
MUERTE_3P = ["{n} muere allí mismo, desangrado en el suelo.",
             "{n} cae muerto en medio de la sala.",
             "{n} fallece antes de que nadie pueda ayudarle.",
             "{n} pierde la vida entre los escombros."]

EXITO = ["Logras abrir la puerta al primer intento, sin el menor ruido.",
         "Consigues que el guardia baje la guardia y te deje pasar.",
         "Aciertas de lleno y el golpe se lleva por delante la lámpara.",
         "Lo convences sin esfuerzo de que retroceda un paso."]
HABILIDADES = ["Percepción", "Sigilo", "Persuasión", "Atletismo", "Engaño"]

_ONSET = ["Zor", "Vel", "Quin", "Brax", "Mor", "Tal", "Dru", "Fen", "Kes", "Ulm", "Yor", "Nax"]
_MID = ["an", "ev", "or", "ul", "ith", "ar"]
_END = ["thek", "mora", "dris", "vell", "gard", "onte", "ulf"]
FRASES_NOMBRES = ["Al fondo alguien murmura el nombre de {a} y luego el de {b}.",
                  "Se dice en la calle que {a} y {b} lo saben todo."]

PALABRAS_OTRO_ALFABETO = ["мир", "огонь", "тень", "ветер", "龍", "影", "炎", "風",
                          "불꽃", "그림자", "ひかり", "かげ"]   # cirílico, CJK, hangul, kana (todos en SUCIO)



# ---------------------------------------------------------------- perturbaciones de turno
def _nombre_pj(ctx):
    """Nombre del PJ del contexto, que usan las plantillas en 3.ª persona."""
    return ctx.pj_nombre


def _p_usurpacion(plantillas, con_nombre, sin_tirada=False):
    """Fábrica de la perturbación de usurpación del PJ (P1/P2): inserta una plantilla de la categoría `cat`.

    Args:
        plantillas: PLANTILLAS_2P (sin nombre) o PLANTILLAS_3P (con el nombre del PJ).
        con_nombre: formatea la plantilla con el nombre del PJ.
        sin_tirada: simula un turno sin tirada del sistema vaciando `ctx.tiradas` (variantes añadidas tras el humo)."""
    def f(texto, ctx, rng, donante=None, *, cat):
        """Perturbación de usurpación: elige una plantilla de `cat` y la inserta al inicio de un párrafo."""
        p = rng.choice(plantillas[cat])
        oracion = p.format(n=_nombre_pj(ctx)) if con_nombre else p
        nuevo, frag = _insertar_al_inicio_de_parrafo(texto, oracion, rng)
        info = {"insertado": frag, "categoria": cat}
        if sin_tirada:      # simula un turno sin tirada del sistema (ver P1_accion_sin_tirada)
            info["tiradas_retiradas"] = len(ctx.tiradas)
            return Resultado(nuevo, ctx.copia(tiradas=[]), info)
        return Resultado(nuevo, ctx.copia(), info)
    return f


def _candidatos_pnj(ctx):
    """Nombres de los PNJ de la campaña que no son PJ, ordenados."""
    return sorted(e["nombre"] for e in ctx.entidades
                  if e["tipo"] == "npc" and e["nombre"] not in ctx.nombres_pj_conocidos)


def _p3(texto, ctx, rng, donante=None, *, estado, modo):
    """P3: inserta un PNJ que actúa o habla y fija su estado (dead/missing) en el contexto.

    Prefiere PNJ no mencionados ya en el texto; el contexto se manipula porque en los datos reales casi no hay PNJ muertos activos."""
    nombres = _candidatos_pnj(ctx)
    nuevos = [n for n in nombres if n not in texto] or nombres
    n = rng.choice(nuevos)
    plantilla = rng.choice(PNJ_ACTUA if modo == "actua" else PNJ_HABLA)
    nuevo, frag = _insertar_al_inicio_de_parrafo(texto, plantilla.format(n=n), rng)
    estados = dict(ctx.estados_pnj)
    estados[n] = estado
    return Resultado(nuevo, ctx.copia(estados_pnj=estados),
                     {"insertado": frag, "pnj": n, "estado": estado, "modo": modo})


def _p4(texto, ctx, rng, donante=None, *, persona):
    """P4: inserta la muerte del PJ narrada en 2.ª o 3.ª persona; el HP del contexto sigue siendo > 0 (contradicción buscada)."""
    if persona == "2p":
        oracion = rng.choice(MUERTE_2P)
    else:
        oracion = rng.choice(MUERTE_3P).format(n=_nombre_pj(ctx))
    nuevo, frag = _insertar_al_inicio_de_parrafo(texto, oracion, rng)
    return Resultado(nuevo, ctx.copia(), {"insertado": frag, "persona": persona})


def _nombre_inventado(rng):
    """Nombre inventado por composición de sílabas, improbable como vocabulario de la campaña."""
    return rng.choice(_ONSET) + rng.choice(_MID) + rng.choice(_END)


def _p5(texto, ctx, rng, donante=None):
    """P5: inserta dos nombres propios inventados que no son conocidos, ni excepciones, ni aparecen ya en el texto."""
    nombres = []
    while len(nombres) < 2:
        n = _nombre_inventado(rng)
        if (n not in nombres and n not in ctx.conocidos and n not in it._STOP_MAYUS
                and n not in texto):
            nombres.append(n)
    oracion = rng.choice(FRASES_NOMBRES).format(a=nombres[0], b=nombres[1])
    nuevo, frag = _insertar_al_inicio_de_parrafo(texto, oracion, rng)
    return Resultado(nuevo, ctx.copia(), {"insertado": frag, "nombres": nombres})


_RE_SLOT = re.compile(r"^(\W*)(\w+)(\W*)$")


def _barajar_oracion(oracion, rng):
    """Baraja las palabras que empiezan en minúscula; mayúsculas, cifras,
    puntuación y espacios quedan en su sitio. None si no hay nada que barajar."""
    trozos = re.split(r"(\s+)", oracion)
    slots = []          # (índice de trozo, prefijo, palabra, sufijo)
    for i, t in enumerate(trozos):
        m = _RE_SLOT.match(t)
        if m and m.group(2)[0].isalpha() and m.group(2)[0].islower():
            slots.append((i, m.group(1), m.group(2), m.group(3)))
    palabras = [s[2] for s in slots]
    if len(slots) < 4 or len(set(palabras)) < 2:
        return None
    for _ in range(20):
        nuevas = palabras[:]
        rng.shuffle(nuevas)
        if nuevas != palabras:
            break
    else:
        return None
    for (i, pre, _, suf), w in zip(slots, nuevas):
        trozos[i] = pre + w + suf
    return "".join(trozos)


def _p6(texto, ctx, rng, donante=None, frac=0.3):
    """P6: baraja las palabras en minúscula de ~`frac` de las oraciones de la zona narrativa.

    Mayúsculas, cifras y puntuación quedan fijas, por lo que TTR, Fernández-Huerta y Jaccard son invariantes
    por construcción (control exacto)."""
    partes = _partir_zona(texto)
    piezas = re.split(r"(?<=[.!?])(\s+)", partes[2])   # [oración, sep, oración, ...]
    idx_or = list(range(0, len(piezas), 2))
    n = len(idx_or)
    barajables = [i for i in idx_or if _barajar_oracion(piezas[i], random.Random(0)) is not None]
    k = min(len(barajables), max(1, round(frac * n)))
    elegidas = sorted(rng.sample(barajables, k)) if k else []
    for i in elegidas:
        piezas[i] = _barajar_oracion(piezas[i], rng)
    return Resultado(_rearmar(partes, "".join(piezas)), ctx.copia(),
                     {"oraciones_barajadas": [i // 2 for i in elegidas],
                      "oraciones_intactas": n - len(elegidas)})


def _p7(texto, ctx, rng, donante=None):
    """P7: duplica un párrafo (de 40+ caracteres si hay) de la zona narrativa."""
    partes = _partir_zona(texto)
    parrafos = partes[2].split("\n\n")
    largos = [i for i, p in enumerate(parrafos) if len(p) >= 40] or list(range(len(parrafos)))
    i = rng.choice(largos)
    parrafos.insert(i + 1, parrafos[i])
    return Resultado(_rearmar(partes, "\n\n".join(parrafos)), ctx.copia(), {"parrafo": i})


def _p8(texto, ctx, rng, donante=None):
    """P8: sustituye el texto por la narración de un turno de OTRO par (contaminación cruzada)."""
    if donante is None:
        raise ValueError("P8 requiere `donante` (narración de un turno de OTRO par)")
    return Resultado(donante, ctx.copia(), {"donante_len": len(donante)})


def _p10(texto, ctx, rng, donante=None):
    """P10: inserta narración de éxito y añade al contexto una pifia (1 natural), contradicción que CR-1 debe detectar."""
    pifia = {"etiqueta": rng.choice(HABILIDADES), "dado": 1, "dados": (1,), "modificador": 3,
             "total": 4, "critico": False, "pifia": True}
    nuevo, frag = _insertar_al_inicio_de_parrafo(texto, rng.choice(EXITO), rng)
    return Resultado(nuevo, ctx.copia(tiradas=list(ctx.tiradas) + [pifia]),
                     {"insertado": frag, "habilidad": pifia["etiqueta"]})


def _p11a(texto, ctx, rng, donante=None):
    """P11a: inyecta el formato G1 (bloques narrativa y mecánica con una línea de tirada) en un texto de G2."""
    hab = rng.choice(HABILIDADES)
    n = rng.randint(2, 19)
    cd = rng.randint(10, 18)
    res = "Éxito" if n >= cd else "Fallo"
    linea = f"{hab}: {res} ({n} vs CD {cd})."
    return Resultado(f"narrativa\n{texto.strip()}\n\nmecanica\n{linea}", ctx.copia(),
                     {"linea": linea})


def _p11b(texto, ctx, rng, donante=None):
    """P11b: elimina el formato G1 (etiquetas y bloque mecánica) del texto, con prosa() de validacion_generar."""
    return Resultado(prosa(texto, "G1"), ctx.copia(), {})


def _p12(texto, ctx, rng, donante=None):
    """P12: inserta tres palabras de otro alfabeto (cirílico, CJK, hangul o kana) en huecos entre palabras."""
    partes = _partir_zona(texto)
    core = partes[2]
    huecos = [m.end() for m in re.finditer(r" (?=\S)", core)]
    pos = sorted(rng.sample(huecos, 3), reverse=True)
    palabras = rng.sample(PALABRAS_OTRO_ALFABETO, 3)
    for p, w in zip(pos, palabras):
        core = core[:p] + w + " " + core[p:]
    return Resultado(_rearmar(partes, core), ctx.copia(), {"palabras": palabras})


# ---------------------------------------------------------------- elegibilidad
def _sin_tiradas(texto, ctx):
    """Elegible solo si el turno no tiene tiradas."""
    return not ctx.tiradas


def _hay_pnj(texto, ctx):
    """Elegible solo si la campaña tiene algún PNJ no PJ."""
    return bool(_candidatos_pnj(ctx))


def _hp_positivo(texto, ctx):
    """Elegible solo si el HP actual del PJ es conocido y mayor que 0."""
    return ctx.hp_current is not None and ctx.hp_current > 0


def _g2_sin_etiquetas(texto, ctx):
    """Elegible solo para turnos de G2 sin etiquetas de formato."""
    return ctx.brazo == "G2" and not ETIQ.search(texto)


def _g1_con_etiquetas(texto, ctx):
    """Elegible solo para turnos de G1 con etiquetas de formato."""
    return ctx.brazo == "G1" and bool(ETIQ.search(texto))


def _siempre(texto, ctx):
    """Elegible siempre."""
    return True


@dataclass
class Perturbacion:
    """Entrada del catálogo: id, descripción, ámbito ("turno" o "ventana"), función y regla de elegibilidad."""
    id: str
    descripcion: str
    ambito: str
    funcion: object
    elegible: object = _siempre


CATALOGO: dict = {}


def _reg(pid, descripcion, funcion, elegible=_siempre, ambito="turno"):
    """Registra una perturbación en CATALOGO."""
    CATALOGO[pid] = Perturbacion(pid, descripcion, ambito, funcion, elegible)


for _c in CATEGORIAS:
    _reg(f"P1_{_c}", f"Usurpación en 2.ª persona ({_c})",
         (lambda cat: lambda t, c, r, d=None: _p_usurpacion(PLANTILLAS_2P, False)(t, c, r, d, cat=cat))(_c),
         _sin_tiradas if _c == "accion" else _siempre)
    _reg(f"P2_{_c}", f"Usurpación en 3.ª persona con el nombre del PJ ({_c})",
         (lambda cat: lambda t, c, r, d=None: _p_usurpacion(PLANTILLAS_3P, True)(t, c, r, d, cat=cat))(_c),
         _sin_tiradas if _c == "accion" else _siempre)
# Añadidas tras el humo (--rapido): 149 de 150 turnos reales llevan tirada del sistema, y
# qn2_pj_accion_revisar solo mira turnos SIN tirada; P1_accion/P2_accion quedan casi «no aplica».
# Estas variantes retiran las tiradas del contexto perturbado (turno simulado sin tirada).
_reg("P1_accion_sin_tirada", "Usurpación en 2.ª persona (acción física) en un turno simulado sin tirada",
     lambda t, c, r, d=None: _p_usurpacion(PLANTILLAS_2P, False, True)(t, c, r, d, cat="accion"))
_reg("P2_accion_sin_tirada", "Usurpación en 3.ª persona con nombre (acción física) en un turno simulado sin tirada",
     lambda t, c, r, d=None: _p_usurpacion(PLANTILLAS_3P, True, True)(t, c, r, d, cat="accion"))
for _est in ("dead", "missing"):
    for _modo in ("actua", "habla"):
        _reg(f"P3_{_est}_{_modo}", f"PNJ {_est} {'actúa' if _modo == 'actua' else 'habla'}",
             (lambda e, m: lambda t, c, r, d=None: _p3(t, c, r, d, estado=e, modo=m))(_est, _modo),
             _hay_pnj)
_reg("P4_2p", "Muerte del PJ narrada en 2.ª persona con HP>0",
     lambda t, c, r, d=None: _p4(t, c, r, d, persona="2p"), _hp_positivo)
_reg("P4_3p", "Muerte del PJ narrada en 3.ª persona con HP>0",
     lambda t, c, r, d=None: _p4(t, c, r, d, persona="3p"), _hp_positivo)
_reg("P5", "Nombres propios inventados", _p5)
_reg("P6", "Corrupción gramatical: barajar palabras en minúscula en ~30 % de oraciones", _p6)
_reg("P7", "Párrafo duplicado", _p7)
_reg("P8", "Contaminación cruzada: narración de un turno de OTRO par", _p8)
_reg("P9", "Permutación del orden de turnos vecinos (ventana de 8; Barzilay & Lapata 2008)",
     None, ambito="ventana")
_reg("P10", "Pifia (1 natural) con narración de éxito", _p10)
_reg("P11a_inyeccion", "Inyección del formato G1 (etiquetas + línea mecánica) en texto de G2",
     _p11a, _g2_sin_etiquetas)
_reg("P11b_eliminacion", "Eliminación del formato G1 (etiquetas + bloque mecánica) en texto de G1",
     _p11b, _g1_con_etiquetas)
_reg("P12", "Tres palabras en otro alfabeto", _p12)


def elegible(pid, texto, ctx):
    """Indica si la perturbación `pid` se puede aplicar a ese turno y contexto."""
    return bool(CATALOGO[pid].elegible(texto, ctx))


def perturbar(pid, texto, ctx, rng, donante=None):
    """Aplica la perturbación de turno `pid` sin mutar texto ni contexto.

    Args:
        donante: narración de otro par, solo para P8.

    Raises:
        ValueError: si `pid` es de ventana."""
    p = CATALOGO[pid]
    if p.ambito != "turno":
        raise ValueError(f"{pid} es de ventana: usa perturbar_ventana")
    return p.funcion(texto, ctx, rng, donante)


def perturbar_ventana(pid, textos, rng):
    """P9: permutación aleatoria (distinta de la identidad en la práctica) del orden de los textos de la ventana.

    Raises:
        ValueError: si `pid` no es de ventana."""
    if CATALOGO[pid].ambito != "ventana":
        raise ValueError(f"{pid} es de turno: usa perturbar")
    n = len(textos)
    ident = list(range(n))
    perm = ident[:]
    for _ in range(100):
        rng.shuffle(perm)
        if perm != ident:
            break
    return ResultadoVentana([textos[i] for i in perm], {"perm": perm})


# ================================================================== ESPERADO
# Escrito ANTES de correr el arnés sobre datos reales. No se edita tras ver resultados.
# Valores: booleanos -> "se_dispara" | "sin_cambio"; numéricos -> "sube" | "baja" | "sin_cambio".
def _mk(se_dispara=(), sube=(), baja=(), sin_cambio=()):
    """Construye {instrumento: dirección} de la tabla ESPERADO a partir de los grupos de direcciones."""
    d = {}
    for nombre in se_dispara:
        d[nombre] = "se_dispara"
    for nombre in sube:
        d[nombre] = "sube"
    for nombre in baja:
        d[nombre] = "baja"
    for nombre in sin_cambio:
        d[nombre] = "sin_cambio"
    return d


_CTRL_BOOL = ("meta_comentario", "comenta_reglas", "cr1_veredicto_contradice_narracion",
              "qn2_pj_piensa_narrado", "qn2_pj_accion_revisar", "cl2_pnj_inactivo_actua",
              "cl2_pc_hp_contradice_narracion", "cr2_nombres_no_reconocidos")


def _sin(*excepto):
    """Booleanos de control «sin cambio», excepto los indicados."""
    return tuple(n for n in _CTRL_BOOL if n not in excepto)


ESPERADO = {}
for _c in CATEGORIAS:
    # P1/P2: el detector qn2_pj_piensa_narrado declara medir pensamientos/emociones/decisiones
    # del PJ (piensa|siente|decide|comprende); qn2_pj_accion_revisar, acciones físicas no declaradas.
    _piensa = _c in ("decision", "pensamiento", "emocion")
    _acc = _c == "accion"
    for _p in ("P1", "P2"):
        ESPERADO[f"{_p}_{_c}"] = _mk(
            se_dispara=(["qn2_pj_piensa_narrado"] if _piensa else []) + (["qn2_pj_accion_revisar"] if _acc else []),
            sin_cambio=_sin(*(["qn2_pj_piensa_narrado"] if _piensa else []),
                            *(["qn2_pj_accion_revisar"] if _acc else [])))
for _p in ("P1", "P2"):
    ESPERADO[f"{_p}_accion_sin_tirada"] = _mk(se_dispara=["qn2_pj_accion_revisar"],
                                              sin_cambio=_sin("qn2_pj_accion_revisar"))
for _e in ("dead", "missing"):
    for _m in ("actua", "habla"):
        ESPERADO[f"P3_{_e}_{_m}"] = _mk(
            se_dispara=["cl2_pnj_inactivo_actua", "cl2_pnj_inactivo_refinado"],
            sin_cambio=_sin("cl2_pnj_inactivo_actua"))
for _p in ("P4_2p", "P4_3p"):
    ESPERADO[_p] = _mk(se_dispara=["cl2_pc_hp_contradice_narracion"],
                       sin_cambio=_sin("cl2_pc_hp_contradice_narracion"))
ESPERADO["P5"] = _mk(
    se_dispara=["cr2_nombres_no_reconocidos"],
    sube=["cr2_n_nombres_no_reconocidos"],
    baja=["cr2_entidad_grafo_densidad"],      # oración añadida sin entidades conocidas: nodo sin aristas
    sin_cambio=_sin("cr2_nombres_no_reconocidos"))
ESPERADO["P6"] = _mk(
    baja=["grammaticality_lt"],
    sin_cambio=list(_sin()) + ["qn1_ttr", "qn1_legibilidad_fh", "cl2_lugar_jaccard_similarity",
                               "cr2_entidad_grafo_densidad", "entity_coreference_rate"])
ESPERADO["P7"] = _mk(
    sube=["qn1_ngram_repeticion"], baja=["qn1_ttr"],
    sin_cambio=list(_sin()) + ["cl2_lugar_jaccard_similarity"])
ESPERADO["P8"] = _mk(
    se_dispara=["cr2_nombres_no_reconocidos"],
    sube=["cr2_n_nombres_no_reconocidos"],
    baja=["cl2_lugar_jaccard_similarity", "cr2_entidad_grafo_densidad", "grafo_lema_densidad"],
    sin_cambio=["cl2_pc_hp_contradice_narracion", "cl2_pnj_inactivo_actua"])
ESPERADO["P9"] = _mk(
    baja=["ventana_jaccard_medio"],
    sube=["ventana_bucles_visitas", "ventana_bucles_ciclos"],
    sin_cambio=["ventana_consistencia_V", "ventana_coherencia_C", "ventana_entity_coreference_medio"])
ESPERADO["P10"] = _mk(se_dispara=["cr1_veredicto_contradice_narracion"],
                      sin_cambio=_sin("cr1_veredicto_contradice_narracion"))
_FORMATO = dict(sin_cambio=["qn1_ttr", "qn1_ngram_repeticion", "qn1_legibilidad_fh",
                            "cl2_lugar_jaccard_similarity", "cr2_entidad_grafo_densidad",
                            "grammaticality_lt", "cr2_nombres_no_reconocidos",
                            "meta_comentario", "comenta_reglas"])
ESPERADO["P11a_inyeccion"] = _mk(**_FORMATO)
ESPERADO["P11b_eliminacion"] = _mk(**_FORMATO)
ESPERADO["P12"] = _mk(baja=["grammaticality_lt"], sube=["qn1_ttr"],
                      sin_cambio=["cr2_nombres_no_reconocidos", "cl2_pnj_inactivo_actua",
                                  "cl2_pc_hp_contradice_narracion"])

_ESPERADO_INICIAL = copy.deepcopy(ESPERADO)


POSTERIORES_AL_HUMO = ("P1_accion_sin_tirada", "P2_accion_sin_tirada")   # añadidas tras el humo (ver _reg)


def hash_esperado(original=False):
    """SHA-256 de la tabla ESPERADO pre-especificada; el informe lo imprime. `original=True`
    excluye las variantes añadidas después del humo (el hash del 2026-09-20 18:29)."""
    tabla = {k: v for k, v in _ESPERADO_INICIAL.items() if not (original and k in POSTERIORES_AL_HUMO)}
    return hashlib.sha256(json.dumps(tabla, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def registrar_esperado(pid, instrumento, direccion):
    """Añade la expectativa de un instrumento NUEVO (p. ej. los detectores de 2.ª persona)
    ANTES de correrlo. No sirve para reescribir las expectativas ya pre-especificadas."""
    if instrumento not in it.INSTRUMENTOS:
        raise ValueError(f"instrumento no registrado: {instrumento}")
    validas = {"se_dispara", "sin_cambio"} if it.INSTRUMENTOS[instrumento].tipo == "bool" \
        else {"sube", "baja", "sin_cambio"}
    if direccion not in validas:
        raise ValueError(f"dirección {direccion!r} inválida para {instrumento}: {sorted(validas)}")
    if instrumento in _ESPERADO_INICIAL.get(pid, {}):
        raise ValueError(f"{pid}/{instrumento} ya estaba pre-especificado: no se reescribe")
    ESPERADO[pid][instrumento] = direccion
