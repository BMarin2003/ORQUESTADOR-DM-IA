r"""
VERTICAL SLICE — un turno completo, de punta a punta.

Conecta por primera vez las piezas que hasta ahora solo se probaron aisladas:

    estado (Postgres)
      → contexto de escena
        → JUGADOR agéntico          Gemma 4 31B (desde Par 04; Hermes-3 en Par01-03)
          → dados deterministas
            → DM                    Gemma 4 31B
              → EXTRACTOR           Gemma 4 31B
                → apply_delta
                  → estado nuevo

Cada paso verifica lo que produce antes de pasar al siguiente. Es donde
salen los bugs de integración: en esta sesión, seis fallos silenciosos solo
aparecieron ejecutando, y el primero de este script fue que `SET LOCAL` no
admite parámetros en Postgres.

Uso:
  py orquestador\vertical_slice.py
  py orquestador\vertical_slice.py --turnos 3
  py orquestador\vertical_slice.py --pj PJ18 --seco     (sin escribir en la base)
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
# fix ya aplicado en fixtures/generar_seed.py por el mismo motivo. Bug
# real encontrado en Par 07-17 (2026-09-18): 11 corridas lanzadas con
# Start-Process cayeron así, algunas a mitad del primer turno.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent


def _slug(texto):
    """Título de campaña -> slug para nombres de archivo autodescriptivos.

    "Par 02 · G2 (Monolítico) · Vela Honda" -> "par_02_monolitico_vela_honda".
    Sin acentos, sin separadores raros, todo en minúscula. Ver punto 30 de
    la bitácora QM.
    """
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w]+", "_", s).strip("_").lower()
    return s or "sin_titulo"
sys.path.insert(0, str(RAIZ / "jugador"))
sys.path.insert(0, str(RAIZ / "orquestador"))
import dados          # noqa: E402
import db as bd       # noqa: E402

BASE = "https://api.deepinfra.com/v1/openai"
MODELO_DM = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")
# Jugador migrado a Gemma (2026-09-17, decisión del usuario): antes usaba
# Hermes-3-Llama-3.1-70B, un modelo de 70B ~5.4x más caro por token que
# Gemma-4-31B (ver PRECIOS_USD_POR_1M abajo) -- eso hacía que UNA sola
# llamada del jugador pesara más en el costo real que TODAS las llamadas
# del DM/Extractor juntas en G2, y a veces más que los hasta 6 roles del
# propio sistema multiagente en G1. Insostenible para lo que se está
# comparando: el costo debería estar dominado por la arquitectura bajo
# estudio (G1/G2), no por el agente jugador, que es un actor de soporte
# idéntico en ambos brazos. Desde Par 04 en adelante, jugador y DM usan el
# mismo modelo (Gemma) -- Par 01/02/03 (real) siguen documentados con
# Hermes como jugador, ver nota metodológica en el plan de cierre.
MODELO_JUGADOR = os.environ.get("DMIA_MODELO_JUGADOR",
                                "google/gemma-4-31B-it")

# Precios reales (USD por 1M tokens), tarifa estándar de DeepInfra --
# hallazgo 2026-09-17: el costo impreso al final de la sesión sumaba TODOS
# los tokens (jugador + DM/extractor) bajo una sola tarifa, calibrada de
# hecho solo para el modelo del DM. El jugador usa un modelo distinto y
# bastante más caro (70B vs 31B) -- esto explicaba un gasto real en
# DeepInfra mayor al costo que este script venía imprimiendo. Verificado
# 2026-09-17 contra el reporte de uso REAL de la cuenta del usuario
# (deepinfra-usage-2026-09.csv, no una página de precios de terceros):
# Hermes-3-Llama-3.1-70B $0.70/1M input Y output (coincide exacto);
# gemma-4-31B-it $0.13/1M input, $0.38/1M output (corregido -- una
# estimación anterior con la página pública de precios había dado
# $0.09/$0.34, algo distinto de la tarifa real facturada a esta cuenta).
PRECIOS_USD_POR_1M = {
    "google/gemma-4-31B-it": (0.13, 0.38),
    "NousResearch/Hermes-3-Llama-3.1-70B": (0.70, 0.70),
}
PRECIO_DEFECTO = (0.09, 0.34)  # respaldo si el modelo no está en la tabla

PENSAMIENTO = re.compile(r"<think>.*?</think>", re.S | re.I)
VALLA = re.compile(r"^\s*```[a-z]*\s*$", re.M)


def jaccard_palabras(a, b):
    """Superposición léxica simple -- proxy tier 3 (nunca booleano de
    fallo), no el entity-grid real de Barzilay & Lapata (requiere
    correferencia + SVM entrenado, ver 'QM - Respaldo bibliografico
    instrumentos deterministicos.md', corrección sobre este chequeo)."""
    wa = set(re.findall(r"\w+", a.lower()))
    wb = set(re.findall(r"\w+", b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


_VOCALES_ES = "aeiouáéíóúü"
_RE_GRUPO_VOCALICO = re.compile(f"[{_VOCALES_ES}]+")


def contar_silabas_es(palabra):
    """Aproximación determinística: cada grupo de vocales consecutivas
    cuenta como una sílaba. Subestima hiatos reales, pero es la
    aproximación estándar usada en herramientas de legibilidad simples
    y basta como proxy -- nunca se usa como chequeo pass/fail."""
    grupos = _RE_GRUPO_VOCALICO.findall(palabra.lower())
    return max(1, len(grupos))


def fernandez_huerta(texto):
    """Índice de legibilidad de Fernández-Huerta (1959), adaptación al
    español de la fórmula tipo Flesch. L = 206.84 - 60*(sílabas/palabra)
    - 1.02*(palabras/frase). Determinístico, Tier 3 (proxy descriptivo,
    nunca pass/fail) -- ver nota de respaldo bibliográfico."""
    palabras = re.findall(r"[a-záéíóúñü]+", texto.lower())
    frases = [f for f in re.split(r"[.!?]+", texto) if f.strip()]
    if not palabras or not frases:
        return None
    silabas = sum(contar_silabas_es(p) for p in palabras)
    palabras_por_frase = len(palabras) / len(frases)
    L = 206.84 - 60 * (silabas / len(palabras)) - 1.02 * palabras_por_frase
    return round(L, 2)



def entidades_conocidas(ents, pj_nombre):
    """Vocabulario de entidades reales de la campaña: nombre completo +
    cada palabra suelta de 3+ letras de cada entidad y del PJ. Se
    reutiliza tanto en CR-2 (nombres no reconocidos) como en el grafo de
    recurrencia de entidad (Guinaudeau & Strube 2013, ver más abajo) --
    antes se recalculaba por separado en cada sitio."""
    conocidos = set()
    for nombre in [e["nombre"] for e in ents] + [pj_nombre]:
        conocidos.add(nombre)
        conocidos.update(p for p in nombre.split() if len(p) >= 3)
    return conocidos


def entidad_grafo_densidad(texto, conocidos):
    """Proxy Tier 3 (nunca pass/fail) inspirado en Guinaudeau & Strube
    (2013), Graph-based Local Coherence Modeling: mide continuidad
    temática DENTRO de la narración del turno como densidad de un grafo
    donde los nodos son oraciones y una arista conecta dos oraciones que
    comparten al menos una entidad real de la campaña (el gazetteer de
    la base de datos, no un sustantivo genérico del texto). Simplifica
    deliberadamente el método real del paper (que usa roles gramaticales
    -- sujeto/objeto -- y un ranking SVM entrenado sobre miles de pares
    etiquetados): acá solo se toma la idea de fondo -- presencia/ausencia
    de entidad conocida entre oraciones --, igual que ya se documentó
    para CR-2/Barzilay & Lapata en la nota de respaldo bibliográfico.
    Devuelve None si la narración tiene menos de 2 oraciones (no hay
    pares que formar)."""
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
    """Llama a chat/completions de DeepInfra y devuelve `{texto, tin, tout, ms}` (None ante error HTTP no transitorio). Quita `<think>` y vallas; reintenta cortes de red y 429/502/503/504 con backoff."""
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
        """POST con reintentos: backoff ante saturación (429/502/503/504) y cortes de red; otros HTTPError se propagan de inmediato."""
        # DeepInfra corta la conexión de tanto en tanto en llamadas largas
        # (visto en corridas reales de 250+ turnos: TimeoutError/URLError
        # tras 5-80 minutos de trabajo bueno). Sin reintento, cada corte
        # obligaba a relanzar el script a mano -- inviable para una
        # campaña de 1,750 turnos. Reintenta con backoff antes de rendirse
        # de verdad (fallo persistente sí debe propagar, no quedarse en
        # un bucle silencioso).
        intento = 0
        sobrecarga = 0
        while True:
            try:
                with urllib.request.urlopen(peticion, timeout=300) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                # Bug encontrado en Par 07-17 (2026-09-18, ~19:40): con 22
                # corridas en paralelo, DeepInfra devolvió 429 "Model busy,
                # retry later" (engine_overloaded) y las ~20 corridas
                # cayeron en el mismo cuarto de hora, porque el bloque de
                # abajo trata TODO HTTPError como fatal. 429/502/503/504
                # SÍ son transitorios (a diferencia de 401/402): se
                # reintenta con backoff exponencial acotado (10s..300s,
                # hasta max_sobrecarga intentos ~ 2 h) + jitter para que
                # las 22 no vuelvan a golpear a la vez. Un 429 no se
                # factura ni cambia el resultado: es neutral entre brazos.
                if e.code in (429, 502, 503, 504) and sobrecarga < max_sobrecarga:
                    sobrecarga += 1
                    pausa = min(300, 10 * 2 ** min(sobrecarga - 1, 5)) + random.uniform(0, 10)
                    print(f"    (HTTP {e.code}, modelo saturado: reintento "
                          f"{sobrecarga}/{max_sobrecarga} en {pausa:.0f}s)",
                          file=sys.stderr)
                    time.sleep(pausa)
                    continue
                # HTTPError es subclase de URLError -- sin este except
                # aparte, CUALQUIER respuesta de error de la API (401,
                # 402 saldo agotado, 404, 422, 500...) caía en el except
                # de abajo y se reintentaba con backoff (10/20/40s) como
                # si fuera un corte de red transitorio. Un 402 no se
                # arregla reintentando -- nunca se va a resolver solo
                # esperando. Propagar de inmediato al manejo que ya
                # existe más arriba en llamar() (fallback de
                # chat_template_kwargs/response_format, o mensaje HTTP
                # {code} y return None). Encontrado 2026-09-16 cuando
                # Par 02 real se quedó sin saldo en DeepInfra a mitad de
                # la corrida y cada llamada perdió ~70s en reintentos
                # inútiles antes de rendirse.
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
    """Extrae un objeto JSON del texto del modelo (con o sin vallas) o None si no hay uno válido."""
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
    """Duplica cada escritura de stdout a la consola Y a un archivo abierto
    por el propio Python en UTF-8. Antes el usuario capturaba la consola con
    `Measure-Command { ... } | Tee-Object -FilePath log.txt` en PowerShell,
    y esa captura llegaba con mojibake severo (p.ej. «Monol├¡tico» en vez de
    «Monolítico») -- corrupción de la codificación de PowerShell al procesar
    el pipeline, no un problema de los datos (que se escriben aparte, vía
    psycopg, siempre en UTF-8 correcto). La solución no es reparar ese
    archivo sino dejar de depender de él: este script ahora escribe su
    propia bitácora en Markdown, en UTF-8, directamente desde Python -- ver
    "QM - Respaldo bibliografico instrumentos deterministicos.md", punto 21.
    """
    def __init__(self, *streams):
        """Recibe los flujos destino de la escritura."""
        self.streams = streams

    def write(self, data):
        """Escribe `data` en todos los flujos."""
        for s in self.streams:
            s.write(data)

    def flush(self):
        """Vacía todos los flujos."""
        for s in self.streams:
            s.flush()


def paso(n, titulo):
    """Imprime el encabezado Markdown `### [n] titulo` de un paso de la bitácora."""
    # Antes usaba separadores de caracteres de dibujo de caja ('─'*74),
    # que se ven bien en una consola pero no significan nada en Markdown.
    # Como esta misma salida ahora se escribe tal cual a la bitácora .md
    # (ver Tee más arriba), el separador tiene que ser Markdown real.
    print(f"\n### [{n}] {titulo}\n")


def main():
    """CLI del turno completo G2 (monolítico): valida entorno y archivos, elige campaña y PJ, abre la bitácora Markdown (Tee) y delega en `_cuerpo_principal`."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--pj", default="PJ02")
    ap.add_argument("--turnos", type=int, default=1)
    ap.add_argument("--seco", action="store_true",
                    help="no escribe en la base; solo muestra qué haría")
    ap.add_argument("--campaign-id", default=None,
                    help="UUID de la campaña a usar. Si se omite, se usa "
                         "la campaña más antigua (comportamiento previo, "
                         "pensado para el fixture de desarrollo).")
    args = ap.parse_args()

    # Comprobar TODO lo necesario antes de gastar una sola llamada. La
    # primera versión descubría que DMIA_MODELO estaba vacío en el paso 4,
    # después de pagar el jugador y los dados.
    faltan = [v for v in ("DEEPINFRA_API_KEY", "DMIA_MODELO") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Falta en el entorno: {', '.join(faltan)}\n"
                 f"  DEEPINFRA_API_KEY  la clave de la API\n"
                 f"  DMIA_MODELO        p.ej. google/gemma-4-31B-it\n"
                 f"Carga el .env y comprueba que las variables tienen valor.")
    for nombre, ruta in (("prompt del jugador", RAIZ / "jugador" / "prompt.md"),
                         ("prompt de G2", RAIZ / "dm" / "prompt_g2.md"),
                         ("prompt del extractor", RAIZ / "extractor" / "prompt.md"),
                         ("contrato", RAIZ / "extractor" / "contrato.json"),
                         ("personajes", RAIZ / "jugador" / "personajes_jugadores.json")):
        if not ruta.exists():
            sys.exit(f"No encuentro el {nombre}: {ruta}")

    # ------------------------------------------------------------ 0. estado
    import psycopg
    with psycopg.connect(bd.DSN) as c:
        if args.campaign_id:
            r = c.execute("SELECT id, title FROM campaigns WHERE id = %s",
                         (args.campaign_id,)).fetchone()
            if not r:
                sys.exit(f"No existe la campaña {args.campaign_id}")
        else:
            r = c.execute("SELECT id, title FROM campaigns ORDER BY created_at LIMIT 1").fetchone()
            if not r:
                sys.exit("No hay campañas en la base. Carga fixtures/seed.sql")
    camp = bd.Campaña(r[0])
    cab = camp.cabecera()

    pjs = json.loads((RAIZ / "jugador" / "personajes_jugadores.json")
                     .read_text(encoding="utf-8"))["personajes"]
    pj = next(p for p in pjs if p["id"] == args.pj)
    # Guard contra el bug del extractor (ver QM - Respaldo bibliografico...,
    # "Implementación" punto 6): a veces crea un npc con el mismo nombre que
    # el propio PJ actuando (p.ej. "Nadia" como npc nuevo). Sin este filtro,
    # esa fila espuria contamina la detección de PNJ presentes y los
    # chequeos CL-2/CR-2, que tratan `ents` como si todo lo tipo "npc" fuera
    # realmente un PNJ.
    nombres_pj_conocidos = {p["nombre"] for p in pjs}

    prompt_jugador = (RAIZ / "jugador" / "prompt.md").read_text(encoding="utf-8")
    prompt_dm = (RAIZ / "dm" / "prompt_g2.md").read_text(encoding="utf-8")
    prompt_extractor = (RAIZ / "extractor" / "prompt.md").read_text(encoding="utf-8")
    contrato = json.loads((RAIZ / "extractor" / "contrato.json")
                          .read_text(encoding="utf-8"))

    # ------------------------------------------------------ bitácora .md
    # Antes la única forma de conservar la salida era que el usuario
    # capturara la consola con PowerShell (Tee-Object), y esa captura
    # llegaba corrupta (mojibake) porque la codificación de PowerShell no
    # es confiable para esto. Ahora el propio script escribe su bitácora
    # directamente en UTF-8, desde Python, sin pasar por la consola --
    # ver "QM - Respaldo bibliografico instrumentos deterministicos.md",
    # punto 21. Se genera SIEMPRE, no solo cuando el usuario se acuerda de
    # envolver el comando en Tee-Object.
    logs_dir = RAIZ / "logs"
    logs_dir.mkdir(exist_ok=True)
    marca = time.strftime("%Y%m%d_%H%M%S")
    # Punto 30 (bitácora QM): antes el nombre solo llevaba el campaign_id
    # corto, sin distinguir Par/arquitectura -- obligaba a renombrar a mano
    # para diferenciar Par01/02/03 de un vistazo. Ahora antepone un slug
    # del título real de la campaña, autodescriptivo desde que se genera.
    slug_titulo = _slug(cab["title"])
    nombre_log = re.sub(
        r"[^\w.-]+", "_",
        f"{slug_titulo}_{str(camp.campaign_id)[:8]}_"
        f"turnos_{cab['current_turn'] + 1}-{cab['current_turn'] + args.turnos}_{marca}.md")
    ruta_log = logs_dir / nombre_log
    archivo_log = open(ruta_log, "w", encoding="utf-8")
    stdout_original = sys.stdout
    sys.stdout = Tee(stdout_original, archivo_log)
    print(f"(bitácora en Markdown: {ruta_log})", file=stdout_original)

    try:
        print(f"\n# VERTICAL SLICE — {cab['title']} ({cab['architecture']})\n")
        print(f"- **DM:** `{MODELO_DM}`")
        print(f"- **jugador:** `{MODELO_JUGADOR}` ({pj['nombre']}, desvío {pj['desvio']})")
        print(f"- **turno:** {cab['current_turn'] + 1}"
              + ("  _(SECO — no se escribe nada)_" if args.seco else ""))

        _cuerpo_principal(args, camp, cab, pj, pjs, nombres_pj_conocidos,
                          prompt_jugador, prompt_dm, prompt_extractor,
                          contrato)
    finally:
        sys.stdout = stdout_original
        archivo_log.close()
        print(f"(bitácora guardada: {ruta_log})")


def _cuerpo_principal(args, camp, cab, pj, pjs, nombres_pj_conocidos,
                      prompt_jugador, prompt_dm, prompt_extractor,
                      contrato):
    """Bucle de turnos G2: contexto, jugador, dados, DM, extractor, apply_delta, validación del turno y costo por modelo."""
    # Mismo bug que en vertical_slice_g1.py (encontrado en Par 02 real,
    # 2026-09-15): este default venía hardcodeado a "Sargento Brea" (PNJ
    # del piloto "Vado de Ceniza") -- funcionaba por casualidad mientras
    # cada campaña nueva reutilizara ese nombre. Fix simétrico en ambos
    # brazos para no sesgar la comparación (mismo criterio que el fix de
    # affinity, puntos 16-19 de la bitácora QM). Arranca vacío -- el
    # primer PNJ real de la campaña se resuelve dentro del loop.
    presentes = []
    coste_por_modelo = {}

    def sumar_coste(modelo, r):
        """Acumula tokens de entrada y salida por modelo."""
        c = coste_por_modelo.setdefault(modelo, {"tin": 0, "tout": 0})
        c["tin"] += r["tin"]; c["tout"] += r["tout"]
    # Fijo ANTES del bucle: turn_id = turno_inicial + 1 + i. La línea de
    # abajo (cab["current_turn"] = turn_id) actualiza `cab` para que
    # game_day/current_turn reflejen el último turno escrito, pero si
    # esta fórmula leyera cab["current_turn"] en vez de turno_inicial,
    # cada turno sumaría su propio turn_id de más -- crecimiento
    # cuadrático (con 250 turnos, turn_id terminaba en ~31,400 en vez de
    # 250, lleno de huecos). Bug real, encontrado en la primera campaña
    # real del par 1 -- ver "QM - Respaldo bibliografico...", punto 19.
    turno_inicial = cab["current_turn"]

    for i in range(args.turnos):
        turn_id = turno_inicial + 1 + i

        # Contador de turno visible en vivo y en la bitácora (nuevo
        # 2026-09-16, pedido tras Par 02 real: sin esto, saber en qué
        # turno se cortó una corrida exigía reconstruirlo a mano contando
        # "### [1]" en el log). `grep "^## Turno " bitacora.md` da el
        # avance completo de una corrida de un vistazo.
        print(f"\n## Turno {turn_id} — {i+1}/{args.turnos} de esta corrida "
              f"(objetivo final de la campaña: {turno_inicial + args.turnos})\n")

        # ------------------------------------------------- 1. estado y escena
        paso(1, "ESTADO Y CONTEXTO (desde Postgres)")
        # game_day se refresca cada turno -- antes `cab` se leía una sola
        # vez fuera del bucle y quedaba desactualizado si un turno movía
        # el día de juego (nunca pasaba porque ese camino estaba roto,
        # ver el fix del paso 8; ahora que funciona, sí puede cambiar).
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
            # con la escena de apertura equivocada.
            sys.exit(
                f"No hay ningún turno registrado (turn_log) para la "
                f"campaña {camp.campaign_id} -- falta sembrar el turno 0 "
                f"(escena de apertura) antes de generar. No se arranca "
                f"con una escena por defecto.")
        escena = ultimo["dm_output"]

        # PNJ presentes: derivado de la escena, no hardcodeado (ver QM -
        # Respaldo bibliografico..., "Pendiente"). Un PNJ cuenta como
        # presente si su nombre completo o alguna palabra suelta de 3+
        # letras aparece en la escena que el jugador está a punto de
        # responder, y sigue con status alive. Si no se detecta ninguno
        # (escena puramente ambiental, o el DM no repitió el nombre), se
        # conserva la lista del turno anterior -- contexto_escena() sigue
        # necesitando saber de quién hablar, y vaciarla perdería el bond/
        # secreto/disposición que ya se estaba inyectando.
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
        if not antes:
            print("  (ningún PNJ conocido detectado en la escena todavía)")
        else:
            print(f"  {antes['name']}: {antes['status']}, aprecio "
                  f"{antes['affinity']} ({antes['banda']}), "
                  f"{antes['hechos']} hechos conocidos")
        # MUN-1/2 compartido (ver db.eventos_reloj_turno): lo que un reloj
        # disparó el turno anterior se narra AHORA, al abrir este turno.
        eventos_reloj = camp.eventos_reloj_turno(turn_id - 1) if turn_id > 1 else []
        ctx = camp.contexto_escena(presentes, eventos_reloj)
        print(f"  {len(ents)} entidades · contexto de {len(ctx)} caracteres")

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
        paso(3, "DADOS (deterministas, del sistema)")
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

        # ------------------------------------------------------------ 4. DM
        paso(4, "DM")
        cb = cab.get("content_boundaries") or {}
        rojas = cb.get("hard_lines") or []
        velos = cb.get("veils") or []
        limites = ("\nLÍMITES DE CONTENIDO\n"
                   + f"  líneas rojas (NUNCA aparecen): {', '.join(rojas) if rojas else 'ninguna declarada'}\n"
                   + f"  velos (se cortan en negro): {', '.join(velos) if velos else 'ninguno'}\n"
                   + "  No escales el material más allá de lo que el estado describe.\n"
                   + "  Si la base dice 'desalojo de puestos', es un desalojo de\n"
                   + "  puestos: no lo conviertas en algo peor.\n")
        user_dm = (f"CONFIGURACIÓN\n  tono: {cab['world_tone']} · registro: "
                   f"{cab['party_register']} · visibilidad de reglas: "
                   f"{cab['rules_visibility']}\n{limites}{ctx}\n"
                   f"ESCENA ACTUAL\n{escena}\n\n"
                   f"TURNO DEL JUGADOR\n{buffer_txt}")
        r = llamar(MODELO_DM, prompt_dm, user_dm, max_tokens=500, temp=0.8)
        if not r:
            sys.exit("El DM no respondió")
        sumar_coste(MODELO_DM, r)
        narracion = r["texto"]
        # Red de seguridad compartida con G1 (Par 18+, ver dados.META_OOC): si el
        # DM sale del papel ("[necesito que realices una tirada]") se regenera
        # hasta 2 veces; el texto meta NO debe entrar al historial (en Par 07-17
        # el 69 % de estos turnos venía justo después de otro: el DM se imitaba).
        reintentos_meta = 0
        while dados.es_meta_ooc(narracion) and reintentos_meta < 2:
            reintentos_meta += 1
            print(f"  ⚠ DM fuera de personaje: regenerando ({reintentos_meta}/2)")
            r2 = llamar(MODELO_DM, prompt_dm, user_dm + dados.AVISO_META,
                        max_tokens=500, temp=0.8)
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

        # ---------------------------------------------------- 5. verificación
        paso(5, "VERIFICACIÓN DE LA NARRACIÓN")
        problemas = []
        val = {"raw_flags": {}}
        if reintentos_meta:
            val["raw_flags"]["guard_meta_reintentos"] = reintentos_meta
        # El DM metió "[Tirada de Percepción necesaria... resuelvo la
        # reacción de la PNJ]" pese a tenerlo prohibido. El verificador
        # anterior no lo veía.
        if re.search(r"\[[^\]]{20,}\]", narracion):
            problemas.append("meta-comentario entre corchetes")
            val["raw_flags"]["meta_comentario"] = True
        if re.search(r"\b(tirada de \w+ necesaria|resuelvo la|como DM|"
                     r"seg[úu]n las reglas|no obstante,? al haber)\b",
                     narracion, re.I):
            problemas.append("comenta sus propias reglas")
            val["raw_flags"]["comenta_reglas"] = True

        # CR-1 (tier 1, precedente directo RPGBench MEC/ECE/VUE): veredicto
        # determinista real (pifia) contradicho por la narración.
        for t in tiradas:
            if t["pifia"] and re.search(r"\b(logras|consigues|aciertas|lo convences)\b",
                                        narracion, re.I):
                msg = f"pifia en {t['etiqueta']} pero narra éxito"
                problemas.append(msg)
                val["cr1_veredicto_contradice_narracion"] = True
                val["cr1_evidencia"] = msg

        # QN-2 (tier 1): pensamientos del PJ narrados (viola la regla de oro).
        m = re.search(rf"\b{re.escape(pj['nombre'])}\s+(piensa|siente|decide|comprende)",
                      narracion, re.I)
        if m:
            problemas.append("narra pensamientos del PJ (viola la regla de oro)")
            val["qn2_pj_piensa_narrado"] = True
            val["qn2_pj_piensa_evidencia"] = m.group(0)

        # QN-2 (tier 4, "revisar", nunca "problema" duro -- herramienta
        # general sin validación propia para esta tarea, como PredPatt):
        # el PJ ejecuta una acción física narrada sin tirada del sistema
        # detrás. Muchas acciones legítimamente no requieren tirada, así
        # que esto solo marca para revisión humana.
        m = re.search(rf"\b{re.escape(pj['nombre'])}\s+(ataca|golpea|convence|"
                      r"esquiva|salta|derriba|desarma)\b", narracion, re.I)
        if m and not tiradas:
            val["qn2_pj_accion_revisar"] = True
            val["qn2_pj_accion_evidencia"] = m.group(0)

        # CL-2 (tier 1, precedente FIREBALL "Removing Player Agency"): un
        # PNJ con status != alive narrado como si siguiera presente y activo.
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

        # CL-2 (tier 1, precedente FIREBALL "Hit Point Reasoning"): solo PC
        # -- npcs no tiene hp_current/hp_max en este esquema, solo status.
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

        # Tier 3 (proxy, JAMÁS booleano de fallo): continuidad léxica con la
        # escena anterior (ver corrección Barzilay & Lapata) y diversidad
        # léxica / repetición de n-gramas de la narración misma (Li et al.
        # 2016, siempre acompañado de otras métricas, nunca solo).
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

        # ---------------------------------------------------- 6. extractor
        paso(6, "EXTRACTOR")
        lista = "\n".join(f"  {e['nombre']:26s} {e['tipo']}" for e in ents)
        user_ex = (f"ENTIDADES EXISTENTES\n{lista}\n{ctx}\n"
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

        # ------------------------------------------- 7. validar antes de escribir
        paso(7, "VALIDACIÓN DE LO EXTRAÍDO")
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
            # Guarda añadida 2026-09-16 (auditoría diff G1/G2): mismo
            # patrón que el bug 1 de Par 02 real (delta del Mundo que no
            # era un objeto, en G1) -- ahí nunca se disparó porque el
            # extractor usa json_mode (esquema forzado), pero es la misma
            # clase de riesgo si el LLM alguna vez devuelve un elemento
            # suelto que no sea dict. Barato blindarlo ahora.
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
        validos_c = []
        for cr in creaciones:
            ev = cr.get("evidence", "") or ""
            nom = (cr.get("name") or "").strip()
            if cr.get("entity_type") not in CREABLES:
                print(f"  ✗ tipo no creable: {cr.get('entity_type')}")
            # Bug de raíz encontrado en la novena/décima pasada (ver "QM -
            # Respaldo bibliografico instrumentos deterministicos.md",
            # "Pendiente"): el extractor a veces propone un NPC con el
            # mismo nombre del PJ que está actuando -- create_entity() es
            # idempotente por nombre pero solo DENTRO de cada tabla
            # (npcs/characters), así que un "npc" y un "character" con
            # igual nombre no chocan a nivel de base y el duplicado se
            # crea igual. Antes esto solo se neutralizaba río abajo, en el
            # guard de CL-2 (turn_validation nunca lo marcaba "problema")
            # y en entidades_conocidas()/reporte_validacion.py (que igual
            # lo cuentan como candidato a protagonista de C/V, ver el caso
            # "Nadia" verificado en la novena pasada). Cortado acá, en la
            # raíz, antes de que la fila espuria llegue a existir.
            elif cr.get("entity_type") == "npc" and nom in nombres_pj_conocidos:
                print(f"  ✗ NPC propuesto coincide con un PJ existente "
                      f"({nom}), no se crea duplicado")
            # Punto 29 (bitácora QM): el guard de arriba solo cubría PJ vs
            # NPC nuevo -- no NPC-ya-sembrado vs NPC "nuevo" propuesto por
            # el extractor. Detectado en Par02 G1 (vertical_slice_g1.py),
            # pero el mismo hueco existe aquí; se corrige en los dos scripts
            # a la vez para no dejarlo abierto solo del lado G2.
            elif (cr.get("entity_type") == "npc"
                  and nom in {e["nombre"] for e in ents if e["tipo"] == "npc"}):
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

        # CR-2 (tier 2, dato estructurado -- matching contra la base, no NLI
        # de texto libre): nombres propios en la narración que no están en
        # la lista de entidades conocidas de la campaña. Stoplist mínimo
        # para no marcar inicios de frase o el propio PJ.
        # Nombres completos Y cada palabra suelta de >=3 letras ("Sargento
        # Brea" también matchea "Brea" a secas, que es como la narración
        # suele referirse a un PNJ después de presentarlo una vez).
        # `conocidos` ya se calculó al inicio del bucle (entidades_conocidas)
        # y se reutiliza acá tal cual, para no recalcularlo dos veces.
        STOP_MAYUS = {"El", "La", "Los", "Las", "Un", "Una", "Unos", "Unas",
                      "Cuando", "Si", "Pero", "Y", "Aunque", "Tras", "Al",
                      "Ella", "Él", "Sargento", "Vado", "Ceniza"}
        # No basta con \b[A-Z]...\b: el español capitaliza tras punto,
        # ¿/¡ y el guión largo de diálogo (—), y eso disparaba falsos
        # positivos ("Extiende", "Sus", "Tienes" tras "—") que no son
        # nombres propios. Se excluye toda palabra cuyo carácter previo
        # (ignorando espacios) sea un límite de oración/diálogo.
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

        # CL-1 (tier 2, dato estructurado): el extractor propuso un campo
        # que mutable_fields -- la verdad de la BASE, no el contrato.json
        # del LLM -- no reconoce como mutable para ese entity_type. Esto es
        # independiente del filtro de lista blanca del paso 7 (que ya usa
        # contrato.json): detecta drift entre el contrato del LLM y la base.
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

        # -------------------------------------------------------- 8. escribir
        paso(8, "ESCRITURA" + ("  [SECO — omitida]" if args.seco else ""))
        if not args.seco:
            camp.registrar_turno(turn_id, [{"pc": pj["id"], "text": accion}],
                                 narracion,
                                 bool(validos_ev or validos_d or validos_c))
            # turn_validation: requiere que la fila de turn_log ya exista
            # (FK compuesta contra turn_log(campaign_id, turn_id)), por eso
            # va justo después de registrar_turno y nunca en modo --seco.
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
            print(f"  → turn_validation registrado"
                  + (f" ⚠ {len(tier12)} problema(s) tier 1-2" if tier12 else
                     " (sin problemas tier 1-2)"))
            # Las creaciones van PRIMERO: un delta puede referirse a algo
            # que este mismo turno acaba de introducir.
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
                # RAISE EXCEPTION cualquier valor fuera de ese rango --
                # validación de dominio, no algo para "arreglar" del lado
                # de la base. Este clamp SÍ estaba en vertical_slice_g1.py
                # (bitácora QM puntos 16-19) pero, pese a que el vault
                # decía "corregido en ambos brazos", nunca llegó aquí --
                # descubierto recién en Par 02 real (2026-09-16) cuando
                # una racha de eventos ideal_honored sobre el mismo PNJ
                # llevó el acumulado a 103.0 y tumbó la corrida. Acotar
                # ANTES de escribir, igual que ya hace apply_delta con
                # LEAST(GREATEST(...)) para el resto de campos de
                # disposición. Fix ahora sí simétrico en los dos brazos.
                nuevo = max(-100.0, min(100.0,
                            float(antes["affinity"] or 0) + float(res["d_affinity"])))
                did = camp.aplicar("npc", nid, "affinity", nuevo, turn_id,
                                   "extracted", e["evidence"])
                print(f"  → delta {did}: {e['entity']} affinity "
                      f"{antes['affinity']} → {nuevo:.1f}  ({res['band']})")
                print(f"     {res['outcome'][:66]}")
            dias_transcurridos = 0
            for d in validos_d:
                # "world" no es una fila (id_de() no lo mapea a ninguna
                # tabla -- game_day vive en `campaigns`, apply_delta ya
                # lo sabe y no necesita entity_id). Llamar a id_de() con
                # "world" antes de este chequeo reventaba con KeyError;
                # nunca se disparó porque el extractor nunca había
                # emitido este delta todavía, pero el camino estaba roto.
                if d["entity_type"] == "world":
                    eid = None
                else:
                    eid = camp.id_de(d["entity_type"], d["entity"])
                    if not eid:
                        print(f"  ✗ entidad inexistente: {d['entity']}")
                        continue

                # Si el CAMPO mismo es una referencia (p.ej. npc.location_id
                # -> location), el extractor entrega el NOMBRE del lugar,
                # no su id -- igual que entity/entity_type arriba, pero
                # este resuelve el sujeto, no el valor. apply_delta castea
                # el value directo a uuid; sin esto, un nombre como
                # "El Mercado Bajo" revienta con InvalidTextRepresentation.
                # Nunca se había disparado porque el extractor nunca había
                # emitido antes un delta sobre un campo tipo "ref".
                valor = d["value"]
                campo_info = contrato["campos_directos"].get(
                    d["entity_type"], {}).get(d["field"], {})
                if campo_info.get("tipo") == "ref":
                    ref_id = camp.id_de(campo_info["entidad"], valor)
                    if not ref_id:
                        print(f"  ✗ referencia inexistente: "
                              f"{campo_info['entidad']} «{valor}»")
                        continue
                    # id_de() devuelve uuid.UUID (psycopg lo castea así al
                    # leer una columna uuid) y aplicar() hace
                    # json.dumps(value) -- UUID no es serializable a JSON.
                    # Nunca se había disparado porque el extractor nunca
                    # había emitido antes un delta sobre un campo tipo
                    # "ref" (ver comentario arriba).
                    valor = str(ref_id)

                try:
                    did = camp.aplicar(d["entity_type"], eid, d["field"],
                                       valor, turn_id, "extracted", d["evidence"])
                except Exception as e:
                    # Bug encontrado en Par 05 real (2026-09-18, turno ~3):
                    # el extractor puede proponer un campo que SÍ está en la
                    # lista blanca de contrato.json (por eso pasa el chequeo
                    # del paso 7) pero con un VALOR que la base rechaza por
                    # dominio/enum -- visto con location.state = "observed",
                    # que no es un valor válido para ese campo. Este loop de
                    # escritura de deltas del extractor es compartido de
                    # verdad por G1 y G2 (a diferencia del loop de deltas
                    # del Mundo, exclusivo de G1, que ya tenía esta misma
                    # protección desde Par 01 real) y no tenía ninguna red
                    # de seguridad -- tumbaba la corrida completa. Mismo
                    # criterio que ya se aplicó ahí: avisar y seguir, no
                    # abortar una corrida de 1,400 turnos por un valor que
                    # el extractor no debía proponer.
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

            # MUN-1/2, compartido con G1 (ver db.avanzar_relojes): si el
            # extractor marcó que pasaron días de juego, los relojes de
            # facción avanzan aquí mismo -- aritmética, no juicio del DM.
            # Lo que dispare se narra en el turno SIGUIENTE (paso 1 de la
            # próxima iteración lo recoge vía eventos_reloj_turno()).
            if dias_transcurridos > 0:
                # avanzar_relojes() devuelve columnas crudas de
                # advance_clocks() (clock_id, faction_id, agenda, event) --
                # sin el nombre de la facción, a diferencia de
                # eventos_reloj_turno() que sí hace el JOIN. No hace
                # falta el nombre aquí, solo confirmar qué disparó.
                disparados = camp.avanzar_relojes(dias_transcurridos, turn_id)
                for ev in disparados:
                    print(f"  ⏰ reloj disparado: agenda «{ev['agenda']}» "
                          f"(facción {ev['faction_id']})")
        else:
            print("  (nada escrito)")

        # Reloj del mundo determinista (db.sincronizar_dia): el día de juego
        # sale del turno, no del extractor (que nunca lo emitió en Par01-17).
        # Idéntico en G1. Va aparte del `if` de arriba: corre CADA turno.
        if not args.seco:
            for ev in camp.sincronizar_dia(turn_id):
                print(f"  ⏰ reloj disparado: agenda «{ev['agenda']}» "
                      f"(facción {ev['faction_id']})")

        # ------------------------------------------------------ 9. comprobar
        paso(9, "ESTADO DESPUÉS")
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


def ficha_jugador(pj):
    """Ficha del jugador agéntico como texto para su prompt: ejes en bandas, agenda, actitud ante lo urgente y ejemplares si existen."""
    p = pj["personalidad"]
    def b(v, neg, pos):
        """Etiqueta de un eje: `neg` si v < -40, `pos` si v > 40, "equilibrado" en medio."""
        return neg if v < -40 else pos if v > 40 else "equilibrado"
    def bd_(v):
        """Actitud ante lo urgente según el desvío (<=30 acude, <=60 mixto, >60 prioriza lo suyo)."""
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


if __name__ == "__main__":
    main()