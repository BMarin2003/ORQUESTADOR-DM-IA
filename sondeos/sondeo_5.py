r"""
SONDEO 5 — El jugador agéntico.

Genera el 100% del input de las 54 campañas. Si sale colaborativo y blando
—sigue los ganchos, nunca se desvía— entonces QN-2 (reactividad significativa
a la agencia del jugador) **no se ejerce nunca**, y se pierde uno de los seis
indicadores. Ambos brazos reciben el mismo input pobre, así que la comparación
técnicamente funciona pero mide menos de lo que debería.

Qué mide:

  DISCIPLINA (automático, determinista)
    · ¿inventa números de tirada?        ← lo más grave: sesga las 54 campañas
    · ¿usa {habilidad} para declarar?
    · ¿narra el mundo o decide su propio resultado?
    · ¿mete meta-comentarios?
    · ¿es breve?

  DESVÍO (comparativo)
    La misma escena a un personaje con desvio bajo y otro con desvio alto.
    Si ambos responden igual, el parámetro no hace nada y QN-2 no se ejerce.

  CARÁCTER (lectura humana)
    ¿La respuesta encaja con sus ejes de personalidad?

Uso:
  py sondeos\sondeo_5.py --modelo <modelo-jugador>
  py sondeos\sondeo_5.py --modelo X --personajes PJ02,PJ18,PJ25
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "jugador"))
import dados  # noqa: E402

BASE = "https://api.deepinfra.com/v1/openai"

# Escenas con gancho CLARO del DM. Si el agente lo sigue siempre, no hay
# agencia; si nunca lo sigue, es ruido. Lo que se busca es que dependa del
# personaje.
ESCENAS = [
    {
        "id": "E1",
        "_mide": "gancho explícito y urgente frente a los objetivos propios",
        "dm": ("El mensajero te alcanza en la puerta de la posada, sin aliento. "
               "\"El capitán te necesita en el puente. Ahora. Dice que si no vas "
               "antes del amanecer, no habrá puente al que ir.\" Se queda ahí, "
               "esperando tu respuesta, con el caballo ya girado hacia el camino. "
               "Al otro lado de la plaza, un vendedor ordena sin prisa un puesto "
               "de mapas viejos; lleva ahí toda la semana."),
    },
    {
        "id": "E2",
        "_mide": "presión moral: la opción eficiente contradice el carácter",
        "dm": ("El carcelero mira a un lado y a otro antes de hablar. \"Veinte "
               "coronas y la celda del fondo amanece abierta. Nadie pregunta, "
               "nadie firma nada.\" Dentro, el prisionero os observa sin decir "
               "palabra. No sabéis si es inocente."),
    },
    {
        "id": "E4",
        "_mide": ("control: gancho sin alternativa. NO mide desvío — negarse "
                  "significaría no hacer nada. Sirve para ver si el personaje "
                  "acepta limpiamente cuando no hay motivo para no hacerlo."),
        "dm": ("El capitán te espera en la puerta, con el caballo ensillado y "
               "otro de las riendas. \"Nos vamos al puente. Ahora.\" No hay nadie "
               "más en la calle, ni nada que hacer aquí. Solo él, los dos "
               "caballos, y la pregunta."),
    },
    {
        "id": "E3",
        "_mide": "escena muerta: ¿el jugador propone algo o espera?",
        "dm": ("La taberna está medio vacía. Llueve fuera. El posadero seca vasos "
               "sin mirar a nadie y el fuego está bajo. No pasa nada."),
    },
]


def cargar(rel):
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


PENSAMIENTO = re.compile(r"<think>.*?</think>", re.S | re.I)
VALLA = re.compile(r"^\s*```[a-z]*\s*$", re.M)

HABILIDADES = {
    "atletismo", "acrobacias", "juego de manos", "sigilo", "arcanos",
    "historia", "investigación", "naturaleza", "religión", "perspicacia",
    "medicina", "percepción", "supervivencia", "trato con animales",
    "engaño", "intimidación", "interpretación", "persuasión",
}


def llamar(key, modelo, system, user, max_tokens=500):
    """Desactiva el razonamiento: la familia Qwen3 lo trae ACTIVADO por
    defecto y se come el presupuesto de tokens antes de responder.

    Y para un jugador es doblemente inadecuado: un jugador reacciona, no
    delibera media página. A 39.000 llamadas eso se paga en cada turno."""
    cuerpo = {"model": modelo,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user + "\n\n/no_think"}],
              "temperature": 0.8, "max_tokens": max_tokens,
              "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps(cuerpo).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        det = e.read().decode()[:200]
        if "chat_template_kwargs" in det or e.code == 422:
            cuerpo.pop("chat_template_kwargs", None)
            req2 = urllib.request.Request(
                f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req2, timeout=180) as r:
                d = json.loads(r.read().decode())
        else:
            print(f"  HTTP {e.code}: {det}", file=sys.stderr)
            return None
    msg = d["choices"][0]["message"]
    bruto = (msg.get("content") or "")
    razono = bool(PENSAMIENTO.search(bruto)) or bool(msg.get("reasoning_content"))
    limpio = VALLA.sub("", PENSAMIENTO.sub("", bruto)).strip()
    # Restos de un <think> truncado por max_tokens
    if limpio.lower().startswith("<think>"):
        limpio = ""
    return {"texto": limpio, "razono": razono,
            "vacio_por_razonamiento": razono and not limpio,
            "tin": d.get("usage", {}).get("prompt_tokens") or 0,
            "tout": d.get("usage", {}).get("completion_tokens") or 0,
            "ms": round((time.time() - t0) * 1000)}


# --- patrones de indisciplina ---------------------------------------------
# El jugador NO decide cómo reacciona un PNJ. Cualquier verbo en tercera
# persona con un PNJ como sujeto es narrar el mundo.
NARRA_MUNDO = re.compile(
    r"\b(?:el|la|los|las)\s+"
    r"(?:posader[oa]|carceler[oa]|mensajer[oa]|guardias?|vendedor(?:a)?|"
    r"capit[áa]n|prisioner[oa]|tabernero|mercader(?:es)?|clientes?)\s+"
    r"(?:\w+\s+){0,2}"
    r"(?:asiente|responde|sonríe|mira|levanta|contesta|acepta|niega|frunce|"
    r"se\s+r[íi]e|se\s+gira|se\s+acerca|dice|habla|calla|duda|obedece|"
    r"retrocede|apart[ao]|entrega|saca|guarda)", re.I)
DECIDE_RESULTADO = re.compile(
    r"\b(?:consigo|logro|lo consigo|acierto|tengo éxito|funciona|"
    r"me sale bien|lo convenzo|lo intimido con éxito)\b", re.I)
# Hablarse a sí mismo por su nombre: rompe la primera persona.
def detecta_autodirigirse(texto, nombre, otros=()):
    """Se dirige a sí mismo, o peor: se llama con el nombre de OTRO personaje.

    Senna abrió un turno con "¿Cuál es el plan, Maelis?" — no solo se habla a
    sí misma, sino que usa el nombre de otro PJ. La versión anterior solo
    buscaba su propio nombre y no lo veía."""
    nombres = [nombre] + [n for n in otros if n and n != nombre]
    for n in nombres:
        if re.search(rf"[\"«,]\s*{re.escape(n)}\s*[\"».?!]", texto):
            return True
        if re.search(rf"\b{re.escape(n)}\s*,\s*(?:no|s[íi]|ven|espera|vamos|qu[ée])",
                     texto, re.I):
            return True
    return False


# Plural de grupo: el MVP es un solo jugador, no hay compañeros.
PLURAL_GRUPO = re.compile(
    r"\b(?:nos\s+(?:deje|dejen|vamos|acercamos|quedamos)|"
    r"estemos|tenemos que|vayamos|nuestro grupo|mis compañeros|"
    r"¿vamos|no podemos quedarnos)\b", re.I)

# Árbol de decisión: el jugador debe hacer UNA cosa y esperar.
CONDICIONAL = re.compile(
    r"\bsi\s+(?:el|la|los|las|me|no|hay|acepta|accede|responde|se\s|"
    r"parece|sale|cuenta|dice)\b.{0,70}?[,:]\s*"
    r"(?:\{|intento|pregunto|me\s|le\s|lo\s|a[ñn]ado|insisto|negocio|vuelvo|voy)",
    re.I)

META = re.compile(
    r"\b(?:como jugador|mi personaje (?:haría|debería)|creo que el (?:dm|máster)|"
    r"la trama|el sistema|esta escena|narrativamente)\b", re.I)
DIALOGO = re.compile(r"[\"«][^\"»]{3,}[\"»]")

# El jugador escribe la RÉPLICA de un PNJ: se está montando la escena entera.
# Frases entre comillas que solo un PNJ diría, o narración atribuyéndoselas.
REPLICA_PNJ = re.compile(
    r"(?:dice|responde|contesta|replica|añade)\s+el\s+\w+|"
    r"[\"«]\s*(?:no es asunto tuyo|o pagas|no tengo todo el día|"
    r"eso no te incumbe|lárgate|ya te he dicho)", re.I)


def solapamiento_dm(texto, dm, minimo=8):
    """El jugador abre citando literalmente al DM.

    Senna lo hizo en dos de las tres últimas corridas: repetía el párrafo
    entero del carcelero antes de responder. Se detecta buscando la secuencia
    literal más larga compartida."""
    a, b = texto.split(), dm.split()
    mejor = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while (i + k < len(a) and j + k < len(b)
                   and a[i + k].lower().strip('.,"«»¿?¡!') ==
                       b[j + k].lower().strip('.,"«»¿?¡!')):
                k += 1
            mejor = max(mejor, k)
    return mejor >= minimo, mejor


def revisar(texto, nombre="", otros=(), dm=""):
    habs = dados.extraer_habilidades(texto)
    validas = {dados.normalizar(x) for x in HABILIDADES}
    inventadas = [h for h in habs
                  if dados.normalizar(h.split(" para ")[0]) not in validas]
    return {
        "habilidad_inventada": bool(inventadas),
        "inventadas": inventadas,
        "autodirigirse": (detecta_autodirigirse(texto, nombre, otros)
                          if nombre else False),
        "plural_grupo": bool(PLURAL_GRUPO.search(texto)),
        "condicional": bool(CONDICIONAL.search(texto)),
        "replica_pnj": bool(REPLICA_PNJ.search(texto)),
        "cita_al_dm": solapamiento_dm(texto, dm)[0] if dm else False,
        # Recita la instrucción en vez de jugarla.
        # Umbral alto: 6 palabras contra un documento de 130 líneas dispara
        # solo. Con 10 seguidas ya es recitación real, no coincidencia.
        "recita_prompt": (solapamiento_dm(texto, globals().get("_PROMPT", ""),
                                          minimo=10)[0]
                          if globals().get("_PROMPT") else False),
        "dado_inventado": dados.detecta_dado_inventado(texto),
        "declara_habilidad": bool(habs),
        "habilidades": habs,
        "narra_mundo": bool(NARRA_MUNDO.search(texto)),
        "decide_resultado": bool(DECIDE_RESULTADO.search(texto)),
        "meta": bool(META.search(texto)),
        "tiene_dialogo": bool(DIALOGO.search(texto)),
        "palabras": len(texto.split()),
    }


def banda_desvio(v):
    """El modelo no ve el número: ve la conducta.

    Mismo principio que las bandas de disposición de los PNJ. Pasar
    'desvio: 20' obliga al modelo a conectar un número con una descripción
    que está a varios párrafos de distancia, y no lo hace."""
    if v <= 30:
        return ("Si el DM plantea algo urgente, VAS. Puedes fijarte en otras "
                "cosas de pasada, pero atiendes primero lo que se te pide. "
                "No antepones lo tuyo a lo urgente.")
    if v <= 60:
        return ("Atiendes lo urgente, pero te tomas un momento para lo que te "
                "interesa, antes o después.")
    return ("Lo urgente del DM es una opción más. Si algo tuyo está en juego, "
            "va primero: lo urgente puede esperar, o servirte de excusa.")


def ejemplares_texto(pj):
    """Los ejemplos PROPIOS del personaje, no un ejemplo compartido.

    El ejemplo compartido enseñaba postura, no formato: los tres personajes
    copiaban la actitud desafiante del único ejemplo del prompt. Ver
    generar_ejemplares.py."""
    ej = pj.get("ejemplares")
    if not ej:
        return ""
    return f"""
