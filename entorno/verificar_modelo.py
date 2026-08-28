#!/usr/bin/env python3
"""
Verifica el entorno de inferencia y genera un manifiesto de reproducibilidad.

Por qué existe:
  El ID de modelo no basta como ancla de validez. Un proveedor puede cambiar
  la cuantización, el motor de inferencia o la plantilla de chat sin cambiar
  el ID. La huella detecta eso: mismo prompt, temperatura 0, hash de la
  salida. Si el hash cambia entre la recolección de G2 y la de G1, el
  artefacto cambió a mitad del experimento.

  Es la misma lección que LightRAG: los fallos que importan son los
  silenciosos.

Uso:
  export DEEPINFRA_API_KEY=...
  python3 verificar_modelo.py --modelo "google/gemma-4-31b-it"
  python3 verificar_modelo.py --comparar manifiesto_2026-08-24.json
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.deepinfra.com/v1/openai"

# Prompts de huella. Fijos para siempre: si cambian, las huellas antiguas
# dejan de ser comparables. Elegidos para ejercitar español, instrucción
# corta y formato.
HUELLA = [
    ("es_narrativa", "Describe en una sola frase una torre de peaje al amanecer."),
    ("es_instruccion", "Responde solo con el número: ¿cuántos lados tiene un d20?"),
    ("es_formato", "Devuelve exactamente este JSON y nada más: {\"ok\": true}"),
]


def pedir(path, key, payload=None, metodo="GET"):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode() if payload else None,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method=metodo,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode()[:400]
        print(f"\n  HTTP {e.code} en {path}\n  {cuerpo}", file=sys.stderr)
        if e.code == 401:
            print("  → La clave no es válida o no está activa.", file=sys.stderr)
        if e.code == 404:
            print("  → El ID de modelo no existe. Cópialo EXACTO del catálogo:\n"
                  "    los IDs llevan prefijo de organización y no tienen alias.",
                  file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n  Sin conexión a DeepInfra: {e.reason}", file=sys.stderr)
        sys.exit(1)


def listar(key, filtro):
    datos = pedir("/models", key)
    modelos = [m["id"] for m in datos.get("data", [])]
    if filtro:
        modelos = [m for m in modelos if filtro.lower() in m.lower()]
    return sorted(modelos)


def huella(key, modelo):
    """Temperatura 0 y seed fijo. Determinismo no garantizado, pero la
    divergencia sí es señal de que algo cambió."""
    resultados = {}
    for nombre, prompt in HUELLA:
        t0 = time.time()
        r = pedir("/chat/completions", key, {
            "model": modelo,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "seed": 42,
            "max_tokens": 120,
        }, "POST")
        texto = r["choices"][0]["message"]["content"]
        uso = r.get("usage", {})
        resultados[nombre] = {
            "sha256": hashlib.sha256(texto.encode()).hexdigest(),
            "muestra": texto[:120],
            "tokens_in": uso.get("prompt_tokens"),
            "tokens_out": uso.get("completion_tokens"),
            "latencia_ms": round((time.time() - t0) * 1000),
        }
        print(f"  {nombre:16s} {resultados[nombre]['sha256'][:16]}  "
              f"{resultados[nombre]['latencia_ms']:>5} ms")
    return resultados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", help="ID exacto del catálogo")
    ap.add_argument("--listar", nargs="?", const="", help="Lista modelos (filtro opcional)")
    ap.add_argument("--comparar", help="Compara contra un manifiesto previo")
    ap.add_argument("--salida", default=None)
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        print("Falta DEEPINFRA_API_KEY en el entorno.", file=sys.stderr)
        sys.exit(1)

    if args.listar is not None:
        for m in listar(key, args.listar):
            print(m)
        return

    if not args.modelo:
        ap.error("indica --modelo o --listar")

    print(f"\nModelo   {args.modelo}")
    print(f"Endpoint {BASE}\n")

    disponibles = listar(key, None)
    if args.modelo not in disponibles:
        print(f"  '{args.modelo}' NO aparece en el catálogo.", file=sys.stderr)
        print(f"  Busca el ID correcto con:  --listar gemma", file=sys.stderr)
        sys.exit(1)
    print("  catálogo         ok")

    print("\nHuella de determinismo:")
    hue = huella(key, args.modelo)

    manifiesto = {
        "generado": datetime.now(timezone.utc).isoformat(),
        "proveedor": "deepinfra",
        "endpoint": BASE,
        "modelo": args.modelo,
        "parametros_huella": {"temperature": 0, "seed": 42, "max_tokens": 120},
        "huella": hue,
        "nota_cuantizacion": (
            "Anotar a mano desde la página del modelo si el proveedor la "
            "publica. Si no la publica, la huella es el ancla: un cambio de "
            "hash indica que el artefacto servido cambió."
        ),
    }

    destino = args.salida or f"manifiesto_{datetime.now().strftime('%Y-%m-%d')}.json"

    if args.comparar:
        previo = json.load(open(args.comparar, encoding="utf-8"))
        print(f"\nComparando contra {args.comparar} ({previo['generado'][:10]})")
        if previo["modelo"] != args.modelo:
            print(f"  MODELO DISTINTO: {previo['modelo']} → {args.modelo}")
        cambios = [n for n in hue
                   if previo["huella"].get(n, {}).get("sha256") != hue[n]["sha256"]]
        if cambios:
            print(f"\n  ⚠  HUELLA CAMBIADA en: {', '.join(cambios)}")
            for n in cambios:
                print(f"     antes: {previo['huella'][n]['muestra'][:70]}")
                print(f"     ahora: {hue[n]['muestra'][:70]}")
            print("\n  El artefacto servido no es el mismo. Si esto ocurre a mitad\n"
                  "  de la recolección, las campañas de ambos grupos NO son\n"
                  "  comparables. Documentar y decidir antes de continuar.")
            sys.exit(2)
        print("  huella idéntica  ok — mismo artefacto servido")

    with open(destino, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2, ensure_ascii=False)
    print(f"\nManifiesto escrito en {destino}")
    print("Versiónalo en git: es la prueba de qué modelo generó cada campaña.")


if __name__ == "__main__":
    main()
