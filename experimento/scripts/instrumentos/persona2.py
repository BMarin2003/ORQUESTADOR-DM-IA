#!/usr/bin/env python3
"""
persona2.py -- detector DETERMINISTA (sin LLM, sin APIs) de USURPACIÓN DE AGENCIA
y de MUERTE DEL PJ en narración de un DM en español, en SEGUNDA persona.

Por qué existe: los detectores de motor/orquestador/vertical_slice.py (qn2_pj_piensa_narrado,
qn2_pj_accion_revisar, cl2_pc_hp_contradice_narracion) buscan «<Nombre PJ> piensa|siente|...»
en 3.ª persona. El DM real narra en 2.ª persona («Decides...», «te acercas») y casi nunca
nombra al PJ, así que dieron 0 marcas en 58 800 turnos. Este módulo cubre la 2.ª persona
y conserva la 3.ª con nombre (parámetro nombre_pj) como CONTROL POSITIVO.

API
    detectar_usurpacion(dm_texto, accion_jugador, nlp, nombre_pj=None) -> list[dict]
    narra_muerte_pj(dm_texto, nlp, nombre_pj=None) -> dict | None
    analizar_completo(dm_texto, accion_jugador, nlp, nombre_pj=None) -> (hallazgos, excluidos)

Hallazgo = {categoria, confianza ('alta'|'media'), verbo_lema, evidencia, inicio, fin,
            tirada_declarada, declarada, persona ('2'|'3'), explicito}
  * evidencia = la oración que contiene el disparador.
  * inicio/fin = offsets de CARACTER del disparador (verbo o locución) en dm_texto, de modo
    que dm_texto[inicio:fin] es «decides», «te das cuenta»...; NO son los offsets de la oración.
  * tirada_declarada: la acción del jugador traía un tag de tirada tipo {Percepción}.
  * declarada: el lema del verbo (o un sinónimo del léxico) aparece en la acción del jugador.
    Para HABLA también cuenta que la acción traiga una cita entre comillas/raya.
  * explicito: hay «tú» como sujeto explícito junto al verbo.
  * persona '3' = control positivo (nombre del PJ como sujeto).

Categorías (definición operacional; ver lexicon_persona2.json y sus fuentes)
  VOLICION  decidir, elegir, optar, querer, te obligas a...          (alta)
  COGNICION pensar, comprender, saber, recordar, te das cuenta,
            se te ocurre, tienes la sensación de...                  (alta; media si ambiguo)
  EMOCION   sentir/tener + sustantivo emocional, te invade el miedo,
            te asusta...                                             (alta; media en «directo»)
  HABLA     dices, murmuras, respondes...                            (alta)
  ACCION_NO_DECLARADA  verbo físico intencional en 2.ª persona cuyo
            lema (ni sinónimo) está en la acción del jugador         (media)
  MUERTE_PJ (solo narra_muerte_pj)

EXCLUSIONES (cada una con justificación)
  * Percepción sensorial (ves, oyes, notas, percibes, encuentras, descubres, sientes frío...):
    el jugador no puede «declarar» lo que el entorno le muestra; es información del mundo,
    no agencia. sentir sin sustantivo emocional se excluye por defecto (ver «límites»).
  * Consecuencias mecánicas/reflejos involuntarios (tropiezas, caes, sangras, te estremeces...).
  * Ejecución de lo declarado (mismo lema o sinónimo obvio): solo excluye ACCION_NO_DECLARADA;
    en las otras categorías el hallazgo se conserva con declarada=True para poder separarlo.
  * Texto entre comillas/rayas de diálogo (voz de un PNJ que habla al PJ con «tú»),
    [texto fuera de personaje], preguntas «¿...?» al jugador y cláusulas condicionales
    («si decides...»): no narran al PJ.
  * Formas nominales homógrafas (las dudas, tus notas): regla de contexto para 2sg ambiguas.

Otras decisiones: (1) 2sg solo en presente/pretérito/imperfecto; futuro y condicional («quedarás»,
«jurarías») son predicción o hipótesis y no se marcan. (2) «Tus dedos recorren el metal»: parte
MOTORA del cuerpo del PJ como sujeto = acción del PJ (ACCION, media) con la misma regla de
«declarada»; ojos/mirada/oídos no cuentan (percepción). (3) «intentas + inf», «sigues + gerundio»:
el núcleo es el verbo que sigue; si el jugador declaró ese verbo (o sinónimo) se descarta.

REGLA DE «DECLARADA» v2 (solo ACCION_NO_DECLARADA; configurable con config={...}, CONFIG_V1 = regla v1)
  Una acción física del DM cuenta como EJECUCIÓN de lo declarado (no se marca) si se cumple alguna:
   (verbo)      el lema o un sinónimo (léxico: «sinonimos» + «sinonimos_ampliados») está en la acción del jugador;
   (movimiento) el verbo del DM es de desplazamiento del cuerpo (mover, alejar, retroceder, deslizar...) y el
                jugador declaró algún verbo de movimiento;
   (cuerpo)     el sujeto es una parte motora del cuerpo del PJ («tus dedos rozan...») y el jugador declaró un
                verbo genérico de manipulación/movimiento (tocar, examinar, recorrer, tantear, sacar, quitar...);
   (contenido)  algún lema de contenido (ni palabra función ni verbo del léxico) de la CLÁUSULA del DM aparece en
                la acción del jugador (igualdad laxa: mismo prefijo >= 4 letras, tolera número/género).
  Además: lo que el jugador DICE entre comillas/rayas no es acción declarada; «accidentalmente/sin querer» hace
  involuntaria la acción; «te vuelves invisible» es cambio de estado; «intentas/sigues + inf/ger» hereda lo
  declarado por su núcleo. Cada regla se apaga con config (ver CONFIG_DEFECTO). Métrica PRIMARIA del instrumento =
  usurpación mental/verbal (VOLICION+COGNICION+EMOCION+HABLA: regla de oro de motor/dm/prompt_g2.md); ACCION_NO_DECLARADA
  es SECUNDARIA y EXPERIMENTAL.

PROCEDENCIA Y CONGELAMIENTO: el léxico y las reglas se elaboraron y depuraron con los turnos listados en
datos/validacion/persona2_desarrollo_turnos.csv (muestra de exploración semilla 777, muestra de evaluación y reserva de
semilla 20260920). A PARTIR DE LA VERSIÓN «declarada v2» EL DETECTOR QUEDA CONGELADO: la auditoría de confirmación
(confirmacion_persona2.py, semilla 20260921) usa solo turnos fuera de ese archivo y no se ajusta nada tras mirarla.

Límites conocidos (honestidad): el léxico es finito (verbo fuera de lista = falso negativo);
otras perífrasis («logras abrir», «empiezas a correr») no se analizan; el «tú» genérico/impersonal
(«cuando sabes que el tiempo se agota») SÍ se marca (falso positivo conocido); «sientes que X» sin
sustantivo emocional se excluye (pierde intuiciones); adjetivos homógrafos tras «y» («confusas y
esquivas») se leen como verbo; la equivalencia declarada/no declarada sigue siendo léxica y de
alcance de CLÁUSULA (un detalle nuevo con otro verbo y otro objeto se marca; un detalle de otra
CLASE que el jugador no mencionó, p. ej. «Sacas tu daga» tras «Me acerco», también); las citas de varios párrafos se emparejan por línea; subjuntivo/imperativo/vos no se analizan; en
3.ª persona con nombre solo se ve el primer verbo tras el nombre («Osric se levanta y comprende...»
marca «levantar» y no «comprender»).
El modelo es_core_news_sm etiqueta mal los verbos de 2.ª persona (medido: solo ~15 % de los
hallazgos tienen Person=2; «Sientes» -> PROPN, «Murmuras» -> NOUN), por eso el reconocimiento de
formas es LÉXICO (tablas de conjugación generadas del léxico); spaCy aporta la tokenización con
offsets y, como respaldo, Person=2/lemma para formas que las tablas no cubran. El detector da la
MISMA salida con nlp=None (medido en 600 turnos): hoy spaCy no aporta hallazgos.
"""
import bisect
import json
import re
import unicodedata
from pathlib import Path

