import sys
from pathlib import Path
R = Path(r"C:\BMARIN2003\DEV\proyecto\experimento\scripts")
for p in ("reporte_v2", "instrumentos", "sensibilidad", ""):
    sys.path.insert(0, str(R / p))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import datos
with datos.abrir_conexion() as conn:
    cols = conn.execute("""select table_name, string_agg(column_name||':'||data_type, ', ' order by ordinal_position) c
                           from information_schema.columns where table_schema='public' group by table_name order by 1""").fetchall()
    for r in cols:
        print(r["table_name"], "->", r["c"][:400])
