"""Exploración SOLO sobre la partición de desarrollo de persona2: para cada hallazgo del detector congelado
reconstruye el contexto D&D del turno (habilidad declarada, tirada determinista, resultado) para diseñar la
regla v4. No toca la partición de prueba."""
import csv, json, sys, collections
from pathlib import Path
S = Path(r"C:\BMARIN2003\DEV\proyecto\experimento\scripts")
for p in ("reporte_v2", "instrumentos", "sensibilidad", ""):
    sys.path.insert(0, str(S / p))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import recalcular_persona2 as R
A = Path(r"C:\BMARIN2003\DEV\proyecto\datos\validacion_v2")
part = {r["id"]: r["conjunto"] for r in csv.DictReader(open(A / "particion_persona2.csv", encoding="utf-8-sig"))}
clave = [r for r in csv.DictReader(open(A / "clave.csv", encoding="utf-8-sig")) if r["tipo"] == "persona2"]
dev = [c for c in clave if part.get(c["id"]) == "desarrollo"]
pares = {p["par"]: p for p in R._pares.todos()}
nombres = R.cargar_nombres()
SAB = {"percepcion", "investigacion", "perspicacia", "arcanos", "historia", "naturaleza", "religion", "medicina", "supervivencia", "inteligencia", "sabiduria"}
SOC = {"persuasion", "engano", "intimidacion", "interpretacion", "carisma"}
FIS = {"atletismo", "acrobacias", "sigilo", "juego de manos", "fuerza", "destreza", "constitucion"}
def tipo(et):
    e = R.P._plano(et) if hasattr(R.P, "_plano") else et.lower()
    e = e.strip()
    if e in SAB: return "cognitiva"
    if e in SOC: return "social"
    if e in FIS: return "fisica"
    if "ataque" in e or "iniciativa" in e or "conjuro" in e or "salvacion" in e: return "combate/salv"
    return "otra:" + e
out, cnt = [], collections.Counter()
with R.datos.abrir_conexion() as conn:
    cache = {}
    for c in dev:
        k = (c["par"], c["brazo"])
        if k not in cache:
            p = pares[c["par"]]
            cache[k] = R.datos.DatosCampana(conn, p["campaign_g1" if c["brazo"] == "G1" else "campaign_g2"], c["brazo"], c["par"])
        dc, t = cache[k], int(c["turn_id"])
        f = dc.turnos.get(t)
        buf = f["player_buffer"] or []
        pj = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
        texto, accion = R.normalizar_turno(f["dm_output"], c["brazo"]), R.jugador(buf)
        tir = dc.tiradas(t)
        tirs = [{"hab": x["etiqueta"], "tipo": tipo(x["etiqueta"]), "dado": x["dado"], "total": x["total"],
                 "exito15": x["total"] >= 15} for x in tir]
        hs = R.P.detectar_usurpacion(texto, accion, None, nombres.get(pj))
        hs = [h for h in hs if h["categoria"] in R.PRIM]
        for h in hs:
            tt = tirs[0]["tipo"] if tirs else "sin_tirada"
            cnt[(h["categoria"], "decl" if h["declarada"] else "no_decl", tt)] += 1
        out.append({"id": c["id"], "par": c["par"], "brazo": c["brazo"], "turn": t, "accion": accion, "tiradas": tirs,
                    "hallazgos": [{"cat": h["categoria"], "verbo": h["verbo_lema"], "decl": h["declarada"],
                                   "evid": h["evidencia"]} for h in hs]})
(A / "_trabajo" / "_dev_contexto_dnd.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("items dev:", len(out), " con hallazgo:", sum(1 for o in out if o["hallazgos"]),
      " con tirada:", sum(1 for o in out if o["tiradas"]))
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print(v, k)