_RUTA_LEX = Path(__file__).resolve().parent / "lexicon_persona2.json"


# ══════════════════════════ utilidades de texto ══════════════════════════

def _plano(s):
    """minúsculas sin acentos, LONGITUD-PRESERVANTE (un carácter -> un carácter)."""
    return "".join((unicodedata.normalize("NFD", c)[:1].lower() or c) for c in s)


_PUNT = set(list(".,;:!?—…()¿¡«»\"“”[]"))
_RE_TIRADA = re.compile(r"\{[^{}]+\}")


# ══════════════════════════ carga del léxico ══════════════════════════

def _ort_1sg(lema_p, raiz, ton):
    """1.ª persona del presente con los cambios ortográficos frecuentes (solo para 'declarada')."""
    if lema_p.endswith(("ger", "gir")):
        return ton[:-1] + "j" + "o" if ton.endswith("g") else ton + "o"
    if lema_p.endswith("guir"):
        return ton[:-2] + "go" if ton.endswith("gu") else ton + "o"
    if lema_p.endswith(("cer", "cir")) and len(raiz) >= 2:
        if raiz[-2] in "aeiou":
            return raiz[:-1] + "zco"
        return raiz[:-1] + "zo"
    return ton + "o"


def _paradigma(lema_p, ton, p3):
    """(formas_2sg, formas_3sg, exactas_declaradas) en 'plano'."""
    ar = lema_p.endswith("ar")
    raiz = lema_p[:-2]
    # solo presente, pretérito e imperfecto: futuro y condicional (dirás, jurarías) son predicción o
    # hipótesis («quedarás acorralado», «jurarías que...»), no narración de un hecho del PJ
    f2 = {ton + ("as" if ar else "es"), raiz + ("aste" if ar else "iste"),
          raiz + ("abas" if ar else "ias")}
    f3 = {ton + ("a" if ar else "e"), p3 + ("o" if ar else "io"),
          raiz + ("aba" if ar else "ia")}
    part = raiz + ("ado" if ar else "ido")
    ex = {lema_p, part, raiz + ("ando" if ar else "iendo"), ton + ("a" if ar else "e"),
          ton + ("an" if ar else "en"), raiz + ("aba" if ar else "ia"), p3 + ("o" if ar else "io"),
          _ort_1sg(lema_p, raiz, ton), raiz + ("e" if ar else "i"), raiz + "o"}
    if lema_p.endswith("car"):
        ex.add(raiz[:-1] + "que")
    elif lema_p.endswith("gar"):
        ex.add(raiz + "ue")
    elif lema_p.endswith("zar"):
        ex.add(raiz[:-1] + "ce")
    return f2, f3, ex, part


def _parse_entrada(x, cat):
    """cadena o dict del léxico -> dict normalizado con formas y matcher de 'declarada'."""
    flags = set()
    if isinstance(x, str):
        base, _, fl = x.partition("@")
        flags = set(f for f in fl.split(",") if f)
        partes = base.split(":")
        lema = partes[0]
        lema_p = _plano(lema)
        raiz = lema_p[:-2]
        ton = _plano(partes[1]) if len(partes) > 1 and partes[1] else raiz
        p3 = _plano(partes[2]) if len(partes) > 2 and partes[2] else raiz
        f2, f3, ex, part = _paradigma(lema_p, ton, p3)
        pl3 = {ton + ("an" if lema_p.endswith("ar") else "en"), p3 + ("aron" if lema_p.endswith("ar") else "ieron"),
               raiz + ("aban" if lema_p.endswith("ar") else "ian")}
        pref = set()
        exactas = set(ex)
        for r in {ton, raiz}:
            (pref if len(r) >= 5 else exactas).add(r)
        # raíces cortas: sus formas exactas ya están en 'ex'
    else:
        lema = x["lema"]
        lema_p = _plano(lema)
        if x.get("te"):
            flags.add("te")
        if x.get("nte"):
            flags.add("nte")
        f2, f3 = set(), set()
        pl3 = {_plano(f) for f in x.get("formas_3pl", [])}
        pref, exactas = set(), set()
        if lema_p.endswith(("ar", "er", "ir")):
            raiz = lema_p[:-2]
            _, _, ex, _ = _paradigma(lema_p, raiz, raiz)
            exactas |= ex
        for f in x.get("formas_2sg", []):
            f2.add(_plano(f))
        for f in x.get("formas_3sg", []):
            f3.add(_plano(f))
        for d in x.get("decl", []):
            d = _plano(d)
            (pref.add(d[:-1]) if d.endswith("*") else exactas.add(d))
        part = None
    return {"lema": lema, "cat": cat, "te": "te" in flags, "nte": "nte" in flags,
            "media": "m" in flags, "f2": f2, "f3": f3, "pl3": pl3, "pref": pref, "exactas": exactas,
            "part": part}


_PART_IRREG = {"dicho": "decir", "puesto": "poner", "vuelto": "volver", "abierto": "abrir",
               "roto": "romper", "cubierto": "cubrir"}
_DAR2 = {"das", "diste", "dabas", "daras", "darias"}
_HAS = {"has", "habias", "hubiste", "habras"}


