"""
Exporta la transcripción de una campaña a Markdown limpio, leyendo
directo de Postgres (turn_log) -- no del log de consola, que puede llegar
mojibake por la codificación con la que PowerShell capture la salida
(ver "QM - Respaldo bibliografico...", punto 21). Los datos en la base
están en UTF-8 correcto porque se escriben vía psycopg, nunca pasaron
por la consola de Windows.

Uso: python exportar_transcripcion_md.py <campaign_id> [archivo_salida.md]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db as bd
import psycopg
from psycopg.rows import dict_row


def main():
    """Exporta a Markdown la transcripción de una campaña: el turno 0 como corpus de lore y luego cada turno con la acción del jugador y la narración."""
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    campaign_id = sys.argv[1]
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f"transcripcion_{campaign_id[:8]}.md")

    camp = bd.Campaña(campaign_id)
    cab = camp.cabecera()

    with psycopg.connect(bd.DSN, row_factory=dict_row) as c:
        filas = c.execute(
            "SELECT turn_id, player_buffer, dm_output, scene_tone "
            "FROM turn_log WHERE campaign_id = %s ORDER BY turn_id",
            (campaign_id,)).fetchall()

    out = []
    out.append(f"# {cab['title']}\n")
    out.append(f"Arquitectura: `{cab['architecture']}` · Turnos: {len(filas) - 1} "
               f"(más el turno 0, corpus de lore)\n")

    for f in filas:
        if f["turn_id"] == 0:
            out.append("## Turno 0 — Corpus de lore (contexto inicial)\n")
            out.append(f["dm_output"] or "")
            out.append("\n---\n")
            continue

        out.append(f"## Turno {f['turn_id']}\n")
        for entrada in (f["player_buffer"] or []):
            texto = entrada.get("text", "")
            out.append(f"**Jugador:** {texto}\n")
        if f["dm_output"]:
            out.append(f"\n**DM:**\n\n{f['dm_output']}\n")
        out.append("\n---\n")

    salida.write_text("\n".join(out), encoding="utf-8")
    print(f"Escrito: {salida} ({len(filas)} turnos)")


if __name__ == "__main__":
    main()
