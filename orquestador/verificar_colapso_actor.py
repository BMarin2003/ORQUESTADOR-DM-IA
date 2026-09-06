r"""
Verifica el prompt del Actor (dm/prompt_actor_g1.md) contra el bug ya
documentado en QM - Lecciones de ingeniería §2: un ejemplo único de
reacción enseñó postura, no formato, y la frase se filtró literal en dos
modelos. El corolario para G1 dice: "si los PNJ colapsan en la misma
respuesta, CL-1 no puede medir nada" — CL-1/CL-2 son justo los
indicadores de Coherencia Longitudinal (personajes) y el colapso golpea
también "reactividad significativa a la agencia del jugador" (Calidad
Narrativa Emergente): si dos PNJ con ejes opuestos responden igual al
mismo disparador, el indicador queda en cero por diseño del prompt, no
por lo que el modelo sabe hacer.

Tres comprobaciones automáticas:

  1. FUGA DE EJEMPLO   ninguna de las líneas de ejemplo marcadas en el
                       prompt (las que ilustran cada eje) debe aparecer
                       literal en ninguna salida generada.
  2. DIVERGENCIA        para cada PAR de PNJ con el eje relevante en
                       extremos opuestos, frente al MISMO disparador, la
                       superposición léxica de "linea" no debe superar un
                       umbral. Ojo (Lección 6): esto NO es lo mismo que
                       convergencia léxica natural — el umbral es alto a
                       propósito para no marcar como colapso dos personajes
                       que coinciden en la manera obvia de decir algo.
  3. ARRAIGO            el PNJ no debe mencionar nada que no esté en su
                       `conocimiento` declarado en la entrada (chequeo de
                       palabras clave marcadas como "secreto_ajeno" en el
                       caso, que NO debería aparecer en la línea).

Llama al modelo: tiene costo real. Necesita DEEPINFRA_API_KEY +
DMIA_MODELO cargados en el entorno.

Uso:
  py orquestador\verificar_colapso_actor.py
"""
import argparse
import json
import os
import re
import sys
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
from vertical_slice import llamar, parsear_json  # noqa: E402

PROMPT_PATH = RAIZ / "dm" / "prompt_actor_g1.md"
MODELO = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")

# Líneas de ejemplo marcadas en el prompt con "> *Ejemplo" — se extraen
# programáticamente en vez de copiarlas a mano, para que si el prompt
# cambia, el detector no quede desactualizado en silencio (Lección 1:
# "afirmar antes de parchear").
EJEMPLO = re.compile(r'"([^"]{15,})"')

# Grupos: cada grupo enfrenta el MISMO disparador a fichas con el eje
# relevante en extremos opuestos. Se espera divergencia, no un valor de
# salida concreto — no hay "respuesta correcta", solo "no deben coincidir".
GRUPOS = [
    {
        "nombre": "soborno · principle alto vs bajo",
        "disparador": ("El grupo le ofrece 50 monedas de oro a cambio de "
                       "mirar hacia otro lado."),
        "fichas": [
            {"nombre": "Sargento Brea", "principle": 85, "boldness": 40,
             "warmth": -10, "candor": 60,
             "voice_notes": "habla cortante, frases cortas, nunca jura"},
            {"nombre": "Ordulf el cambista", "principle": -80, "boldness": 20,
             "warmth": 10, "candor": -30,
             "voice_notes": "siempre sonríe al hablar de dinero, regatea todo"},
        ],
    },
    {
        "nombre": "amenaza · boldness alto vs bajo",
        "disparador": ("El grupo golpea la mesa y dice que si no coopera, "
                       "\"esto se pone feo para ti\"."),
        "fichas": [
            {"nombre": "Kael el forjador", "principle": 20, "boldness": 90,
             "warmth": 0, "candor": 70,
             "voice_notes": "voz grave, no se apura al responder"},
            {"nombre": "Mira la escribiente", "principle": 20, "boldness": -85,
             "warmth": 30, "candor": -20,
             "voice_notes": "tartamudea bajo presión, evita mirar a los ojos"},
        ],
    },
]

CASO_ARRAIGO = {
    "nombre": "arraigo · no revela lo que no sabe",
    "ficha": {"nombre": "Tavio el posadero", "principle": 10, "boldness": 10,
              "warmth": 40, "candor": 20,
              "voice_notes": "chismoso pero nunca sobre lo que no vio con sus ojos"},
    "conocimiento": "Vio al grupo entrar a la posada anoche. Nada más.",
    "secreto_ajeno": "la Baronesa",  # no está en su conocimiento
    "pregunta": "El grupo le pregunta: \"¿sabes algo de los planes de la Baronesa?\"",
}


def frases_ejemplo(prompt_texto):
    return [m for m in EJEMPLO.findall(prompt_texto) if len(m.split()) >= 4]


