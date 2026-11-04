"""Volcado exploratorio de hallazgos primarios de persona2 en todo el corpus, EXCLUYENDO los turnos de la partición
de prueba. Sirve para cuantificar clases (informativa / actitudinal / emoción de resultado / emoción hacia agentes)
antes de cerrar la regla v4."""
import csv, json, sys, time
from pathlib import Path
S = Path(r"C:\BMARIN2003\DEV\proyecto\experimento\scripts\reporte_v2")
sys.path.insert(0, str(S))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import recalcular_persona2_v4 as V
R = V.R
VAL = V.VAL
part = {r["id"]: r["conjunto"] for r in csv.DictReader(open(VAL / "particion_persona2.csv", encoding="utf-8-sig"))}
prueba = {(r["par"], r["brazo"], int(r["turn_id"])) for r in csv.DictReader(open(VAL / "clave.csv", encoding="utf-8-sig"))
          if r["tipo"] == "persona2" and part.get(r["id"]) == "prueba"}
nombres, t0 = R.cargar_nombres(), time.time()
dest = VAL / "_trabajo" / "_volcado_v4.jsonl"
n = 0
with R.datos.abrir_conexion() as conn, open(dest, "w", encoding="utf-8") as out:
    for p in R._pares.todos():
        for brazo in ("G1", "G2"):
            dc = R.datos.DatosCampana(conn, p["campaign_g1" if brazo == "G1" else "campaign_g2"], brazo, p["par"])
            for t in range(1, 1401):
                if (p["par"], brazo, t) in prueba:
                    continue
                r = V.evaluar(dc, t, nombres)
                if r is None:
                    continue
                hs, tir, accion = r
                for h in hs:
                    if h["motivo"] in ("R1",):
                        continue
                    f = dc.turnos[t]
                    dm = R.normalizar_turno(f["dm_output"], brazo)
                    out.write(json.dumps({"par": p["par"], "brazo": brazo, "t": t, "cat": h["categoria"], "lema": h["verbo_lema"],
                                          "motivo": h["motivo"], "d20": [x["dado"] for x in tir], "hab": [x["etiqueta"] for x in tir],
                                          "ctx": dm[max(0, h["inicio"] - 90):h["fin"] + 120].replace("\n", " "),
                                          "accion": (accion or "")[:300]}, ensure_ascii=False) + "\n")
                    n += 1
            print(f"par{p['par']} {brazo} listo ({n} hallazgos, {time.time() - t0:.0f} s)", flush=True)
print("FIN", n)
