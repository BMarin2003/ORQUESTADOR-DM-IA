r"""
SONDEO 4 — El extractor.

Es el punto único de fallo de la coherencia longitudinal: si sub-detecta en
silencio, el mundo no evoluciona y desde fuera parece que "el modelo no
recuerda bien". Y de él dependen las métricas deterministas que el asesor
exige como validación computacional.

Mide contra los 16 turnos de fixtures con ground truth:

  PRECISIÓN  de lo que emitió, cuánto era correcto
             ← la métrica que importa. Sobre-extraer es IRRECUPERABLE:
               entra al canon y nada lo señala después.

  RECALL     de lo que debía encontrar, cuánto encontró
             ← sub-detectar es recuperable: el turn_log queda íntegro y se
               puede reprocesar con mejor prompt.

  EVIDENCIA  qué proporción de las citas es literal
             ← si esto es bajo, apply_delta rechazará casi todo

Los 6 turnos NEGATIVOS (sin nada que extraer) son los más informativos:
T05 intención no ejecutada · T12 sarcasmo · T04 gag repetido.

Uso:
  py sondeos\sondeo_4.py --modelo google/gemma-4-31B-it
  py sondeos\sondeo_4.py --modelo google/gemma-4-31B-it --repeticiones 3
  py sondeos\sondeo_4.py --modelo google/gemma-4-31B-it --solo T05,T12
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
RAIZ = Path(__file__).resolve().parent.parent.parent


def cargar(rel):
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


def entidades_disponibles(world, personas):
    ent = []
    for l in world["locations"]:
        ent.append(f"  {l['key']:22s} location   {l['name']}")
    for f in world["factions"]:
        ent.append(f"  {f['key']:22s} faction    {f['name']}")
    for q in world["quests"]:
        ent.append(f"  {q['key']:22s} quest      {q['title']}")
    for c in world["characters"]:
        ent.append(f"  {c['key']:22s} character  {c['name']} (personaje jugador)")
    for k, p in personas.items():
        if not k.startswith("_"):
            ent.append(f"  {k:22s} npc        {p['name']}")
    return "\n".join(ent)



def contexto_escena(turno, personas, world, compromisos):
    """Lo que la base sabe y el turno no dice.

    Variante A del sondeo 4B: F1 67% frente a 18% del prompt sin contexto,
    sin falsos positivos añadidos. El extractor no falla por sobrecarga
    cognitiva sino por falta de información que solo existe en la base.

    En produccion sale de: npc_bond_targets, npc_secrets sin revelar,
    quests activas, entity_relations de faccion, y los promise_made
    registrados que siguen abiertos.
    """
    partes = []

    presentes = turno.get("npcs_present") or []
    for k in presentes:
        p = personas.get(k)
        if not p:
            continue
        ibf = p.get("ibf") or {}
        lin = [f"  {p['name']} ({k})"]
        vin = [f"{t['type']}:{t['key']}" for t in (ibf.get("bond_targets") or [])]
        if vin:
            lin.append(f"    aprecia y protegeria: {', '.join(vin)}")
        for sec in (p.get("secrets") or []):
            if not sec.get("revealed_at_turn"):
                lin.append(f"    guarda este secreto: {sec['content']}")
        partes.append("\n".join(lin))

    activas = [q for q in world["quests"] if q["status"] in ("active", "unknown")]
    if activas:
        lin = ["  objetivos abiertos:"]
        for q in activas:
            lin.append(f"    - {q['key']}: {q['title']} [{q['status']}]")
            if q.get("completion_condition"):
                lin.append(f"      se cierra cuando: {q['completion_condition']}")
        partes.append("\n".join(lin))

    if world.get("factions"):
        partes.append("  facciones:\n" + "\n".join(
            f"    - {f['key']}: {f['name']}"
            f"{' (aun no sabe del grupo)' if not f.get('knows_about_party') else ''}"
            for f in world["factions"]))

    if compromisos:
        partes.append("  compromisos del grupo aun abiertos:\n" + "\n".join(
            f"    - {c}" for c in compromisos))

    if not partes:
        return ""
    return "\nLO QUE SABE LA BASE Y EL TURNO NO DICE\n" + "\n".join(partes) + "\n"



def condiciones(turno, personas, world, compromisos):
    """Condiciones declaradas que este turno podría satisfacer.

    Todas vienen de la base: completion_condition de las misiones,
    reveal_condition de los secretos sin revelar, y los promise_made abiertos.

    Se comprueban con una llamada aparte y barata: preguntar "¿este turno
    cumple esta condición escrita?" es una pregunta binaria y cerrada, muy
    distinta de la extracción abierta. Pedirle las dos cosas al extractor
    a la vez era el origen de los fallos de recall.
    """
    out = []
    for q in world["quests"]:
        if q["status"] in ("active", "unknown") and q.get("completion_condition"):
            out.append({"id": f"quest:{q['key']}:completed", "tipo": "mision",
                        "texto": q["completion_condition"],
                        "_delta": ("quest", q["key"], "status", "completed")})
    for k in (turno.get("npcs_present") or []):
        p = personas.get(k) or {}
        for i, sec in enumerate(p.get("secrets") or []):
            if not sec.get("revealed_at_turn"):
                out.append({"id": f"secret:{k}:{i}", "tipo": "secreto",
                            "texto": sec["reveal_condition"],
                            "_delta": ("npc", k, "secret_revealed", f"secreto_{i}"),
                            "_evento": (k, "secret_entrusted")})
    turno_actual = turno.get("id")
    for i, c in enumerate(compromisos):
        pnj = c.get("pnj") if isinstance(c, dict) else None
        txt = c["texto"] if isinstance(c, dict) else c
        # Un compromiso contraído en ESTE turno no puede cumplirse ni
        # incumplirse todavía. Se excluye deterministamente en vez de
        # confiar en que el modelo entienda la secuencia temporal.
        if isinstance(c, dict) and c.get("turno") is not None \
           and c["turno"] == turno_actual:
            continue
        out.append({"id": f"promesa:{i}", "tipo": "compromiso", "texto": txt,
                    "_evento_cumplida": (pnj, "promise_kept"),
                    "_evento_incumplida": (pnj, "promise_broken")})
    return out


def aplicar_condiciones(cumplidas, conds, salida):
    """Traduce las condiciones cumplidas a eventos y deltas. Determinista."""
    idx = {c["id"]: c for c in conds}
    for c in cumplidas:
        spec = idx.get(c.get("id"))
        if not spec:
            continue
        ev = c.get("evidence", "")
        if spec["tipo"] == "compromiso":
            res = c.get("resultado")
            par = spec["_evento_cumplida"] if res == "cumplida" else spec["_evento_incumplida"]
            if par[0]:
                salida["events"].append({"entity": par[0], "event_kind": par[1],
                                         "evidence": ev})
        else:
            if spec.get("_evento"):
                salida["events"].append({"entity": spec["_evento"][0],
                                         "event_kind": spec["_evento"][1],
                                         "evidence": ev})
            t, e, f, v = spec["_delta"]
            salida["deltas"].append({"entity": e, "entity_type": t, "field": f,
                                     "value": v, "evidence": ev})
    return salida


def llamar(key, modelo, system, user):
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps({
            "model": modelo,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0,
            "max_tokens": 800,
            "response_format": {"type": "json_object"},
        }).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode()[:200]
        # Algunos modelos no admiten response_format; reintenta sin él.
        if "response_format" in cuerpo or e.code == 422:
            return llamar_sin_formato(key, modelo, system, user)
        print(f"  HTTP {e.code}: {cuerpo}", file=sys.stderr)
        return None
    return {"texto": d["choices"][0]["message"]["content"],
            "tokens_in": d.get("usage", {}).get("prompt_tokens"),
            "tokens_out": d.get("usage", {}).get("completion_tokens"),
            "ms": round((time.time() - t0) * 1000)}


def llamar_sin_formato(key, modelo, system, user):
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps({
            "model": modelo,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0, "max_tokens": 800}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode())
    return {"texto": d["choices"][0]["message"]["content"],
            "tokens_in": d.get("usage", {}).get("prompt_tokens"),
            "tokens_out": d.get("usage", {}).get("completion_tokens"),
            "ms": round((time.time() - t0) * 1000)}


def parsear(texto):
    limpio = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
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
    """Compara la salida contra el ground truth del turno."""
    full = " ".join(m["text"] for m in turno["player_buffer"]) + " " + turno["dm_output"]
    r = {"tp": 0, "fp": 0, "fn": 0, "ev_ok": 0, "ev_total": 0,
         "wit_ok": 0, "wit_esp": 0, "invalidos": [], "detalle": []}
    # witnessed se reporta aparte: es señal para la propagación, no parte
    # de la precisión de extracción.
    esp_wit = {(d["entity"], d["field"]): d["witnessed"]
               for d in turno["expected_deltas"] if "witnessed" in d}
    r["wit_esp"] = len(esp_wit)

    # ---- eventos
    esp_e = {(e["entity"], e["event_kind"]) for e in turno["expected_events"]}
    obt_e = set()
    for e in salida["events"]:
        ent, kind = e.get("entity"), e.get("event_kind")
        ev = e.get("evidence", "") or ""
        r["ev_total"] += 1
        if ev and ev in full:
            r["ev_ok"] += 1
        if kind not in contrato["event_kinds"]:
            r["invalidos"].append(f"event_kind desconocido: {kind}")
            continue
        obt_e.add((ent, kind))

    # ---- deltas directos
    esp_d = {(d["entity"], d["field"]) for d in turno["expected_deltas"]}
    obt_d = set()
    campos = contrato["campos_directos"]
    for d in salida["deltas"]:
        ent, tipo, campo = d.get("entity"), d.get("entity_type"), d.get("field")
        ev = d.get("evidence", "") or ""
        r["ev_total"] += 1
        if ev and ev in full:
            r["ev_ok"] += 1
        if tipo not in campos or campo not in campos.get(tipo, {}):
            r["invalidos"].append(f"campo fuera de lista blanca: {tipo}.{campo}")
            continue
        obt_d.add((ent, campo))
        if (ent, campo) in esp_wit and d.get("witnessed") == esp_wit[(ent, campo)]:
            r["wit_ok"] += 1

    esp, obt = esp_e | esp_d, obt_e | obt_d
    r["tp"] = len(esp & obt)
    r["fp"] = len(obt - esp)
    r["fn"] = len(esp - obt)
    r["detalle"] = {"acertados": sorted(esp & obt),
                    "sobrantes": sorted(obt - esp),
                    "perdidos": sorted(esp - obt)}
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--repeticiones", type=int, default=1)
    ap.add_argument("--solo", default=None, help="ids separados por coma")
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY. Carga el .env primero.")

    contrato = cargar("extractor/contrato.json")
    prompt = (RAIZ / "extractor" / "prompt.md").read_text(encoding="utf-8")
    world = cargar("fixtures/world.json")
    personas = cargar("fixtures/personas.json")
    turnos = cargar("fixtures/turns.json")

    if args.solo:
        ids = {x.strip() for x in args.solo.split(",")}
        turnos = [t for t in turnos if t["id"] in ids]

    lista = entidades_disponibles(world, personas)
    # En produccion: SELECT de los promise_made abiertos. Aqui, fijos.
    # 'turno' = cuándo se contrajo. En producción viene del promise_made
    # registrado; sirve para excluirlo del turno en que se hace la promesa.
    COMPROMISOS = [
        {"pnj": "brea", "turno": "T00",
         "texto": "El grupo se comprometió a ir a hablar con Herda, "
                  "la vendedora del Mercado Bajo."},
        {"pnj": "brea", "turno": "T17",
         "texto": "El grupo se comprometió a traer a Brea las fichas "
                  "del peaje nocturno como prueba."},
    ]
    p_verif = (RAIZ / "extractor" / "verificador.md").read_text(encoding="utf-8")
    tot = defaultdict(int)
    por_tipo = defaultdict(lambda: defaultdict(int))
    registro = []

    print(f"\n{'='*72}\nSONDEO 4 · EXTRACTOR · {args.modelo}\n{'='*72}")

    for turno in turnos:
        neg = not turno["expected_events"] and not turno["expected_deltas"]
        etiqueta = "NEGATIVO" if neg else turno["kind"]
        print(f"\n{turno['id']} · {etiqueta}")

        for rep in range(args.repeticiones):
            ctx = contexto_escena(turno, personas, world,
                                  [c["texto"] for c in COMPROMISOS])
            user = (f"ENTIDADES EXISTENTES\n{lista}\n{ctx}\n"
                    f"TURNO\n"
                    + "\n".join(f"{m['pc']}: {m['text']}" for m in turno["player_buffer"])
                    + f"\nDM: {turno['dm_output']}")
            res = llamar(key, args.modelo, prompt, user)
            if res is None:
                print("   llamada fallida")
                continue
            salida = parsear(res["texto"])
            if salida is None:
                print(f"   JSON no parseable: {res['texto'][:80]}")
                tot["json_malo"] += 1
                continue

            # Segunda pasada: condiciones declaradas. Pregunta binaria y cerrada.
            conds = condiciones(turno, personas, world, COMPROMISOS)
            if conds:
                lista_c = "\n".join(f"  [{c['id']}] ({c['tipo']}) {c['texto']}"
                                    for c in conds)
                uv = (f"CONDICIONES DECLARADAS\n{lista_c}\n\nTURNO\n"
                      + "\n".join(f"{m['pc']}: {m['text']}" for m in turno["player_buffer"])
                      + f"\nDM: {turno['dm_output']}")
                rv = llamar(key, args.modelo, p_verif, uv)
                if rv:
                    tot["tokens_in"] += rv["tokens_in"] or 0
                    tot["tokens_out"] += rv["tokens_out"] or 0
                    try:
                        obj = json.loads(re.sub(r"^```(?:json)?|```$", "",
                                                rv["texto"].strip(), flags=re.M).strip())
                        cumplidas = obj.get("cumplidas") or []
                    except Exception:
                        cumplidas = []
                    if cumplidas:
                        salida = aplicar_condiciones(cumplidas, conds, salida)

            ev = evaluar(turno, salida, contrato)
            for k in ("tp", "fp", "fn", "ev_ok", "ev_total", "wit_ok", "wit_esp"):
                tot[k] += ev[k]
                por_tipo[etiqueta][k] += ev[k]
            tot["llamadas"] += 1
            tot["tokens_in"] += res["tokens_in"] or 0
            tot["tokens_out"] += res["tokens_out"] or 0

            marca = "ok " if ev["fp"] == 0 and ev["fn"] == 0 else "   "
            print(f"  {marca}tp={ev['tp']} fp={ev['fp']} fn={ev['fn']}  "
                  f"evidencia {ev['ev_ok']}/{ev['ev_total']}  {res['ms']} ms")
            if ev["detalle"]["sobrantes"]:
                print(f"     SOBRA  {ev['detalle']['sobrantes']}")
            if ev["detalle"]["perdidos"]:
                print(f"     FALTA  {ev['detalle']['perdidos']}")
            for i in ev["invalidos"]:
                print(f"     INVÁLIDO  {i}")

            registro.append({"turno": turno["id"], "rep": rep, "salida": salida,
                             "eval": ev, "ms": res["ms"]})

    # ------------------------------------------------------------- resumen
    tp, fp, fn = tot["tp"], tot["fp"], tot["fn"]
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    ev_pct = tot["ev_ok"] / tot["ev_total"] if tot["ev_total"] else 1.0

    print(f"\n{'='*72}\nRESULTADO\n{'='*72}")
    print(f"  precisión   {prec:.1%}   ← la que importa (sobre-extraer es irrecuperable)")
    print(f"  recall      {rec:.1%}   ← sub-detectar se arregla reprocesando")
    print(f"  F1          {f1:.1%}")
    print(f"  evidencia literal  {ev_pct:.1%}  ({tot['ev_ok']}/{tot['ev_total']})")
    if tot["wit_esp"]:
        print(f"  testigos           {tot['wit_ok']}/{tot['wit_esp']}  "
              f"← señal para la propagación a facciones, no afecta P/R")
    if tot["json_malo"]:
        print(f"  JSON no parseable  {tot['json_malo']}")

    print("\n  por tipo de turno:")
    for tipo, d in sorted(por_tipo.items()):
        p = d["tp"] / (d["tp"] + d["fp"]) if d["tp"] + d["fp"] else 1.0
        print(f"    {tipo:16s} tp={d['tp']:>3} fp={d['fp']:>3} fn={d['fn']:>3}  "
              f"precisión {p:.0%}")

    coste = (tot["tokens_in"] * 0.09 + tot["tokens_out"] * 0.34) / 1e6
    print(f"\n  {tot['llamadas']} llamadas · "
          f"{tot['tokens_in']}→{tot['tokens_out']} tokens · ${coste:.4f}")

    destino = RAIZ / f"sondeo4_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    json.dump({"modelo": args.modelo, "fecha": datetime.now().isoformat(),
               "precision": prec, "recall": rec, "f1": f1,
               "evidencia_literal": ev_pct, "registro": registro},
              open(destino, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  detalle en {destino.name}")

    print("\nLECTURA")
    if fp and por_tipo["NEGATIVO"]["fp"]:
        print(f"  ⚠ {por_tipo['NEGATIVO']['fp']} falsos positivos en turnos NEGATIVOS.")
        print("    Son intenciones no ejecutadas, sarcasmo o gags. Es el fallo")
        print("    grave: eso entraría al canon y nada lo señalaría después.")
    if ev_pct < 0.8:
        print(f"  ⚠ Solo {ev_pct:.0%} de las citas es literal. apply_delta")
        print("    rechazaría el resto. Revisar si el prompt es claro o si hace")
        print("    falta aflojar a coincidencia difusa.")
    if prec >= 0.9 and ev_pct >= 0.9:
        print("  Precisión y evidencia altas: el extractor es usable.")
        if rec < 0.7:
            print(f"  Recall {rec:.0%} es bajo pero recuperable — el turn_log queda")
            print("  íntegro y se puede reprocesar con mejor prompt más adelante.")


if __name__ == "__main__":
    main()