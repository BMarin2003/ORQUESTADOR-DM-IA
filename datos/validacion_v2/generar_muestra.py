"""
Validación humana v2 -- genera la muestra estratificada (solo SELECT, sin LLM, detectores sin tocar).

persona2: Sí 100 (máx. 5 por campaña) + No 300 (máx. 8 por campaña), asignación proporcional por brazo.
PNJ:      Sí 100 (máx. 30 por campaña, sin proporción por brazo: el detector solo se activa en 6 campañas)
          + No-mencionado 50 + No-sin-mención 50 (máx. 3 por campaña), proporcional por brazo.
Excluye: turnos de desarrollo de persona2, turno 1 y todo turno ya etiquetado en la validación anterior.
El texto que ve el evaluador es el MISMO texto normalizado que recibió el detector.
Salidas (validacion_v2/):
  items.json -> lo que ve el evaluador (id, tipo, pj, accion, texto, hecho); orden aleatorio
  clave.csv  -> PRIVADO: id, tipo, estrato, par, brazo, campaign_id, turn_id, detector (0/1), pnj
    PYTHONUTF8=1 py validacion_v2/generar_muestra.py
"""
import csv
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AQUI = Path(__file__).resolve().parent
for _p in (RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad",
           RAIZ / "scripts" / "instrumentos", RAIZ / "orquestador"):
    sys.path.insert(0, str(_p))

import datos                                              # noqa: E402
import pares as _pares                                    # noqa: E402
from evaluar_persona2 import cargar_nombres, jugador      # noqa: E402
from normalizacion import normalizar_turno                # noqa: E402

SEMILLA = 20261028
ESTADO = {"dead": "fallecido", "missing": "desaparecido", "captured": "capturado"}
VAL = RAIZ / "validacion"


def verificar_congelado():
    """persona2.py y su léxico deben coincidir con el hash congelado (rutas del archivo, con o sin prefijo experimento/)."""
    for linea in (VAL / "persona2_congelado.sha256").read_text(encoding="utf-8").splitlines():
        if not linea.strip() or linea.startswith("#"):
            continue
        h, ruta = linea.split(None, 1)
        ruta = ruta.strip().lstrip("*")
        local = RAIZ / ruta
        if not local.exists():
            local = RAIZ / ruta.replace("experimento/", "", 1)
        if hashlib.sha256(local.read_bytes()).hexdigest() != h:
            sys.exit(f"ABORTA: {local} no coincide con el hash congelado")