def _cargar():
    """Carga lexicon_persona2.json y construye las tablas de formas (2sg, 3sg, 3pl, participios, infinitivos/gerundios, sinónimos y listas de contexto) que usa todo el detector; se ejecuta una vez al importar."""
    lex = json.loads(_RUTA_LEX.read_text(encoding="utf-8"))
    t2, t3, part, t3pl = {}, {}, {}, {}
    entradas = {}          # lema -> entrada (para matchers)
    por_lema = {}

    def registrar(x, cat, tablas=True):
        """Indexa una entrada del léxico en las tablas de formas y por lema; con `tablas=False` solo sirve para «declarada» y no genera hallazgos."""
        e = _parse_entrada(x, cat)
        if not tablas:      # solo para «declarada»: no genera hallazgos
            entradas.setdefault(e["lema"], e)
            por_lema.setdefault(_plano(e["lema"]), []).append(e)
            return e
        for f in e["f2"]:
            t2.setdefault(f, []).append(e)
        for f in e["f3"]:
            t3.setdefault(f, []).append(e)
        for f in e["pl3"]:
            t3pl.setdefault(f, []).append(e)
        if e["part"] and cat in ("VOLICION", "COGNICION", "EMOCION", "HABLA", "ACCION"):
            part.setdefault(e["part"], e)
        entradas.setdefault(e["lema"], e)
        por_lema.setdefault(_plano(e["lema"]), []).append(e)
        return e

    for cat, lst in lex["verbos"].items():
        for x in lst:
            registrar(x, cat)
    for cat, lst in lex["excluidos"].items():
        for x in lst:
            registrar(x, cat)
    for x in lex.get("red_amplia", []):
        registrar(x, "RED")
    for x in lex.get("solo_declaracion", []):
        registrar(x, "DECL", tablas=False)
    for irr, lema in _PART_IRREG.items():
        if lema in entradas:
            part.setdefault(irr, entradas[lema])

    # sentir / tener: tratamiento especial (dependen del sustantivo que sigue)
    for f in ("sientes", "sentiste", "sentias", "sentiras", "sentirias"):
        t2.setdefault(f, []).append({"lema": "sentir", "cat": "SENTIR", "te": False, "nte": False, "media": False})
    for f in ("siente", "sintio", "sentia", "sentira"):
        t3.setdefault(f, []).append({"lema": "sentir", "cat": "SENTIR", "te": False, "nte": False, "media": False})
    for f in ("tienes", "tuviste", "tenias", "tendras", "tendrias"):
        t2.setdefault(f, []).append({"lema": "tener", "cat": "TENER", "te": False, "nte": False, "media": False})
    for f in ("tiene", "tuvo", "tenia", "tendra"):
        t3.setdefault(f, []).append({"lema": "tener", "cat": "TENER", "te": False, "nte": False, "media": False})

    # infinitivos y gerundios (para resolver el núcleo de «intentas + inf», «sigues + gerundio»)
    inf_ger, inf_ger_v1 = {}, {}
    for lema_p, lst in por_lema.items():
        for e in lst:
            if e["cat"] not in ("VOLICION", "COGNICION", "EMOCION", "HABLA", "ACCION", "DECL", "PERCEPCION"):
                continue
            tablas = [inf_ger] + ([inf_ger_v1] if e["cat"] in ("VOLICION", "COGNICION", "EMOCION", "HABLA", "ACCION") else [])
            for tb in tablas:
                tb.setdefault(lema_p, set()).add(e["lema"])
                if lema_p.endswith(("ar", "er", "ir")):
                    tb.setdefault(lema_p[:-2] + ("ando" if lema_p.endswith("ar") else "iendo"), set()).add(e["lema"])
    # sinónimos -> matcher por lema (unión de los matchers de cada miembro del grupo)
    grupos, grupos2 = {}, {}
    for g in lex["sinonimos"]:
        for m in g:
            grupos.setdefault(m, set()).update(g)
            grupos2.setdefault(m, set()).update(g)
    da = lex["declarada_accion"]
    for g in da["sinonimos_ampliados"]:
        for m in g:
            grupos2.setdefault(m, set()).update(g)
    sn = lex["sustantivos"]
    ctx = lex["contexto"]
    imp = lex["impacto_te"]
    return {
        "t2": t2, "t3": t3, "t3pl": t3pl, "part": part, "inf_ger": inf_ger, "inf_ger_v1": inf_ger_v1,
        "cuerpo": {_plano(x) for x in lex["contexto"]["partes_del_cuerpo_motoras"]}, "entradas": entradas, "grupos": grupos,
        "por_lema_plano": por_lema, "grupos2": grupos2,
        "gen_cuerpo": da["cuerpo_jugador"], "gen_mov": da["movimiento_jugador"], "mov_dm": set(da["movimiento_dm"]),
        "stop": {_plano(x) for x in da["stopwords_contenido"]},
        "marc_invol": [_plano(x) for x in da["marcadores_involuntario"]],
        "emo": {_plano(x) for x in sn["emocion"]},
        "pens": {_plano(x) for x in sn["pensamiento"]},
        "sens": {_plano(x) for x in sn["sensorial"]},
        "det": set(ctx["det_prep_previos"]),
        "inicio": set(ctx["inicio_de_clausula"]),
        "gap": {_plano(x) for x in ctx["adverbios_entre_nombre_y_verbo"]},
        "ambig": {_plano(x) for x in ctx["formas_2sg_ambiguas"]},
        "imp_sust": {_plano(x) for x in imp["formas_con_sustantivo"]},
        "imp_dir": {_plano(x) for x in imp["formas_directo"]},
        "imp_lemas": [(_plano(x)[:-2], x) for x in imp["con_sustantivo"]],
        "red_te": {_plano(x) for x in lex.get("red_impacto_te", [])},
    }


_L = _cargar()

# matchers extra para locuciones y verbos especiales (para «declarada»)
_MATCH_ESPECIAL = {
    "darse cuenta": ({"cuenta"}, set()),
    "dar un paso": (set(), {"paso", "pasos", "vuelta", "salto", "giro"}),
    "sentir": ({"sient", "sint"}, {"sentir", "sentia", "sentiras"}),
    "sentirse": ({"sient", "sint"}, {"sentir", "sentia", "sentiras"}),
    "tener": (set(), {"tengo", "tiene", "tuve", "tenia"}),
}


def _matcher_de(lema, amp=False):
    """(prefijos, exactas) del lema y de todos sus sinónimos (amp=True: grupos ampliados de la v2)."""
    lemas = {lema} | _L["grupos2" if amp else "grupos"].get(lema, set())
    pref, ex = set(), set()
    for m in lemas:
        if m in _MATCH_ESPECIAL:
            p, e = _MATCH_ESPECIAL[m]
            pref |= p
            ex |= e
            continue
        for ent in _L["por_lema_plano"].get(_plano(m), []):
            pref |= ent["pref"]
            ex |= ent["exactas"]
    return pref, ex


_CACHE_MATCH = {}


def _match(lema, amp=False):
    """`_matcher_de` con caché por (lema, amp)."""
    if (lema, amp) not in _CACHE_MATCH:
        _CACHE_MATCH[(lema, amp)] = _matcher_de(lema, amp)
    return _CACHE_MATCH[(lema, amp)]


def _matcher_lista(lemas):
    """unión de los matchers de una lista de lemas (sin sinónimos)."""
    pref, ex = set(), set()
    for m in lemas:
        for ent in _L["por_lema_plano"].get(_plano(m), []):
            pref |= ent["pref"]
            ex |= ent["exactas"]
    return pref, ex


_GEN_CUERPO = _matcher_lista(_L["gen_cuerpo"])
_GEN_MOV = _matcher_lista(_L["gen_mov"])


# ══════════════════════════ configuración de «declarada» ══════════════════════════
CONFIG_DEFECTO = {
    "sinonimos_ampliados": True,    # grupos de sinónimos de la v2 (separar~alejar, recoger~levantar, acercar~inclinar...)
    "accion_sin_dialogo": True,     # lo que el jugador DICE (comillas/rayas) no cuenta como acción declarada
    "movimiento_generico": True,    # «Te desplazas» declarado por cualquier verbo de movimiento del jugador
    "cuerpo_generico": True,        # «Tus dedos rozan...» declarado por un verbo genérico de manipulación/movimiento
    "contenido": True,              # lema de contenido de la cláusula del DM presente en la acción del jugador
    "ambito_contenido": "clausula",  # 'clausula' (entre , ; : . ...) | 'oracion'
    "min_prefijo_contenido": 4,     # longitud mínima del prefijo común para igualar dos palabras de contenido
    "residuales_v2b": True,         # «accidentalmente» = involuntario; «te vuelves invisible» = cambio de estado;
                                    # núcleo de «intentas/sigues + inf/ger» ampliado (tantear, examinar...)
}
CONFIG_V1 = dict(CONFIG_DEFECTO, sinonimos_ampliados=False, accion_sin_dialogo=False, movimiento_generico=False,
                 cuerpo_generico=False, contenido=False, residuales_v2b=False)


