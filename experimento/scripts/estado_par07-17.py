#!/usr/bin/env python3
"""
Consulta rápida de estado -- las 22 campañas de Par 07-17 (real), leyendo
los campaign_id desde docs/ids_par07-17.json (no hardcodeados a mano).

Muestra current_turn real de cada campaña para saber exactamente cuándo una
tanda terminó (todas en 1400/1400) y, si alguna se cortó antes, cuántos
turnos hay que pasarle al resume (1400 - current_turn) sin pasarse.

Uso: python experimento/scripts/estado_par07-17.py [--arm G2|G1|ambos]
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "motor" / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

OBJETIVO = 1400


def main():
    """Muestra el avance (turno actual frente al objetivo) de las campañas del lote y cuántas faltan, filtrable por brazo."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["G2", "G1", "ambos"], default="ambos")
    ap.add_argument("--ids", default="docs/ids_par07-17.json",
                    help="archivo de ids del lote (Par 18-27: docs/ids_par18-27.json)")
    args = ap.parse_args()

    data = json.loads((RAIZ / args.ids).read_text(encoding="utf-8"))

    campos = []
    if args.arm in ("G2", "ambos"):
        campos.append(("campaign_g2", "G2 (monolítico)"))
    if args.arm in ("G1", "ambos"):
        campos.append(("campaign_g1", "G1 (multiagente)"))

    with psycopg.connect(db.DSN) as c:
        completas, en_curso = 0, []
        for r in data:
            for campo, etiqueta in campos:
                cid = r[campo]
                row = c.execute(
                    "SELECT current_turn FROM campaigns WHERE id=%s", (cid,)).fetchone()
                if row is None:
                    print(f"Par {r['par']} {etiqueta}: NO ENCONTRADA ({cid})")
                    continue
                turno = row[0]
                restantes = OBJETIVO - turno
                etiqueta_par = f"Par {r['par']} {etiqueta} · {r['lugar']}"
                if restantes <= 0:
                    completas += 1
                    print(f"{etiqueta_par}: {turno}/{OBJETIVO} -- LISTA"
                          + (f" (excedente {-restantes}, decidir qué hacer)" if restantes < 0 else ""))
                else:
                    en_curso.append((etiqueta_par, turno, restantes))
                    print(f"{etiqueta_par}: {turno}/{OBJETIVO} "
                          f"-- faltan {restantes} (si se corta, reanudar con --turnos {restantes})")

    total = len(data) * len(campos)
    print(f"\n{completas}/{total} campañas en 1400/1400.")
    if not en_curso:
        print("Tanda completa -- lista para exportar/reportar o lanzar la siguiente tanda.")


if __name__ == "__main__":
    main()
