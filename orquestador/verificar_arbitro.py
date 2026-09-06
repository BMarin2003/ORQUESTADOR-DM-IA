r"""
Verifica el prompt del Árbitro de G1 (dm/prompt_arbitro_g1.md) antes de
darlo por cerrado — mismo patrón y mismo principio de
verificar_fugas_narrador.py: lo que se puede comprobar en código, se
comprueba en código; lo que necesita ojo humano (¿la respuesta del tutor
es realmente clara? ¿el veredicto sin tirada es razonable?), se imprime
completo para que lo leas.

Comprobaciones automáticas:
  1. FUGA DE PROMPT      igual que en el Narrador: ninguna cadena de 6+
                         palabras del prompt debe aparecer en la salida.
  2. FORMA DE LA SALIDA  modo tutor -> {"respuesta": str}
                         modo veredicto_sin_tirada -> objeto "veredicto"
                         con exactamente las claves que espera
                         dm/prompt_narrador_g1.md (veredicto, cd, resultado,
                         recurso_consumido, correccion_al_jugador) — es la
                         comprobación de que el fix de nombre (§ "veredicto"
                         como objeto completo) de verdad se respeta.
  3. TUTOR NO NARRA      el modo tutor no debe sonar a narración: no debe
                         aparecer una tirada inventada, ni prosa evocadora
                         con verbos de escena (ves, sientes, hueles...).

Llama al modelo: tiene costo real y necesita DEEPINFRA_API_KEY +
DMIA_MODELO cargados en el entorno.

Uso:
  py orquestador\verificar_arbitro.py
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
from vertical_slice import llamar, parsear_json  # noqa: E402

PROMPT_PATH = RAIZ / "dm" / "prompt_arbitro_g1.md"
MODELO = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")

VERBOS_ESCENA = re.compile(r"\b(ves|sientes|hueles|escuchas|percibes)\b", re.I)
CLAVES_VEREDICTO = {"veredicto", "cd", "resultado", "recurso_consumido",
                     "correccion_al_jugador"}

CASOS = [
    {
        "nombre": "tutor · pregunta de reglas entre corchetes",
        "modo": "tutor",
        "entrada": "[¿puedo usar mi ataque de oportunidad si el enemigo "
                   "solo se mueve dentro de mi alcance sin alejarse?]",
    },
    {
        "nombre": "tutor · jugador asume mal una regla, corregir sin condescendencia",
        "modo": "tutor",
        "entrada": "[creo que con desventaja se tiran dos d20 y se suman, "
                   "¿verdad?]",
    },
    {
        "nombre": "veredicto_sin_tirada · idea lateral sin tirada previa (NUN-5)",
        "modo": "veredicto_sin_tirada",
        "entrada": ("Buffer del turno: \"En vez de forzar la cerradura, "
                     "vierto aceite de mi lámpara en el mecanismo y luego "
                     "lo prendo fuego para que se deforme el pestillo.\" "
                     "altera_estado=True, no hubo tirada previa."),
    },
    {
        "nombre": "veredicto_sin_tirada · acción claramente mecánica sin tirada -> debe pedirla, no inventar",
        "modo": "veredicto_sin_tirada",
        "entrada": ("Buffer del turno: \"Intento levantar la reja de "
                     "hierro para que el grupo pase por debajo.\" "
                     "altera_estado=True, no hubo tirada previa."),
    },
]


def frases_largas(prompt_texto, n_palabras=6):
    ngramas = []
    for linea in prompt_texto.splitlines():
        limpio = linea.strip().strip("═").strip()
        if len(limpio.split()) < n_palabras:
            continue
        palabras = re.findall(r"\S+", limpio)
        for i in range(len(palabras) - n_palabras + 1):
            ngramas.append(" ".join(palabras[i:i + n_palabras]))
    return ngramas


def buscar_fuga(texto, ngramas):
    for ng in ngramas:
        if ng.lower() in texto.lower():
            return ng
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", type=int, choices=range(1, len(CASOS) + 1),
                     help="corre solo el caso N")
    args = ap.parse_args()

    faltan = [v for v in ("DEEPINFRA_API_KEY", "DMIA_MODELO") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Falta en el entorno: {', '.join(faltan)}")

    prompt_texto = PROMPT_PATH.read_text(encoding="utf-8")
    ngramas = frases_largas(prompt_texto)
    print(f"Prompt: {PROMPT_PATH.name} ({len(prompt_texto)} caracteres, "
          f"{len(ngramas)} n-gramas de 6+ palabras a vigilar)\n")

    coste = {"tin": 0, "tout": 0}
    fallos = []
    casos = [(args.solo, CASOS[args.solo - 1])] if args.solo else list(enumerate(CASOS, 1))

    for i, caso in casos:
        print(f"{'='*74}\n[{i}] {caso['nombre']}\n{'='*74}")
        r = llamar(MODELO, prompt_texto, caso["entrada"], max_tokens=500,
                   temp=0.7, json_mode=True)
        if not r:
            print("  ✗ el modelo no respondió, se salta este caso")
            fallos.append(caso["nombre"])
            continue
        coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
        salida = parsear_json(r["texto"]) or {}
        print(f"  {r['ms']} ms\n  salida: {json.dumps(salida, ensure_ascii=False, indent=2)}\n")

        texto_para_fuga = json.dumps(salida, ensure_ascii=False)
        fuga = buscar_fuga(texto_para_fuga, ngramas)
        if fuga:
            print(f"  ✗ FUGA DE PROMPT detectada: «{fuga}»")
            fallos.append(f"{caso['nombre']} — fuga de prompt")
        else:
            print("  ✓ sin fuga de prompt detectada")

        if caso["modo"] == "tutor":
            if "respuesta" not in salida or not isinstance(salida.get("respuesta"), str):
                print("  ✗ falta la clave 'respuesta' (string) esperada en modo tutor")
                fallos.append(f"{caso['nombre']} — forma de salida incorrecta")
            else:
                print("  ✓ forma de salida correcta ({'respuesta': str})")
            if VERBOS_ESCENA.search(salida.get("respuesta", "")):
                print("  ✗ el tutor suena a narración (verbo de escena detectado)")
                fallos.append(f"{caso['nombre']} — tutor narra en vez de explicar")
            else:
                print("  ✓ no narra, explica")
        else:
            claves = set(salida.keys())
            if claves != CLAVES_VEREDICTO:
                print(f"  ✗ claves esperadas {sorted(CLAVES_VEREDICTO)}, "
                      f"recibidas {sorted(claves)}")
                fallos.append(f"{caso['nombre']} — forma de salida incorrecta")
            else:
                print("  ✓ forma de salida correcta (coincide con el fragmento "
                      "'veredicto' que espera prompt_narrador_g1.md)")

        print()

    print(f"{'='*74}")
    print(f"  {coste['tin']}→{coste['tout']} tokens · "
          f"${(coste['tin']*0.09 + coste['tout']*0.34)/1e6:.4f}")
    if fallos:
        print(f"\n✗ {len(fallos)} problema(s) automático(s) detectado(s):")
        for f in fallos:
            print(f"    - {f}")
        sys.exit(2)
    print(f"\n✓ Sin fugas ni problemas de forma en {len(casos)} de {len(CASOS)} caso(s) corrido(s).")


if __name__ == "__main__":
    main()