def _cfg(config):
    """Mezcla `config` sobre CONFIG_DEFECTO; rechaza opciones desconocidas."""
    c = dict(CONFIG_DEFECTO)
    if config:
        desconocidas = set(config) - set(c)
        if desconocidas:
            raise ValueError(f"opciones de config desconocidas: {sorted(desconocidas)}")
        c.update(config)
    return c


def _es_nombre(n, conj):
    """True si `n` (plano) está en `conj`, incluido su plural regular en -s o -es."""
    return n in conj or (n.endswith("s") and n[:-1] in conj) or (n.endswith("es") and n[:-2] in conj)


# ══════════════════════════ zonas (dónde NO se busca) ══════════════════════════

def _zonas(texto):
    """[(ini, fin, motivo)]: 'cita' (diálogo), 'ooc' ([...]), 'pregunta' (¿...?)."""
    z = []
    for m in re.finditer(r"\[[^\]]*\]", texto):
        z.append((m.start(), m.end(), "ooc"))
    for m in re.finditer(r"«[^»]*»|“[^”]*”", texto):
        z.append((m.start(), m.end(), "cita"))
    off = 0
    for linea in texto.split("\n"):
        # comillas rectas, emparejadas por línea
        idx = [i for i, c in enumerate(linea) if c == '"']
        for a in range(0, len(idx), 2):
            b = idx[a + 1] if a + 1 < len(idx) else len(linea)
            z.append((off + idx[a], off + b + (1 if a + 1 < len(idx) else 0), "cita"))
        # diálogo con raya: la línea empieza por «—»
        s = linea.lstrip()
        if s.startswith("—"):
            p0 = off + (len(linea) - len(s))
            habla = True
            ini = p0 + 1
            for m in re.finditer("—", linea[len(linea) - len(s) + 1:]):
                d = off + (len(linea) - len(s)) + 1 + m.start()
                if habla:
                    z.append((ini, d, "cita"))
                habla = not habla
                ini = d + 1
            if habla:
                z.append((ini, off + len(linea), "cita"))
        off += len(linea) + 1
    for m in re.finditer(r"¿[^?\n]*\?", texto):
        z.append((m.start(), m.end(), "pregunta"))
    return z


def _zona_de(pos, zonas):
    """motivo de la zona que contiene pos ('cita' prevalece), o None."""
    motivo = None
    for a, b, m in zonas:
        if a <= pos < b:
            if m == "cita":
                return "cita"
            motivo = motivo or m
    return motivo


def _oraciones(texto):
    """[(ini, fin)] de oraciones (reglas simples; determinista)."""
    out = []
    for m in re.finditer(r"[^.!?…\n]+(?:[.!?…]+[\"»”)\]]*)?", texto):
        if m.group().strip():
            out.append((m.start(), m.end()))
    return out


# ══════════════════════════ tokenización ══════════════════════════

def _tokens(texto, nlp):
    """Tokeniza con offsets de carácter; con `nlp=None` usa regex (misma salida del detector: spaCy solo aporta Person=2 y lema como respaldo)."""
    toks = []
    if nlp is not None:
        doc = nlp(texto)
        for t in doc:
            if t.is_space:
                continue
            toks.append({"t": t.text, "l": t.text.lower(), "n": _plano(t.text), "i": t.idx,
                         "e": t.idx + len(t.text),
                         "p2": ("2" in t.morph.get("Person")) and ("Fin" in t.morph.get("VerbForm"))
                               and ("Ind" in t.morph.get("Mood")),
                         "lem": _plano(t.lemma_ or "")})
    else:
        for m in re.finditer(r"\w+|[^\w\s]", texto):
            w = m.group()
            toks.append({"t": w, "l": w.lower(), "n": _plano(w), "i": m.start(), "e": m.end(),
                         "p2": False, "lem": ""})
    return toks


# ══════════════════════════ contexto declarado ══════════════════════════

def _mismo_lema(a, b, minp):
    """igualdad laxa de palabras de contenido (plano): mismo lema salvo número/género/derivación corta."""
    if a == b:
        return len(a) >= 3
    n = min(len(a), len(b))
    if n < minp or abs(len(a) - len(b)) > 3:
        return False
    cp = 0
    for x, y in zip(a, b):
        if x != y:
            break
        cp += 1
    return cp >= max(minp, n - 2)


class _Declarado:
    """Lo que el jugador declaró en su acción (tokens, tirada, cita y parte narrada sin diálogo) y la regla de «declarada» v2 para decidir si una acción física del DM es ejecución de lo declarado."""
    def __init__(self, accion, cfg):
        """Normaliza la acción: quita tags de tirada y separa la parte narrada de lo que el jugador dice entre comillas, rayas o corchetes."""
        accion = accion or ""
        self.cfg = cfg
        self.tirada = bool(_RE_TIRADA.search(accion))
        sin_tag = _RE_TIRADA.sub(" ", accion)
        self.toks = re.findall(r"\w+", _plano(sin_tag))
        self.cita = bool(re.search(r"[\"«“]|(?:^|\n)\s*—", accion))
        # acción NARRADA: sin lo que el jugador dice entre comillas/rayas ni corchetes
        z = [(a, b) for a, b, m in _zonas(sin_tag) if m in ("cita", "ooc")]
        narr = []
        pos = 0
        for a, b in sorted(z):
            if a > pos:
                narr.append(sin_tag[pos:a])
            pos = max(pos, b)
        narr.append(sin_tag[pos:])
        self.toks_narr = re.findall(r"\w+", _plano(" ".join(narr)))
        self._contenido = None

    def _toks_accion(self):
        """Tokens de acción declarada: sin diálogo si `accion_sin_dialogo`, con todo en caso contrario (v1)."""
        return self.toks_narr if self.cfg["accion_sin_dialogo"] else self.toks

    def cubre(self, lema, cat=None):
        """¿el lema (o un sinónimo) aparece en la acción declarada? (regla verbal)"""
        pref, ex = _match(lema, bool(self.cfg["sinonimos_ampliados"] and cat == "ACCION"))
        toks = self._toks_accion() if cat == "ACCION" else self.toks
        for w in toks:
            if w in ex or any(w.startswith(p) for p in pref):
                return True
        return cat == "HABLA" and self.cita

    def _tiene(self, matcher):
        """True si algún token de la acción declarada coincide con el matcher (prefijos, formas exactas)."""
        pref, ex = matcher
        return any(w in ex or any(w.startswith(p) for p in pref) for w in self._toks_accion())

    def contenido(self):
        """Lemas de contenido de la acción declarada (>= 3 letras, sin palabras función); se calcula una vez."""
        if self._contenido is None:
            self._contenido = [w for w in self._toks_accion() if len(w) >= 3 and w not in _L["stop"]]
        return self._contenido

    def via_accion(self, lema, sujeto_cuerpo, palabras_dm):
        """None si la acción física NO estaba declarada; si lo estaba, la vía: verbo|movimiento|cuerpo|contenido."""
        c = self.cfg
        if self.cubre(lema, "ACCION"):
            return "verbo"
        if c["movimiento_generico"] and lema in _L["mov_dm"] and self._tiene(_GEN_MOV):
            return "movimiento"
        if c["cuerpo_generico"] and sujeto_cuerpo and self._tiene(_GEN_CUERPO):
            return "cuerpo"
        if c["contenido"] and palabras_dm:
            mp = c["min_prefijo_contenido"]
            mias = self.contenido()
            if any(_mismo_lema(w, v, mp) for w in palabras_dm for v in mias):
                return "contenido"
        return None


