r"""
BARRIDO DE CIERRE DE SESIÓN — capa 2 del cierre de misiones.

Por qué existe:
  El verificador turno a turno es deliberadamente prudente: cerrar una misión
  que sigue abierta queda como canon y nada lo señala después. El precio es
  que algunas misiones resueltas nunca se cierran, y eso ensucia el contexto
  de todas las sesiones siguientes, engaña a stagnation_check y hace que el
  recap diga que algo está pendiente cuando narrativamente se resolvió.

  La razón de fondo por la que el chequeo por turno falla:
  **la evidencia de que una misión se completó suele estar repartida entre
  varios turnos.** Encuentran las fichas en el turno 40, las entregan en el
  55, el PNJ confirma en el 56. Ningún turno aislado cumple la condición;
  la sesión entera sí.

  Este barrido corre UNA vez al cerrar sesión, con el transcript completo en
  contexto. Una llamada por sesión, no por turno.

Orden de las tres capas:
  1. Predicados estructurados  → SQL, sin modelo (check_completion_predicates)
  2. Este barrido              → prosa, una llamada con todo el transcript
  3. Escalado por antigüedad   → producto

Uso:
  py sondeos\barrido_sesion.py --modelo google/gemma-4-31B-it
  py sondeos\barrido_sesion.py --modelo google/gemma-4-31B-it --hasta T16
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

BASE = "https://api.deepinfra.com/v1/openai"
RAIZ = Path(__file__).resolve().parent.parent.parent


def cargar(rel):
    return json.loads((RAIZ / rel).read_text(encoding="utf-8"))


def llamar(key, modelo, system, user, max_tokens=900):
    cuerpo = {"model": modelo,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}],
              "temperature": 0, "max_tokens": max_tokens,
              "response_format": {"type": "json_object"}}
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        det = e.read().decode()[:200]
        if "response_format" in det or e.code == 422:
            cuerpo.pop("response_format")
            req = urllib.request.Request(
                f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read().decode())
        else:
            print(f"HTTP {e.code}: {det}", file=sys.stderr)
            return None
    return {"texto": d["choices"][0]["message"]["content"],
            "tin": d.get("usage", {}).get("prompt_tokens") or 0,
            "tout": d.get("usage", {}).get("completion_tokens") or 0,
            "ms": round((time.time() - t0) * 1000)}


def aplanar(bruto, ids_validos):
    """Normaliza la respuesta del modelo contra los ids que SÍ existen.

    No adivina la estructura: busca cuál de las condiciones conocidas
    referencia cada entrada. Así no puede fabricar ids inexistentes a partir
    de nombres de campo como 'turno' o 'evidence' — que es exactamente lo que
    hacía la versión anterior, destrozando una respuesta correcta.
    """
    validos = set(ids_validos)
    salida, vistos = [], set()

    def recoger(x):
        if isinstance(x, list):
            # Forma de par: ["id", {campos}]. El modelo la usa a menudo y
            # recorrerla elemento a elemento separa el id de sus campos.
            if (len(x) == 2 and isinstance(x[0], str) and x[0] in validos
                    and isinstance(x[1], dict)):
                recoger({"id": x[0], **x[1]})
                return
            for y in x:
                recoger(y)
            return
        if not isinstance(x, dict):
            if isinstance(x, str) and x in validos and x not in vistos:
                vistos.add(x)
                salida.append({"id": x, "evidence": ""})
            return

        # ¿Qué condición conocida referencia este objeto?
        cid = None
        for v in x.values():
            if isinstance(v, str) and v in validos:
                cid = v
                break
        campos = x
        if cid is None:
            for k in x:
                if k in validos:
                    cid = k
                    # Los campos pueden venir anidados bajo la propia clave.
                    if isinstance(x[k], dict):
                        campos = {**x, **x[k]}
                    break

        if cid:
            if cid not in vistos:
                vistos.add(cid)
                salida.append({
                    "id": cid,
                    "evidence": campos.get("evidence") or campos.get("cita") or "",
                    "resultado": campos.get("resultado"),
                    "turno": campos.get("turno") or campos.get("turn") or "",
                })
            return

        # Sin id reconocible: puede ser un contenedor. Baja un nivel.
        for v in x.values():
            if isinstance(v, (list, dict)):
                recoger(v)

    recoger(bruto)
    return salida


def transcript(turnos):
    """El texto de la sesión, con marca de turno para poder citar."""
    partes = []
    for t in turnos:
        partes.append(f"[{t['id']}]")
        for m in t["player_buffer"]:
            partes.append(f"  {m['pc']}: {m['text']}")
        partes.append(f"  DM: {t['dm_output']}")
    return "\n".join(partes)


def condiciones_abiertas(world, personas, compromisos, hasta=None):
    """Todo lo que sigue sin resolverse al cerrar la sesión."""
    out = []
    for q in world["quests"]:
        if q["status"] in ("active", "unknown") and q.get("completion_condition"):
            out.append({"id": f"quest:{q['key']}:completed", "tipo": "mision",
                        "texto": q["completion_condition"]})
    for k, p in personas.items():
        if k.startswith("_"):
            continue
        for i, s in enumerate(p.get("secrets") or []):
            if not s.get("revealed_at_turn"):
                out.append({"id": f"secret:{k}:{i}", "tipo": "secreto",
                            "texto": s["reveal_condition"]})
    for i, c in enumerate(compromisos):
        out.append({"id": f"promesa:{i}", "tipo": "compromiso", "texto": c["texto"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--hasta", default=None, help="id del último turno de la sesión")
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY. Carga el .env primero.")

    world = cargar("fixtures/world.json")
    personas = cargar("fixtures/personas.json")
    turnos = cargar("fixtures/turns.json")
    if args.hasta:
        ids = [t["id"] for t in turnos]
        turnos = turnos[:ids.index(args.hasta) + 1]

    COMPROMISOS = [
        {"pnj": "brea", "texto": "El grupo se comprometió a ir a hablar con Herda, "
                                 "la vendedora del Mercado Bajo."},
        {"pnj": "brea", "texto": "El grupo se comprometió a traer a Brea las fichas "
                                 "del peaje nocturno como prueba."},
    ]

    prompt = (RAIZ / "extractor" / "verificador.md").read_text(encoding="utf-8")
    prompt += """

