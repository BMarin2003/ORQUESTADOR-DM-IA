import sys, json
from pathlib import Path
R = Path(r"C:\BMARIN2003\DEV\proyecto\experimento\scripts")
for p in ("reporte_v2", "instrumentos", "sensibilidad", ""):
    sys.path.insert(0, str(R / p))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import datos, pares
p = pares.todos()[1]
with datos.abrir_conexion() as conn:
    dc = datos.DatosCampana(conn, p["campaign_g2"], "G2", p["par"])
    print("ATRIBUTOS DatosCampana:", [a for a in vars(dc) if not a.startswith("__")])
    n = 0
    for t in range(2, 400):
        f = dc.turnos.get(t)
        if not f:
            continue
        buf = f.get("player_buffer") or []
        txt = json.dumps(buf, ensure_ascii=False)
        if "{" in txt and n < 3:
            n += 1
            print("\n=== turno", t, "claves:", list(f.keys()))
            for k, v in f.items():
                s = json.dumps(v, ensure_ascii=False, default=str)
                print(f"  {k}: {s[:700]}")
