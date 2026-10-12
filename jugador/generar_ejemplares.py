r"""
Genera ejemplares PROPIOS de cada personaje, una sola vez.

Por qué:
  El prompt del jugador llevaba un único ejemplo de turno, y los modelos
  copiaban su POSTURA, no su formato. La frase "no pienso pagar dos veces por
  el mismo puente" apareció literal en dos modelos distintos, y los tres
  personajes —principle +88, +60 y −45, desvío 20, 40 y 85— acabaron todos
  rechazando al capitán.

  Un solo ejemplo no enseña formato: enseña conducta.

Adaptación de Analogical Prompting (Yasunaga et al., ICLR 2024), que hace que
el modelo autogenere ejemplares en vez de recibirlos fijos, y que reporta que
los ejemplares diversos evitan el sobreajuste a los ejemplos.

  Analogical Prompting puro genera ejemplares en CADA problema. Aquí eso
  serían 39.000 generaciones extra, y además contradice el "sé breve, actúa
  en vez de deliberar" que el jugador necesita.

  Variante: generar una sola vez por personaje. 27 llamadas en total. Cada
  personaje lleva SUS ejemplos, derivados de SU ficha, así que no hay un
  ejemplo compartido del que copiar y los ejemplares no pueden contradecir
  la ficha.

Uso:
  py jugador\generar_ejemplares.py --modelo "NousResearch/Hermes-3-Llama-3.1-70B"
  py jugador\generar_ejemplares.py --modelo X --solo PJ02,PJ18
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://api.deepinfra.com/v1/openai"

SISTEMA = """Escribes ejemplos de turnos de un jugador de D&D, para que ese
mismo jugador los tenga como referencia de su propio estilo.

Recibes la ficha de un personaje. Escribes TRES turnos suyos, uno por cada
situación que se te indica. Cada turno debe sonar a ESE personaje concreto:
sus principios, su franqueza, su temple y su forma de tomarse lo que le
piden.

FORMATO DE CADA TURNO
  "Lo que dice en voz alta"
  Lo que hace, en primera persona.
  {Habilidad}      ← opcional, solo si la acción requiere tirada

  Máximo 40 palabras por turno. Una acción, sin condicionales ni "si pasa X".
  Nunca narres cómo reaccionan los demás ni el resultado de tu acción.

Habilidades válidas: Atletismo, Acrobacias, Juego de Manos, Sigilo, Arcanos,
Historia, Investigación, Naturaleza, Religión, Perspicacia, Medicina,
Percepción, Supervivencia, Trato con Animales, Engaño, Intimidación,
Interpretación, Persuasión.

SALIDA
  JSON exacto, sin markdown ni explicaciones:
  {"urgente": "...", "propio": "...", "vacia": "..."}
"""


def cargar(rel):
    """Lee un JSON relativo a la raíz del proyecto."""
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


def banda(v, neg, pos):
    """Etiqueta de un eje de personalidad: `neg` si v < -40, `pos` si v > 40, "equilibrado" en medio."""
    return neg if v < -40 else pos if v > 40 else "equilibrado"


def banda_desvio(v):
    """Texto sobre cómo se toma el personaje lo urgente, según su desvío (<=30 acude, <=60 mixto, >60 prioriza lo suyo)."""
    if v <= 30:
        return ("Cuando le piden algo urgente, VA. Atiende primero lo que se "
                "le pide y deja lo suyo para después.")
    if v <= 60:
        return ("Atiende lo urgente, pero se toma un momento para lo suyo, "
                "antes o después.")
    return ("Lo urgente de otros es una opción más. Si algo suyo está en "
            "juego, va primero.")


def peticion(pj):
    """Prompt de usuario con la ficha del personaje (ejes en bandas, agenda y desvío) para que el modelo escriba sus tres ejemplares."""
    p = pj["personalidad"]
    return f"""FICHA
  {pj['nombre']}, {pj['arquetipo'].lower()}. {pj['clase']} nivel {pj['nivel']},
  trasfondo {pj['trasfondo']}.

  trato        {banda(p['warmth'], 'frío y calculador', 'cálido y afectuoso')}
  franqueza    {banda(p['candor'], 'disimulado, no dice lo que piensa', 'franco, dice lo que piensa')}
  principios   {banda(p['principle'], 'pragmático, el fin justifica los medios', 'principista, hay líneas que no cruza')}
  temple       {banda(p['boldness'], 'cauto, no se expone', 'audaz, va de frente')}

  Objetivos propios:
""" + "\n".join(f"    - {o}" for o in pj["agenda"]) + f"""

  Cómo se toma lo que le piden:
    {banda_desvio(pj['desvio'])}

ESCRIBE TRES TURNOS SUYOS

  "urgente"  Alguien con autoridad le pide ir a un sitio ahora mismo, por algo
             grave, y hay otra cosa que a él le interesa más aquí mismo.

             **Su forma de tomarse lo que le piden decide la respuesta, y no
             es negociable:**
               · Si VA cuando le piden → el turno empieza aceptando y va.
               · Si atiende pero se toma un momento → acepta y luego se
                 desvía a lo suyo.
               · Si lo urgente de otros es una opción más → **SE NIEGA o lo
                 pospone**, y va a lo suyo primero. No acepta por educación.

  "propio"   Nadie le pide nada, pero ve algo que conecta con uno de sus
             objetivos propios. ¿Cómo lo aborda?

  "vacia"    Una escena sin nada que hacer: una sala tranquila, gente que no
             habla. ¿Qué propone para que pase algo?
