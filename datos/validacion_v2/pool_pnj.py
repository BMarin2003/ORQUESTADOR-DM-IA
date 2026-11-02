"""
Validación humana v2 -- universo de turnos ELEGIBLES para el ítem «PNJ inactivo» (solo SELECT, sin LLM).

Para cada una de las 54 campañas (pares.todos()), turnos 2..1400, escribe una fila por turno elegible
(>= 1 PNJ visible con estado != 'alive' al inicio del turno) con:
  crudo      = cl2_pnj_inactivo_actua_v2 (datos_v2/booleanos, texto normalizado)
  refinado   = 1 si RV.pnj_inactivo_refinado (CONGELADO, sin tocar) lo clasifica como «actuando»
  inactivos  = PNJ inactivos visibles: nombre|estado|desde_turno (separados por ';')
  mencionados= los inactivos cuyo nombre aparece literal en el texto normalizado
  pnj_detector = nombres que el refinado devolvió como sujeto (pueden ser PNJ vivos: así es el detector)
Salida: validacion_v2/pool_pnj.csv
    PYTHONUTF8=1 py validacion_v2/pool_pnj.py
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
for _p in (RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    sys.path.insert(0, str(_p))

import datos                                   # noqa: E402
import pares as _pares                         # noqa: E402
import db as bd                                # noqa: E402
import reporte_validacion as RV                # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

HASTA = 1400
BOOL = RAIZ / "datos_v2" / "booleanos"
SALIDA = Path(__file__).resolve().parent / "pool_pnj.csv"


def flags_v2(par, brazo):
    with open(BOOL / f"par{par}_{brazo}.csv", newline="", encoding="utf-8") as fh:
        return {int(r["turn_id"]): r["cl2_pnj_inactivo_actua_v2"] == "1" for r in csv.DictReader(fh)}


def desde(dc, nombre, t):
    """Turno del último cambio de estado anterior a t."""
    ult = None
    for turno, _ in dc._estado.get(nombre, ["alive", []])[1]:
        if turno < t:
            ult = turno
    return ult


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cols = ["par", "brazo", "campaign_id", "turn_id", "crudo", "refinado", "inactivos", "mencionados", "pnj_detector"]
    n_tot = 0
    with open(SALIDA, "w", newline="", encoding="utf-8") as out, datos.abrir_conexion() as conn:
        w = csv.DictWriter(out, fieldnames=cols)
        w.writeheader()
        for p in _pares.todos():
            for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
                cid = p[k]
                dc = datos.DatosCampana(conn, cid, brazo, p["par"])
                camp = bd.Campaña(cid)
                turnos = [t for t in camp.turnos_narracion() if t["turn_id"] <= HASTA]
                tpi = {t["turn_id"]: normalizar_turno(t["dm_output"], brazo) for t in turnos}
                ents = camp.entidades()
                f2 = flags_v2(p["par"], brazo)
                filas_val = [{"turn_id": t, "cl2_pnj_inactivo_actua": f2.get(t, False)} for t in tpi]
                ref = RV.pnj_inactivo_refinado(filas_val, tpi, ents)
                if ref is None:
                    sys.exit("ABORTA: spaCy no disponible; el refinado no puede correr")
                act = {}
                for e in ref["actuando"]:
                    act.setdefault(e["turno"], set()).add(e["pnj"])
                n = 0
                for t in sorted(tpi):
                    if t < 2:
                        continue
                    inact = [(e["nombre"], dc.estado_en(e["nombre"], t)) for e in dc._entidades_en(t) if e["tipo"] == "npc"]
                    inact = [(nm, st) for nm, st in inact if st != "alive"]
                    if not inact:
                        continue
                    texto = tpi[t] or ""
                    w.writerow({
                        "par": p["par"], "brazo": brazo, "campaign_id": cid, "turn_id": t,
                        "crudo": int(f2.get(t, False)), "refinado": int(t in act),
                        "inactivos": ";".join(f"{nm}|{st}|{desde(dc, nm, t)}" for nm, st in inact),
                        "mencionados": ";".join(nm for nm, _ in inact if nm in texto),
                        "pnj_detector": ";".join(sorted(act.get(t, ()))),
                    })
                    n += 1
                n_tot += n
                print(f"par{p['par']} {brazo}: {n} elegibles, {len(act)} refinado-actuando", flush=True)
    print(f"total elegibles: {n_tot} -> {SALIDA}")


if __name__ == "__main__":
    main()
