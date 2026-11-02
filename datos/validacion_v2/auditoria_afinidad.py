"""Auditoría del registro de afinidad (referencia de la pregunta C): 30 cambios de afinidad tomados al azar de la muestra C.
Pregunta a los autores: ¿lo narrado justifica el cambio registrado? Se muestran la banda previa, la nueva y los turnos N-1 y N.
Salidas: auditoria_afinidad.html (formulario Sí/No con exportación) y auditoria_afinidad_clave.csv."""
import csv
import json
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ampliar_cd as A                          # noqa: E402

rng = random.Random(20261103)
with open(AQUI / "clave_cd.csv", newline="", encoding="utf-8") as fh:
    afin = [r for r in csv.DictReader(fh) if r.get("campo") == "npc.affinity"]
afin.sort(key=lambda r: r["id"])
sel = rng.sample(afin, 30)
BANDA = A.BANDA | {"neutral": "neutral"}
items, clave = [], []
with A.G.datos.abrir_conexion() as conn:
    for k, r in enumerate(sel, 1):
        cid, t = r["campaign_id"], int(r["turn_id"])
        d = conn.execute("""SELECT sd.old_value, sd.new_value FROM state_deltas sd JOIN npcs n ON n.id = sd.entity_id
                            WHERE sd.campaign_id=%s AND sd.turn_id=%s AND sd.entity_type='npc' AND sd.field_name='affinity'
                            AND n.name=%s ORDER BY sd.id LIMIT 1""", (cid, t, r["entidad"])).fetchone()
        prev = BANDA[A.RV._banda_afinidad(d["old_value"])] if d and d["old_value"] is not None else "sin registro previo"
        nueva = BANDA[A.RV._banda_afinidad(d["new_value"] if d else r["valor"])]
        tx = {x["turn_id"]: x["dm_output"] for x in conn.execute(
            "SELECT turn_id, dm_output FROM turn_log WHERE campaign_id=%s AND turn_id IN (%s, %s)", (cid, t - 1, t)).fetchall()}
        iid = f"AF{k:02d}"
        items.append({"id": iid, "hecho": f"En el turno {t}, la disposición de {r['entidad']} hacia el personaje jugador pasó de «{prev}» a «{nueva}».",
                      "previo": A.normalizar_turno(tx.get(t - 1, ""), r["brazo"]), "texto": A.normalizar_turno(tx.get(t, ""), r["brazo"]), "turno": t})
        clave.append({"id": iid, "id_muestra_c": r["id"], "par": r["par"], "brazo": r["brazo"], "campaign_id": cid, "turn_id": t,
                      "entidad": r["entidad"], "previa": prev, "nueva": nueva, "detector_jericho": r["detector"]})
with open(AQUI / "auditoria_afinidad_clave.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(clave[0])); w.writeheader(); w.writerows(clave)
html = (AQUI / "auditoria_plantilla.html").read_text(encoding="utf-8")
(AQUI / "auditoria_afinidad.html").write_text(html.replace("__ITEMS__", json.dumps(items, ensure_ascii=False).replace("</", "<\\/")), encoding="utf-8")
print(len(items), "ítems")
