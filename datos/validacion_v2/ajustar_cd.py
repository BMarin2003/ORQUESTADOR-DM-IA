"""
Ajuste de C y D (decisión de los autores, 2026-10-28):
D = 100 turnos al azar (subconjunto aleatorio de los 150 ya medidos) + 50 de la cola baja (z <= percentil 10 de un universo
    de 1 500 turnos computables al azar). La AUC principal se reporta solo con los 100 al azar.
Candidatos de control: C Sí (reconocido, npc.status, nombre en el texto), C No (ninguna palabra >= 4 letras del nombre de la
entidad en los dos turnos), D Sí (z alto, sin texto OOC, turno corto). Reescribe items_cd.json, clave_cd.csv y
candidatos_control_cd.*.
    PYTHONUTF8=1 py validacion_v2/ajustar_cd.py
"""
import csv
import json
import random
import re
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ampliar_cd as A                          # noqa: E402

SEMILLA = 20261101


def palabras(n):
    return [w for w in re.findall(r"\w+", n.lower()) if len(w) >= 4]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = lambda s: print(s, flush=True)   # noqa: E731
    rng = random.Random(SEMILLA)
    items = {i["id"]: i for i in json.loads((AQUI / "items_cd.json").read_text(encoding="utf-8"))}
    with open(AQUI / "clave_cd.csv", newline="", encoding="utf-8") as fh:
        clave = list(csv.DictReader(fh))
    d_ids = sorted(f["id"] for f in clave if f["tipo"] == "accion")
    quedan = set(rng.sample(d_ids, 100))
    clave = [f for f in clave if f["tipo"] != "accion" or f["id"] in quedan]
    items = {k: v for k, v in items.items() if k in {f["id"] for f in clave}}

    campanas = [{"par": p["par"], "brazo": b, "campaign_id": str(p[k])}
                for p in A.G._pares.todos() for b, k in (("G1", "campaign_g1"), ("G2", "campaign_g2"))]
    vistos = A.G.ya_etiquetados()
    for nombre in ("clave.csv", "controles_clave.csv", "clave_cd.csv"):
        with open(AQUI / nombre, newline="", encoding="utf-8") as fh:
            vistos |= {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}
    usados = {i["id"] for i in json.loads((AQUI / "items_final.json").read_text(encoding="utf-8"))} | set(items)

    with A.G.datos.abrir_conexion() as conn:
        universo = A.muestra_d(campanas, vistos, conn, 1500, 40, rng, log)
    zs = sorted(r["z"] for r in universo)
    p10 = zs[int(0.10 * len(zs))]
    log(f"universo D: {len(universo)} turnos · mediana z {statistics.median(zs):.2f} · p10 {p10:.2f}")
    cola = [r for r in universo if r["z"] <= p10]
    rng.shuffle(cola)
    usadas, cola_sel = {}, []
    for r in cola:
        if len(cola_sel) == 50:
            break
        if usadas.get(r["campaign_id"], 0) < 4:
            usadas[r["campaign_id"]] = usadas.get(r["campaign_id"], 0) + 1
            cola_sel.append(r)
    for r in cola_sel:
        iid = A.nuevo_id(rng, usados)
        items[iid] = A.item_d(r, iid)
        clave.append({"id": iid, "tipo": "accion", "estrato": "cola_baja", "par": r["par"], "brazo": r["brazo"],
                      "campaign_id": r["campaign_id"], "turn_id": r["turn_id"], "z": round(r["z"], 4),
                      "crudo": round(r["crudo"], 4), "clase": r["clase"]})
    sel = {(r["campaign_id"], r["turn_id"]) for r in cola_sel}
    resto = [r for r in universo if (r["campaign_id"], r["turn_id"]) not in sel]

    # candidatos de control
    usados_cd = {(f["campaign_id"], int(f["turn_id"])) for f in clave}
    c_si, c_no = A.pool_c(campanas, set(), lambda s: None)
    cand = {"jericho_si": [], "jericho_no": [], "accion_si": []}
    for r in sorted(c_si, key=lambda r: (r["campaign_id"], r["turn_id"])):
        d = r["delta"]
        if ((r["campaign_id"], r["turn_id"]) not in usados_cd and (r["campaign_id"], r["turn_id"]) not in vistos
                and d["entity_type"] == "npc" and d["field_name"] == "status" and d["entity_name"] in r["textos"][0]):
            cand["jericho_si"].append(r)
    rng.shuffle(cand["jericho_si"])
    cand["jericho_si"] = cand["jericho_si"][:10]
    for r in sorted(c_no, key=lambda r: (r["campaign_id"], r["turn_id"])):
        if (r["campaign_id"], r["turn_id"]) in usados_cd or (r["campaign_id"], r["turn_id"]) in vistos:
            continue
        txt = " ".join(r["textos"]).lower()
        if palabras(r["delta"]["entity_name"]) and not any(w in txt for w in palabras(r["delta"]["entity_name"])):
            cand["jericho_no"].append(r)
    rng.shuffle(cand["jericho_no"])
    cand["jericho_no"] = cand["jericho_no"][:10]
    alto = [r for r in resto if "ooc" not in (r["accion"] + r["texto"]).lower() and len(r["texto"].split()) <= 150]
    alto.sort(key=lambda r: -r["z"])
    cand["accion_si"] = alto[:10]

    final = list(items.values())
    rng.shuffle(final)
    (AQUI / "items_cd.json").write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    campos = list(dict.fromkeys(k for f in clave for k in f))
    with open(AQUI / "clave_cd.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(clave)
    A.escribir_candidatos(cand)
    from collections import Counter
    log(f"C+D: {len(final)} ítems · {Counter((f['tipo'], f['estrato']) for f in clave)} · candidatos {[len(v) for v in cand.values()]}")


if __name__ == "__main__":
    main()