# ══════════════════════════ análisis ══════════════════════════

class _Analisis:
    """Análisis de un turno: aplica las reglas del léxico a la narración del DM en 2.ª persona (y en 3.ª con nombre del PJ como control positivo) y acumula hallazgos y exclusiones con su motivo."""
    def __init__(self, dm, accion, nlp, nombre_pj, config=None):
        """Prepara tokens, zonas excluidas (citas, fuera de personaje, preguntas), oraciones y el contexto declarado."""
        self.dm = dm or ""
        self.cfg = _cfg(config)
        self.decl = _Declarado(accion, self.cfg)
        self.nombre_pj = nombre_pj
        self.toks = _tokens(self.dm, nlp) if self.dm.strip() else []
        self.zonas = _zonas(self.dm)
        self.sents = _oraciones(self.dm)
        self._sini = [a for a, _ in self.sents]
        self.hall, self.excl = [], []
        self._vistos = set()

    # ---------- helpers ----------
    def _frase(self, pos):
        """Oración (máx. 400 caracteres) que contiene la posición; sirve de evidencia."""
        j = bisect.bisect_right(self._sini, pos) - 1
        if j < 0:
            return self.dm.strip()[:400]
        a, b = self.sents[j]
        return self.dm[a:b].strip()[:400]

    def _prev(self, k, n=1):
        """Token n posiciones antes de k, o None."""
        return self.toks[k - n] if k - n >= 0 else None

    def _limite(self, tok):
        """True si el token es puntuación que corta la ventana de contexto."""
        return tok["t"] in _PUNT

    def _hay(self, k, valores, atras=2, adelante=0):
        """True si algún token de `valores` está en la ventana (atrás/adelante) de k sin cruzar puntuación."""
        for d in range(1, atras + 1):
            p = self._prev(k, d)
            if p is None or self._limite(p):
                break
            if p["l"] in valores:
                return True
        for d in range(1, adelante + 1):
            if k + d < len(self.toks):
                q = self.toks[k + d]
                if self._limite(q):
                    break
                if q["l"] in valores:
                    return True
        return False

    def _condicional(self, k):
        """True si «si» aparece hasta 8 tokens antes sin cruzar puntuación: cláusula condicional, no narra al PJ."""
        for d in range(1, 9):
            p = self._prev(k, d)
            if p is None or self._limite(p):
                return False
            if p["l"] == "si":
                return True
        return False

    def _ventana_der(self, k, n=7):
        """Tokens normalizados a la derecha de k (hasta n) sin cruzar puntuación."""
        out = []
        for d in range(1, n + 1):
            if k + d >= len(self.toks):
                break
            t = self.toks[k + d]
            if self._limite(t):
                break
            out.append(t["n"])
        return out

    def _ventana_oracion(self, pos, n_tok_centro, radio=7):
        """Tokens normalizados dentro de ±radio del token central, restringidos a su oración."""
        a = max(0, n_tok_centro - radio)
        b = min(len(self.toks), n_tok_centro + radio + 1)
        j = bisect.bisect_right(self._sini, pos) - 1
        oa, ob = self.sents[j] if j >= 0 else (0, len(self.dm))
        return [t["n"] for t in self.toks[a:b] if oa <= t["i"] < ob]

    def _explicito(self, k):
        """True si hay «tú» como sujeto explícito junto al verbo (3 tokens antes o 2 después)."""
        for d in range(1, 4):
            p = self._prev(k, d)
            if p is None or self._limite(p):
                break
            if p["l"] == "tú":
                return True
        for d in range(1, 3):
            if k + d < len(self.toks):
                q = self.toks[k + d]
                if self._limite(q):
                    break
                if q["l"] == "tú":
                    return True
        return False

    # ---------- emisión ----------
    def _bloqueo(self, ini, k):
        """Motivo por el que la posición no se analiza (zona de cita, fuera de personaje, pregunta o condicional), o None."""
        z = _zona_de(ini, self.zonas)
        if z:
            return z
        if k is not None and self._condicional(k):
            return "condicional"
        return None

    def _excluir(self, motivo, lema, cat_pot, ini, fin, k, via=None):
        """Registra una exclusión con su motivo (y vía); lo entrecomillado se descarta sin registrar."""
        z = self._bloqueo(ini, k)
        if z == "cita":
            return
        e = {"motivo": z or motivo, "verbo_lema": lema, "categoria_potencial": cat_pot,
             "evidencia": self._frase(ini), "inicio": ini, "fin": fin}
        if via and not z:
            e["via"] = via
        self.excl.append(e)

    def _clausula(self, ini, fin):
        """(a, b) de la cláusula (u oración, según config) del DM que contiene el disparador."""
        if self.cfg["ambito_contenido"] == "oracion":
            j = bisect.bisect_right(self._sini, ini) - 1
            return self.sents[j] if j >= 0 else (0, len(self.dm))
        cortes = ",;:.!?…\n—¿¡()«»\""
        a = max([self.dm.rfind(c, 0, ini) for c in cortes]) + 1
        hasta = [self.dm.find(c, fin) for c in cortes]
        hasta = [h for h in hasta if h >= 0]
        return a, (min(hasta) if hasta else len(self.dm))

    def _palabras_contenido(self, ini, fin):
        """lemas de contenido (ni función ni verbo del léxico) de la cláusula (u oración) del DM."""
        a, b = self._clausula(ini, fin)
        out = []
        for w in re.findall(r"\w+", _plano(self.dm[a:b])):
            if (len(w) < 3 or w in _L["stop"] or w.endswith("mente") or w.isdigit() or w in _L["t2"]
                    or w in _L["t3"] or w in _L["t3pl"] or w in _L["inf_ger"] or w in _L["part"]):
                continue
            out.append(w)
        return out

    def _emitir(self, cat, conf, lema, ini, fin, k, persona, explicito=False, cuerpo=False):
        """Emite un hallazgo (o una exclusión): decide `declarada` según la categoría, deduplica por (categoría, posición) y las acciones declaradas pasan a exclusiones."""
        z = self._bloqueo(ini, k)
        if z:
            if z != "cita":
                self.excl.append({"motivo": z, "verbo_lema": lema, "categoria_potencial": cat,
                                  "evidencia": self._frase(ini), "inicio": ini, "fin": fin})
            return
        via = None
        if cat == "ACCION":
            via = self.decl.via_accion(lema, cuerpo, self._palabras_contenido(ini, fin) if self.cfg["contenido"] else [])
            decl = via is not None
        else:
            decl = self.decl.cubre(lema, cat)
            via = ("cita" if (cat == "HABLA" and self.decl.cita and not self.decl.cubre(lema)) else "verbo") if decl else None
        if cat == "ACCION" and decl:
            self.excl.append({"motivo": "declarada", "via": via, "verbo_lema": lema, "categoria_potencial": cat,
                              "evidencia": self._frase(ini), "inicio": ini, "fin": fin})
            return
        clave = (cat, ini)
        if clave in self._vistos:
            return
        self._vistos.add(clave)
        self.hall.append({
            "categoria": "ACCION_NO_DECLARADA" if cat == "ACCION" else cat,
            "confianza": conf, "verbo_lema": lema, "evidencia": self._frase(ini),
            "inicio": ini, "fin": fin, "tirada_declarada": self.decl.tirada, "declarada": decl,
            "via_declarada": via, "persona": persona, "explicito": bool(explicito)})

    # ---------- reglas por tipo de entrada ----------
    def _resolver(self, ent, k, ini, fin, persona, explicito, reflexivo, ventana_sujeto_fin=None):
        """aplica la política de la categoría a un verbo candidato en toks[k]."""
        cat, lema = ent["cat"], ent["lema"]
        if cat in ("PERCEPCION", "INVOLUNTARIO"):
            self._excluir(cat.lower(), lema, cat, ini, fin, k)
            return
        if cat == "RED":
            self._excluir("red_amplia", lema, "MENTAL", ini, fin, k)
            return
        if cat == "SENTIR":
            win = self._ventana_der(k)
            emo = any(_es_nombre(n, _L["emo"]) for n in win)
            sens = any(_es_nombre(n, _L["sens"]) for n in win)
            if emo:
                self._emitir("EMOCION", "alta", "sentirse" if reflexivo else "sentir", ini, fin, k, persona, explicito)
            elif reflexivo and not sens:
                self._emitir("EMOCION", "media", "sentirse", ini, fin, k, persona, explicito)
            else:
                self._excluir("sensorial" if sens else "sentir_sin_emocion", "sentir", "EMOCION", ini, fin, k)
            return
        if cat == "TENER":
            win = self._ventana_der(k, 4)
            if win and win[0] == "que":
                return
            if any(_es_nombre(n, _L["emo"]) for n in win):
                self._emitir("EMOCION", "alta", "tener", ini, fin, k, persona, explicito)
            elif any(_es_nombre(n, _L["pens"]) for n in win):
                self._emitir("COGNICION", "media", "tener", ini, fin, k, persona, explicito)
            elif any(_es_nombre(n, _L["sens"]) for n in win):
                self._excluir("sensorial", "tener", "EMOCION", ini, fin, k)
            return
        if lema in ("querer", "desear", "preferir") and self._hay(k, {"que", "como", "cuanto", "donde", "cuando"}, atras=3):
            # «lo que quieres», «como quieres»: relativa/modo, no decisión narrada
            if self._hay(k, {"lo", "como", "cuanto", "donde", "cuando"}, atras=3):
                self._excluir("relativa", lema, cat, ini, fin, k)
                return
        if cat == "ACCION" and lema in ("intentar", "seguir"):
            # perífrasis: el núcleo es el infinitivo/gerundio que sigue; si el jugador declaró ESE verbo
            # (o un sinónimo), la perífrasis es eco de lo declarado, no usurpación
            for d in range(1, 4):
                if k + d >= len(self.toks) or self._limite(self.toks[k + d]):
                    break
                heads = _L["inf_ger" if self.cfg["residuales_v2b"] else "inf_ger_v1"].get(self.toks[k + d]["n"])
                if heads:
                    if any(self.decl.cubre(h, "ACCION" if self.cfg["residuales_v2b"] else None) for h in heads):
                        self._excluir("declarada", lema, cat, ini, fin, k, via="nucleo")
                        return
                    break
        if cat == "ACCION" and self.cfg["residuales_v2b"]:
            a, b = self._clausula(ini, fin)
            texto = _plano(self.dm[a:b])
            if any(m in texto for m in _L["marc_invol"]):
                # «golpeas accidentalmente el tintero»: consecuencia involuntaria, no acción declarable
                self._excluir("involuntario", lema, cat, ini, fin, k, via="marcador")
                return
            if lema == "volver":
                sig = self.toks[k + 1]["n"] if k + 1 < len(self.toks) else ""
                if sig not in ("a", "hacia", "atras", "sobre", "al", "para", "por", "junto", "con", "de"):
                    # «te vuelves invisible»: cambio de estado, no desplazamiento
                    self._excluir("involuntario", lema, cat, ini, fin, k, via="cambio_de_estado")
                    return
        conf = "media" if (cat == "ACCION" or ent["media"]) else "alta"
        self._emitir(cat, conf, lema, ini, fin, k, persona, explicito)

    # ---------- segunda persona ----------
    def _nominal(self, k, tok):
        """True si la forma ambigua (dudas, notas...) se lee como sustantivo/adjetivo."""
        if tok["n"] not in _L["ambig"]:
            return False
        p = self._prev(k)
        if p is None or self._limite(p):
            return False
        return p["l"] not in _L["inicio"]

    def _segunda(self):
        """Busca verbos en 2.ª persona del singular (tablas léxicas; spaCy solo como respaldo), descartando «me/nos dices» y formas nominales, y delega en locuciones y partes del cuerpo."""
        toks = self.toks
        for k, tok in enumerate(toks):
            ents = _L["t2"].get(tok["n"])
            if not ents and tok["p2"] and tok["lem"] in _L["por_lema_plano"]:
                # los verbos «solo declaración» (cat DECL) no tienen tablas: no pueden generar hallazgos
                ents = [e for e in _L["por_lema_plano"][tok["lem"]] if e["cat"] != "DECL"]
            if not ents:
                continue
            p = self._prev(k)
            if p is not None and p["l"] in ("me", "nos"):
                continue        # «me dices...»: voz en 1.ª persona (PNJ), no narración al PJ
            if self._nominal(k, tok):
                continue
            reflexivo = self._hay(k, {"te"}, atras=2)
            explicito = self._explicito(k)
            for ent in ents:
                if ent["te"] and not reflexivo:
                    continue
                if ent["nte"] and reflexivo:
                    continue
                lema = ent["lema"]
                ini, fin = tok["i"], tok["e"]
                if ent["cat"] == "COGNICION" and lema == "preguntar":
                    lema = "preguntarse"
                # perífrasis con locuciones especiales
                self._resolver(ent if lema == ent["lema"] else dict(ent, lema=lema), k, ini, fin, "2",
                               explicito, reflexivo)
            # extras que dependen del verbo (locuciones)
        self._locuciones_2()
        self._parte_cuerpo()

    def _locuciones_2(self):
        """Locuciones y estructuras de 2.ª persona que no son un verbo simple: darse cuenta, dar un paso, se te ocurre, perfecto compuesto, impacto con «te» y patrones regex."""
        toks, n = self.toks, len(self.toks)
        for k, tok in enumerate(toks):
            nn = tok["n"]
            # te das cuenta / te diste cuenta / caes en la cuenta / te has dado cuenta
            if nn in _DAR2 and k + 1 < n and toks[k + 1]["n"] == "cuenta":
                ini = toks[k - 1]["i"] if k and toks[k - 1]["l"] == "te" else tok["i"]
                self._emitir("COGNICION", "alta", "darse cuenta", ini, toks[k + 1]["e"], k, "2", self._explicito(k))
            elif nn == "dado" and k + 1 < n and toks[k + 1]["n"] == "cuenta" and self._prev(k) and self._prev(k)["n"] in _HAS:
                self._emitir("COGNICION", "alta", "darse cuenta", self._prev(k)["i"], toks[k + 1]["e"], k, "2", False)
            elif nn in ("caes", "caiste") and k + 3 < n and [toks[k + j]["n"] for j in (1, 2, 3)] == ["en", "la", "cuenta"]:
                self._emitir("COGNICION", "alta", "darse cuenta", tok["i"], toks[k + 3]["e"], k, "2", False)
            # das un paso / das media vuelta / te das la vuelta
            if nn in _DAR2 and k + 2 < n:
                sig = (toks[k + 1]["n"], toks[k + 2]["n"])
                if sig in (("un", "paso"), ("unos", "pasos"), ("media", "vuelta"), ("la", "vuelta"),
                           ("un", "salto"), ("un", "giro"), ("otro", "paso")):
                    ini = toks[k - 1]["i"] if k and toks[k - 1]["l"] == "te" else tok["i"]
                    self._emitir("ACCION", "media", "dar un paso", ini, toks[k + 2]["e"], k, "2", self._explicito(k))
            # se te ocurre
            if nn == "se" and k + 2 < n and toks[k + 1]["n"] == "te" and toks[k + 2]["n"] in (
                    "ocurre", "ocurren", "ocurrio", "ocurrieron", "ocurria"):
                self._emitir("COGNICION", "alta", "ocurrírsele", tok["i"], toks[k + 2]["e"], k, "2", False)
            # perfecto compuesto: has decidido, te habías dado...
            if nn in _HAS and k + 1 < n:
                ent = _L["part"].get(toks[k + 1]["n"])
                if ent is not None and ent["cat"] in ("VOLICION", "COGNICION", "EMOCION", "HABLA", "ACCION"):
                    reflexivo = self._hay(k, {"te"}, atras=1)
                    if ent["te"] and not reflexivo:
                        continue
                    self._resolver(ent, k, tok["i"], toks[k + 1]["e"], "2", self._explicito(k), reflexivo)
            # red amplia (solo estrato de falsos negativos): te gusta / te sorprende / te parece...
            if nn in _L["red_te"] and self._hay(k, {"te"}, atras=2, adelante=2):
                self._excluir("red_amplia", nn, "MENTAL", tok["i"], tok["e"], k)
            # impacto con «te» (te invade el miedo / te asusta)
            if nn in _L["imp_sust"] or nn in _L["imp_dir"]:
                if self._hay(k, {"te"}, atras=2, adelante=2) and not self._hay(k, {"que"}, atras=1):
                    self._impacto(k, tok)
        self._patrones_regex()

    def _parte_cuerpo(self):
        """«Tus dedos recorren el metal», «Tu mano se cierra...»: acción del PJ narrada con una parte
        motora de su cuerpo como sujeto (3.ª persona gramatical, agente = el PJ). Se trata como
        ACCION (media) y sigue la misma regla de «declarada»; reflejos involuntarios se excluyen."""
        toks, n = self.toks, len(self.toks)
        for k, tok in enumerate(toks):
            if tok["l"] not in ("tu", "tus") or k + 2 >= n:
                continue
            if toks[k + 1]["n"] not in _L["cuerpo"]:
                continue
            j = k + 2
            while j < n and j <= k + 4 and (toks[j]["n"] in ("se", "ya", "no", "apenas", "solo", "lentamente")
                                          or toks[j]["n"].endswith("mente")):
                j += 1
            if j >= n or self._limite(toks[j]):
                continue
            vt = toks[j]
            for ent in list(_L["t3"].get(vt["n"], ())) + list(_L["t3pl"].get(vt["n"], ())):
                if ent["cat"] == "ACCION":
                    self._emitir("ACCION", "media", ent["lema"], tok["i"], vt["e"], j, "2", False, cuerpo=True)
                elif ent["cat"] == "INVOLUNTARIO":
                    self._excluir("involuntario", ent["lema"], "INVOLUNTARIO", tok["i"], vt["e"], j)
                break

    def _impacto(self, k, tok):
        """Clasifica verbos de impacto con «te» («te invade el miedo») según el sustantivo de su oración: emoción, cognición o sensorial (excluido)."""
        nn = tok["n"]
        ini, fin = tok["i"], tok["e"]
        # ampliar el disparador para incluir «te» adyacente
        for d in (1, 2):
            p = self._prev(k, d)
            if p is not None and p["l"] == "te":
                ini = p["i"]
        if nn in _L["imp_dir"]:
            self._emitir("EMOCION", "media", nn, ini, fin, k, "2", False)
            return
        lema = next((inf for r, inf in sorted(_L["imp_lemas"], key=lambda x: -len(x[0])) if nn.startswith(r)), nn)
        if nn in ("da", "dan", "dio", "daba"):
            lema = "dar"
        win = self._ventana_oracion(tok["i"], k)
        if any(_es_nombre(n, _L["emo"]) for n in win):
            self._emitir("EMOCION", "alta", lema, ini, fin, k, "2", False)
        elif any(_es_nombre(n, _L["pens"]) for n in win if n not in ("sensacion", "impresion")):
            self._emitir("COGNICION", "alta", lema, ini, fin, k, "2", False)
        elif any(_es_nombre(n, _L["sens"]) for n in win):
            self._excluir("sensorial", lema, "EMOCION", ini, fin, k)

    def _patrones_regex(self):
        """locuciones sobre texto 'plano' (misma longitud que el original)."""
        pl = _plano(self.dm)
        patrones = [
            (r"\bte\s+(?:viene|vienen|vino|vinieron)\s+a\s+la\s+(?:mente|cabeza)\b", "COGNICION", "alta", "venir a la mente"),
            (r"\bte\s+(?:cruza|cruzan|pasa|pasan|asalta|asaltan|atraviesa|atraviesan)\s+(?:por\s+)?(?:la\s+)?(?:mente|cabeza)\b",
             "COGNICION", "alta", "cruzar la mente"),
            (r"\b(?:tu\s+(?:instinto|intuicion|voz\s+interior|experiencia|sexto\s+sentido)|algo\s+(?:en|dentro\s+de)\s+ti|"
             r"una\s+voz\s+(?:en|dentro\s+de)\s+(?:tu|la)\s+(?:mente|cabeza))\s+te\s+\w+", "COGNICION", "media", "instinto_te"),
        ]
        for rx, cat, conf, lema in patrones:
            for m in re.finditer(rx, pl):
                k = self._tok_en(m.start())
                self._emitir(cat, conf, lema, m.start(), m.end(), k, "2", False)
        # emoción localizada en el PJ: sustantivo emocional + (dentro de ti | en tu pecho...).
        # «en ti» a secas se descartó tras una revisión: suele ser la emoción de un PNJ hacia el PJ
        # («una gratitud depositada en ti»), no del PJ.
        loc = re.compile(r"\b(?:dentro\s+de\s+ti|en\s+tu\s+(?:pecho|interior|corazon|estomago|mente|cabeza|garganta|vientre))\b")
        for m in loc.finditer(pl):
            j = bisect.bisect_right(self._sini, m.start()) - 1
            if j < 0:
                continue
            a, b = self.sents[j]
            palabras = re.findall(r"\w+", pl[a:b])
            if any(_es_nombre(w, _L["emo"]) for w in palabras):
                k = self._tok_en(m.start())
                self._emitir("EMOCION", "media", "en_ti", m.start(), m.end(), k, "2", False)

    def _tok_en(self, pos):
        """Índice del token que contiene la posición de carácter (None si no hay tokens)."""
        ini = [t["i"] for t in self.toks]
        j = bisect.bisect_right(ini, pos) - 1
        return max(j, 0) if self.toks else None

    # ---------- tercera persona (control positivo) ----------
    def _tercera(self):
        """Control positivo: verbos en 3.ª persona con el nombre del PJ como sujeto (tras el nombre, tolerando adverbios y «se») o antepuestos como atribución."""
        if not self.nombre_pj or not self.toks:
            return
        nm = [_plano(w) for w in self.nombre_pj.split() if w]
        variantes = [nm]
        if len(nm) > 1 and len(nm[0]) >= 4:
            variantes.append(nm[:1])
        toks, n = self.toks, len(self.toks)
        usados = set()
        for k in range(n):
            for v in variantes:
                L = len(v)
                if k + L > n or [toks[k + j]["n"] for j in range(L)] != v:
                    continue
                if _zona_de(toks[k]["i"], self.zonas) == "cita":
                    continue
                fin_nombre = k + L - 1
                # verbo DESPUÉS del nombre (tolera adverbios/«se»)
                j = fin_nombre + 1
                saltados = 0
                while j < n and saltados <= 3 and (toks[j]["n"] in _L["gap"] or toks[j]["n"].endswith("mente")):
                    j += 1
                    saltados += 1
                if j < n and not self._limite(toks[j]):
                    self._verbo_3(toks, j, fin_nombre, usados)
                # verbo ANTES del nombre (atribución: «murmura Osric»)
                if k >= 1 and not self._limite(toks[k - 1]):
                    self._verbo_3(toks, k - 1, k - 1, usados, antepuesto=True)

    def _verbo_3(self, toks, j, ref, usados, antepuesto=False):
        """Resuelve el verbo en 3.ª persona en toks[j] (una sola vez por token) para el nombre del PJ."""
        tok = toks[j]
        ents = _L["t3"].get(tok["n"])
        if not ents or j in usados:
            return
        usados.add(j)
        reflexivo = any(t["n"] == "se" for t in toks[ref + 1:j])
        for ent in ents:
            if antepuesto and ent["cat"] not in ("HABLA", "COGNICION"):
                continue
            if ent["te"] and not reflexivo:
                continue
            if ent["nte"] and reflexivo:
                continue
            self._resolver(ent, j, tok["i"], tok["e"], "3", False, reflexivo)

    def correr(self):
        """Ejecuta el análisis en 2.ª y 3.ª persona y devuelve (hallazgos, exclusiones) ordenados por posición."""
        if not self.dm.strip():
            return [], []
        self._segunda()
        self._tercera()
        self.hall.sort(key=lambda h: (h["inicio"], h["categoria"]))
        self.excl.sort(key=lambda h: (h["inicio"], h["motivo"]))
        return self.hall, self.excl