ASÍ JUEGAS TÚ

  Cuando alguien con autoridad te pide algo urgente:
    {ej['urgente']}

  Cuando ves algo que conecta con lo tuyo:
    {ej['propio']}

  Cuando no pasa nada:
    {ej['vacia']}
"""


def ficha_texto(pj):
    p = pj["personalidad"]
    def banda(v, neg, pos):
        return neg if v < -40 else pos if v > 40 else "equilibrado"
    return f"""TU FICHA
  {pj['nombre']}, {pj['arquetipo'].lower()}. {pj['clase']} nivel {pj['nivel']},
  trasfondo {pj['trasfondo']}.

  Cómo eres:
    trato        {banda(p['warmth'], 'frío y calculador', 'cálido y afectuoso')}
    franqueza    {banda(p['candor'], 'disimulado, no dices lo que piensas', 'franco, dices lo que piensas')}
    principios   {banda(p['principle'], 'pragmático, el fin justifica los medios', 'principista, hay líneas que no cruzas')}
    temple       {banda(p['boldness'], 'cauto, no te expones', 'audaz, vas de frente')}

TUS OBJETIVOS PROPIOS
""" + "\n".join(f"  - {o}" for o in pj["agenda"]) + f"""

CÓMO TE TOMAS LO QUE EL DM PLANTEA
  {banda_desvio(pj['desvio'])}
