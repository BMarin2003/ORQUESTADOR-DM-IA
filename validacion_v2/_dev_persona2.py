import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import consolidar_validacion as C
A = Path(__file__).parent
R = json.loads((A / "resultados_validacion_v2.json").read_text(encoding="utf-8"))
ret = R["retenidos"]["persona2"]
part = {r["id"]: r["conjunto"] for r in C.leer(A / "particion_persona2.csv")}
clave = {r["id"]: r for r in C.leer(A / "clave.csv") if r["tipo"] == "persona2"}
resp = {e: {r["id"]: int(r["respuesta"] == "Sí") for r in C.leer(A / "respuestas" / f)} for e, f in C.ARCHIVOS.items()}
cache = {}
out = []
for i, c in clave.items():
    if part[i] != "desarrollo":
        continue
    k = (c["par"], c["brazo"])
    if k not in cache:
        cache[k] = ({int(x["turn_id"]): x for x in C.leer(A.parent / "datos_v2" / "persona2" / f"par{k[0]}_{k[1]}.csv")},
                    {int(x["turn_id"]): x for x in C.leer(A.parent / "datos_v2" / "persona2_v3b" / f"par{k[0]}_{k[1]}.csv")})
    t = int(c["turn_id"])
    v2, v3 = cache[k][0][t], cache[k][1][t]
    out.append({"id": i, "brazo": c["brazo"], "estrato": c["estrato"], "votos": [resp[e][i] for e in ret],
                "v2b": int(v2["primaria"]), "v3b": int(v3["primaria"]),
                "cat_v2b": {x: v2[x] for x in ("VOLICION", "COGNICION", "EMOCION", "HABLA")}})
(A / "_dev_persona2.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(len(out))
