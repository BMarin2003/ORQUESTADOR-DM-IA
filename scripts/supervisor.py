#!/usr/bin/env python3
"""
Supervisor de las corridas Par 07-17: un solo proceso que mantiene UN proceso de
generacion por campania (G2: vertical_slice.py, G1: vertical_slice_g1.py) y relanza
el que se caiga, siempre con --turnos = 1400 - current_turn REAL (regla del plan).

Salvaguardas (para no duplicar trabajo ni corromper estado):
  - nunca lanza una campania que ya tenga un python.exe vivo con su campaign-id;
  - no relanza si hay turnos a medias en Postgres (state_deltas / turn_validation /
    turn_log con turn_id > current_turn): marca BLOQUEADA y avisa -> revisar a mano;
  - se rinde (RENDIDA) si una campania cae 6 veces seguidas sin avanzar ni un turno;
  - espera antes de relanzar (60 s, y crece si no hay progreso, tope 15 min);
  - un solo supervisor a la vez (puerto local como candado).

Uso:  python -u scripts/supervisor.py [--arm ambos|G2|G1] [--pares 07,08,...]
Log:  logs/supervisor.log   (eventos)   +   logs/parNN_g?_sup.log (salida de cada campania)
"""
import argparse
import json
import re
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

OBJETIVO = 1400
MAX_FALLOS = 6
PJ_POR_PAR = {"07": "PJ23", "08": "PJ04", "09": "PJ17", "10": "PJ24", "11": "PJ26",
              "12": "PJ07", "13": "PJ21", "14": "PJ20", "15": "PJ01", "16": "PJ12",
              "17": "PJ22"}
SCRIPT = {"G2": "orquestador/vertical_slice.py", "G1": "orquestador/vertical_slice_g1.py"}
TERMINALES = ("COMPLETA", "BLOQUEADA", "RENDIDA")
LOG = RAIZ / "logs" / "supervisor.log"   # --log lo cambia (Par 18-27: supervisor_par18-27.log)


def log(msg):
    linea = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linea, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(linea + "\n")


def estado_db(cid):
    """(current_turn, filas_a_medias) -- a medias = escritas para un turno > current_turn."""
    with psycopg.connect(db.DSN) as c:
        t = c.execute("SELECT current_turn FROM campaigns WHERE id=%s", (cid,)).fetchone()[0]
        h = sum(c.execute(f"SELECT count(*) FROM {tabla} WHERE campaign_id=%s AND turn_id > %s",
                          (cid, t)).fetchone()[0]
                for tabla in ("state_deltas", "turn_validation", "turn_log"))
    return t, h


def campanias_vivas():
    """campaign-id de todo python.exe de generacion que ya este corriendo (cualquier origen)."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -match 'vertical_slice' } | "
          "ForEach-Object { $_.CommandLine }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=60).stdout
    return set(re.findall(r"--campaign-id ([0-9a-f-]{36})", out))


def lanzar(j, turno):
    j["log"].parent.mkdir(exist_ok=True)
    with j["log"].open("ab") as f:
        j["proc"] = subprocess.Popen(
            [sys.executable, "-u", SCRIPT[j["brazo"]], "--campaign-id", j["cid"],
             "--pj", j["pj"], "--turnos", str(OBJETIVO - turno)],
            cwd=RAIZ, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)
    j["turno_al_lanzar"] = turno
    log(f"[LANZADA] {j['nombre']} desde turno {turno} -> --turnos {OBJETIVO - turno} (PID {j['proc'].pid})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["ambos", "G2", "G1"], default="ambos")
    ap.add_argument("--pares", default=None, help="por defecto, todos los del archivo de ids")
    ap.add_argument("--ids", default="docs/ids_par07-17.json")
    ap.add_argument("--log", default=None, help="log de eventos (por defecto logs/supervisor.log)")
    args = ap.parse_args()
    global LOG
    if args.log:
        LOG = RAIZ / args.log

    candado = socket.socket()
    try:
        candado.bind(("127.0.0.1", 47653))
    except OSError:
        sys.exit("Ya hay un supervisor corriendo (puerto 47653 ocupado). No se lanza otro.")

    ids = {e["par"]: e for e in json.loads((RAIZ / args.ids).read_text(encoding="utf-8"))}
    jobs = []
    for par in (args.pares.split(",") if args.pares else list(ids)):
        par = par.strip().zfill(2)
        for brazo in ("G2", "G1"):
            if args.arm in ("ambos", brazo):
                jobs.append({"nombre": f"Par{par} {brazo}", "brazo": brazo, "par": par,
                             "cid": ids[par]["campaign_g2" if brazo == "G2" else "campaign_g1"],
                             "pj": ids[par].get("pj") or PJ_POR_PAR[par], "proc": None, "fallos": 0, "proximo": 0.0,
                             "turno_al_lanzar": -1, "estado": "ACTIVA",
                             "log": RAIZ / "logs" / f"par{par}_{brazo.lower()}_sup.log"})
    log(f"[SUPERVISOR] arrancado con {len(jobs)} campanias (arm={args.arm})")

    while True:
        for j in jobs:
            if j["estado"] in TERMINALES:
                continue
            p = j["proc"]
            if p is not None and p.poll() is None:
                continue
            try:
                turno, a_medias = estado_db(j["cid"])
            except Exception as e:  # DB caida un rato: no es motivo para rendirse
                log(f"[DB] {j['nombre']}: no pude leer Postgres ({e!r}); reintento luego")
                continue
            if p is not None:
                j["proc"] = None
                j["fallos"] = 0 if turno > j["turno_al_lanzar"] else j["fallos"] + 1
                j["proximo"] = time.time() + min(900, 60 * 2 ** j["fallos"])
                log(f"[REINICIO] {j['nombre']} termino con codigo {p.returncode} en turno {turno} "
                    f"(fallos seguidos sin avanzar: {j['fallos']})")
            if turno >= OBJETIVO:
                j["estado"] = "COMPLETA"
                log(f"[COMPLETA] {j['nombre']} llego a {turno}/{OBJETIVO}")
                continue
            if a_medias:
                j["estado"] = "BLOQUEADA"
                log(f"[BLOQUEADA] {j['nombre']}: {a_medias} fila(s) escritas para un turno > {turno} "
                    f"(turno a medias). NO se relanza; revisar a mano para no aplicar deltas dos veces.")
                continue
            if j["fallos"] >= MAX_FALLOS:
                j["estado"] = "RENDIDA"
                log(f"[RENDIDA] {j['nombre']}: {MAX_FALLOS} caidas seguidas sin avanzar (turno {turno}).")
                continue
            if time.time() < j["proximo"]:
                continue
            try:
                if j["cid"] in campanias_vivas():
                    log(f"[OMITIDA] {j['nombre']}: ya hay un proceso vivo con esa campania (no se duplica)")
                    j["proximo"] = time.time() + 120
                    continue
            except Exception as e:
                log(f"[AVISO] no pude listar procesos ({e!r}); no lanzo {j['nombre']} por precaucion")
                j["proximo"] = time.time() + 120
                continue
            lanzar(j, turno)

        if all(j["estado"] in TERMINALES for j in jobs):
            log("[SUPERVISOR] todas las campanias en estado terminal. Fin.")
            break
        time.sleep(30)


if __name__ == "__main__":
    main()