""" + ejemplares_texto(pj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True,
                    help="Modelo DISTINTO al del DM. Ver --listar en verificar_modelo.py")
    ap.add_argument("--personajes", default=None,
                    help="ids separados por coma; por defecto uno de cada banda de desvío")
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY. Carga el .env primero.")

    prompt = (RAIZ / "jugador" / "prompt.md").read_text(encoding="utf-8")
    globals()["_PROMPT"] = prompt
    todos = cargar("jugador/personajes_jugadores.json")["personajes"]

    if args.personajes:
        ids = {x.strip() for x in args.personajes.split(",")}
        pjs = [p for p in todos if p["id"] in ids]
    else:
        bajo = min(todos, key=lambda p: p["desvio"])
        alto = max(todos, key=lambda p: p["desvio"])
        mut = next(p for p in todos if p.get("deriva"))
        pjs = [bajo, alto, mut]

    print(f"\n{'='*74}\nSONDEO 5 · JUGADOR AGÉNTICO · {args.modelo}\n{'='*74}")
    for p in pjs:
        print(f"  {p['id']} {p['nombre']:9s} {p['arquetipo']:26s} desvio={p['desvio']}"
              + ("  [gris mutable]" if p.get("deriva") else ""))

    registro = []
    fallos = {"dado_inventado": 0, "narra_mundo": 0, "decide_resultado": 0,
              "meta": 0, "habilidad_inventada": 0, "autodirigirse": 0,
              "plural_grupo": 0, "condicional": 0, "replica_pnj": 0,
              "cita_al_dm": 0, "recita_prompt": 0, "razono": 0, "vacio": 0}
    tin = tout = 0

    for esc in ESCENAS:
        print(f"\n{'-'*74}\n{esc['id']} · {esc['_mide']}\n{'-'*74}")
        print(f"DM: {esc['dm'][:150]}...\n")

        for pj in pjs:
            user = (ficha_texto(pj) + "\nEL DM ACABA DE DECIR\n" + esc["dm"]
                    + "\n\n¿Qué haces?")
            r = llamar(key, args.modelo, prompt, user)
            if not r:
                continue
            tin += r["tin"]; tout += r["tout"]
            c = revisar(r["texto"], pj["nombre"],
                        [x["nombre"] for x in todos], esc["dm"])
            for k in ("dado_inventado", "narra_mundo", "decide_resultado",
                      "meta", "habilidad_inventada", "autodirigirse",
                      "plural_grupo", "condicional", "replica_pnj",
                      "cita_al_dm", "recita_prompt"):
                fallos[k] += c[k]
            fallos["razono"] += r["razono"]
            fallos["vacio"] += r["vacio_por_razonamiento"]
            if r["vacio_por_razonamiento"]:
                print(f"  {pj['id']} {pj['nombre']}: RESPUESTA VACÍA — el modelo "
                      f"gastó {r['tout']} tokens razonando y no llegó a responder")
                registro.append({"escena": esc["id"], "pj": pj["id"],
                                 "desvio": pj["desvio"], "texto": "", "checks": c})
                continue

            print(f"  {pj['id']} {pj['nombre']} (desvio {pj['desvio']}) · "
                  f"{c['palabras']} palabras · {r['ms']} ms")
            for linea in r["texto"].splitlines():
                if linea.strip():
                    print(f"      {linea}")

            marcas = []
            if c["dado_inventado"]:
                marcas.append("✗ INVENTÓ UN DADO")
            if c["narra_mundo"]:
                marcas.append("✗ narra el mundo")
            if c["decide_resultado"]:
                marcas.append("✗ decide su resultado")
            if c["meta"]:
                marcas.append("✗ meta-comentario")
            if c["habilidad_inventada"]:
                marcas.append(f"✗ habilidad inexistente {c['inventadas']}")
            if c["autodirigirse"]:
                marcas.append("✗ se habla a sí mismo por su nombre")
            if c["plural_grupo"]:
                marcas.append("✗ habla en plural (no hay grupo)")
            if c["condicional"]:
                marcas.append("✗ árbol de decisión en vez de actuar")
            if c["replica_pnj"]:
                marcas.append("✗ escribe la réplica de un PNJ")
            if c["cita_al_dm"]:
                marcas.append("✗ cita literalmente al DM")
            if c["recita_prompt"]:
                marcas.append("✗ recita la instrucción del prompt")
            if c["palabras"] > 55:
                marcas.append(f"! largo ({c['palabras']} palabras)")
            if c["declara_habilidad"]:
                marcas.append(f"✓ declara {c['habilidades']}")
            if not marcas:
                marcas.append("✓ limpio")
            print(f"      → {'  '.join(marcas)}")

            # Simular la resolución: así se ve lo que recibiría el DM
            if c["declara_habilidad"]:
                texto_dm, tiradas, rechazadas = dados.resolver_turno(
                    r["texto"], "sondeo5", esc["id"])
                for h in rechazadas:
                    print(f"      dado: {h} NO EXISTE — no se tira")
                for t in tiradas:
                    print(f"      dado: {t['etiqueta']} {t['dado']}+{t['modificador']}"
                          f"={t['total']}" + (" CRÍTICO" if t["critico"] else
                                              " PIFIA" if t["pifia"] else ""))
            print()
            registro.append({"escena": esc["id"], "pj": pj["id"],
                             "desvio": pj["desvio"], "texto": r["texto"], "checks": c})

    print(f"{'='*74}\nCOLAPSO DE PERSONAJE\n{'='*74}")
    print("  Si varios personajes responden casi igual a la MISMA escena, el")
    print("  prompt está dictando la respuesta en vez de la ficha. Es el fallo")
    print("  más grave posible: CL-1 mide precisamente que se diferencien.\n")
    colapsos = 0
    for esc in ESCENAS:
        filas = [x for x in registro if x["escena"] == esc["id"] and x["texto"]]
        for i in range(len(filas)):
            for j in range(i + 1, len(filas)):
                ta, tb = filas[i]["texto"], filas[j]["texto"]
                _, n = solapamiento_dm(ta, tb, minimo=10 ** 9)
                corto = min(len(ta.split()), len(tb.split()))
                # La APERTURA es donde vive la postura del personaje. Dos
                # respuestas largas pueden compartir solo las primeras nueve
                # palabras y aun así haber colapsado en lo que importa.
                pa = " ".join(ta.split()[:12])
                pb = " ".join(tb.split()[:12])
                _, na = solapamiento_dm(pa, pb, minimo=10 ** 9)
                colapso_apertura = na >= 7
                if (corto and n / corto > 0.6) or colapso_apertura:
                    colapsos += 1
                    donde = "en la APERTURA" if colapso_apertura else "en el cuerpo"
                    print(f"  ⚠ {esc['id']}: {filas[i]['pj']} y {filas[j]['pj']} "
                          f"colapsan {donde} — {max(n, na)} palabras seguidas")
                    print(f"      {filas[i]['pj']}: «{pa[:62]}»")
                    print(f"      {filas[j]['pj']}: «{pb[:62]}»")
    if not colapsos:
        print("  Sin colapsos: cada personaje responde con sus palabras.")
    else:
        print("\n  OJO: un colapso puede ser CONVERGENCIA LÉXICA, no")
        print("  contaminación. Si dos personajes deciden lo mismo, hay una")
        print("  forma obvia de decirlo en español y coinciden. Comprueba si")
        print("  la frase aparece en el prompt o en los ejemplares antes de")
        print("  tratarlo como fallo.")

    print(f"{'='*74}\nDISCIPLINA\n{'='*74}")
    n = len(registro)
    for k, v in fallos.items():
        estado = "ok" if v == 0 else f"⚠ {v}/{n}"
        print(f"  {k:20s} {estado}")
    decl = sum(1 for x in registro if x["checks"]["declara_habilidad"])
    dial = sum(1 for x in registro if x["checks"]["tiene_dialogo"])
    med = sum(x["checks"]["palabras"] for x in registro) / max(n, 1)
    print(f"  {'declara habilidad':20s} {decl}/{n}")
    print(f"  {'usa diálogo':20s} {dial}/{n}")
    print(f"  {'palabras (media)':20s} {med:.0f}")

    e4 = sorted([x for x in registro if x["escena"] == "E1"],
                key=lambda y: y["desvio"])
    if len(e4) >= 2:
        print(f"\n{'='*74}\nVEREDICTO DEL DESVÍO (E1: gancho CON alternativa real)")
        print(f"{'='*74}")
        print("  El desvío solo se puede medir cuando negarse lleva a algo.")
        print("  En E4 no hay alternativa, así que no discrimina: es control.\n")
        ACEPTA = re.compile(r"\b(voy|ir[ée]|vamos|monto|subo|salgo|recojo|"
                            r"de acuerdo|ahora mismo|enseguida|acompa[ñn]o|"
                            r"sigo|sin perder tiempo)\b", re.I)
        RECHAZA = re.compile(r"\b(puede esperar|no pienso|no voy a|que espere|"
                             r"m[áa]s tarde|no me da la gana|en un rato|luego|"
                             r"despacito|primero (?:voy|quiero|tengo|me))\b", re.I)
        for x in e4:
            t = x["texto"]
            postura = ("rechaza" if RECHAZA.search(t) else
                       "acepta" if ACEPTA.search(t) else "ambigua")
            esperado = ("acepta" if x["desvio"] <= 30 else
                        "rechaza" if x["desvio"] > 60 else "-")
            marca = "ok " if esperado in ("-", postura) else "⚠  "
            print(f"  {marca}desvio {x['desvio']:>3} → {postura:8s} "
                  f"(esperado {esperado})")
            print(f"       {next((l for l in t.splitlines() if l.strip()), '')[:66]}")
        bajo = [x for x in e4 if x["desvio"] <= 30]
        alto = [x for x in e4 if x["desvio"] > 60]
        if bajo and alto:
            b = RECHAZA.search(bajo[0]["texto"]) is None
            a = RECHAZA.search(alto[0]["texto"]) is not None
            print(f"\n  {'El desvío SÍ diferencia sin distracción.' if b and a else ''}"
                  f"{'El desvío NO diferencia ni con el gancho limpio.' if not (b and a) else ''}")
            if not (b and a):
                print("  Revisa los ejemplares del personaje: si el suyo no")
                print("  diferencia, tampoco lo hará en juego. Ver")
                print("  generar_ejemplares.py.")

    print(f"\n{'='*74}\nDESVÍO\n{'='*74}")
    for esc in ESCENAS:
        filas = [x for x in registro if x["escena"] == esc["id"]]
        if len(filas) < 2:
            continue
        print(f"\n  {esc['id']}:")
        for x in sorted(filas, key=lambda y: y["desvio"]):
            primera = next((l for l in x["texto"].splitlines()
                            if l.strip() and not l.strip().startswith("<")), "(vacío)")
            print(f"    desvio {x['desvio']:>3}  {primera[:64]}")

    coste = (tin * 0.09 + tout * 0.34) / 1e6
    print(f"\n  {n} respuestas · {tin}→{tout} tokens · ${coste:.4f}")

    destino = RAIZ / f"sondeo5_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    json.dump({"modelo": args.modelo, "fecha": datetime.now().isoformat(),
               "fallos": fallos, "registro": registro},
              open(destino, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"  detalle en {destino.name}")

    print("\nLECTURA")
    if fallos["vacio"]:
        print(f"  ⚠ {fallos['vacio']}/{n} respuestas VACÍAS por razonamiento.")
        print("    El modelo gastó el presupuesto pensando. Si persiste tras")
        print("    desactivar el pensamiento, elige un modelo sin razonamiento")
        print("    híbrido: Qwen2.5-72B-Instruct o Hermes-3-Llama-3.1-70B.")
    elif fallos["razono"]:
        print(f"  ! {fallos['razono']}/{n} razonaron pero sí respondieron.")
        print("    Funciona, pero encarece cada turno de las 54 campañas.")
    if fallos["dado_inventado"]:
        print("  ⚠ Inventó números de tirada. Es el fallo grave: sesgaría las")
        print("    54 campañas de forma invisible. Reforzar la prohibición.")
    print("  Lo que decide el sondeo lo juzgas tú leyendo: ¿los personajes de")
    print("  desvío alto y bajo responden distinto a la MISMA escena? Si no,")
    print("  el parámetro no hace nada y QN-2 no se ejercerá en las campañas.")


if __name__ == "__main__":
    main()