r"""
Verifica el prompt del Narrador de G1 antes de darlo por cerrado.

Dos comprobaciones automáticas y objetivas (lo que SÍ se puede verificar en
código, siguiendo el principio de "verificar en vez de confiar"):

  1. FUGA DE PROMPT   ninguna cadena de 6+ palabras seguidas del prompt debe
                       aparecer en ninguna narración generada. Es la misma
                       comprobación que se hizo en el extractor y se olvidó
                       en el jugador (docs/QM - Lecciones de ingeniería §2).
  2. VEREDICTO        si el árbitro dijo "fallo", la narración no debe
                       contener palabras de éxito (mismo regex que ya usa
                       vertical_slice.py en su paso 5).

Lo que NO se automatiza aquí, a propósito, porque requiere lectura humana
(mismo principio del §6 de lecciones — "el detector funciona, pero necesita
lectura humana"):
  - si la prosa integra bien los fragmentos o se nota cosida
  - si el modo degradado (falta Actor / falta Mundo) se escribe con calidad
  - si la viñeta ambiental de verdad no engancha trama

Cada caso imprime la salida completa para que la leas. SÍ llama al modelo:
tiene costo real (unos céntimos) y necesita DEEPINFRA_API_KEY + DMIA_MODELO
cargados en el entorno.

Uso:
  py orquestador\verificar_fugas_narrador.py
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

PROMPT_PATH = RAIZ / "dm" / "prompt_narrador_g1.md"
MODELO = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")

EXITO = re.compile(r"\b(logras|consigues|aciertas|lo convences)\b", re.I)
CORCHETES = re.compile(r"\[[^\]]{20,}\]")


def frases_largas(prompt_texto, n_palabras=6):
    """N-gramas de n_palabras+ para detectar fuga literal del prompt.

    Se ignoran líneas de encabezado (═══...═══) y líneas que son solo
    nombres de campo — no tienen prosa que se pueda "filtrar" a una escena.
    """
    ngramas = []
    for linea in prompt_texto.splitlines():
        limpio = linea.strip().strip("═").strip()
        if len(limpio.split()) < n_palabras:
            continue
        palabras = re.findall(r"\S+", limpio)
        for i in range(len(palabras) - n_palabras + 1):
            ngramas.append(" ".join(palabras[i:i + n_palabras]))
    return ngramas


def buscar_fuga(narrativa, ngramas):
    for ng in ngramas:
        if ng.lower() in narrativa.lower():
            return ng
    return None


CASOS = [
    {
        "nombre": "en_rol · veredicto éxito · un PNJ interviene",
        "entrada": {
            "modo": "en_rol",
            "veredicto": {"resultado": "éxito", "cd": 14,
                          "correccion": None},
            "intervenciones": [
                {"pnj": "Sargento Brea",
                 "linea": "No es la primera vez que veo a alguien intentarlo, y tampoco será la última.",
                 "entrega": "sin mirarte, con la vista fija en el carro",
                 "se_niega_a": "confirmar si sospecha de ti"}
            ],
            "boceto_mundo": {"texto": "El puente cruje bajo el peso del carro; "
                                       "más gente se acumula detrás esperando su turno.",
                              "evento_de_reloj": None},
            "faltantes": [],
        },
    },
    {
        "nombre": "en_rol · veredicto fallo (no debe narrar éxito)",
        "entrada": {
            "modo": "en_rol",
            "veredicto": {"resultado": "fallo", "cd": 16,
                          "correccion": None},
            "intervenciones": [
                {"pnj": "Sargento Brea",
                 "linea": "Guárdate esa moneda antes de que alguien más la vea.",
                 "entrega": "en voz baja, sin dejar de vigilar el paso",
                 "se_niega_a": "dejarte pasar sin revisión"}
            ],
            "boceto_mundo": None,
            "faltantes": ["mundo"],
        },
    },
    {
        "nombre": "en_rol · falta el Actor (degradado, sin diálogo)",
        "entrada": {
            "modo": "en_rol",
            "veredicto": {"resultado": "éxito parcial", "cd": 12,
                          "correccion": "el intento cuesta tiempo, no falla del todo"},
            "intervenciones": [],
            "boceto_mundo": {"texto": "El sol empieza a bajar sobre el vado; "
                                       "la fila de carros se hace más larga.",
                              "evento_de_reloj": None},
            "faltantes": ["actor"],
        },
    },
    {
        "nombre": "ambiental (no debe introducir trama)",
        "entrada": {
            "modo": "ambiental",
            "veredicto": None,
            "intervenciones": [],
            "boceto_mundo": {"texto": "Un carguero descarga sacos de grano río abajo.",
                              "evento_de_reloj": None},
            "faltantes": [],
        },
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", type=int, choices=range(1, len(CASOS) + 1),
                     help="corre solo el caso N, para no repagar los demás "
                          "al iterar sobre uno solo")
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
        user = ("ENTRADA (JSON)\n" + json.dumps(caso["entrada"], ensure_ascii=False, indent=2))
        r = llamar(MODELO, prompt_texto, user, max_tokens=500, temp=0.8, json_mode=True)
        if not r:
            print("  ✗ el modelo no respondió, se salta este caso")
            fallos.append(caso["nombre"])
            continue
        coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
        salida = parsear_json(r["texto"]) or {}
        narrativa = salida.get("narrativa", "") or ""
        print(f"  {r['ms']} ms\n")
        print(f"  narrativa:\n    " + narrativa.replace("\n", "\n    "))
        if salida.get("mecanica"):
            print(f"  mecanica: {salida['mecanica']}")
        if salida.get("presion"):
            print(f"  presion: {salida['presion']}")

        print()
        fuga = buscar_fuga(narrativa, ngramas)
        if fuga:
            print(f"  ✗ FUGA DE PROMPT detectada: «{fuga}»")
            fallos.append(f"{caso['nombre']} — fuga de prompt")
        else:
            print("  ✓ sin fuga de prompt detectada")

        if (caso["entrada"].get("veredicto") or {}).get("resultado") == "fallo":
            if EXITO.search(narrativa):
                print("  ✗ veredicto fue FALLO pero la narración usa lenguaje de éxito")
                fallos.append(f"{caso['nombre']} — narra éxito con veredicto de fallo")
            else:
                print("  ✓ respeta el fallo (no narra éxito)")

        if CORCHETES.search(narrativa):
            print("  ⚠ meta-comentario entre corchetes — revisar a mano")

        print()

    print(f"{'='*74}")
    print(f"  {coste['tin']}→{coste['tout']} tokens · "
          f"${(coste['tin']*0.09 + coste['tout']*0.34)/1e6:.4f}")
    if fallos:
        print(f"\n✗ {len(fallos)} problema(s) automático(s) detectado(s):")
        for f in fallos:
            print(f"    - {f}")
        sys.exit(2)
    print(f"\n✓ Sin fugas ni contradicciones de veredicto en {len(casos)} de {len(CASOS)} caso(s) corrido(s).")
    if len(casos) < len(CASOS):
        print("  (corriste --solo: los demás casos no se evaluaron esta vez)")
    print("  Falta la lectura humana: ¿se nota cosido? ¿el modo degradado")
    print("  lee bien? ¿la viñeta ambiental engancha trama sin querer?")


if __name__ == "__main__":
    main()
