import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import consolidar_validacion as C
A = Path(__file__).resolve().parent.parent
R = json.loads((A / "resultados_validacion_v2.json").read_text(encoding="utf-8"))
for t in ("persona2", "pnj", "jericho"):
    print(t, "por_estrato (ref Sí / n):", R[t]["principal"]["por_estrato"])
clave = {r["id"]: r for r in C.leer(A / "clave.csv") + C.leer(A / "clave_cd.csv")}
resp = {e: {r["id"]: int(r["respuesta"] == "Sí") for r in C.leer(A / "respuestas" / f)} for e, f in C.ARCHIVOS.items()}
v3 = {}
for r in clave.values():
    if r["tipo"] == "persona2":
        k = (r["par"], r["brazo"])
        if k not in v3:
            v3[k] = {int(x["turn_id"]): x for x in C.leer(A.parent.parent / "datos" / "datos_v2" / "persona2_v3b" / f"par{r['par']}_{r['brazo']}.csv")}
        v2 = {int(x["turn_id"]): x for x in C.leer(A.parent.parent / "datos" / "datos_v2" / "persona2" / f"par{r['par']}_{r['brazo']}.csv")}
pob = json.loads((A / "poblaciones.json").read_text(encoding="utf-8"))
for t, ret in (("persona2", R["retenidos"]["persona2"]), ("pnj", R["retenidos"]["pnj"]), ("jericho", R["retenidos"]["jericho"])):
    cnt = Counter()
    for i, c in clave.items():
        if c["tipo"] != t:
            continue
        v = [resp[e][i] for e in ret]
        ref = int(2 * sum(v) > len(v))
        det = int(c["detector"])
        cnt[(c["brazo"], c["estrato"], det, ref)] += 1
        if t == "persona2":
            d3 = int(v3[(c["par"], c["brazo"])][int(c["turn_id"])]["primaria"])
            cnt[("v3b", c["brazo"], d3, ref)] += 1
    print(t)
    for k in sorted(cnt):
        print("  ", k, cnt[k])
