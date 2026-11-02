#!/usr/bin/env python3
"""
Prueba de Campaña.sincronizar_dia() (reloj del mundo determinista) contra Postgres.
NUNCA correr contra una campaña real: escribe game_day, turnos y reinicia el reloj.

Uso: crear una campaña desechable (crear_campana_real.py + sembrar_mundo_real.py con
world_par07.json, que trae 1 reloj: progress 3, umbral 10, 0.9/día = 8 días) y
     python experimento/scripts/test_reloj_determinista.py --campaign-id <UUID desechable>
Comprueba: el día sale de turno // TURNOS_POR_DIA, el reloj dispara exactamente en el
turno esperado, el evento llega a eventos_reloj_turno() (lo que lee el turno siguiente),
llamar dos veces es idempotente y tras una "caída" el siguiente turno recupera los días
perdidos (y dispara si toca).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
K = db.TURNOS_POR_DIA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-id", required=True)
    camp = db.Campaña(ap.parse_args().campaign_id)

    def sql(q, *p):
        with camp._conn() as c:
            camp._tx(c)
            return c.execute(q, p).fetchall()

    if sql("SELECT game_day FROM campaigns WHERE id=%s", camp.campaign_id)[0]["game_day"] != 0 \
            or sql("SELECT count(*) n FROM turn_log WHERE campaign_id=%s", camp.campaign_id)[0]["n"] > 1:
        sys.exit("La campaña no está virgen (game_day 0, solo turno 0): usa una desechable recién sembrada.")
    reloj = sql("SELECT progress, threshold, rate_per_game_day r FROM faction_clocks WHERE campaign_id=%s",
                camp.campaign_id)[0]
    dias_necesarios = -(-(float(reloj["threshold"]) - float(reloj["progress"])) // float(reloj["r"]))
    turno_esperado = int(dias_necesarios) * K

    # 1) turnos 1..(esperado+40) con tick cada turno
    disparos = []
    for t in range(1, turno_esperado + 41):
        camp.registrar_turno(t, [{"pc": "PJ23", "text": "x"}], "narración de prueba", False)
        disparos += [(t, ev["agenda"]) for ev in camp.sincronizar_dia(t)]
    assert [t for t, _ in disparos] == [turno_esperado], f"disparo en {disparos}, esperado {turno_esperado}"
    dia = sql("SELECT game_day FROM campaigns WHERE id=%s", camp.campaign_id)[0]["game_day"]
    assert dia == (turno_esperado + 40) // K, dia
    n_clock = sql("SELECT count(*) n FROM state_deltas WHERE campaign_id=%s AND source='clock'",
                  camp.campaign_id)[0]["n"]
    assert n_clock == dia, (n_clock, dia)
    ev = camp.eventos_reloj_turno(turno_esperado)
    assert len(ev) == 1 and ev[0]["on_fire_event"].get("headline"), ev
    print(f"OK 1: día {dia} · {n_clock} deltas 'clock' · reloj disparó en turno {turno_esperado} "
          f"(esperado {turno_esperado}) · evento visible en el turno siguiente: «{ev[0]['on_fire_event']['headline'][:50]}…»")

    # 2) idempotencia
    ultimo = turno_esperado + 40
    assert camp.sincronizar_dia(ultimo) == [] and camp.sincronizar_dia(ultimo) == []
    assert sql("SELECT count(*) n FROM state_deltas WHERE campaign_id=%s AND source='clock'",
               camp.campaign_id)[0]["n"] == n_clock
    print("OK 2: llamar de nuevo en el mismo turno no escribe nada")

    # 3) caída: se pierden turnos sin tick; el siguiente recupera todos los días y dispara
    sql_reset = ("UPDATE faction_clocks SET fired_at_turn=NULL, progress=3 WHERE campaign_id=%s")
    with camp._conn() as c:
        camp._tx(c)
        c.execute(sql_reset, (camp.campaign_id,))
        c.commit()
    salto = ultimo + 30 * K
    camp.registrar_turno(salto, [{"pc": "PJ23", "text": "x"}], "narración de prueba", False)
    disp = camp.sincronizar_dia(salto)
    dia2 = sql("SELECT game_day FROM campaigns WHERE id=%s", camp.campaign_id)[0]["game_day"]
    assert dia2 == salto // K and len(disp) == 1, (dia2, disp)
    print(f"OK 3: tras saltar {30} días sin ticks, un solo tick recupera hasta el día {dia2} y dispara el reloj")
    print("TODO OK")


if __name__ == "__main__":
    main()
