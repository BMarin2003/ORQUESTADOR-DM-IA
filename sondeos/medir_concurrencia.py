r"""
Mide la concurrencia real utilizable en DeepInfra.

No busca el límite documentado, busca el punto donde el throughput POR
CAMPAÑA se degrada. Ese es el número que decide si las 54 campañas tardan
2 días o 10.

Lanza N llamadas simultáneas y mide:
  · latencia p50/p95 por petición
  · tokens/s agregados y por petición
  · errores 429 (rate limit) y otros

Si la latencia individual sube proporcionalmente con N, estás en cola: la
concurrencia extra no compra nada. Si se mantiene plana, escala de verdad.

Uso:
  py sondeos\medir_concurrencia.py --modelo google/gemma-4-31B-it
  py sondeos\medir_concurrencia.py --modelo google/gemma-4-31B-it --niveles 1,4,8,16
"""

import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

BASE = "https://api.deepinfra.com/v1/openai"

# Prompt de carga: pide prosa larga, que es el perfil real del Narrador.
CARGA = ("Describe una escena de mercado medieval al amanecer. "
         "Prosa sensorial, dos párrafos, sin diálogo.")
MAX_TOKENS = 300


def una_llamada(key, modelo, idx):
    payload = json.dumps({
        "model": modelo,
        "messages": [{"role": "user", "content": CARGA}],
        "temperature": 0.7,
        "max_tokens": MAX_TOKENS,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode())
            cab = {k.lower(): v for k, v in r.headers.items()
                   if "ratelimit" in k.lower() or "retry" in k.lower()}
        dt = time.time() - t0
        out = d.get("usage", {}).get("completion_tokens", 0)
        return {"ok": True, "ms": round(dt * 1000), "tokens_out": out,
                "tok_s": round(out / dt, 1) if dt else 0, "cabeceras": cab}
    except urllib.error.HTTPError as e:
        return {"ok": False, "ms": round((time.time() - t0) * 1000),
                "codigo": e.code, "cuerpo": e.read().decode()[:120]}
    except Exception as e:
        return {"ok": False, "ms": round((time.time() - t0) * 1000),
                "codigo": "exc", "cuerpo": str(e)[:120]}


def nivel(key, modelo, n):
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=n) as ex:
        res = list(ex.map(lambda i: una_llamada(key, modelo, i), range(n)))
    pared = time.time() - t0

    ok = [r for r in res if r["ok"]]
    err = [r for r in res if not r["ok"]]
    r429 = [r for r in err if r.get("codigo") == 429]

    if not ok:
        return {"n": n, "ok": 0, "err": len(err), "r429": len(r429),
                "muestra_error": err[0].get("cuerpo") if err else ""}

    lat = sorted(r["ms"] for r in ok)
    tot_out = sum(r["tokens_out"] for r in ok)
    return {
        "n": n,
        "ok": len(ok),
        "err": len(err),
        "r429": len(r429),
        "p50_ms": lat[len(lat) // 2],
        "p95_ms": lat[min(int(len(lat) * 0.95), len(lat) - 1)],
        "tok_s_por_peticion": round(statistics.mean(r["tok_s"] for r in ok), 1),
        "tok_s_agregado": round(tot_out / pared, 1),
        "pared_s": round(pared, 1),
        "cabeceras": next((r["cabeceras"] for r in ok if r["cabeceras"]), {}),
        "muestra_error": err[0].get("cuerpo") if err else "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--niveles", default="1,2,4,8,16")
    ap.add_argument("--pausa", type=float, default=5.0,
                    help="segundos entre niveles, para no arrastrar rate limit")
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY")

    niveles = [int(x) for x in args.niveles.split(",")]
    total = sum(niveles)
    print(f"\nModelo {args.modelo}")
    print(f"Niveles {niveles} → {total} llamadas de ~{MAX_TOKENS} tokens")
    print(f"Costo aproximado: ${(total * (40 * 0.09 + MAX_TOKENS * 0.34)) / 1_000_000:.4f}\n")

    print(f"{'N':>4} {'ok':>4} {'429':>4} {'p50 ms':>8} {'p95 ms':>8} "
          f"{'tok/s c/u':>10} {'tok/s tot':>10} {'pared s':>8}")
    print("-" * 62)

    filas = []
    base_tok_s = None
    for i, n in enumerate(niveles):
        r = nivel(key, args.modelo, n)
        filas.append(r)
        if r["ok"] == 0:
            print(f"{n:>4} {0:>4} {r['r429']:>4}   TODAS FALLARON  {r['muestra_error'][:30]}")
        else:
            print(f"{n:>4} {r['ok']:>4} {r['r429']:>4} {r['p50_ms']:>8} {r['p95_ms']:>8} "
                  f"{r['tok_s_por_peticion']:>10} {r['tok_s_agregado']:>10} {r['pared_s']:>8}")
            if base_tok_s is None:
                base_tok_s = r["tok_s_por_peticion"]
        if r.get("cabeceras"):
            print(f"     cabeceras: {r['cabeceras']}")
        if i < len(niveles) - 1:
            time.sleep(args.pausa)

    # ------------------------------------------------------------- lectura
    print("\n" + "=" * 62)
    utiles = [f for f in filas if f["ok"] > 0]
    if not utiles:
        sys.exit("Ninguna llamada tuvo éxito.")

    print("LECTURA\n")
    con429 = [f["n"] for f in filas if f["r429"] > 0]
    if con429:
        print(f"  Rate limit (429) a partir de N={min(con429)}.")
    else:
        print(f"  Sin 429 hasta N={max(f['n'] for f in filas)}.")

    # Degradación: ¿cae el throughput por petición al subir N?
    print()
    for f in utiles:
        caida = 100 * (1 - f["tok_s_por_peticion"] / base_tok_s) if base_tok_s else 0
        marca = "  ← degradado" if caida > 30 else ""
        print(f"  N={f['n']:<3} {f['tok_s_por_peticion']:>6} tok/s por petición "
              f"({caida:+5.0f}% vs N=1){marca}")

    mejor = max(utiles, key=lambda f: f["tok_s_agregado"])
    print(f"\n  Throughput agregado máximo en N={mejor['n']} "
          f"({mejor['tok_s_agregado']} tok/s).")

    # Proyección a las campañas
    print("\nPROYECCIÓN — 54 campañas (27 pares)")
    for turnos, etiqueta in [(480, "4 sesiones × 120"), (720, "6 sesiones × 120")]:
        # ~500 tokens de salida por turno cerrado, ~2.5 llamadas medias
        tok_campana = turnos * 500 * 2.5
        for f in utiles:
            if f["n"] not in (1, mejor["n"]):
                continue
            horas = (tok_campana * 54) / (f["tok_s_agregado"] * 3600)
            print(f"  {etiqueta:<20} N={f['n']:<3} → {horas:6.1f} h "
                  f"({horas/24:.1f} días)")

    destino = f"concurrencia_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    json.dump({"modelo": args.modelo, "fecha": datetime.now().isoformat(),
               "niveles": filas}, open(destino, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"\nDetalle en {destino}")
    print("\nQué buscar: si tok/s por petición cae >30% al subir N, estás en")
    print("cola y la concurrencia extra no compra nada. Si se mantiene plana,")
    print("escala de verdad y puedes paralelizar campañas.")


if __name__ == "__main__":
    main()
