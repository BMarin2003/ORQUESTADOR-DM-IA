r"""
SONDEO 4B — Dos estrategias para subir el recall del extractor, comparadas
sobre los turnos que fallaron.

CONTEXTO
  El sondeo 4 dio precisión 83%, recall 33%, evidencia literal 100%.
  Esas cifras están en la parte alta de lo publicado para extracción de
  eventos zero-shot (líneas base habituales: F1 30-50 con Llama3-70B;
  15% macro-F1 con GPT-4.1 en eventos biomédicos en francés).
  El modo de fallo —el modelo se vuelve conservador y no emite nada— está
  documentado, y se atribuye a sobrecarga: ontología + disparadores +
  formato a la vez.

VARIANTES
  A · CONTEXTO   Un prompt, más un bloque con vínculos, secretos sin revelar
                 y promesas pendientes de los PNJ en escena.
                 Hipótesis: falla por falta de información.
                 Riesgo: si la causa es sobrecarga, esto la agrava.

  B · DOS ETAPAS Dreamer (divergente, sin ontología, maximiza recall) →
                 Grounder (convergente, mapea al enum cerrado).
                 Hipótesis: falla por sobrecarga.
                 La regla de evidencia literal ya hace de Judge, gratis.

  BASE           El prompt actual, para comparar sobre los mismos turnos.

COSTE
  Solo los turnos que fallan más dos negativos, para verificar que la
  precisión no se derrumba. ~21 llamadas, unos 2 céntimos.

Uso:
  py sondeos\sondeo_4b.py --modelo google/gemma-4-31B-it
  py sondeos\sondeo_4b.py --modelo google/gemma-4-31B-it --variantes base,B
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE = "https://api.deepinfra.com/v1/openai"
RAIZ = Path(__file__).resolve().parent.parent

# Los cinco que fallaron + dos negativos de control.
TURNOS_DEFECTO = "T07,T11,T13,T14,T16,T05,T12"


def cargar(rel):
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


def texto(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def lista_entidades(world, personas):
    e = []
    for l in world["locations"]:
        e.append(f"  {l['key']:22s} location   {l['name']}")
    for f in world["factions"]:
        e.append(f"  {f['key']:22s} faction    {f['name']}")
    for q in world["quests"]:
        e.append(f"  {q['key']:22s} quest      {q['title']}")
    for c in world["characters"]:
        e.append(f"  {c['key']:22s} character  {c['name']} (personaje jugador)")
    for k, p in personas.items():
        if not k.startswith("_"):
            e.append(f"  {k:22s} npc        {p['name']}")
    return "\n".join(e)


def contexto_escena(turno, personas, world):
    """Variante A: lo que la base sabe y el turno no dice.

    En producción sale de npc_bond_targets, npc_secrets y de los compromisos
    registrados. Aquí se construye desde los fixtures para poder probarlo
    sin tocar la base.
    """
    presentes = turno.get("npcs_present") or []
    if not presentes:
        return ""
    loc = {l["key"]: l["name"] for l in world["locations"]}
    bloques = []
    for k in presentes:
        p = personas.get(k)
        if not p:
            continue
        ibf = p.get("ibf") or {}
        lineas = [f"  {p['name']} ({k})"]
        vin = [f"{t['type']}:{t['key']}" for t in (ibf.get("bond_targets") or [])]
        if vin:
            lineas.append(f"    aprecia y protegería: {', '.join(vin)}")
        sec = [s["content"] for s in (p.get("secrets") or [])
               if not s.get("revealed_at_turn")]
        for s in sec:
            lineas.append(f"    guarda este secreto: {s}")
        bloques.append("\n".join(lineas))

    # Compromisos abiertos del grupo — en producción vienen de la base.
    compromisos = ["El grupo se comprometió a ir a hablar con Herda, "
                   "la vendedora del Mercado Bajo, y aún no lo ha hecho.",
                   "El grupo se comprometió a conseguir pruebas del peaje "
                   "nocturno para la Sargento Brea."]
    return ("\nLO QUE SABE LA BASE Y EL TURNO NO DICE\n"
            + "\n".join(bloques)
            + "\n  compromisos abiertos del grupo:\n"
            + "\n".join(f"    - {c}" for c in compromisos) + "\n")


def llamar(key, modelo, system, user, json_mode=True, max_tokens=800):
    cuerpo = {"model": modelo,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}],
              "temperature": 0, "max_tokens": max_tokens}
    if json_mode:
        cuerpo["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        det = e.read().decode()[:200]
        if json_mode and ("response_format" in det or e.code == 422):
            return llamar(key, modelo, system, user, False, max_tokens)
        print(f"    HTTP {e.code}: {det}", file=sys.stderr)
        return None
    return {"texto": d["choices"][0]["message"]["content"],
            "tin": d.get("usage", {}).get("prompt_tokens") or 0,
            "tout": d.get("usage", {}).get("completion_tokens") or 0,
            "ms": round((time.time() - t0) * 1000)}


def parsear(t):
    limpio = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip()
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
    return {"events": o.get("events") or [], "deltas": o.get("deltas") or []}


def evaluar(turno, salida, contrato):
    full = " ".join(m["text"] for m in turno["player_buffer"]) + " " + turno["dm_output"]
    r = {"tp": 0, "fp": 0, "fn": 0, "ev_ok": 0, "ev_total": 0, "invalidos": []}
    esp = {(e["entity"], e["event_kind"]) for e in turno["expected_events"]} | \
          {(d["entity"], d["field"]) for d in turno["expected_deltas"]}
    obt = set()
    for e in salida["events"]:
        r["ev_total"] += 1
        if (e.get("evidence") or "") in full and e.get("evidence"):
            r["ev_ok"] += 1
        if e.get("event_kind") not in contrato["event_kinds"]:
            r["invalidos"].append(f"event_kind: {e.get('event_kind')}")
            continue
        obt.add((e.get("entity"), e.get("event_kind")))
    campos = contrato["campos_directos"]
    for d in salida["deltas"]:
        r["ev_total"] += 1
        if (d.get("evidence") or "") in full and d.get("evidence"):
            r["ev_ok"] += 1
        if d.get("field") not in campos.get(d.get("entity_type"), {}):
            r["invalidos"].append(f"campo: {d.get('entity_type')}.{d.get('field')}")
            continue
        obt.add((d.get("entity"), d.get("field")))
    r["tp"], r["fp"], r["fn"] = len(esp & obt), len(obt - esp), len(esp - obt)
    r["sobra"], r["falta"] = sorted(obt - esp), sorted(esp - obt)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--turnos", default=TURNOS_DEFECTO)
    ap.add_argument("--variantes", default="base,A,B")
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY. Carga el .env primero.")

    contrato = cargar("extractor/contrato.json")
    p_base = texto("extractor/prompt.md")
    p_dream = texto("extractor/dreamer.md")
    p_ground = texto("extractor/grounder.md")
    world, personas = cargar("fixtures/world.json"), cargar("fixtures/personas.json")
    todos = cargar("fixtures/turns.json")

    ids = [x.strip() for x in args.turnos.split(",")]
    turnos = [t for t in todos if t["id"] in ids]
    variantes = [v.strip() for v in args.variantes.split(",")]
    ents = lista_entidades(world, personas)

    tot = defaultdict(lambda: defaultdict(int))
    registro = []

    print(f"\n{'='*72}\nSONDEO 4B · ESTRATEGIAS DE EXTRACCIÓN · {args.modelo}")
    print(f"{len(turnos)} turnos × {len(variantes)} variantes\n{'='*72}")

    for turno in turnos:
        neg = not turno["expected_events"] and not turno["expected_deltas"]
        cuerpo = ("\n".join(f"{m['pc']}: {m['text']}" for m in turno["player_buffer"])
                  + f"\nDM: {turno['dm_output']}")
        print(f"\n{turno['id']} · {'NEGATIVO' if neg else turno['kind']}")

        for v in variantes:
            if v == "base":
                user = f"ENTIDADES EXISTENTES\n{ents}\n\nTURNO\n{cuerpo}"
                res = llamar(key, args.modelo, p_base, user)
                if not res:
                    continue
                salida = parsear(res["texto"])
                tin, tout, ms, extra = res["tin"], res["tout"], res["ms"], ""

            elif v == "A":
                ctx = contexto_escena(turno, personas, world)
                user = f"ENTIDADES EXISTENTES\n{ents}\n{ctx}\nTURNO\n{cuerpo}"
                res = llamar(key, args.modelo, p_base, user)
                if not res:
                    continue
                salida = parsear(res["texto"])
                tin, tout, ms, extra = res["tin"], res["tout"], res["ms"], ""

            else:  # B — dos etapas
                r1 = llamar(key, args.modelo, p_dream, f"TURNO\n{cuerpo}",
                            json_mode=False, max_tokens=600)
                if not r1:
                    continue
                hallazgos = r1["texto"].strip()
                user = (f"ENTIDADES EXISTENTES\n{ents}\n\n"
                        f"CAMBIOS DETECTADOS (en forma libre)\n{hallazgos}\n\n"
                        f"TURNO ORIGINAL\n{cuerpo}")
                r2 = llamar(key, args.modelo, p_ground, user)
                if not r2:
                    continue
                salida = parsear(r2["texto"])
                tin = r1["tin"] + r2["tin"]
                tout = r1["tout"] + r2["tout"]
                ms = r1["ms"] + r2["ms"]
                n = len([l for l in hallazgos.splitlines() if l.strip().startswith("-")])
                extra = f"  dreamer: {n} hallazgos" if n else "  dreamer: SIN CAMBIOS"

            if salida is None:
                print(f"  {v:5s} JSON no parseable")
                tot[v]["json_malo"] += 1
                continue

            ev = evaluar(turno, salida, contrato)
            for k in ("tp", "fp", "fn", "ev_ok", "ev_total"):
                tot[v][k] += ev[k]
            tot[v]["tin"] += tin
            tot[v]["tout"] += tout
            tot[v]["ms"] += ms

            ok = "ok " if ev["fp"] == 0 and ev["fn"] == 0 else "   "
            print(f"  {v:5s} {ok}tp={ev['tp']} fp={ev['fp']} fn={ev['fn']}  "
                  f"ev {ev['ev_ok']}/{ev['ev_total']}  {ms:>6} ms{extra}")
            if ev["sobra"]:
                print(f"          SOBRA {ev['sobra']}")
            if ev["falta"]:
                print(f"          FALTA {ev['falta']}")
            for i in ev["invalidos"]:
                print(f"          INVÁLIDO {i}")
            registro.append({"turno": turno["id"], "variante": v,
                             "salida": salida, "eval": ev})

    print(f"\n{'='*72}\nCOMPARATIVA\n{'='*72}")
    print(f"{'':6} {'prec':>7} {'recall':>7} {'F1':>7} {'evid':>7} "
          f"{'tp':>4} {'fp':>4} {'fn':>4} {'tokens':>9} {'coste':>9}")
    mejor = None
    for v in variantes:
        d = tot[v]
        p = d["tp"] / (d["tp"] + d["fp"]) if d["tp"] + d["fp"] else 1.0
        r = d["tp"] / (d["tp"] + d["fn"]) if d["tp"] + d["fn"] else 1.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        e = d["ev_ok"] / d["ev_total"] if d["ev_total"] else 1.0
        c = (d["tin"] * 0.09 + d["tout"] * 0.34) / 1e6
        print(f"{v:6} {p:>6.0%} {r:>7.0%} {f1:>7.0%} {e:>7.0%} "
              f"{d['tp']:>4} {d['fp']:>4} {d['fn']:>4} "
              f"{d['tin']+d['tout']:>9} {'$'+format(c,'.4f'):>9}")
        if mejor is None or f1 > mejor[1]:
            mejor = (v, f1, p, r)

    print(f"\nLECTURA")
    print(f"  Mejor F1: variante {mejor[0]} ({mejor[1]:.0%})")
    neg_fp = sum(1 for x in registro
                 if x["variante"] == mejor[0] and x["turno"] in ("T05", "T12")
                 and x["eval"]["fp"] > 0)
    if neg_fp:
        print(f"  ⚠ La variante ganadora produce falsos positivos en turnos")
        print(f"    negativos. Subir recall a costa de precisión NO compensa:")
        print(f"    sobre-extraer entra al canon y nada lo señala después.")
    else:
        print(f"  Sin falsos positivos en los negativos de control.")
    if "B" in variantes and "base" in variantes:
        rb = tot["B"]["tin"] + tot["B"]["tout"]
        rr = tot["base"]["tin"] + tot["base"]["tout"]
        if rr:
            print(f"  B cuesta {rb/rr:.1f}× los tokens de base. La extracción corre")
            print(f"  en batch al cerrar sesión, fuera del camino crítico del juego.")

    destino = RAIZ / f"sondeo4b_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    json.dump({"modelo": args.modelo, "fecha": datetime.now().isoformat(),
               "totales": {k: dict(v) for k, v in tot.items()},
               "registro": registro},
              open(destino, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  detalle en {destino.name}")


if __name__ == "__main__":
    main()