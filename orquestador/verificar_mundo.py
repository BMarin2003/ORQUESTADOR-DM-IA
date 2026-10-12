r"""
Verifica el prompt del Mundo (dm/prompt_mundo_g1.md) -- mismo patrón que
los verificadores anteriores: lo que se puede comprobar en código, se
comprueba en código; lo que necesita ojo humano (¿el boceto es
evocador?, ¿la semilla encaja de verdad?) se imprime completo.

Comprobaciones automáticas:
  1. FUGA DE PROMPT       igual que siempre: ninguna cadena de 6+
                          palabras del prompt debe aparecer en la salida.
  2. NO FUERZA LA SEMILLA cuando se le da una escena donde el grupo está
                          enfrascado en algo no planeado, debe poder
                          devolver `planteada: false` en vez de forzarla
                          -- si SIEMPRE la plantea pase lo que pase, es
                          la señal de "nunca anules una decisión para
                          forzar una ruta" rota.
  3. PROPAGACIÓN CON RAZÓN si sugiere propagación, cada entrada debe
                          traer una `razon` no vacía -- una propagación
                          sin vía de conocimiento declarada es la
                          telepatía que el prompt prohíbe explícitamente.

Llama al modelo: tiene costo real. Necesita DEEPINFRA_API_KEY +
DMIA_MODELO cargados en el entorno.

Uso:
  py orquestador\verificar_mundo.py
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

PROMPT_PATH = RAIZ / "dm" / "prompt_mundo_g1.md"
MODELO = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")

CASOS = [
    {
        "nombre": "lugar nuevo · boceto de trazo grueso (MUN-4, no se fija)",
        "entrada": {
            "lugar_necesita_boceto": True,
            "fijar_al_responder": False,
            "semilla_candidata": None,
            "escena": "El grupo entra por primera vez a un mercado costero al atardecer.",
        },
    },
    {
        "nombre": "pregunta concreta · el detalle se fija (MUN-5)",
        "entrada": {
            "lugar_necesita_boceto": True,
            "fijar_al_responder": True,
            "semilla_candidata": None,
            "escena": ("El jugador pregunta específicamente qué hay detrás del "
                       "mostrador del prestamista Ordulf."),
        },
    },
    {
        "nombre": "semilla candidata que NO encaja -- no debe forzarse",
        "entrada": {
            "lugar_necesita_boceto": False,
            "fijar_al_responder": False,
            "semilla_candidata": {"kind": "threat",
                                  "content": "Una secta se reúne en las catacumbas del templo."},
            "escena": ("El grupo decidió pasar la tarde reparando su carreta en "
                       "un taller, sin ningún interés en explorar nada más."),
        },
    },
    {
        "nombre": "propagación · un PNJ con vínculo pudo enterarse",
        "entrada": {
            "lugar_necesita_boceto": False,
            "fijar_al_responder": False,
            "semilla_candidata": None,
            "escena": ("El grupo humilló públicamente al Sargento Brea en la plaza. "
                       "Ordulf, su viejo amigo, estaba entre la multitud presente."),
        },
    },
]


def frases_largas(prompt_texto, n_palabras=6):
    """N-gramas de `n_palabras` palabras consecutivas de cada línea larga del prompt, para detectar fugas literales en la salida."""
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
    """Primer n-grama del prompt presente en el texto (sin distinguir mayúsculas), o None."""
    for ng in ngramas:
        if ng.lower() in texto.lower():
            return ng
    return None


def main():
    """CLI: corre los casos del Mundo contra el modelo y comprueba fuga de prompt, que no fuerce la semilla y que toda propagación traiga `razon`; sale con 2 si hay problemas."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", type=int, choices=range(1, len(CASOS) + 1))
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
        user = "ENTRADA (JSON)\n" + json.dumps(caso["entrada"], ensure_ascii=False, indent=2)
        r = llamar(MODELO, prompt_texto, user, max_tokens=600, temp=0.8, json_mode=True)
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

        if "no encaja" in caso["nombre"] or "NO encaja" in caso["nombre"]:
            semilla = salida.get("semilla_plantada") or {}
            if semilla.get("planteada") is True:
                print("  ⚠ plantó la semilla en una escena donde el grupo estaba "
                      "enfrascado en otra cosa -- revisar a mano si de verdad encajó")
            else:
                print("  ✓ no forzó la semilla en una escena que no la pedía")

        if "propagación" in caso["nombre"]:
            props = salida.get("propagacion_sugerida") or []
            sin_razon = [p for p in props if not (p or {}).get("razon", "").strip()]
            if sin_razon:
                print(f"  ✗ propagación sin razón declarada (telepatía): {sin_razon}")
                fallos.append(f"{caso['nombre']} — propagación sin vía de conocimiento")
            elif props:
                print(f"  ✓ propagación con razón declarada en las {len(props)} entrada(s)")
            else:
                print("  · no sugirió propagación en este caso (revisar a mano si debía)")

        print()

    print(f"{'='*74}")
    print(f"  {coste['tin']}→{coste['tout']} tokens · "
          f"${(coste['tin']*0.09 + coste['tout']*0.34)/1e6:.4f}")
    if fallos:
        print(f"\n✗ {len(fallos)} problema(s) automático(s) detectado(s):")
        for f in fallos:
            print(f"    - {f}")
        sys.exit(2)
    print(f"\n✓ Sin fugas ni problemas automáticos en {len(casos)} de {len(CASOS)} caso(s) corrido(s).")


if __name__ == "__main__":
    main()