"""


def llamar(key, modelo, system, user, max_tokens=700):
    """Llama a chat/completions de DeepInfra con temperatura 0.9; si rechaza `chat_template_kwargs` (422) reintenta sin él. Devuelve `{texto, tin, tout}` o None ante otro error HTTP."""
    cuerpo = {"model": modelo,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user + "\n\n/no_think"}],
              "temperature": 0.9, "max_tokens": max_tokens,
              "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        det = e.read().decode()[:200]
        if "chat_template_kwargs" in det or e.code == 422:
            cuerpo.pop("chat_template_kwargs", None)
            req = urllib.request.Request(
                f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read().decode())
        else:
            print(f"    HTTP {e.code}: {det}", file=sys.stderr)
            return None
    return {"texto": d["choices"][0]["message"]["content"],
            "tin": d.get("usage", {}).get("prompt_tokens") or 0,
            "tout": d.get("usage", {}).get("completion_tokens") or 0}


def parsear(texto):
    """Extrae el JSON de la respuesta (sin vallas ni `<think>`) y devuelve las claves urgente/propio/vacia como texto, o None si falta alguna."""
    limpio = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    limpio = re.sub(r"<think>.*?</think>", "", limpio, flags=re.S | re.I).strip()
    try:
        o = json.loads(limpio)
    except Exception:
        m = re.search(r"\{.*\}", limpio, re.S)
        if not m:
            return None
        try:
            o = json.loads(m.group(0))
        except Exception:
            return None
    if not all(k in o for k in ("urgente", "propio", "vacia")):
        return None
    return {k: str(o[k]).strip() for k in ("urgente", "propio", "vacia")}


# El modelo a veces devuelve la plantilla del formato en vez de contenido.
BASURA = re.compile(r"lo que (?:dice|haces?) en voz alta|"
                    r"\{Habilidad\}|lo que haces, en primera persona|"
                    r"^\s*<.*>\s*$", re.I)


def valido(ej):
    """Un ejemplar que repite la plantilla envenena al personaje durante toda
    su campaña. Se rechaza y se reintenta."""
    for k, v in ej.items():
        if not v or len(v.split()) < 5:
            return False, f"{k} demasiado corto"
        if BASURA.search(v):
            return False, f"{k} repite la plantilla"
    return True, ""


ACEPTA = re.compile(r"\b(voy|ir[ée]|vamos|ahora mismo|salgo|recojo|monto|"
                    r"me pongo en marcha|enseguida|de acuerdo|sin perder tiempo|"
                    r"acompa[ñn]o|sigo)\b", re.I)
RECHAZA = re.compile(r"\b(puede esperar|no pienso|no voy a ir|que espere|"
                     r"m[áa]s tarde|no me da la gana|primero (?:voy|quiero|"
                     r"tengo)|en un rato|luego|despacito|no corro)\b", re.I)


def main():
    """CLI: genera con el modelo los ejemplares de cada personaje (hasta 3 intentos), contrasta su postura con el desvío esperado y reescribe personajes_jugadores.json."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--solo", default=None)
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY. Carga el .env primero.")

    datos = cargar("jugador/personajes_jugadores.json")
    pjs = datos["personajes"]
    if args.solo:
        ids = {x.strip() for x in args.solo.split(",")}
        objetivo = [p for p in pjs if p["id"] in ids]
    else:
        objetivo = pjs

    print(f"\n{'='*74}\nEJEMPLARES POR PERSONAJE · {args.modelo}")
    print(f"{len(objetivo)} personajes · una llamada cada uno\n{'='*74}")

    tin = tout = fallos = 0
    for pj in objetivo:
        ej = None
        for intento in range(3):
            r = llamar(key, args.modelo, SISTEMA, peticion(pj))
            if not r:
                continue
            tin += r["tin"]; tout += r["tout"]
            cand = parsear(r["texto"])
            if not cand:
                continue
            ok, motivo = valido(cand)
            if ok:
                ej = cand
                break
            if intento == 2:
                print(f"  ✗  {pj['id']} {pj['nombre']:9s} descartado: {motivo}")
        if not ej:
            print(f"  ✗  {pj['id']} {pj['nombre']:9s} sin ejemplares tras 3 intentos")
            fallos += 1
            continue
        pj["ejemplares"] = ej

        postura = ("acepta" if ACEPTA.search(ej["urgente"]) else
                   "rechaza" if RECHAZA.search(ej["urgente"]) else "ambigua")
        esperado = ("acepta" if pj["desvio"] <= 30 else
                    "rechaza" if pj["desvio"] > 60 else "cualquiera")
        marca = "ok " if esperado in ("cualquiera", postura) else "⚠  "
        print(f"  {marca}{pj['id']} {pj['nombre']:9s} desvio {pj['desvio']:>3} · "
              f"{postura:8s} (esperado {esperado})")
        print(f"       urgente: {ej['urgente'][:78].splitlines()[0]}")

    datos["_ejemplares_modelo"] = args.modelo
    destino = RAIZ / "jugador" / "personajes_jugadores.json"
    json.dump(datos, open(destino, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    con = sum(1 for p in pjs if p.get("ejemplares"))
    print(f"\n  {con}/{len(pjs)} personajes con ejemplares · {fallos} fallos")
    print(f"  {tin}→{tout} tokens · ${(tin*0.09 + tout*0.34)/1e6:.4f}")
    print(f"  escrito en {destino.name}")
    print("\n  Comprueba que los de desvío bajo ACEPTAN y los de desvío alto")
    print("  RECHAZAN. Si no, los ejemplares heredan el sesgo que venían a")
    print("  corregir y no sirven.")


if __name__ == "__main__":
    main()