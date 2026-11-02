import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import consolidar_validacion as C
A = Path(__file__).parent
R = json.loads((A / "resultados_validacion_v2.json").read_text(encoding="utf-8"))
clave = {r["id"]: r for r in C.leer(A / "clave.csv")}
resp = {e: {r["id"]: int(r["respuesta"] == "Sí") for r in C.leer(A / "respuestas" / f)} for e, f in C.ARCHIVOS.items()}
ret = R["retenidos"]["persona2"]
out = []
for i, c in clave.items():
    if c["tipo"] == "persona2" and c["estrato"] == "no":
        v = [resp[e][i] for e in ret]
        if sum(v) >= 2:
            out.append({"id": i, "brazo": c["brazo"], "votos": sum(v)})
(A / "_fn_persona2.json").write_text(json.dumps(out), encoding="utf-8")
print(len(out))