# ══════════════════════════ API pública ══════════════════════════

def analizar_completo(dm_texto, accion_jugador, nlp, nombre_pj=None, config=None):
    """(hallazgos, excluidos). 'excluidos' documenta qué se descartó y por qué
    (percepcion, involuntario, sensorial, declarada, pregunta, condicional, ooc,
    relativa, red_amplia, sentir_sin_emocion); no incluye lo entrecomillado."""
    return _Analisis(dm_texto, accion_jugador, nlp, nombre_pj, config).correr()


def detectar_usurpacion(dm_texto, accion_jugador, nlp, nombre_pj=None, config=None):
    """Solo los hallazgos de `analizar_completo`; API del instrumento."""
    return analizar_completo(dm_texto, accion_jugador, nlp, nombre_pj, config)[0]


# ══════════════════════════ muerte del PJ ══════════════════════════

_MUERTE_2 = re.compile(
    r"\b(?:mueres|has muerto|has fallecido|estas muert[oa]|caes muert[oa]|caes sin vida|pierdes la vida|"
    r"falleces|expiras|sucumbes|te desplomas (?:muert[oa]|sin vida)|yaces (?:sin vida|muert[oa])|"
    r"exhalas (?:tu )?(?:ultimo|postrer) (?:aliento|suspiro)|tu ultimo aliento|"
    r"tu (?:corazon|vida) (?:se detiene|se apaga|deja de latir|se extingue)|tu cuerpo (?:cae|yace) sin vida|"
    r"tu cadaver)\b")
