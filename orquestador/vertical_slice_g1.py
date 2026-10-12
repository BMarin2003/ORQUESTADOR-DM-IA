r"""
VERTICAL SLICE G1 — un turno completo del brazo multiagente, de punta a
punta. Hermano de vertical_slice.py (G2, monolítico): mismo jugador,
mismos dados, mismo extractor, mismos chequeos de turn_validation -- lo
único que cambia es CÓMO se produce `narracion`, que aquí no la escribe
un solo DM sino cinco roles separados:

    estado (Postgres)
      → JUGADOR agéntico          (compartido con G2)
        → dados deterministas     (compartido con G2)
          → ROUTER                determinista, sin LLM (orquestador/router.py)
            → ÁRBITRO             código + LLM solo si hace falta juicio
              → ACTOR(ES)         un LLM por PNJ que responde (get_persona)
                → MUNDO           código + LLM solo si hay boceto/semilla
                  → NARRADOR      el único que escribe prosa
                    → EXTRACTOR   (compartido con G2)
                      → apply_delta / propagate_from_delta / plantar_semilla
                        → estado nuevo

Primera corrida real de este script: a diferencia de vertical_slice.py
(que ya pasó por varias pasadas de bugs encontrados en producción, ver
"QM - Respaldo bibliografico instrumentos deterministicos.md"), esto es
la primera vez que los cinco roles se conectan de punta a punta con datos
reales -- es esperable encontrar bugs de integración en los primeros
turnos, igual que pasó con G2 la primera vez.

Uso:
  py orquestador\vertical_slice_g1.py --campaign-id <UUID> --pj PJ01 --turnos 5
  py orquestador\vertical_slice_g1.py --campaign-id <UUID> --pj PJ01 --turnos 3 --seco
"""

import argparse
import json
import os
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

# Windows usa cp1252 en stdout/stderr cuando no hay consola adjunta (p. ej.
# Start-Process con -RedirectStandardOutput a un archivo): cualquier
# carácter fuera de latin-1 -- una tilde ya sobrevive como mojibake, pero
# "✓"/"✗" no tienen ni siquiera esa aproximación -- revienta con
# UnicodeEncodeError y tumba la corrida entera a mitad de turno. Mismo
# fix ya aplicado en fixtures/generar_seed.py por el mismo motivo, y en el
# gemelo vertical_slice.py (G2). Bug real encontrado en Par 07-17
# (2026-09-18): 11 corridas lanzadas con Start-Process cayeron así,
# algunas a mitad del primer turno.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent


def _slug(texto):
    """Título de campaña -> slug para nombres de archivo autodescriptivos.

    "Par 02 · G1 (Multiagente) · Vela Honda" -> "par_02_multiagente_vela_honda".
    Sin acentos, sin separadores raros, todo en minúscula. Ver punto 30 de
    la bitácora QM.
    """
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w]+", "_", s).strip("_").lower()
    return s or "sin_titulo"
sys.path.insert(0, str(RAIZ / "jugador"))
sys.path.insert(0, str(RAIZ / "orquestador"))
import dados          # noqa: E402
import db as bd        # noqa: E402
import router as rtr    # noqa: E402
import arbitro as arb   # noqa: E402
import mundo as mun     # noqa: E402

BASE = "https://api.deepinfra.com/v1/openai"
MODELO_DM = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")
# Jugador migrado a Gemma (2026-09-17, decisión del usuario) -- mismo
# criterio y mismo cambio que en vertical_slice.py (G2), ver el comentario
# largo ahí para el detalle completo. Simétrico en ambos brazos, así que
# no afecta la comparación G1 vs G2 (el jugador siempre fue y sigue siendo
# idéntico en los dos), solo corrige que el costo total esté dominado por
# el agente de soporte en vez de por la arquitectura bajo estudio.
MODELO_JUGADOR = os.environ.get("DMIA_MODELO_JUGADOR",
                                "google/gemma-4-31B-it")

# Precios reales (USD por 1M tokens), tarifa estándar de DeepInfra -- ver
# el mismo comentario en vertical_slice.py (G2). El jugador usa un modelo
# distinto (y más caro) que los 6 roles restantes de G1, que comparten
# MODELO_DM -- sumar todo bajo una sola tarifa subestimaba el costo real.
# Verificado 2026-09-17 contra el reporte de uso real de la cuenta
# (deepinfra-usage-2026-09.csv): Hermes $0.70/$0.70, Gemma $0.13/$0.38.
PRECIOS_USD_POR_1M = {
    "google/gemma-4-31B-it": (0.13, 0.38),
    "NousResearch/Hermes-3-Llama-3.1-70B": (0.70, 0.70),
}
PRECIO_DEFECTO = (0.09, 0.34)  # respaldo si el modelo no está en la tabla

PENSAMIENTO = re.compile(r"<think>.*?</think>", re.S | re.I)
VALLA = re.compile(r"^\s*```[a-z]*\s*$", re.M)

# Vocabulario válido de entity_type (ver id_de() en db.py) más los
# sinónimos en español que ya se vieron en producción viniendo del LLM de
# Mundo -- ese prompt no fuerza el vocabulario exacto tan estrictamente
# como el contrato del extractor (corregido en dm/prompt_mundo_g1.md,
# 2026-09-11), así que esto queda como red de seguridad para no perder una
# corrida entera de 200 turnos por un solo delta mal etiquetado.
ENTITY_TYPES_VALIDOS = {"npc", "location", "faction", "quest",
                        "character", "world"}
SINONIMOS_ENTITY_TYPE = {
    "lugar": "location", "ubicacion": "location", "ubicación": "location",
    "personaje": "character", "pj": "character",
    "faccion": "faction", "facción": "faction",
    "mision": "quest", "misión": "quest",
    "pnj": "npc",
    "mundo": "world",
}


def normalizar_entity_type(valor):
    """Minúsculas + sinónimo conocido, o el valor normalizado tal cual si
    no hay sinónimo (para que quien llama pueda decidir qué hacer con un
    tipo genuinamente desconocido, en vez de que esto decida por él)."""
    tipo = (valor or "").strip().lower()
    return SINONIMOS_ENTITY_TYPE.get(tipo, tipo)


# ─────────────────────────────────────────────────────────────────────────
# Piezas idénticas a vertical_slice.py (deliberadamente NO importadas desde
# allá para no arriesgar el script de G2 ya validado con un refactor de
# última hora -- duplicado, no reutilizado, a propósito. Si diverge de su
# gemelo en el futuro, hay que corregir ambos lados a mano.)
# ─────────────────────────────────────────────────────────────────────────