═══ MODO BARRIDO DE SESIÓN ═══

Ahora no recibes un turno suelto: recibes **la sesión completa**, con los
turnos marcados como [T01], [T02]...

La evidencia de que una condición se cumplió puede estar **repartida entre
varios turnos**. Búscala en toda la sesión, no en un turno aislado.

Cada entrada lleva OBLIGATORIAMENTE estos tres campos:

  {"id": "<id exacto de la lista>",
   "turno": "[T16]",
   "evidence": "<cita literal copiada de ese turno>"}

**Una entrada sin `evidence` se descarta entera.** No basta con nombrar la
condición: hay que citar el texto que demuestra que se cumplió. Si no
encuentras una cita literal que lo demuestre, esa condición no se cumplió.

Nunca devuelvas una lista de ids sueltos. Siempre objetos con los tres campos.

Sigue aplicando la misma prudencia: ante la duda, no la incluyas.
"""

    conds = condiciones_abiertas(world, personas, COMPROMISOS)

    sin_cond = [q["key"] for q in world["quests"]
                if q["status"] in ("active", "unknown")
                and not q.get("completion_condition")]
    if sin_cond:
        print(f"\n  ⚠ Misiones abiertas SIN completion_condition: {sin_cond}")
        print("    El barrido no puede cerrarlas. Revisa que world.json sea la")
        print("    versión con condiciones de cierre declaradas.\n")
    texto = transcript(turnos)

    print(f"\n{'='*72}\nBARRIDO DE CIERRE DE SESIÓN · {args.modelo}\n{'='*72}")
    print(f"  {len(turnos)} turnos · {len(conds)} condiciones abiertas · "
          f"{len(texto)} caracteres de transcript\n")
    for c in conds:
        print(f"  [{c['id']}] ({c['tipo']}) {c['texto'][:64]}")

    lista = "\n".join(f"  [{c['id']}] ({c['tipo']}) {c['texto']}" for c in conds)
    user = f"CONDICIONES ABIERTAS\n{lista}\n\nSESIÓN COMPLETA\n{texto}"

    res = llamar(key, args.modelo, prompt, user)
    if not res:
        sys.exit(1)


    try:
        obj = json.loads(re.sub(r"^```(?:json)?|```$", "", res["texto"].strip(),
                                flags=re.M).strip())
    except Exception:
        print(f"\nJSON no parseable:\n{res['texto'][:300]}")
        sys.exit(1)

    cumplidas = aplanar(obj.get("cumplidas") or obj.get("satisfechas") or obj,
                        [c["id"] for c in conds])

    print(f"\n{'-'*72}\nRESULTADO  ({res['ms']} ms · "
          f"{res['tin']}→{res['tout']} tokens · "
          f"${(res['tin']*0.09 + res['tout']*0.34)/1e6:.4f})\n{'-'*72}")

    if not cumplidas:
        print("  Ninguna condición se cerró en esta sesión.")
    idx = {c["id"]: c for c in conds}
    aceptadas, rechazadas = [], []
    for c in cumplidas:
        if c.get("id") not in idx:
            rechazadas.append((c.get("id"), "id desconocido"))
            continue
        ev = (c.get("evidence") or "").strip()
        if not ev:
            rechazadas.append((c["id"], "sin cita — no se puede verificar"))
            continue
        if ev not in texto:
            rechazadas.append((c["id"], f"cita no literal: «{ev[:50]}»"))
            continue
        aceptadas.append(c)

    for c in aceptadas:
        res_c = f" [{c['resultado']}]" if c.get("resultado") else ""
        print(f"  ✓ {c['id']}{res_c}  {c.get('turno','')}")
        print(f"      «{c['evidence'][:90]}»")
    for cid, motivo in rechazadas:
        print(f"  ✗ {cid} — {motivo}")

    print(f"\n  {len(aceptadas)} aceptadas · {len(rechazadas)} rechazadas")
    if rechazadas and not aceptadas:
        print("  El modelo identificó condiciones pero sin cita verificable.")
        print("  Revisa la respuesta cruda en el JSON: puede haber devuelto")
        print("  solo la lista de ids en vez de objetos completos.")
    cumplidas = aceptadas

    # --- contraste con el ground truth de los fixtures
    print(f"\n{'-'*72}\nCONTRASTE\n{'-'*72}")
    esperado = set()
    for t in turnos:
        for d in t["expected_deltas"]:
            if d["entity_type"] == "quest" and d["field"] == "status":
                esperado.add(f"quest:{d['entity']}:completed")
            if d["field"] == "secret_revealed":
                esperado.add(f"secret:{d['entity']}:0")
        for e in t["expected_events"]:
            if e["event_kind"] in ("promise_kept", "promise_broken"):
                esperado.add("promesa:*")
    obtenido = {c.get("id") for c in cumplidas}
    print(f"  esperado por los fixtures: {sorted(esperado) or 'nada'}")
    print(f"  cerrado por el barrido:    {sorted(obtenido) or 'nada'}")
    falta = {e for e in esperado if e != "promesa:*"} - obtenido
    if falta:
        print(f"  sigue sin cerrarse:        {sorted(falta)}")
    else:
        print(f"  sin misiones ni secretos pendientes de cierre")

    destino = RAIZ / f"barrido_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    json.dump({"modelo": args.modelo, "turnos": [t["id"] for t in turnos],
               "condiciones": conds,
               "respuesta_cruda": res["texto"],
               "cumplidas": cumplidas, "rechazadas": rechazadas},
              open(destino, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  detalle en {destino.name}")


if __name__ == "__main__":
    main()