_MUERTE_3 = ("(?:ha muerto|muere|murio|cae muert[oa]|cae sin vida|fallece|fallecio|perece|perecio|"
             "pierde la vida|yace (?:sin vida|muert[oa])|expira|expiro|sucumbe|sucumbio|"
             "exhala su ultimo (?:aliento|suspiro)|esta muert[oa]|se desploma (?:muert[oa]|sin vida))")
_PRE_NO = re.compile(r"(?:\bsi\b|\bcasi\b|a punto de|\bpodrias\b|\bpuedes\b|\bpodras\b|quizas|tal vez|\btemes\b|"
                     r"\bcomo si\b|\bimaginas\b|\bsuenas\b|\bno\s+(?:\w+\s+)?|\bnunca\b|\bjamas\b|\bcuando\b\s+\w+\s+\w+\s+\w+)\s*$")
_POST_HIPERBOLE = re.compile(r"^\s+de\s+(?:ganas|risa|hambre|sed|frio|miedo|curiosidad|verguenza|envidia|celos|"
                             r"aburrimiento|cansancio|impaciencia|sueno|amor|pena|calor|dolor|nervios)\b")


def narra_muerte_pj(dm_texto, nlp, nombre_pj=None):
    """dict del primer pasaje que narra la muerte del PJ, o None. Léxico-regex: nlp no se usa
    (se acepta por uniformidad de firma; la precisión de estas locuciones no gana con el parser)."""
    if not dm_texto or not dm_texto.strip():
        return None
    pl = _plano(dm_texto)
    zonas = _zonas(dm_texto)
    sents = _oraciones(dm_texto)
    sini = [a for a, _ in sents]
    candidatos = [(m, "2") for m in _MUERTE_2.finditer(pl)]
    if nombre_pj:
        nm = [re.escape(_plano(w)) for w in nombre_pj.split() if w]
        nombres = [r"\s+".join(nm)]
        if len(nm) > 1 and len(nm[0]) >= 4:
            nombres.append(nm[0])
        for nombre in nombres:
            rx = re.compile(rf"\b{nombre}\s+{_MUERTE_3}\b")
            candidatos += [(m, "3") for m in rx.finditer(pl)]
    for m, persona in sorted(candidatos, key=lambda x: x[0].start()):
        if _zona_de(m.start(), zonas) is not None:
            continue
        j = bisect.bisect_right(sini, m.start()) - 1
        a = sents[j][0] if j >= 0 else 0
        pre = pl[a:m.start()]
        # se corta al último signo de cláusula para no arrastrar negaciones lejanas
        pre = re.split(r"[,;:—]", pre)[-1]
        if _PRE_NO.search(pre):
            continue
        if _POST_HIPERBOLE.match(pl[m.end():m.end() + 20]) or (persona == "2" and pl[m.start():m.end()] == "mueres"
                                                              and _POST_HIPERBOLE.match(pl[m.end():m.end() + 20])):
            continue
        b = sents[j][1] if j >= 0 else len(dm_texto)
        return {"categoria": "MUERTE_PJ", "confianza": "alta", "verbo_lema": "morir",
                "evidencia": dm_texto[a:b].strip()[:400], "inicio": m.start(), "fin": m.end(),
                "tirada_declarada": False, "declarada": False, "persona": persona,
                "explicito": False}
    return None
