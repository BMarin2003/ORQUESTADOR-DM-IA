"""
Exporta la transcripción COMPLETA y LIMPIA de una campaña, en un solo
archivo, leyendo directo de Postgres (turn_log) en vez de concatenar los
.md de log de cada corrida/reanudación.

Por qué desde la base y no desde los logs de la corrida:
  El motor es resumible por diseño -- current_turn vive en Postgres, no en
  el nombre del archivo de log -- así que cuando una campaña se generó en
  varias corridas (crashes, cortes de saldo, reanudaciones), el estado
  real siempre está completo y en orden en `turn_log`, sin importar cuántos
  archivos de log haya en logs/. Pegar los .md a mano arrastra ruido de
  diagnóstico (pasos [1]..[13], costos, reintentos) y corre el riesgo real
  de solapar o saltarse turnos si dos corridas se superponen en rango.
  Leer turn_log da la transcripción real, turno por turno, una sola vez
  cada uno, en el orden correcto -- siempre.

Uso:
  python scripts/exportar_transcripcion.py --campaign-id <uuid> \
      [--hasta-turno N] [--salida ruta.md]

--hasta-turno: corta la transcripción en ese turno (para el caso de una
  campaña que se pasó del objetivo, p. ej. Par 02 G2 en turno 1667 con
  objetivo 1400 -- exportar con --hasta-turno 1400 para que la
  transcripción represente el mismo tramo que su par).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402


def main():
    """Exporta la transcripción de una campaña (hasta --hasta-turno) a un archivo Markdown, leyendo los turnos de Postgres."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-id", required=True)
    ap.add_argument("--hasta-turno", type=int, default=None)
    ap.add_argument("--salida", default=None)
    args = ap.parse_args()

    with psycopg.connect(db.DSN, row_factory=dict_row) as conn:
        camp = conn.execute(
            "SELECT id, title, current_turn, created_at FROM campaigns "
            "WHERE id = %s", (args.campaign_id,)).fetchone()
        if camp is None:
            sys.exit(f"Campaña no encontrada: {args.campaign_id}")

        q = ("SELECT turn_id, player_buffer, dm_output FROM turn_log "
             "WHERE campaign_id = %s")
        params = [args.campaign_id]
        if args.hasta_turno:
            q += " AND turn_id <= %s"
            params.append(args.hasta_turno)
        q += " ORDER BY turn_id"
        turnos = conn.execute(q, params).fetchall()

    if not turnos:
        sys.exit("No hay turnos registrados para esa campaña (¿campaign-id correcto?).")

    limite = args.hasta_turno or camp["current_turn"]
    salida = Path(args.salida) if args.salida else Path(
        f"transcripcion_{camp['title'].replace(' ', '_').replace('·', '-')}"
        f"_1-{limite}.md")

    with salida.open("w", encoding="utf-8") as f:
        f.write(f"# {camp['title']}\n\n")
        f.write(f"Campaña: `{camp['id']}`  \n")
        f.write(f"Creada: {camp['created_at']}  \n")
        f.write(f"Turnos en esta transcripción: {turnos[0]['turn_id']}"
                f"–{turnos[-1]['turn_id']} ({len(turnos)} turnos)  \n")
        if args.hasta_turno and camp["current_turn"] > args.hasta_turno:
            f.write(f"**Nota:** la campaña avanzó hasta el turno "
                    f"{camp['current_turn']}; esta transcripción se cortó "
                    f"en {args.hasta_turno} a propósito (ver `--hasta-turno`, "
                    f"para comparar el mismo tramo que su par).  \n")
        f.write("\n---\n\n")

        for t in turnos:
            f.write(f"## Turno {t['turn_id']}\n\n")
            buffer = t["player_buffer"] or []
            for entrada in buffer:
                texto = entrada.get("text", "") if isinstance(entrada, dict) else str(entrada)
                f.write(f"**Jugador:** {texto}\n\n")
            f.write(f"{t['dm_output'] or ''}\n\n")

    print(f"Transcripción escrita: {salida} ({len(turnos)} turnos, "
          f"{salida.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
