"""
Validación humana v2 -- preguntas C (Jericho-QA) y D (respuesta a la acción específica, CR-2a z). Solo SELECT, sin LLM,
instrumentos sin tocar (se llaman las mismas funciones del repositorio).

C: unidad = un delta narrable (npc.status, npc.affinity con cruce de banda, quest.status con vocabulario distintivo),
   texto = turnos N y N+1 normalizados (ventana=1 de jericho_qa_recall). Estratos: reconocido 100 / no reconocido 100,
   proporcional por brazo, máx. 10 por campaña (el universo es de solo 750 deltas evaluables).
D: unidad = un turno (acción del jugador + respuesta del DM limpiada con prosa(), el mismo texto que lematiza el
   instrumento). 150 turnos computables (z no nulo), proporcional por brazo, máx. 4 por campaña. El z se calcula y se
   guarda ANTES del etiquetado; no se binariza.
Excluye turno 1, turnos > 1400, la muestra A/B (clave.csv, controles_clave.csv) y la validación anterior.
Salidas: items_cd.json, clave_cd.csv (PRIVADO), candidatos_control_cd.json/.md
    PYTHONUTF8=1 py validacion_v2/ampliar_cd.py
"""
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
for _p in (AQUI, RAIZ / "scripts" / "instrumentos", RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts",
           RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    sys.path.insert(0, str(_p))

import generar_muestra as G                    # noqa: E402
import db as bd                                # noqa: E402
import reporte_validacion as RV                # noqa: E402
import respuesta_accion as ra                  # noqa: E402
import lemas_es as le                          # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402
from validacion_generar import prosa           # noqa: E402

SEMILLA = 20261031
HASTA = 1400
EST_NPC = {"dead": "fallecido", "missing": "desaparecido", "captured": "capturado"}
EST_QUEST = {"completed": "completada", "failed": "fallida", "abandoned": "abandonada"}
BANDA = {"hostile": "hostil", "wary": "recelosa", "cold": "fría", "cordial": "cordial", "loyal": "leal", "devoted": "devota"}


def valor(d):
    return str(d["new_value"]).strip('"').lower()


def hecho_c(d):
    campo, n = f"{d['entity_type']}.{d['field_name']}", d["entity_name"]
    if campo == "npc.status":
        return f"En el turno {d['turn_id']}, {n} pasó a estar {EST_NPC[valor(d)]}."
    if campo == "quest.status":
        return f"En el turno {d['turn_id']}, la misión «{n}» pasó a estar {EST_QUEST[valor(d)]}."
    return f"En el turno {d['turn_id']}, la disposición de {n} hacia el personaje jugador pasó a ser {BANDA[RV._banda_afinidad(d['new_value'])]}."


def pool_c(campanas, vistos, log):
    si, no = [], []
    for c in campanas:
        camp = bd.Campaña(c["campaign_id"])
        tpi = {t["turn_id"]: normalizar_turno(t["dm_output"], c["brazo"]) for t in camp.turnos_narracion() if t["turn_id"] <= HASTA}
        for d in camp.deltas_narrables():
            t = d["turn_id"]
            if not 2 <= t <= HASTA or (c["campaign_id"], t) in vistos:
                continue
            r = RV.jericho_qa_recall([d], tpi)
            if r["n_total"] != 1:
                continue                                   # no evaluable para el instrumento (sin vocabulario o sin cruce de banda)
            fila = dict(c, turn_id=t, delta=d, textos=[tpi.get(t, ""), tpi.get(t + 1, "")])
            (no if r["no_reconocidos"] else si).append(fila)
        log(f"  C par{c['par']} {c['brazo']}: acumulado Sí {len(si)} / No {len(no)}")
    return si, no


class PoolD:
    """Carga perezosa, por campaña, del reservorio de acciones y los tokens de respuesta (misma caché de lemas que la tesis)."""
    def __init__(self, conn):
        self.conn, self.c = conn, {}

    def campana(self, cid):
        if cid not in self.c:
            rs = [r for r in self.conn.execute("SELECT turn_id, player_buffer, dm_output FROM turn_log WHERE campaign_id=%s "
                                               "ORDER BY turn_id", (cid,)).fetchall() if r["turn_id"] <= HASTA]
            ts = [r["turn_id"] for r in rs if r["turn_id"] >= 1]
            por_t = {r["turn_id"]: r for r in rs}
            textos = {t: por_t[t]["dm_output"] or "" for t in ts}
            acciones = {t: por_t[t]["player_buffer"] for t in ts}
            tokR = dict(zip(ts, le.tokens_lote_cacheado(f"R_{cid}", [textos[t] for t in ts])))
            clases = {t: ra.clasificar_accion(acciones[t]) for t in ts}
            tokA = le.tokens_lote_cacheado(f"A_{cid}", [ra.texto_accion(acciones[t]) if clases[t] != "solo_tag" else "" for t in ts])
            pool = ra.PoolAcciones(cid, {t: le.filtrar(tk) for t, tk in zip(ts, tokA)}, clases)
            self.c[cid] = (textos, acciones, tokR, clases, pool)
        return self.c[cid]


def muestra_d(campanas, vistos, conn, n, tope, rng, log):
    cand = [dict(c, turn_id=t) for c in campanas for t in range(2, HASTA + 1) if (c["campaign_id"], t) not in vistos]
    grupos = defaultdict(list)
    for r in cand:
        grupos[r["brazo"]].append(r)
    cuota = {b: round(n * len(v) / len(cand)) for b, v in grupos.items()}
    cuota[max(cuota, key=lambda k: len(grupos[k]))] += n - sum(cuota.values())
    P, out = PoolD(conn), []
    for b, v in sorted(grupos.items()):
        rng.shuffle(v)
        usados, k = Counter(), 0
        for r in v:
            if k == cuota[b]:
                break
            if usados[r["campaign_id"]] >= tope:
                continue
            textos, acciones, tokR, clases, pool = P.campana(r["campaign_id"])
            if r["turn_id"] not in textos:
                continue
            m = ra.medir(pool, r["turn_id"], None, tokens_respuesta=tokR[r["turn_id"]])
            if m["z"] is None:
                continue                                   # no computable para el instrumento: no entra
            usados[r["campaign_id"]] += 1
            k += 1
            out.append(dict(r, z=m["z"], crudo=m["crudo"], clase=m["clase"], accion=G.jugador(acciones[r["turn_id"]]),
                            texto=prosa(textos[r["turn_id"]], "G1")))
        log(f"  D {b}: {k} turnos")
    return out


def nuevo_id(rng, usados):
    while True:
        iid = f"V{rng.randint(100000, 999999)}"
        if iid not in usados:
            usados.add(iid)
            return iid


def item_c(r, iid):
    return {"id": iid, "tipo": "jericho", "hecho": hecho_c(r["delta"]), "texto": r["textos"][0], "texto2": r["textos"][1],
            "turno": r["turn_id"]}


def item_d(r, iid):
    return {"id": iid, "tipo": "accion", "pj": "", "accion": r["accion"], "texto": r["texto"]}


def fila_c(r, iid, estrato, extra=None):
    d = r["delta"]
    return {"id": iid, "tipo": "jericho", "estrato": estrato, "par": r["par"], "brazo": r["brazo"], "campaign_id": r["campaign_id"],
            "turn_id": r["turn_id"], "campo": f"{d['entity_type']}.{d['field_name']}", "entidad": d["entity_name"],
            "valor": str(d["new_value"]), "detector": int(estrato == "si"), **(extra or {})}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = lambda s: print(s, flush=True)   # noqa: E731
    rng = random.Random(SEMILLA)
    campanas = [{"par": p["par"], "brazo": b, "campaign_id": str(p[k])}
                for p in G._pares.todos() for b, k in (("G1", "campaign_g1"), ("G2", "campaign_g2"))]
    vistos = G.ya_etiquetados()
    for nombre in ("clave.csv", "controles_clave.csv"):
        with open(AQUI / nombre, newline="", encoding="utf-8") as fh:
            vistos |= {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}
    usados = {i["id"] for i in json.loads((AQUI / "items_final.json").read_text(encoding="utf-8"))}

    c_si, c_no = pool_c(campanas, vistos, log)
    log(f"pool C: reconocido {len(c_si)} | no reconocido {len(c_no)}")
    sel_si, sel_no = G.muestrear(c_si, 100, 10, rng), G.muestrear(c_no, 100, 10, rng)
    items, clave = [], []
    for estrato, sel in (("si", sel_si), ("no", sel_no)):
        for r in sel:
            iid = nuevo_id(rng, usados)
            items.append(item_c(r, iid))
            clave.append(fila_c(r, iid, estrato))
            vistos.add((r["campaign_id"], r["turn_id"]))

    with G.datos.abrir_conexion() as conn:
        sel_d = muestra_d(campanas, vistos, conn, 150, 4, rng, log)
        for r in sel_d:
            iid = nuevo_id(rng, usados)
            items.append(item_d(r, iid))
            clave.append({"id": iid, "tipo": "accion", "estrato": "aleatorio", "par": r["par"], "brazo": r["brazo"],
                          "campaign_id": r["campaign_id"], "turn_id": r["turn_id"], "z": round(r["z"], 4),
                          "crudo": round(r["crudo"], 4), "clase": r["clase"]})
            vistos.add((r["campaign_id"], r["turn_id"]))
        extra_d = muestra_d(campanas, vistos, conn, 200, 4, rng, log)

    # candidatos a control
    usados_c = {(r["campaign_id"], r["turn_id"]) for r in sel_si + sel_no}
    cand = {"jericho_si": [], "jericho_no": [], "accion_si": [], "accion_no": []}
    for r in sorted(c_si, key=lambda r: (r["campaign_id"], r["turn_id"])):
        d = r["delta"]
        if (r["campaign_id"], r["turn_id"]) in usados_c or d["field_name"] != "status" or d["entity_type"] != "npc":
            continue
        if d["entity_name"] in r["textos"][0] and len(cand["jericho_si"]) < 10 and rng.random() < 0.3:
            cand["jericho_si"].append(r)
    for r in sorted(c_no, key=lambda r: (r["campaign_id"], r["turn_id"])):
        d = r["delta"]
        if (r["campaign_id"], r["turn_id"]) in usados_c:
            continue
        if d["entity_name"] not in " ".join(r["textos"]) and len(cand["jericho_no"]) < 10 and rng.random() < 0.3:
            cand["jericho_no"].append(r)
    corto = [r for r in extra_d if len(r["texto"].split()) <= 150]
    corto.sort(key=lambda r: r["z"])
    cand["accion_no"], cand["accion_si"] = corto[:10], corto[-10:][::-1]

    rng.shuffle(items)
    (AQUI / "items_cd.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    campos = sorted({k for f in clave for k in f}, key=lambda k: list(clave[0]).index(k) if k in clave[0] else 99)
    with open(AQUI / "clave_cd.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(clave)
    escribir_candidatos(cand)
    log(f"items C+D: {len(items)} | {Counter((f['tipo'], f['estrato'], f['brazo']) for f in clave)}")


def escribir_candidatos(cand):
    js = {}
    with open(AQUI / "candidatos_control_cd.md", "w", encoding="utf-8") as fh:
        fh.write("# Candidatos a ítems de control — preguntas C y D\n\nElegir 5 «Sí» y 5 «No» por pregunta. "
                 "En D, la respuesta esperada es la que ustedes fijen; el z se muestra solo para orientar la elección.\n")
        for cel, v in cand.items():
            js[cel] = []
            fh.write(f"\n## {cel} ({len(v)} candidatos)\n")
            esp = "Sí" if cel.endswith("_si") else "No"
            for k, r in enumerate(v, 1):
                if cel.startswith("jericho"):
                    it = item_c(r, "")
                    fh.write(f"\n### [ ] {cel}-{k:02d} · par{r['par']} {r['brazo']} turno {r['turn_id']} · esperada: **{esp}**\n\n"
                             f"**Hecho:** {it['hecho']}\n\n**Turno {r['turn_id']}:**\n> {it['texto'].replace(chr(10), chr(10) + '> ')}\n\n"
                             f"**Turno {r['turn_id'] + 1}:**\n> {it['texto2'].replace(chr(10), chr(10) + '> ')}\n")
                    js[cel].append(dict(it, esperada=esp, par=r["par"], brazo=r["brazo"], campaign_id=r["campaign_id"], turn_id=r["turn_id"]))
                else:
                    fh.write(f"\n### [ ] {cel}-{k:02d} · par{r['par']} {r['brazo']} turno {r['turn_id']} · z = {r['z']:.2f} · esperada: **{esp}**\n\n"
                             f"**Acción del jugador:**\n> {r['accion'].replace(chr(10), ' ')}\n\n**Turno del DM:**\n> {r['texto'].replace(chr(10), chr(10) + '> ')}\n")
                    js[cel].append(dict(item_d(r, ""), esperada=esp, par=r["par"], brazo=r["brazo"], campaign_id=r["campaign_id"],
                                        turn_id=r["turn_id"], z=r["z"]))
    (AQUI / "candidatos_control_cd.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
