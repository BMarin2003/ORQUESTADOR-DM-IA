"""
A4a (parte 3): los instrumentos a NIVEL DE CAMPAÑA de orquestador/reporte_validacion.py (bucles, relojes reconocidos, Papalampidi C y V,
Jericho recall, ECR, grafo por lema, PNJ inactivo refinado) recalculados sobre texto NORMALIZADO para las 42 campañas, junto al valor v1
(texto crudo, lo que ve el reporte original). Se llama a las MISMAS funciones que reporte_validacion.main(); solo cambia el dm_output.

Salida: datos_v2/campana/parNN_G?.json con {"v1": {...}, "v2": {...}}. Solo SELECT; nada de LLM. Reanuda: salta lo ya calculado.
    PYTHONUTF8=1 py scripts/reporte_v2/recalcular_campana.py [--pares 07,08] [--forzar]
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                                   # noqa: E402
import pares as _pares                         # noqa: E402
import db as bd                                # noqa: E402
import reporte_validacion as RV                # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

DESTINO = RAIZ / "datos_v2" / "campana"
BOOL = RAIZ / "datos_v2" / "booleanos"


def resumen(turnos, ents, relojes, deltas, filas_val):
    """Instrumentos a nivel de campaña de `reporte_validacion` (bucles, relojes, Papalampidi C/L/V, Jericho, ECR, grafo por lema, PNJ inactivo refinado).

    Llama a las mismas funciones que `reporte_validacion.main()`; solo cambia el `dm_output` de entrada.
    """
    ubic = [e for e in ents if e["tipo"] == "location"]
    tpi = {f["turn_id"]: f["dm_output"] for f in turnos}
    b = RV.detector_bucles(turnos, ubic)
    rel = RV.relojes_no_reconocidos(relojes, tpi)
    C, L, _ = RV.coherencia_entidad_C(turnos, ents)
    V, _ = RV.consistencia_atributos_V(turnos, ents)
    j = RV.jericho_qa_recall(deltas, tpi)
    e = RV.entity_coreference_rate(turnos, ents)
    g = RV.reporte_grafo_lema(turnos, ents)
    p = RV.pnj_inactivo_refinado(filas_val, tpi, ents)
    return {
        "bucles_ciclos": len(b["ciclos"]), "bucles_visitas": b["num_visitas"], "bucles_ubicaciones": b["num_ubicaciones_distintas"],
        "relojes_disparados": len(rel), "relojes_reconocidos": sum(1 for r in rel if r["reconocido"]),
        "papalampidi_C": C, "papalampidi_L": L, "papalampidi_V": V,
        "jericho_recall": j["recall_global"], "jericho_n": j["n_total"],
        "ecr": e["promedio"], "ecr_n": e["n_turnos_con_entidad"],
        "grafo_lema": g["promedio"] if g else None,
        "pnj_refinado_actuando": len(p["actuando"]) if p else None,
        "pnj_refinado_solo_referenciado": len(p["solo_referenciado"]) if p else None,
    }


def flags_v2(par, brazo):
    """{turn_id: bool} de `cl2_pnj_inactivo_actua_v2` ya recalculado en `datos_v2/booleanos/`."""
    ruta = BOOL / f"par{par}_{brazo}.csv"
    with open(ruta, newline="", encoding="utf-8") as fh:
        return {int(r["turn_id"]): r["cl2_pnj_inactivo_actua_v2"] == "1" for r in csv.DictReader(fh)}


def procesar(par, brazo, cid):
    """Resumen v1 (texto crudo) y v2 (texto normalizado) de una campaña, limitado a 1 400 turnos.

    En v2 sustituye `cl2_pnj_inactivo_actua` por el booleano recalculado sobre texto normalizado.
    """
    camp = bd.Campaña(cid)
    with camp._conn() as c:
        camp._tx(c)
        filas_val = c.execute("SELECT * FROM turn_validation WHERE campaign_id=%s ORDER BY turn_id", (cid,)).fetchall()
    HASTA = 1400                                     # diseño: 1 400 turnos (Par02 G2 tiene 1 668)
    filas_val = [f for f in filas_val if f["turn_id"] <= HASTA]
    turnos = [t for t in camp.turnos_narracion() if t["turn_id"] <= HASTA]
    ents = camp.entidades()
    relojes = [r for r in camp.relojes_disparados() if r["fired_at_turn"] <= HASTA]
    deltas = [d for d in camp.deltas_narrables() if d["turn_id"] <= HASTA]
    v1 = resumen(turnos, ents, relojes, deltas, filas_val)
    turnos2 = [dict(t, dm_output=normalizar_turno(t["dm_output"], brazo)) for t in turnos]
    f2 = flags_v2(par, brazo)
    filas2 = [dict(f, cl2_pnj_inactivo_actua=f2.get(f["turn_id"], bool(f["cl2_pnj_inactivo_actua"]))) for f in filas_val]
    v2 = resumen(turnos2, ents, relojes, deltas, filas2)
    return {"v1": v1, "v2": v2, "n_turnos": len(turnos)}


def main():
    """Calcula `procesar` para cada campaña de `pares.todos()` y guarda `datos_v2/campana/parNN_G?.json`; salta las existentes salvo `--forzar`."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", default="")
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    filtro = {p for p in a.pares.split(",") if p}
    pares = [p for p in _pares.todos() if not filtro or p["par"] in filtro]
    DESTINO.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for k, p in enumerate(pares, 1):
        for brazo in ("G1", "G2"):
            ruta = DESTINO / f"par{p['par']}_{brazo}.json"
            if ruta.exists() and not a.forzar:
                print(f"[{k:2}/{len(pares)}] par{p['par']} {brazo}: ya existe", flush=True)
                continue
            t1 = time.time()
            r = procesar(p["par"], brazo, p["campaign_g1" if brazo == "G1" else "campaign_g2"])
            ruta.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"[{k:2}/{len(pares)}] par{p['par']} {brazo}: {time.time() - t1:5.1f}s (total {(time.time() - t0) / 60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