def jaccard_palabras(a, b):
    wa = set(re.findall(r"\w+", a.lower()))
    wb = set(re.findall(r"\w+", b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


_VOCALES_ES = "aeiouáéíóúü"
_RE_GRUPO_VOCALICO = re.compile(f"[{_VOCALES_ES}]+")


def contar_silabas_es(palabra):
    grupos = _RE_GRUPO_VOCALICO.findall(palabra.lower())
    return max(1, len(grupos))


def fernandez_huerta(texto):
    palabras = re.findall(r"[a-záéíóúñü]+", texto.lower())
    frases = [f for f in re.split(r"[.!?]+", texto) if f.strip()]
    if not palabras or not frases:
        return None
    silabas = sum(contar_silabas_es(p) for p in palabras)
    palabras_por_frase = len(palabras) / len(frases)
    L = 206.84 - 60 * (silabas / len(palabras)) - 1.02 * palabras_por_frase
    return round(L, 2)


def entidades_conocidas(ents, pj_nombre):
    conocidos = set()
    for nombre in [e["nombre"] for e in ents] + [pj_nombre]:
        conocidos.add(nombre)
        conocidos.update(p for p in nombre.split() if len(p) >= 3)
    return conocidos


def entidad_grafo_densidad(texto, conocidos):
    frases = [f for f in re.split(r"[.!?]+", texto) if f.strip()]
    if len(frases) < 2:
        return None
    entidades_por_frase = []
    for frase in frases:
        presentes = {tok for tok in conocidos
                     if re.search(rf"\b{re.escape(tok)}\b", frase)}
        entidades_por_frase.append(presentes)
    n = len(frases)
    posibles = n * (n - 1) // 2
    aristas = sum(
        1
        for i in range(n)
        for j in range(i + 1, n)
        if entidades_por_frase[i] & entidades_por_frase[j]
    )
    return round(aristas / posibles, 3) if posibles else None


def llamar(modelo, system, user, max_tokens=600, temp=0.8, json_mode=False):
    key = os.environ.get("DEEPINFRA_API_KEY")
    cuerpo = {"model": modelo,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}],
              "temperature": temp, "max_tokens": max_tokens,
              "chat_template_kwargs": {"enable_thinking": False}}
    if json_mode:
        cuerpo["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"}, method="POST")
    t0 = time.time()

    def _post(peticion, reintentos=4, espera=10, max_sobrecarga=30):
        intento = 0
        sobrecarga = 0
        while True:
            try:
                with urllib.request.urlopen(peticion, timeout=300) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                # Idéntico a vertical_slice.py (G2) -- mismo bug, mismo
                # fix, para no romper la comparación entre brazos. Ver
                # el comentario largo en el gemelo de G2 para el
                # detalle completo de por qué hacía falta (incluido el
                # reintento de 429/502/503/504 agregado en Par 07-17,
                # 2026-09-18: engine_overloaded tumbó ~20 corridas).
                if e.code in (429, 502, 503, 504) and sobrecarga < max_sobrecarga:
                    sobrecarga += 1
                    pausa = min(300, 10 * 2 ** min(sobrecarga - 1, 5)) + random.uniform(0, 10)
                    print(f"    (HTTP {e.code}, modelo saturado: reintento "
                          f"{sobrecarga}/{max_sobrecarga} en {pausa:.0f}s)",
                          file=sys.stderr)
                    time.sleep(pausa)
                    continue
                raise
            except (TimeoutError, urllib.error.URLError) as e:
                intento += 1
                if intento >= reintentos:
                    raise
                print(f"    (red: {e!r}, reintento {intento}/{reintentos} "
                      f"en {espera}s)", file=sys.stderr)
                time.sleep(espera)
                espera *= 2

    try:
        d = _post(req)
    except urllib.error.HTTPError as e:
        det = e.read().decode()[:200]
        if any(k in det for k in ("chat_template_kwargs", "response_format")) or e.code == 422:
            cuerpo.pop("chat_template_kwargs", None)
            cuerpo.pop("response_format", None)
            req = urllib.request.Request(
                f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"}, method="POST")
            d = _post(req)
        else:
            print(f"    HTTP {e.code}: {det}", file=sys.stderr)
            return None
    txt = VALLA.sub("", PENSAMIENTO.sub("", d["choices"][0]["message"]["content"] or "")).strip()
    u = d.get("usage", {})
    return {"texto": txt, "tin": u.get("prompt_tokens") or 0,
            "tout": u.get("completion_tokens") or 0,
            "ms": round((time.time() - t0) * 1000)}


def parsear_json(texto):
    limpio = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    try:
        return json.loads(limpio)
    except Exception:
        m = re.search(r"\{.*\}", limpio, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def paso(n, titulo):
    print(f"\n### [{n}] {titulo}\n")


def ficha_jugador(pj):
    p = pj["personalidad"]
    def b(v, neg, pos):
        return neg if v < -40 else pos if v > 40 else "equilibrado"
    def bd_(v):
        if v <= 30:
            return ("Si el DM plantea algo urgente, VAS. Atiendes primero lo "
                    "que se te pide.")
        if v <= 60:
            return "Atiendes lo urgente, pero te tomas un momento para lo tuyo."
        return "Lo urgente del DM es una opción más. Lo tuyo va primero."
    t = f"""TU FICHA
  {pj['nombre']}, {pj['arquetipo'].lower()}. {pj['clase']} nivel {pj['nivel']}.
    trato        {b(p['warmth'], 'frío y calculador', 'cálido y afectuoso')}
    franqueza    {b(p['candor'], 'disimulado', 'franco')}
    principios   {b(p['principle'], 'pragmático', 'principista')}
    temple       {b(p['boldness'], 'cauto', 'audaz')}

TUS OBJETIVOS PROPIOS
""" + "\n".join(f"  - {o}" for o in pj["agenda"]) + f"""

CÓMO TE TOMAS LO QUE EL DM PLANTEA
  {bd_(pj['desvio'])}
"""
    ej = pj.get("ejemplares")
    if ej:
        t += f"""
ASÍ JUEGAS TÚ
  Cuando te piden algo urgente:   {ej['urgente']}
  Cuando ves algo tuyo:           {ej['propio']}
  Cuando no pasa nada:            {ej['vacia']}
"""
    return t


def ficha_pnj_actor(persona):
    """Texto de la ficha completa que recibe el Actor (dm/prompt_actor_g1.md)
    -- traduce lo que devuelve db.get_persona() a la forma que el prompt
    describe: los 4 ejes, los rasgos ricos, IBF, conocimiento hasta este
    turno, y sus secretos CON contenido (el Actor sí los conoce)."""
    n = persona["npc"]
    ibf = persona["ibf"] or {}
    disp = persona["disposicion"] or {}
    t = [f"TU FICHA — {n['name']} ({n.get('species') or 'sin especie declarada'}"
         f", {n.get('social_role') or 'sin rol social declarado'})",
         f"  ejes: warmth={n['warmth']} candor={n['candor']} "
         f"principle={n['principle']} boldness={n['boldness']}"]
    if n.get("traits"):
        t.append(f"  rasgos: {', '.join(n['traits'])}")
    if n.get("internal_contradiction"):
        t.append(f"  contradicción interna: {n['internal_contradiction']}")
    if n.get("taboos"):
        t.append(f"  tabúes: {', '.join(n['taboos'])}")
    if n.get("voice_notes"):
        t.append(f"  voz: {n['voice_notes']}")
    if n.get("stated_desire"):
        t.append(f"  dice querer: {n['stated_desire']}")
    if n.get("actual_need"):
        t.append(f"  en realidad necesita: {n['actual_need']}")
    if n.get("fear"):
        t.append(f"  teme: {n['fear']}")
    if ibf.get("ideal_text"):
        t.append(f"  ideal: {ibf['ideal_text']}")
    if ibf.get("bond_text"):
        t.append(f"  vínculo: {ibf['bond_text']} (fuerza {ibf.get('bond_strength')})")
    if ibf.get("flaw_text"):
        t.append(f"  defecto: {ibf['flaw_text']}")
    if disp.get("banda"):
        t.append(f"  tu disposición hacia el grupo ahora mismo: {disp['banda']}")
    if persona["conocimiento"]:
        t.append("  lo que sabes hasta ahora:")
        for k in persona["conocimiento"]:
            t.append(f"    - {k['fact']}")
    if persona["secretos"]:
        t.append("  tus secretos (solo tú los conoces, revélalos SOLO si se "
                 "cumple su condición):")
        for s in persona["secretos"]:
            estado = "ya revelado" if s["revealed_at_turn"] is not None else "sin revelar"
            t.append(f"    - [{estado}] {s['content']} "
                     f"(condición: {s['reveal_condition']})")
    return "\n".join(t)


def renderizar_eventos_reloj(eventos_reloj):
    if not eventos_reloj:
        return None
    lin = []
    for ev in eventos_reloj:
        ofe = ev.get("on_fire_event") or {}
        partes_detalle = [ofe[k] for k in ("headline", "consequence") if ofe.get(k)]
        detalle = " — ".join(partes_detalle) if partes_detalle else ev.get("agenda")
        lin.append(f"{ev['faccion']} · {ev['agenda']}: {detalle}")
    return "\n".join(lin)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pj", default="PJ01")
    ap.add_argument("--turnos", type=int, default=1)
    ap.add_argument("--seco", action="store_true",
                    help="no escribe en la base; solo muestra qué haría")
    ap.add_argument("--campaign-id", required=True,
                    help="UUID de la campaña G1 a usar (no hay campaña por "
                         "defecto para este script: G1 siempre corre sobre "
                         "una campaña explícita, nunca 'la más antigua').")
    args = ap.parse_args()

    faltan = [v for v in ("DEEPINFRA_API_KEY", "DMIA_MODELO") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Falta en el entorno: {', '.join(faltan)}\n"
                 f"  DEEPINFRA_API_KEY  la clave de la API\n"
                 f"  DMIA_MODELO        p.ej. google/gemma-4-31B-it\n"
                 f"Carga el .env y comprueba que las variables tienen valor.")
    for nombre, ruta in (("prompt del jugador", RAIZ / "jugador" / "prompt.md"),
                         ("prompt del Actor G1", RAIZ / "dm" / "prompt_actor_g1.md"),
                         ("prompt del Árbitro G1", RAIZ / "dm" / "prompt_arbitro_g1.md"),
                         ("prompt del Mundo G1", RAIZ / "dm" / "prompt_mundo_g1.md"),
                         ("prompt del Narrador G1", RAIZ / "dm" / "prompt_narrador_g1.md"),
                         ("prompt del extractor", RAIZ / "extractor" / "prompt.md"),
                         ("contrato", RAIZ / "extractor" / "contrato.json"),
                         ("personajes", RAIZ / "jugador" / "personajes_jugadores.json")):
        if not ruta.exists():
            sys.exit(f"No encuentro el {nombre}: {ruta}")

    import psycopg
    with psycopg.connect(bd.DSN) as c:
        r = c.execute("SELECT id, title, architecture FROM campaigns WHERE id = %s",
                     (args.campaign_id,)).fetchone()
        if not r:
            sys.exit(f"No existe la campaña {args.campaign_id}")
        if r[2] != "mas":
            sys.exit(f"La campaña {args.campaign_id} tiene architecture="
                     f"'{r[2]}', no 'mas' -- este script es solo para el "
                     f"brazo G1. Usa vertical_slice.py para 'monolithic'.")
    camp = bd.Campaña(r[0])
    cab = camp.cabecera()

    pjs = json.loads((RAIZ / "jugador" / "personajes_jugadores.json")
                     .read_text(encoding="utf-8"))["personajes"]
    pj = next(p for p in pjs if p["id"] == args.pj)
    nombres_pj_conocidos = {p["nombre"] for p in pjs}

    prompt_jugador = (RAIZ / "jugador" / "prompt.md").read_text(encoding="utf-8")
    prompt_actor = (RAIZ / "dm" / "prompt_actor_g1.md").read_text(encoding="utf-8")
    prompt_arbitro = (RAIZ / "dm" / "prompt_arbitro_g1.md").read_text(encoding="utf-8")
    prompt_mundo = (RAIZ / "dm" / "prompt_mundo_g1.md").read_text(encoding="utf-8")
    prompt_narrador = (RAIZ / "dm" / "prompt_narrador_g1.md").read_text(encoding="utf-8")
    prompt_extractor = (RAIZ / "extractor" / "prompt.md").read_text(encoding="utf-8")
    contrato = json.loads((RAIZ / "extractor" / "contrato.json")
                          .read_text(encoding="utf-8"))

    logs_dir = RAIZ / "logs"
    logs_dir.mkdir(exist_ok=True)
    marca = time.strftime("%Y%m%d_%H%M%S")
    # Punto 30 (bitácora QM): el nombre de archivo antes solo llevaba
    # "g1_<campaign_id corto>", sin distinguir a qué Par pertenece --
    # obligaba a renombrar a mano después para poder diferenciar
    # Par01/02/03 de un vistazo. Ahora se antepone un slug del título real
    # de la campaña (p.ej. "Par 02 · G1 (Multiagente) · Vela Honda" ->
    # "par_02_g1_multiagente_vela_honda"), autodescriptivo desde que se
    # genera -- ya no depende de renombrar después.
    slug_titulo = _slug(cab["title"])
    nombre_log = re.sub(
        r"[^\w.-]+", "_",
        f"{slug_titulo}_g1_{str(camp.campaign_id)[:8]}_"
        f"turnos_{cab['current_turn'] + 1}-{cab['current_turn'] + args.turnos}_{marca}.md")
    ruta_log = logs_dir / nombre_log
    archivo_log = open(ruta_log, "w", encoding="utf-8")
    stdout_original = sys.stdout
    sys.stdout = Tee(stdout_original, archivo_log)
    print(f"(bitácora en Markdown: {ruta_log})", file=stdout_original)

    try:
        print(f"\n# VERTICAL SLICE G1 — {cab['title']} ({cab['architecture']})\n")
        print(f"- **modelo (todos los roles):** `{MODELO_DM}`")
        print(f"- **jugador:** `{MODELO_JUGADOR}` ({pj['nombre']}, desvío {pj['desvio']})")
        print(f"- **turno:** {cab['current_turn'] + 1}"
              + ("  _(SECO — no se escribe nada)_" if args.seco else ""))

        _cuerpo_principal(args, camp, cab, pj, nombres_pj_conocidos,
                          prompt_jugador, prompt_actor, prompt_arbitro,
                          prompt_mundo, prompt_narrador, prompt_extractor,
                          contrato)
    finally:
        sys.stdout = stdout_original
        archivo_log.close()
        print(f"(bitácora guardada: {ruta_log})")


def _cuerpo_principal(args, camp, cab, pj, nombres_pj_conocidos,
                      prompt_jugador, prompt_actor, prompt_arbitro,
                      prompt_mundo, prompt_narrador, prompt_extractor,
                      contrato):
    # Bug encontrado en Par 02 real (2026-09-15, turno 177): este default
    # venía hardcodeado a "Sargento Brea" (PNJ del piloto "Vado de
    # Ceniza") -- funcionaba por casualidad mientras cada campaña nueva
    # reutilizara ese nombre. En cuanto una campaña con reparto propio
    # (Alto Ferrena) tiene una escena sin ningún PNJ conocido detectado,
    # camp.estado_pnj("Sargento Brea") devuelve None y revienta el print
    # de abajo. Arranca vacío -- el primer PNJ real de la campaña se
    # resuelve dentro del loop, contra los PNJ que sí existen aquí.
    presentes = []
    coste_por_modelo = {}

    def sumar_coste(modelo, r):
        c = coste_por_modelo.setdefault(modelo, {"tin": 0, "tout": 0})
        c["tin"] += r["tin"]; c["tout"] += r["tout"]

    turno_inicial = cab["current_turn"]

    for i in range(args.turnos):
        turn_id = turno_inicial + 1 + i
        reintentos_meta = 0   # regeneraciones de la red de seguridad (dados.META_OOC)

        # Contador de turno visible en vivo y en la bitácora (nuevo
        # 2026-09-16, pedido tras Par 02 real: sin esto, saber en qué
        # turno se cortó una corrida exigía reconstruirlo a mano contando
        # "### [1]" en el log). `grep "^## Turno " bitacora.md` da el
        # avance completo de una corrida de un vistazo. Simétrico con
        # vertical_slice.py.
        print(f"\n## Turno {turn_id} — {i+1}/{args.turnos} de esta corrida "
              f"(objetivo final de la campaña: {turno_inicial + args.turnos})\n")

        # ------------------------------------------------- 1. estado y escena
        paso(1, "ESTADO Y CONTEXTO (desde Postgres)")
        cab["game_day"] = camp.cabecera()["game_day"]
        ents = camp.entidades()
        conocidos = entidades_conocidas(ents, pj["nombre"])
        ultimo = camp.escena_actual()
        if ultimo is None:
            # Antes esto caía a un texto hardcodeado de "Vado de Ceniza"
            # (lore del piloto), código muerto que nunca se disparó porque
            # la siembra de corpus real siempre deja un turno 0 real en la
            # base -- pero código muerto peligroso: si algún par futuro se
            # lanzara sin sembrar ese turno 0, la campaña arrancaría
            # narrando la ambientación de OTRO par sin que nada lo avisara.
            # Mismo criterio que dados.py: no inventar, fallar fuerte y
            # explícito antes de gastar presupuesto real en una corrida
            # con la escena de apertura equivocada. Simétrico con
            # vertical_slice.py.
            sys.exit(
                f"No hay ningún turno registrado (turn_log) para la "
                f"campaña {camp.campaign_id} -- falta sembrar el turno 0 "
                f"(escena de apertura) antes de generar. No se arranca "
                f"con una escena por defecto.")
        escena = ultimo["dm_output"]
        location_id_actual = ultimo["location_id"]

        detectados = []
        for e in ents:
            if e["tipo"] != "npc" or e["nombre"] in nombres_pj_conocidos:
                continue
            tokens = [e["nombre"]] + [p for p in e["nombre"].split() if len(p) >= 3]
            if any(t in escena for t in tokens):
                estado = camp.estado_pnj(e["nombre"])
                if estado and estado["status"] == "alive":
                    detectados.append(e["nombre"])
        if detectados:
            presentes = detectados
        elif not presentes:
            # Fallback campaña-agnóstico: cualquier PNJ vivo ya sembrado
            # en ESTA campaña, en vez de un nombre hardcodeado de otro
            # escenario. Puede seguir vacío (campaña sin PNJ vivo
            # detectable todavía) -- se maneja abajo sin reventar.
            npcs_conocidos = [e["nombre"] for e in ents if e["tipo"] == "npc"]
            presentes = npcs_conocidos[:1]

        antes = camp.estado_pnj(presentes[0]) if presentes else None
        if antes:
            print(f"  {antes['name']}: {antes['status']}, aprecio "
                  f"{antes['affinity']} ({antes['banda']}), "
                  f"{antes['hechos']} hechos conocidos")
        else:
            print("  (ningún PNJ conocido detectado en la escena todavía)")
        eventos_reloj = camp.eventos_reloj_turno(turn_id - 1) if turn_id > 1 else []

        # ------------------------------------------------------- 2. jugador
        paso(2, f"JUGADOR — {pj['nombre']}")
        ficha = ficha_jugador(pj)
        r = llamar(MODELO_JUGADOR, prompt_jugador,
                   f"{ficha}\n\nEL DM ACABA DE DECIR\n{escena}\n\n¿Qué haces?",
                   max_tokens=300)
        if not r:
            sys.exit("El jugador no respondió")
        sumar_coste(MODELO_JUGADOR, r)
        accion = r["texto"]
        print(f"  {r['ms']} ms\n")
        for l in accion.splitlines():
            if l.strip():
                print(f"> {l}")

        # --------------------------------------------------------- 3. dados
        paso(3, "DADOS (deterministas, del sistema, compartido con G2)")
        buffer_txt, tiradas, rechazadas = dados.resolver_turno(
            accion, str(camp.campaign_id), turn_id,
            tabla_modificadores=dados.tabla_pj(pj))
        if not tiradas and not rechazadas:
            print("  sin tiradas declaradas")
        for t in tiradas:
            print(f"  {t['etiqueta']}: {t['dado']}+{t['modificador']}={t['total']}"
                  + ("  CRÍTICO" if t["critico"] else "  PIFIA" if t["pifia"] else ""))
        for h in rechazadas:
            print(f"  {h}: NO EXISTE — no se tira")

        # ------------------------------------------------------- 4. router
        paso(4, "ROUTER (determinista, sin LLM)")
        historial_modos, ultimo_pnj_hablo = camp.historial_router()
        clasif = rtr.clasificar_turno(buffer_txt, presentes, ultimo_pnj_hablo,
                                      historial_modos)
        print(f"  modo={clasif['modo']} · requiere_arbitro={clasif['requiere_arbitro']}"
              f" · pnj_que_responden={clasif['pnj_que_responden']}"
              f" · altera_estado={clasif['altera_estado']} · peso={clasif['peso']}")

        faltantes = []
        cb = cab.get("content_boundaries") or {}
        rojas = cb.get("hard_lines") or []
        velos = cb.get("veils") or []
        limites_txt = (f"líneas rojas (NUNCA aparecen): "
                       f"{', '.join(rojas) if rojas else 'ninguna declarada'}\n"
                       f"velos (se cortan en negro): "
                       f"{', '.join(velos) if velos else 'ninguno'}")

        if clasif["modo"] == "fuera_de_rol":
            # OOC-1..6: no hay Actor ni Mundo ni Narrador -- la respuesta
            # del Árbitro en modo tutor va directo al jugador.
            paso("5a", "ÁRBITRO — modo tutor (fuera de rol)")
            user_arb = (f"MODO: tutor\nBUFFER DEL JUGADOR\n{buffer_txt}\n\n"
                       f"CONFIGURACIÓN\n  visibilidad de reglas: "
                       f"{cab['rules_visibility']}\n{limites_txt}")
            r = llamar(MODELO_DM, prompt_arbitro, user_arb, max_tokens=400, temp=0.3)
            if not r:
                sys.exit("El Árbitro (tutor) no respondió")
            sumar_coste(MODELO_DM, r)
            parsed = parsear_json(r["texto"]) or {}
            narracion = parsed.get("respuesta") or "(el Árbitro no devolvió respuesta)"
            print(f"  {r['ms']} ms\n")
            for l in narracion.splitlines():
                if l.strip():
                    print(f"> {l}")
            router_modo_reg = clasif["modo"]
            router_last_npc_id = None
        else:
            # ---------------------------------------------------- 5. árbitro
            paso(5, "ÁRBITRO")
            veredicto = None
            if clasif["requiere_arbitro"]:
                banda = None
                if clasif["pnj_que_responden"]:
                    est = camp.estado_pnj(clasif["pnj_que_responden"][0])
                    banda = est["banda"] if est else None
                ver = arb.resolver_veredicto(buffer_txt, clasif["altera_estado"], banda)
                if ver is None:
                    veredicto = None
                elif ver.get("necesita_juicio"):
                    user_arb = (f"MODO: veredicto_sin_tirada\nBUFFER DEL JUGADOR\n"
                               f"{buffer_txt}\n\nCONTEXTO\n{escena}\n"
                               f"disposición del PNJ interpelado: {banda or 'n/a'}\n"
                               f"{limites_txt}")
                    r = llamar(MODELO_DM, prompt_arbitro, user_arb,
                              max_tokens=300, temp=0.3, json_mode=True)
                    if not r:
                        print("  ✗ el Árbitro (veredicto sin tirada) no respondió"
                              " -- se narra sin resolver nada mecánico")
                        faltantes.append("Árbitro")
                    else:
                        sumar_coste(MODELO_DM, r)
                        veredicto = parsear_json(r["texto"])
                        if not veredicto or veredicto.get("veredicto") is None:
                            # NUN-3/4: el Árbitro pidió una tirada que este
                            # script automatizado no puede solicitarle al
                            # jugador a mitad de turno -- se degrada a "sin
                            # veredicto" (limitación conocida, documentada
                            # en el vault, no un bug silencioso).
                            veredicto = None
                        print(f"  {r['ms']} ms · veredicto="
                              f"{veredicto.get('veredicto') if veredicto else None}")
                else:
                    veredicto = ver
                    print(f"  veredicto mecánico: {veredicto['veredicto']} "
                          f"(CD {veredicto['cd']}, resultado {veredicto['resultado']})")
            else:
                print("  no requerido este turno")

            # ---------------------------------------------------- 6. actor(es)
            paso(6, "ACTOR(ES)")
            intervenciones = []
            if not clasif["pnj_que_responden"]:
                print("  nadie a quien responder este turno")
            for nombre_pnj in clasif["pnj_que_responden"]:
                persona = camp.get_persona(nombre_pnj, turn_id)
                if not persona:
                    print(f"  ✗ PNJ sin ficha en la base: {nombre_pnj} -- se omite")
                    faltantes.append("Actor")
                    continue
                ficha_pnj = ficha_pnj_actor(persona)
                user_actor = (f"{ficha_pnj}\n\nESCENA ACTUAL\n{escena}\n\n"
                              f"EL JUGADOR ACABA DE HACER/DECIR\n{buffer_txt}")
                r = llamar(MODELO_DM, prompt_actor, user_actor,
                          max_tokens=250, temp=0.85, json_mode=True)
                if not r:
                    print(f"  ✗ el Actor de {nombre_pnj} no respondió")
                    faltantes.append("Actor")
                    continue
                sumar_coste(MODELO_DM, r)
                parsed = parsear_json(r["texto"])
                if not parsed or not parsed.get("linea"):
                    print(f"  ✗ el Actor de {nombre_pnj} no devolvió una línea válida")
                    faltantes.append("Actor")
                    continue
                intervenciones.append({"pnj": nombre_pnj, **parsed})
                print(f"  {nombre_pnj} ({r['ms']} ms): «{parsed['linea'][:80]}»")

            # ---------------------------------------------------- 7. mundo
            paso(7, "MUNDO")
            lugar = camp.lugar_estado(location_id_actual) if location_id_actual else None
            semillas = camp.semillas_sin_ubicar()
            # Heurística: una pregunta que el jugador no dirigió a ningún
            # PNJ presente es, por descarte, una pregunta sobre el entorno
            # (MUN-5). Igual que otras heurísticas del proyecto (ver
            # router.py, VERBOS_INTENCION): un falso positivo aquí solo
            # cuesta fijar una descripción de más, no rompe nada río abajo.
            escena_pregunta = "?" in buffer_txt and not clasif["pnj_que_responden"]
            res_mundo = mun.resolver_mundo(lugar, eventos_reloj, semillas, escena_pregunta)
            print(f"  necesita_llm={res_mundo['necesita_llm']} · "
                  f"lugar_repite={res_mundo['lugar_repite']} · "
                  f"lugar_necesita_boceto={res_mundo['lugar_necesita_boceto']}")

            boceto = res_mundo["descripcion"]
            semilla_plantada = None
            propagacion_sugerida = []
            deltas_mundo = []
            if res_mundo["necesita_llm"]:
                user_mundo = (
                    f"lugar_necesita_boceto: {res_mundo['lugar_necesita_boceto']}\n"
                    f"fijar_al_responder: {res_mundo['fijar_al_responder']}\n"
                    f"semilla_candidata: {json.dumps(res_mundo['semilla_candidata'], ensure_ascii=False)}\n\n"
                    f"CONTEXTO\n{escena}\n\nTURNO DEL JUGADOR\n{buffer_txt}\n"
                    f"{limites_txt}")
                r = llamar(MODELO_DM, prompt_mundo, user_mundo,
                          max_tokens=400, temp=0.7, json_mode=True)
                if not r:
                    print("  ✗ el Mundo no respondió")
                    faltantes.append("Mundo")
                else:
                    sumar_coste(MODELO_DM, r)
                    parsed = parsear_json(r["texto"]) or {}
                    # Bug encontrado en Par 13 G1 (2026-09-18, ~17:15): la
                    # salida del Mundo puede tener una forma inesperada (un
                    # elemento de "propagacion_sugerida" que es un string
                    # suelto, no un objeto -- mismo tipo de fallo ya visto
                    # en "deltas" en Par 02). Se normaliza aquí para que
                    # ni el JSON entero (lista en vez de objeto) ni
                    # "semilla_plantada" (string en vez de objeto) puedan
                    # tumbar la corrida más adelante con un .get().
                    if not isinstance(parsed, dict):
                        print(f"  ✗ (Mundo) salida no es un objeto, ignorada: {parsed!r:.120}")
                        parsed = {}
                    boceto = parsed.get("boceto") or boceto
                    semilla_plantada = parsed.get("semilla_plantada")
                    if not isinstance(semilla_plantada, dict):
                        semilla_plantada = None
                    propagacion_sugerida = parsed.get("propagacion_sugerida") or []
                    deltas_mundo = parsed.get("deltas") or []
                    if not isinstance(propagacion_sugerida, list):
                        propagacion_sugerida = []
                    if not isinstance(deltas_mundo, list):
                        deltas_mundo = []
                    print(f"  {r['ms']} ms · boceto={'sí' if boceto else 'no'} "
                          f"· semilla_plantada="
                          f"{semilla_plantada.get('planteada') if semilla_plantada else None}")

            boceto_mundo_txt_partes = []
            reloj_txt = renderizar_eventos_reloj(eventos_reloj)
            if reloj_txt:
                boceto_mundo_txt_partes.append(f"ya ocurrió y aún no se narró:\n{reloj_txt}")
            if boceto:
                boceto_mundo_txt_partes.append(boceto)
            boceto_mundo_txt = "\n\n".join(boceto_mundo_txt_partes) or None

            # -------------------------------------------------- 8. narrador
            paso(8, "NARRADOR")
            contexto_narrador = camp.contexto_escena_narrador(presentes)
            fragmentos = {
                "modo": clasif["modo"],
                "veredicto": veredicto,
                "intervenciones": intervenciones,
                "boceto_mundo": boceto_mundo_txt,
                "faltantes": faltantes,
            }
            user_narrador = (
                f"CONFIGURACIÓN\n  tono: {cab['world_tone']} · registro: "
                f"{cab['party_register']} · visibilidad de reglas: "
                f"{cab['rules_visibility']}\n{limites_txt}\n\n"
                f"FRAGMENTOS\n{json.dumps(fragmentos, ensure_ascii=False, indent=2)}\n\n"
                f"CONTEXTO ADICIONAL DE LA BASE\n{contexto_narrador}\n\n"
                f"ESCENA ANTERIOR\n{escena}\n\nTURNO DEL JUGADOR\n{buffer_txt}")
            r = llamar(MODELO_DM, prompt_narrador, user_narrador,
                      max_tokens=500, temp=0.8)
            if not r:
                sys.exit("El Narrador no respondió")
            sumar_coste(MODELO_DM, r)
            narracion = r["texto"]
            # Red de seguridad compartida con G2 (Par 18+, ver dados.META_OOC).
            # En Par 07-17 G1 nunca la habría necesitado (0 de 15 400 turnos).
            while dados.es_meta_ooc(narracion) and reintentos_meta < 2:
                reintentos_meta += 1
                print(f"  ⚠ Narrador fuera de personaje: regenerando ({reintentos_meta}/2)")
                r2 = llamar(MODELO_DM, prompt_narrador,
                            user_narrador + dados.AVISO_META, max_tokens=500, temp=0.8)
                if not r2:
                    break
                sumar_coste(MODELO_DM, r2)
                r, narracion = r2, r2["texto"]
            if dados.es_meta_ooc(narracion):
                narracion = dados.quitar_meta_ooc(narracion)
            print(f"  {r['ms']} ms\n")
            for l in narracion.splitlines():
                if l.strip():
                    print(f"> {l}")

            router_modo_reg = clasif["modo"]
            router_last_npc_id = (camp.id_de("npc", clasif["pnj_que_responden"][0])
                                  if clasif["pnj_que_responden"] else None)

        # ---------------------------------------------- 9. verificación
        # Idéntica a G2 (mismo instrumento, para que la comparación entre
        # brazos sea justa -- ver "QM - Respaldo bibliografico
        # instrumentos deterministicos.md").
        paso(9, "VERIFICACIÓN DE LA NARRACIÓN")
        problemas = []
        val = {"raw_flags": {}}
        if reintentos_meta:
            val["raw_flags"]["guard_meta_reintentos"] = reintentos_meta
        if re.search(r"\[[^\]]{20,}\]", narracion):
            problemas.append("meta-comentario entre corchetes")
            val["raw_flags"]["meta_comentario"] = True
        if re.search(r"\b(tirada de \w+ necesaria|resuelvo la|como DM|"
                     r"seg[úu]n las reglas|no obstante,? al haber)\b",
                     narracion, re.I):
            problemas.append("comenta sus propias reglas")
            val["raw_flags"]["comenta_reglas"] = True

        for t in tiradas:
            if t["pifia"] and re.search(r"\b(logras|consigues|aciertas|lo convences)\b",
                                        narracion, re.I):
                msg = f"pifia en {t['etiqueta']} pero narra éxito"
                problemas.append(msg)
                val["cr1_veredicto_contradice_narracion"] = True
                val["cr1_evidencia"] = msg

        m = re.search(rf"\b{re.escape(pj['nombre'])}\s+(piensa|siente|decide|comprende)",
                      narracion, re.I)
        if m:
            problemas.append("narra pensamientos del PJ (viola la regla de oro)")
            val["qn2_pj_piensa_narrado"] = True
            val["qn2_pj_piensa_evidencia"] = m.group(0)

        m = re.search(rf"\b{re.escape(pj['nombre'])}\s+(ataca|golpea|convence|"
                      r"esquiva|salta|derriba|desarma)\b", narracion, re.I)
        if m and not tiradas:
            val["qn2_pj_accion_revisar"] = True
            val["qn2_pj_accion_evidencia"] = m.group(0)

        for e in ents:
            if (e["tipo"] != "npc" or e["nombre"] not in narracion
                    or e["nombre"] in nombres_pj_conocidos):
                continue
            estado = camp.estado_pnj(e["nombre"])
            if estado and estado["status"] != "alive":
                val["cl2_pnj_inactivo_actua"] = True
                val["cl2_pnj_evidencia"] = (
                    f"{e['nombre']} (status={estado['status']}) mencionado "
                    f"en: «{narracion[:120]}»")
                problemas.append(f"PNJ inactivo mencionado actuando: "
                                 f"{e['nombre']} ({estado['status']})")
                break

        hp = camp.hp_pj(pj["nombre"])
        if hp and hp["hp_current"] is not None:
            narra_muerte = re.search(
                rf"\b{re.escape(pj['nombre'])}\s+(muere|cae muerto|fallece|"
                r"pierde la vida)\b", narracion, re.I)
            if narra_muerte and hp["hp_current"] > 0:
                val["cl2_pc_hp_contradice_narracion"] = True
                val["cl2_pc_hp_evidencia"] = (
                    f"hp_current real={hp['hp_current']}/{hp['hp_max']} pero "
                    f"narra: «{narra_muerte.group(0)}»")
                problemas.append("narra muerte del PJ con HP real > 0")

        val["cl2_lugar_jaccard_similarity"] = round(jaccard_palabras(escena, narracion), 3)
        val["cr2_entidad_grafo_densidad"] = entidad_grafo_densidad(narracion, conocidos)
        palabras_narr = re.findall(r"\w+", narracion.lower())
        if palabras_narr:
            val["qn1_ttr"] = round(len(set(palabras_narr)) / len(palabras_narr), 3)
            bigramas = list(zip(palabras_narr, palabras_narr[1:]))
            if bigramas:
                val["qn1_ngram_repeticion"] = round(
                    1 - len(set(bigramas)) / len(bigramas), 3)
        val["qn1_legibilidad_fh"] = fernandez_huerta(narracion)

        print("  " + ("\n  ".join(f"⚠ {p}" for p in problemas)
                      if problemas else "sin problemas detectados"))

        # ---------------------------------------------------- 10. extractor
        paso(10, "EXTRACTOR (compartido con G2)")
        lista = "\n".join(f"  {e['nombre']:26s} {e['tipo']}" for e in ents)
        user_ex = (f"ENTIDADES EXISTENTES\n{lista}\n"
                   f"TURNO\n{pj['nombre']}: {accion}\nDM: {narracion}")
        r = llamar(MODELO_DM, prompt_extractor, user_ex,
                   max_tokens=800, temp=0, json_mode=True)
        if not r:
            sys.exit("El extractor no respondió")
        sumar_coste(MODELO_DM, r)
        salida = parsear_json(r["texto"]) or {"events": [], "deltas": []}
        eventos = salida.get("events") or []
        deltas = salida.get("deltas") or []
        creaciones = salida.get("creaciones") or []
        print(f"  {r['ms']} ms · {len(eventos)} eventos · {len(deltas)} deltas"
              f" · {len(creaciones)} creaciones")

        # ------------------------------------------- 11. validar antes de escribir
        paso(11, "VALIDACIÓN DE LO EXTRAÍDO")
        completo = f"{accion} {narracion}"
        validos_ev, validos_d = [], []
        for e in eventos:
            ev = e.get("evidence", "") or ""
            if e.get("event_kind") not in contrato["event_kinds"]:
                print(f"  ✗ event_kind desconocido: {e.get('event_kind')}")
            elif ev not in completo:
                print(f"  ✗ evidencia no literal: «{ev[:50]}»")
            else:
                validos_ev.append(e)
                print(f"  ✓ evento {e['entity']} · {e['event_kind']}")
        for d in deltas:
            # Guarda añadida 2026-09-16 (auditoría diff G1/G2), simétrica
            # con vertical_slice.py -- mismo patrón que la guarda de
            # deltas_mundo más abajo (bug 1 de Par 02 real), pero para el
            # extractor (compartido con G2) en vez del rol Mundo
            # (exclusivo de G1).
            if not isinstance(d, dict):
                print(f"  ✗ delta malformado (no es objeto): {d!r}")
                continue
            ev = d.get("evidence", "") or ""
            campos = contrato["campos_directos"].get(d.get("entity_type"), {})
            if d.get("field") not in campos:
                print(f"  ✗ campo fuera de lista blanca: "
                      f"{d.get('entity_type')}.{d.get('field')}")
            elif ev not in completo:
                print(f"  ✗ evidencia no literal: «{ev[:50]}»")
            else:
                validos_d.append(d)
                print(f"  ✓ delta {d['entity']} · {d['entity_type']}.{d['field']}"
                      f" = {d.get('value')}")
        CREABLES = {"npc", "location", "item", "faction", "quest"}
        GENERICOS = re.compile(r"^\s*(?:el|la|los|las|un|una|unos|unas)\s+\w+\s*$", re.I)
        # Punto 29 (bitácora QM): el guard original solo comparaba contra
        # nombres_pj_conocidos (los PJ), no contra NPCs YA SEMBRADOS/creados
        # en la campaña -- si el extractor proponía "crear NPC: <nombre de
        # un NPC ya sembrado>" (p.ej. porque no lo tenía en su ventana de
        # contexto), nada lo detenía y se creaba una fila de entidad
        # duplicada con el mismo nombre. Detectado en Par02 G1 (Hendrik Vall
        # duplicado, Ysolda Marn desplazada del top-3 de la sección 4).
        nombres_npc_existentes = {e["nombre"] for e in ents if e["tipo"] == "npc"}
        validos_c = []
        for cr in creaciones:
            ev = cr.get("evidence", "") or ""
            nom = (cr.get("name") or "").strip()
            if cr.get("entity_type") not in CREABLES:
                print(f"  ✗ tipo no creable: {cr.get('entity_type')}")
            elif cr.get("entity_type") == "npc" and nom in nombres_pj_conocidos:
                print(f"  ✗ NPC propuesto coincide con un PJ existente "
                      f"({nom}), no se crea duplicado")
            elif cr.get("entity_type") == "npc" and nom in nombres_npc_existentes:
                print(f"  ✗ NPC propuesto ya existe como entidad de la "
                      f"campaña ({nom}), no se crea duplicado")
            elif len(nom) < 3 or GENERICOS.match(nom):
                print(f"  ✗ nombre genérico, es atrezzo: «{nom}»")
            elif ev not in completo:
                print(f"  ✗ evidencia no literal: «{ev[:50]}»")
            elif len(validos_c) >= 1:
                print(f"  ✗ tope de 1 creación por turno, descartada: «{nom}»")
            else:
                validos_c.append(cr)
                print(f"  ✓ creación {cr['entity_type']}: {nom}")

        if not validos_ev and not validos_d and not validos_c:
            print("  nada que escribir (correcto si el turno no cambió el mundo)")

        STOP_MAYUS = {"El", "La", "Los", "Las", "Un", "Una", "Unos", "Unas",
                      "Cuando", "Si", "Pero", "Y", "Aunque", "Tras", "Al",
                      "Ella", "Él", "Sargento", "Vado", "Ceniza"}
        LIMITES = set(".!?¿¡—\n\"'")
        no_reconocidos = set()
        for m in re.finditer(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b", narracion):
            palabra = m.group(0)
            if palabra in conocidos or palabra in STOP_MAYUS:
                continue
            prefijo = narracion[:m.start()].rstrip()
            if prefijo and prefijo[-1] in LIMITES:
                continue
            if not prefijo:
                continue
            no_reconocidos.add(palabra)
        no_reconocidos = sorted(no_reconocidos)
        if no_reconocidos:
            val["cr2_nombres_no_reconocidos"] = no_reconocidos
            print(f"  ⚠ nombres no reconocidos: {', '.join(no_reconocidos)}")

        for d in deltas:
            if d.get("entity_type") == "world":
                continue
            mutables = camp.campos_mutables(d.get("entity_type"))
            if mutables and d.get("field") not in mutables:
                val["cl1_campo_inmutable_alterado"] = True
                val["cl1_campo_evidencia"] = (
                    f"{d.get('entity_type')}.{d.get('field')} = "
                    f"{d.get('value')} (no está en mutable_fields)")
                print(f"  ⚠ campo no mutable propuesto: "
                      f"{d.get('entity_type')}.{d.get('field')}")
                break

        # -------------------------------------------------------- 12. escribir
        paso(12, "ESCRITURA" + ("  [SECO — omitida]" if args.seco else ""))
        dias_transcurridos = 0
        if not args.seco:
            camp.registrar_turno(turn_id, [{"pc": pj["id"], "text": accion}],
                                 narracion,
                                 bool(validos_ev or validos_d or validos_c),
                                 router_modo=router_modo_reg,
                                 router_last_npc=router_last_npc_id)
            if val.get("raw_flags"):
                val["raw_flags"] = json.dumps(val["raw_flags"], ensure_ascii=False)
            else:
                val.pop("raw_flags", None)
            camp.registrar_validacion(turn_id, cab["architecture"], val)
            tier12 = [k for k in ("cr1_veredicto_contradice_narracion",
                                  "cl2_pnj_inactivo_actua",
                                  "cl2_pc_hp_contradice_narracion",
                                  "qn2_pj_piensa_narrado",
                                  "cl1_campo_inmutable_alterado")
                     if val.get(k)]
            print("  → turn_validation registrado"
                  + (f" ⚠ {len(tier12)} problema(s) tier 1-2" if tier12 else
                     " (sin problemas tier 1-2)"))

            for cr in validos_c:
                padre = (camp.id_de("location", cr["dentro_de"])
                         if cr.get("dentro_de") else None)
                res = camp.crear(cr["entity_type"], cr["name"], turn_id,
                                 cr["evidence"], padre, None,
                                 cr.get("descripcion"))
                print(f"  → {res['motivo']}: {cr['entity_type']} {cr['name']}")
            for e in validos_ev:
                nid = camp.id_de("npc", e["entity"])
                if not nid:
                    print(f"  ✗ PNJ inexistente: {e['entity']}")
                    continue
                res = camp.resolver_evento(nid, e["event_kind"])
                if not res:
                    print(f"  ✗ evento sin magnitud: {e['event_kind']}")
                    continue
                # mutable_fields fija npc.affinity en [-100, 100]
                # (migrations/001_schema.sql) y apply_delta() RECHAZA con
                # RAISE EXCEPTION cualquier valor fuera de ese rango -- a
                # propósito, es una validación de dominio, no algo para
                # "arreglar" del lado de la base. Sin acotar aquí, una
                # racha larga de eventos positivos sobre el mismo PNJ (se
                # vio en producción: +2 por competence_shown, turno tras
                # turno, terminó en 121.0) tumba el turno entero. Acotar
                # ANTES de escribir, igual que ya hace apply_delta con
                # LEAST(GREATEST(...)) para el resto de campos de
                # disposición. Idéntico a vertical_slice.py (G2) -- mismo
                # bug, mismo fix, para no romper la comparación entre
                # brazos.
                nuevo = max(-100.0, min(100.0,
                            float(antes["affinity"] or 0) + float(res["d_affinity"])))
                did = camp.aplicar("npc", nid, "affinity", nuevo, turn_id,
                                   "extracted", e["evidence"])
                print(f"  → delta {did}: {e['entity']} affinity "
                      f"{antes['affinity']} → {nuevo:.1f}  ({res['band']})")
                print(f"     {res['outcome'][:66]}")
            for d in validos_d:
                if d["entity_type"] == "world":
                    eid = None
                else:
                    eid = camp.id_de(d["entity_type"], d["entity"])
                    if not eid:
                        print(f"  ✗ entidad inexistente: {d['entity']}")
                        continue

                valor = d["value"]
                campo_info = contrato["campos_directos"].get(
                    d["entity_type"], {}).get(d["field"], {})
                if campo_info.get("tipo") == "ref":
                    ref_id = camp.id_de(campo_info["entidad"], valor)
                    if not ref_id:
                        print(f"  ✗ referencia inexistente: "
                              f"{campo_info['entidad']} «{valor}»")
                        continue
                    valor = str(ref_id)

                try:
                    did = camp.aplicar(d["entity_type"], eid, d["field"],
                                       valor, turn_id, "extracted", d["evidence"])
                except Exception as e:
                    # Idéntico a vertical_slice.py (G2) -- mismo bug (Par 05
                    # real, 2026-09-18), mismo fix, en el mismo loop
                    # compartido de escritura de deltas del extractor. Ver
                    # el comentario largo en el gemelo de G2 para el detalle
                    # completo.
                    print(f"  ✗ delta rechazado por la base "
                          f"({d['entity_type']}.{d['field']} = {valor!r}): {e}")
                    continue
                v = str(d["value"])
                print(f"  → delta {did}: {d['entity']}.{d['field']} = "
                      f"{v[:56]}{'…' if len(v) > 56 else ''}")
                if d.get("witnessed") and d["field"] == "status":
                    for p in camp.propagar("npc", eid, d["field"], d["value"],
                                           turn_id, True):
                        print(f"  → propagado a {p['faction_name']}: {p['motivo']}")
                if d["entity_type"] == "world" and d["field"] == "game_day":
                    dias_transcurridos = int(d["value"]) - int(cab["game_day"])

            # Efectos propios del Agente del Mundo (exclusivo de G1): los
            # deltas que el Mundo propuso, la semilla que plantó y la
            # propagación que sugirió, más fijar la descripción del lugar
            # si correspondía (MUN-5/6/7).
            if clasif["modo"] != "fuera_de_rol":
                for d in deltas_mundo:
                    # Bug encontrado en Par 02 real (2026-09-15): el Mundo
                    # puede devolver un elemento de "deltas" que no es un
                    # objeto (visto: un entero suelto en la lista). d.get()
                    # revienta antes de llegar a cualquier guarda posterior
                    # -- por eso este chequeo va primero y por separado del
                    # try/except de más abajo (ese cubre el rechazo de la
                    # base, no un delta mal formado desde el origen).
                    if not isinstance(d, dict):
                        print(f"  ✗ (Mundo) delta malformado (no es "
                              f"objeto): {d!r}")
                        continue
                    tipo = normalizar_entity_type(d.get("entity_type"))
                    if tipo not in ENTITY_TYPES_VALIDOS:
                        print(f"  ✗ (Mundo) entity_type no reconocido "
                              f"(ni por sinónimo): {d}")
                        continue
                    eid = (None if tipo == "world"
                           else camp.id_de(tipo, d.get("entity_id")
                                           or d.get("entity")))
                    if tipo != "world" and not eid:
                        print(f"  ✗ (Mundo) entidad inexistente: {d}")
                        continue
                    try:
                        did = camp.aplicar(tipo, eid, d["field"],
                                           d["value"], turn_id, "extracted",
                                           f"(Mundo) {d.get('field')}")
                        print(f"  → delta (Mundo) {did}: {tipo}.{d.get('field')}")
                    except Exception as e:
                        # Bug encontrado en Par 04 (2026-09-14, turno 4):
                        # el Agente del Mundo puede proponer un campo que no
                        # está en la lista blanca de apply_delta() (p.ej.
                        # "descripcion" para location, o "attitude" para npc
                        # -- visto en producción, distintos campos cada vez,
                        # ninguno en mutable_fields). A diferencia de los
                        # otros loops de este bloque (entity_type no
                        # reconocido, entidad inexistente), esta llamada no
                        # tenía ninguna red de seguridad y tumbaba la corrida
                        # completa. Igual que "evento sin magnitud" en otras
                        # partes del script: se avisa y se sigue, no se
                        # aborta una corrida de 1,400 turnos por un campo que
                        # el Mundo no debía proponer.
                        print(f"  ✗ (Mundo) delta rechazado por la base "
                              f"({tipo}.{d.get('field')}): {e}")

                for prop in propagacion_sugerida:
                    # Bug de Par 13 G1 (2026-09-18): ver comentario en el
                    # parseo de la salida del Mundo. Esta era la línea que
                    # tumbó la corrida (AttributeError: 'str' object has
                    # no attribute 'get'); "deltas" ya tenía esta guarda.
                    if not isinstance(prop, dict):
                        print(f"  ✗ (Mundo) propagación sugerida malformada "
                              f"(no es objeto): {prop!r}")
                        continue
                    nid = camp.id_de("npc", prop.get("entidad"))
                    if nid:
                        print(f"  → propagación sugerida por Mundo hacia "
                              f"{prop.get('entidad')}: {prop.get('razon')}")

                if semilla_plantada and semilla_plantada.get("planteada") and \
                   res_mundo.get("semilla_candidata") and location_id_actual:
                    camp.plantar_semilla(res_mundo["semilla_candidata"]["id"],
                                         location_id_actual, turn_id)
                    print(f"  → semilla plantada: "
                          f"{res_mundo['semilla_candidata']['id']}")

                if res_mundo["fijar_al_responder"] and boceto and location_id_actual:
                    camp.fijar_lugar(location_id_actual, boceto, turn_id)
                    print("  → lugar fijado (MUN-5/6/7): no se vuelve a "
                          "regenerar su descripción")

            if dias_transcurridos > 0:
                disparados = camp.avanzar_relojes(dias_transcurridos, turn_id)
                for ev in disparados:
                    print(f"  ⏰ reloj disparado: agenda «{ev['agenda']}» "
                          f"(facción {ev['faction_id']})")
        else:
            print("  (nada escrito)")

        # Reloj del mundo determinista (db.sincronizar_dia): el día de juego
        # sale del turno, no del extractor (que nunca lo emitió en Par01-17).
        # Idéntico en G2. Va aparte del `if` de arriba: corre CADA turno.
        if not args.seco:
            for ev in camp.sincronizar_dia(turn_id):
                print(f"  ⏰ reloj disparado: agenda «{ev['agenda']}» "
                      f"(facción {ev['faction_id']})")

        # ------------------------------------------------------ 13. comprobar
        paso(13, "ESTADO DESPUÉS")
        despues = camp.estado_pnj(presentes[0])
        cambio = (antes["affinity"] != despues["affinity"]
                  or antes["status"] != despues["status"]
                  or antes["hechos"] != despues["hechos"])
        print(f"  {despues['name']}: {despues['status']}, aprecio "
              f"{despues['affinity']} ({despues['banda']}), "
              f"{despues['hechos']} hechos, "
              f"{despues['secretos_revelados']} secretos revelados")
        print(f"  {'ESTADO MODIFICADO' if cambio else 'sin cambios de estado'}")
        cab["current_turn"] = turn_id

    print("\n---\n")
    tin_total = tout_total = 0
    costo_total = 0.0
    detalle_costo = []
    for modelo, c in coste_por_modelo.items():
        tin_total += c["tin"]; tout_total += c["tout"]
        p_in, p_out = PRECIOS_USD_POR_1M.get(modelo, PRECIO_DEFECTO)
        if modelo not in PRECIOS_USD_POR_1M:
            print(f"  (aviso: sin precio conocido para {modelo}, usando tarifa "
                  f"de respaldo ${PRECIO_DEFECTO[0]}/${PRECIO_DEFECTO[1]} por 1M "
                  f"-- puede no reflejar el costo real, verificar contra el "
                  f"dashboard de DeepInfra)", file=sys.stderr)
        costo_modelo = (c["tin"] * p_in + c["tout"] * p_out) / 1e6
        costo_total += costo_modelo
        detalle_costo.append(f"  - `{modelo}`: {c['tin']}→{c['tout']} tokens · ${costo_modelo:.4f}")
    print(f"**Costo total de la sesión:** {tin_total}→{tout_total} tokens · "
          f"${costo_total:.4f}")
    for linea in detalle_costo:
        print(linea)


if __name__ == "__main__":
    main()
