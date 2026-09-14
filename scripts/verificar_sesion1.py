import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db as bd
import psycopg

campaign_id = sys.argv[1] if len(sys.argv) > 1 else "7b7a3cd5-91e3-467f-a817-9abadaf31d78"

camp = bd.Campaña(campaign_id)
cab = camp.cabecera()
print("cabecera:", cab)

with psycopg.connect(bd.DSN) as c:
    r = c.execute(
        "SELECT count(*) AS n, min(turn_id) AS min_t, max(turn_id) AS max_t "
        "FROM turn_log WHERE campaign_id = %s", (campaign_id,)).fetchone()
    print("turn_log:", r)
    faltantes = c.execute(
        "SELECT expected.t FROM generate_series(0, 250) AS expected(t) "
        "LEFT JOIN turn_log tl ON tl.campaign_id = %s AND tl.turn_id = expected.t "
        "WHERE tl.id IS NULL ORDER BY 1", (campaign_id,)).fetchall()
    print(f"turnos faltantes (0-250): {[f[0] for f in faltantes] if faltantes else 'ninguno -- completa'}")
