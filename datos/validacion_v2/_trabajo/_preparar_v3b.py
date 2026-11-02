"""1) Copia 'secundaria' y 'muerte' de persona2/ (v2b, sin cambios) a persona2_v3b/ para que el pipeline lea archivos completos.
2) Hace configurable la carpeta de persona2 en consolidar.py y medidas_cierre.py (variable de entorno P2_DIR, por defecto 'persona2')."""
import csv
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V2, V3 = RAIZ / "datos" / "datos_v2" / "persona2", RAIZ / "datos" / "datos_v2" / "persona2_v3b"
for f in sorted(V3.glob("par*_G?.csv")):
    base = {r["turn_id"]: r for r in csv.DictReader(open(V2 / f.name, newline="", encoding="utf-8"))}
    filas = list(csv.DictReader(open(f, newline="", encoding="utf-8")))
    for r in filas:
        r["secundaria"], r["muerte"] = base[r["turn_id"]]["secundaria"], base[r["turn_id"]]["muerte"]
        assert r["en_desarrollo"] == base[r["turn_id"]]["en_desarrollo"]
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
print("v3b completados:", len(list(V3.glob("par*_G?.csv"))))

for nombre, viejo, nuevo in [
    ("consolidar.py", 'ruta = D2 / "persona2" / rc.nombre_csv(par, brazo)',
     'ruta = D2 / os.environ.get("P2_DIR", "persona2") / rc.nombre_csv(par, brazo)'),
    ("medidas_cierre.py", 'else "persona2")) / rc.nombre_csv(par, brazo)',
     'else os.environ.get("P2_DIR", "persona2"))) / rc.nombre_csv(par, brazo)'),
]:
    p = RAIZ / "experimento" / "scripts" / "reporte_v2" / nombre
    s = p.read_text(encoding="utf-8")
    if nuevo not in s:
        assert viejo in s, nombre
        s = s.replace(viejo, nuevo)
        if "\nimport os\n" not in s:
            s = s.replace("\nimport ", "\nimport os\nimport ", 1)
        p.write_text(s, encoding="utf-8")
    print(nombre, "ok")