def ya_etiquetados():
    vistos = set()
    for nombre, col in (("confirmacion_persona2_clave.csv", "turn_id"), ("auditoria_persona2_clave.csv", "turn_id"),
                        ("brecha4_clave.csv", "turno_evaluado")):
        with open(VAL / nombre, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                vistos.add((r["campaign_id"], int(r[col])))
    return vistos


def muestrear(pool, n, tope, rng, prop_brazo=True):
    """Asignación proporcional por brazo (o un solo grupo); dentro, orden aleatorio con tope por campaña."""
    grupos = defaultdict(list)
    for r in pool:
        grupos[r["brazo"] if prop_brazo else "todos"].append(r)
    cuota = {b: round(n * len(v) / len(pool)) for b, v in grupos.items()}
    cuota[max(cuota, key=lambda k: len(grupos[k]))] += n - sum(cuota.values())
    elegidos = []
    for b, v in sorted(grupos.items()):
        v = sorted(v, key=lambda r: (r["campaign_id"], r["turn_id"]))
        rng.shuffle(v)
        usados, tomados = Counter(), []
        for r in v:
            if len(tomados) == cuota[b]:
                break
            if usados[r["campaign_id"]] < tope:
                usados[r["campaign_id"]] += 1
                tomados.append(r)
        if len(tomados) < cuota[b]:
            sys.exit(f"ABORTA: tope {tope} no alcanza la cuota {cuota[b]} ({b})")
        elegidos += tomados
    return elegidos


def pools(campanas, vistos):
    p2_si, p2_no = [], []
    for c in campanas:
        with open(RAIZ / "datos_v2" / "persona2" / f"par{c['par']}_{c['brazo']}.csv", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                t = int(r["turn_id"])
                if t < 2 or r["en_desarrollo"] == "1" or (c["campaign_id"], t) in vistos:
                    continue
                (p2_si if r["primaria"] == "1" else p2_no).append(dict(c, turn_id=t))
    pnj_si, pnj_menc, pnj_nomenc = [], [], []
    with open(AQUI / "pool_pnj.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            t = int(r["turn_id"])
            if (r["campaign_id"], t) in vistos:
                continue
            ina = [x.split("|") for x in r["inactivos"].split(";")]
            fila = {"par": r["par"], "brazo": r["brazo"], "campaign_id": r["campaign_id"], "turn_id": t, "inactivos": ina,
                    "mencionados": [m for m in r["mencionados"].split(";") if m],
                    "detector_pnj": [m for m in r["pnj_detector"].split(";") if m]}
            if r["refinado"] == "1":
                pnj_si.append(fila)
            elif fila["mencionados"]:
                pnj_menc.append(fila)
            else:
                pnj_nomenc.append(fila)
    return p2_si, p2_no, pnj_si, pnj_menc, pnj_nomenc


def hecho(nombre, inactivos):
    for nm, st, desde in inactivos:
        if nm == nombre:
            cuando = f"desde el turno {desde}" if desde not in (None, "", "None") else "desde el inicio de la campaña"
            return f"{nm} figura como {ESTADO.get(st, st)} {cuando}."
    raise ValueError(nombre)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    verificar_congelado()
    rng = random.Random(SEMILLA)
    campanas = [{"par": p["par"], "brazo": b, "campaign_id": str(p[k])}
                for p in _pares.todos() for b, k in (("G1", "campaign_g1"), ("G2", "campaign_g2"))]
    p2_si, p2_no, pnj_si, pnj_menc, pnj_nomenc = pools(campanas, ya_etiquetados())
    print(f"pools: p2 Sí {len(p2_si)} | p2 No {len(p2_no)} | PNJ Sí {len(pnj_si)} | PNJ No-menc {len(pnj_menc)} | PNJ No-sin {len(pnj_nomenc)}")
    sel = ([("persona2", "si", r) for r in muestrear(p2_si, 100, 5, rng)]
           + [("persona2", "no", r) for r in muestrear(p2_no, 300, 8, rng)]
           + [("pnj", "si", r) for r in muestrear(pnj_si, 100, 30, rng, prop_brazo=False)]
           + [("pnj", "no_mencionado", r) for r in muestrear(pnj_menc, 50, 3, rng)]
           + [("pnj", "no_sin_mencion", r) for r in muestrear(pnj_nomenc, 50, 3, rng)])
    ids = rng.sample(range(100000, 999999), len(sel))
    nombres_pj = cargar_nombres()
    cache, items, clave = {}, [], []
    with datos.abrir_conexion() as conn:
        for (tipo, estrato, r), num in zip(sel, ids):
            cid = r["campaign_id"]
            if cid not in cache:
                cache[cid] = datos.DatosCampana(conn, cid, r["brazo"], r["par"])
            f = cache[cid].turnos[r["turn_id"]]
            buf = f["player_buffer"] or []
            pc = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
            it = {"id": f"V{num}", "tipo": tipo, "pj": nombres_pj.get(pc) or cache[cid].pj_nombre,
                  "accion": jugador(buf), "texto": normalizar_turno(f["dm_output"], r["brazo"])}
            pnj = ""
            if tipo == "pnj":
                cand = {"si": [n for n in r["detector_pnj"] if n in {x[0] for x in r["inactivos"]}],
                        "no_mencionado": r["mencionados"], "no_sin_mencion": [x[0] for x in r["inactivos"]]}[estrato]
                pnj = rng.choice(sorted(cand))
                it["hecho"] = hecho(pnj, r["inactivos"])
            items.append(it)
            clave.append({"id": it["id"], "tipo": tipo, "estrato": estrato, "par": r["par"], "brazo": r["brazo"],
                          "campaign_id": cid, "turn_id": r["turn_id"], "detector": int(estrato == "si"), "pnj": pnj})
    rng.shuffle(items)
    (AQUI / "items.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(AQUI / "clave.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(clave[0]))
        w.writeheader()
        w.writerows(clave)
    print("muestra:", Counter((c["tipo"], c["estrato"], c["brazo"]) for c in clave))
    print("campañas distintas:", len({c["campaign_id"] for c in clave}), "| items:", len(items))


if __name__ == "__main__":
    main()
