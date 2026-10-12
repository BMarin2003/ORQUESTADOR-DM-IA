#!/usr/bin/env python3
"""
procedencia_persona2.py -- registra QUÉ turnos se usaron para DESARROLLAR el detector persona2
(SOLO SELECT; escribe únicamente validacion/persona2_desarrollo_turnos.csv).

Regla de procedencia: cualquier turno que haya servido para construir léxicos, ajustar reglas o
depurar queda en ese archivo; la auditoría de confirmación (confirmacion_persona2.py) usa SOLO turnos
que NO están en él. El detector queda CONGELADO tras la iteración «regla de declarada v2».

Usos registrados (columna «uso»):
  exploracion_lexico_semilla777   810 turnos de los 9 pares fuera de la muestra de evaluación
                                  (45 por campaña y brazo) que se leyeron para redactar los léxicos
  evaluacion_semilla20260920      los 600 turnos de evaluación (25 por par y brazo, 12 pares)
  reserva_depuracion              los 4 800 turnos de reserva (200 por par y brazo) analizados para
                                  la muestra de auditoría de desarrollo y la depuración de reglas
  sondeo_manual                   3 turnos (pares 07, ambos brazos: 100, 101, 500) leídos al inicio
Los turnos que cumplen varios usos aparecen una vez con los usos unidos por «+».
Se reproducen exactamente las semillas y el código de muestreo con los que se usaron (evaluar_persona2.muestrear).

Uso: PYTHONUTF8=1 py scripts/instrumentos/procedencia_persona2.py
"""
import csv
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import evaluar_persona2 as E  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

SALIDA = E.RAIZ / "validacion" / "persona2_desarrollo_turnos.csv"
SEMILLA_EVAL = 20260920
SEMILLA_EXPLORACION = 777


def main():
    """Reconstruye con las semillas originales los turnos usados para desarrollar el detector (exploración, evaluación, reserva, sondeo) y los guarda con su uso; la confirmación los excluye."""
    nombres = E.cargar_nombres()
    pares = E.cargar_pares()
    rnd = random.Random(SEMILLA_EVAL)
    en_eval = {p["par"] for p in rnd.sample(pares, E.N_PARES)}
    resto = [p for p in pares if p["par"] not in en_eval]
    filas = {}          # (campaign_id, turn_id) -> [brazo, par, set(usos)]

    def anota(cid, t, brazo, par, uso):
        """Registra un uso para un turno; un turno con varios usos acumula todos."""
        filas.setdefault((cid, int(t)), [brazo, par, set()])[2].add(uso)

    with psycopg.connect(E.db.DSN, row_factory=dict_row) as conn:          # SOLO SELECT
        rnd2 = random.Random(SEMILLA_EXPLORACION)
        for p in resto:
            for brazo, cid in (("G1", p["campaign_g1"]), ("G2", p["campaign_g2"])):
                tids = rnd2.sample(range(1, 1401), 45)
                existentes = conn.execute(
                    "SELECT turn_id FROM turn_log WHERE campaign_id=%s AND turn_id = ANY(%s)", (cid, tids)).fetchall()
                for f in existentes:
                    anota(cid, f["turn_id"], brazo, p["par"], "exploracion_lexico_semilla777")
        ev, rs, _ = E.muestrear(conn, SEMILLA_EVAL, E.TURNOS_POR_PAR, E.RESERVA_POR_PAR, nombres)
    for r in ev:
        anota(r["campaign_id"], r["turn_id"], r["brazo"], r["par"], "evaluacion_semilla20260920")
    for r in rs:
        anota(r["campaign_id"], r["turn_id"], r["brazo"], r["par"], "reserva_depuracion")
    p07 = next(p for p in pares if p["par"] == "07")
    for brazo, cid in (("G1", p07["campaign_g1"]), ("G2", p07["campaign_g2"])):
        for t in (100, 101, 500):
            anota(cid, t, brazo, "07", "sondeo_manual")

    SALIDA.parent.mkdir(exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["campaign_id", "turn_id", "brazo", "par", "uso"])
        for (cid, t), (brazo, par, usos) in sorted(filas.items()):
            w.writerow([cid, t, brazo, par, "+".join(sorted(usos))])
    from collections import Counter
    c = Counter(u for _, _, usos in filas.values() for u in usos)
    print(f"{len(filas)} turnos distintos escritos en {SALIDA}")
    print("  por uso:", dict(c))


if __name__ == "__main__":
    main()
