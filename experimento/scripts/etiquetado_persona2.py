#!/usr/bin/env python3
"""
Hoja de etiquetado CIEGA para auditar el detector persona2 (Plan A, paso A3).

Muestra al etiquetador SOLO la acción declarada por el jugador y el turno COMPLETO del DM (con el
formato normalizado de G1, `prosa`), en orden aleatorio. NO muestra brazo, par, campaña, categoría
detectada ni la frase marcada: ver el resultado del detector sesga (efecto ancla).

Entrada: datos/validacion/confirmacion_persona2_clave.csv (id_muestra, campaign_id, turn_id, brazo, estrato…).
Salida:  datos/validacion/etiquetado_persona2_<evaluador>.html  (autónomo; guarda solo; exporta CSV).

Uso: python experimento/scripts/etiquetado_persona2.py [--evaluador E1] [--fraccion 1.0] [--semilla 20260921]
  --fraccion 0.2  genera el subconjunto del 20 % (estratificado por estrato) para el segundo etiquetador.
"""
import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "motor" / "orquestador"))
sys.path.insert(0, str(RAIZ / "experimento" / "scripts"))
import db  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402
from validacion_generar import prosa  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    """Genera el formulario HTML autónomo de etiquetado de persona2 para un evaluador: toma la clave (submuestra estratificada reproducible si --fraccion < 1), carga acción y narración de cada turno desde Postgres y baraja el orden con semilla por evaluador."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaluador", default="E1")
    ap.add_argument("--fraccion", type=float, default=1.0)
    ap.add_argument("--semilla", type=int, default=20260921)
    args = ap.parse_args()

    clave = list(csv.DictReader((RAIZ / "datos" / "validacion" / "confirmacion_persona2_clave.csv").open(encoding="utf-8-sig")))
    if args.fraccion < 1.0:                      # submuestra estratificada, reproducible
        rnd = random.Random(f"{args.semilla}|sub")
        por_estrato = defaultdict(list)
        for r in clave:
            por_estrato[r["estrato"]].append(r)
        clave = []
        for est in sorted(por_estrato):
            filas = sorted(por_estrato[est], key=lambda r: r["id_muestra"])
            rnd.shuffle(filas)
            clave += filas[:max(1, round(len(filas) * args.fraccion))]
    items = []
    with psycopg.connect(db.DSN, row_factory=dict_row) as conn:
        for r in clave:
            t = conn.execute("SELECT player_buffer, dm_output FROM turn_log WHERE campaign_id=%s AND turn_id=%s",
                             (r["campaign_id"], int(r["turn_id"]))).fetchone()
            accion = "\n".join((x.get("text", "") if isinstance(x, dict) else str(x)) for x in (t["player_buffer"] or []))
            items.append({"id": r["id_muestra"], "accion": accion.strip(), "dm": prosa(t["dm_output"], r["brazo"])})
    random.Random(f"{args.semilla}|{args.evaluador}|orden").shuffle(items)

    plantilla = (RAIZ / "experimento" / "scripts" / "etiquetado_formulario.html").read_text(encoding="utf-8")
    datos = json.dumps({"evaluador": args.evaluador, "items": items}, ensure_ascii=False).replace("</", "<\\/")
    salida = RAIZ / "datos" / "validacion" / f"etiquetado_persona2_{args.evaluador}.html"
    salida.write_text(plantilla.replace("__DATOS__", datos), encoding="utf-8")
    print(f"{len(items)} turnos -> {salida}")


if __name__ == "__main__":
    main()