def jaccard_palabras(a, b):
    wa = set(re.findall(r"\w+", a.lower()))
    wb = set(re.findall(r"\w+", b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def pedir_linea(prompt_texto, ficha, disparador, conocimiento=None):
    entrada = {
        "tu_ficha": ficha,
        "tu_conocimiento": conocimiento or "Lo que es obvio para cualquiera en la escena.",
        "escena": disparador,
    }
    user = "ENTRADA (JSON)\n" + json.dumps(entrada, ensure_ascii=False, indent=2)
    r = llamar(MODELO, prompt_texto, user, max_tokens=300, temp=0.9, json_mode=True)
    if not r:
        return None, None
    salida = parsear_json(r["texto"]) or {}
    return salida, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umbral", type=float, default=0.55,
                     help="máxima superposición léxica (Jaccard) tolerada "
                          "entre dos PNJ con ejes opuestos ante el mismo "
                          "disparador antes de marcarlo como posible colapso")
    args = ap.parse_args()

    faltan = [v for v in ("DEEPINFRA_API_KEY", "DMIA_MODELO") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Falta en el entorno: {', '.join(faltan)}")

    prompt_texto = PROMPT_PATH.read_text(encoding="utf-8")
    ejemplos = frases_ejemplo(prompt_texto)
    print(f"Prompt: {PROMPT_PATH.name} ({len(prompt_texto)} caracteres, "
          f"{len(ejemplos)} frases de ejemplo a vigilar)\n")

    coste = {"tin": 0, "tout": 0}
    fallos = []

    for grupo in GRUPOS:
        print(f"{'='*74}\n[{grupo['nombre']}]\n{'='*74}")
        salidas = []
        for ficha in grupo["fichas"]:
            salida, r = pedir_linea(prompt_texto, ficha, grupo["disparador"])
            if not salida:
                print(f"  ✗ {ficha['nombre']}: el modelo no respondió")
                fallos.append(f"{grupo['nombre']} — {ficha['nombre']} sin respuesta")
                continue
            coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
            linea = salida.get("linea", "") or ""
            print(f"  {ficha['nombre']} (principle={ficha.get('principle')}, "
                  f"boldness={ficha.get('boldness')}):")
            print(f"    linea:   {linea}")
            print(f"    entrega: {salida.get('entrega')}")

            fuga = next((e for e in ejemplos if e.lower() in linea.lower()), None)
            if fuga:
                print(f"    ✗ FUGA DE EJEMPLO detectada: «{fuga}»")
                fallos.append(f"{grupo['nombre']} — {ficha['nombre']} — fuga de ejemplo")
            salidas.append((ficha["nombre"], linea))
        print()

        for (na, la), (nb, lb) in combinations(salidas, 2):
            sim = jaccard_palabras(la, lb)
            if sim > args.umbral:
                print(f"  ✗ POSIBLE COLAPSO: {na} vs {nb} — superposición "
                      f"léxica {sim:.2f} > {args.umbral} pese a ejes opuestos")
                fallos.append(f"{grupo['nombre']} — colapso {na}/{nb} ({sim:.2f})")
            else:
                print(f"  ✓ {na} vs {nb} divergen (superposición {sim:.2f})")
        print()

    print(f"{'='*74}\n[{CASO_ARRAIGO['nombre']}]\n{'='*74}")
    salida, r = pedir_linea(prompt_texto, CASO_ARRAIGO["ficha"],
                             CASO_ARRAIGO["pregunta"], CASO_ARRAIGO["conocimiento"])
    if not salida:
        print("  ✗ el modelo no respondió")
        fallos.append("arraigo — sin respuesta")
    else:
        coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
        linea = salida.get("linea", "") or ""
        print(f"  linea: {linea}\n  se_niega_a: {salida.get('se_niega_a')}\n")
        if CASO_ARRAIGO["secreto_ajeno"].lower() in linea.lower():
            print(f"  ✗ el PNJ menciona «{CASO_ARRAIGO['secreto_ajeno']}», "
                  f"que no está en su conocimiento declarado")
            fallos.append("arraigo — PNJ revela lo que no sabe")
        else:
            print("  ✓ no menciona lo que está fuera de su conocimiento declarado")

    print(f"\n{'='*74}")
    print(f"  {coste['tin']}→{coste['tout']} tokens · "
          f"${(coste['tin']*0.09 + coste['tout']*0.34)/1e6:.4f}")
    if fallos:
        print(f"\n✗ {len(fallos)} problema(s) automático(s) detectado(s):")
        for f in fallos:
            print(f"    - {f}")
        sys.exit(2)
    print(f"\n✓ Sin fugas de ejemplo, sin colapso detectado, arraigo respetado.")


if __name__ == "__main__":
    main()
