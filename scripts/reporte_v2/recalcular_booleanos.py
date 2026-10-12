"""
A4a (parte 2): recalcula `cr1_veredicto_contradice_narracion` y `cl2_pnj_inactivo_actua` sobre texto NORMALIZADO
para las 42 campañas de Par07-27 y compara G1 vs G2 antes (v1 = lo guardado en turn_validation) y después (v2).

Estos dos detectores necesitan tiradas y estados de PNJ, que `recalcular.py` no reconstruye, así que aquí se usa el
contexto completo del arnés (`DatosCampana.contexto`, validado contra turn_validation). Columnas de cada CSV
(`datos_v2/booleanos/parNN_G?.csv`): turn_id y, por instrumento, `_v1` (guardado), `_crudo` (recalculado sobre texto
crudo: control de fidelidad, debe igualar a v1) y `_v2` (texto normalizado). Solo SELECT; nada de LLM.

    PYTHONUTF8=1 py scripts/reporte_v2/recalcular_booleanos.py [--pares 07,08] [--forzar]
"""
import argparse
import csv
import json
import os
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
import instrumentos_texto as it                # noqa: E402
import comparar_v1_v2 as cmp                   # noqa: E402
import recalcular as rc                        # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

DESTINO = RAIZ / "datos_v2" / "booleanos"
INSTR = ["cr1_veredicto_contradice_narracion", "cl2_pnj_inactivo_actua"]
COLUMNAS = ["turn_id"] + [f"{i}_{v}" for i in INSTR for v in ("v1", "crudo", "v2")]
INFORME = RAIZ / "docs" / "reportes" / "reporte_v2_booleanos.md"


def _b(x):
    """Convierte a 0/1, conservando None."""
    return None if x is None else int(bool(x))


def procesar(conn, par, brazo, cid, hasta=1400):
    """Recalcula los dos detectores booleanos de una campaña turno a turno con el contexto completo del arnés.

    Returns:
        Filas con, por instrumento, `_v1` (guardado por el motor), `_crudo` (recalculado sobre texto crudo,
        control de fidelidad que debe igualar a v1) y `_v2` (texto normalizado).
    """
    dc = datos.DatosCampana(conn, cid, brazo, par)
    guardado = datos.guardado_en_turn_validation(conn, cid, range(1, hasta + 1))
    filas = []
    for t in range(1, hasta + 1):
        if t not in dc.turnos:
            continue
        ctx = dc.contexto(t)
        crudo = it.calcular(dc.texto(t), ctx, nombres=set(INSTR))
        norm = it.calcular(normalizar_turno(dc.texto(t), brazo), ctx, nombres=set(INSTR))
        g = guardado.get(t) or {}
        f = {"turn_id": t}
        for i in INSTR:
            f[f"{i}_v1"], f[f"{i}_crudo"], f[f"{i}_v2"] = _b(g.get(i)), _b(crudo[i]), _b(norm[i])
        filas.append(f)
    return filas


def escribir(ruta, filas):
    """Escribe el CSV de una campaña de forma atómica (.tmp y `os.replace`), con celda vacía para None."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNAS)
        for f in filas:
            w.writerow(["" if f.get(c) is None else f[c] for c in COLUMNAS])
    os.replace(tmp, ruta)


def fidelidad(todas):
    """Por brazo e instrumento: turnos comparables, discrepancias crudo≠v1, y turnos donde v2≠v1."""
    out = {}
    for (par, brazo), filas in todas.items():
        for i in INSTR:
            r = out.setdefault(f"{i}|{brazo}", {"n": 0, "crudo_ne_v1": 0, "v2_ne_v1": 0, "v1_pos": 0, "v2_pos": 0,
                                                 "v1_a_v2": 0, "v2_a_v1": 0})
            for f in filas:
                a, c, b = f[f"{i}_v1"], f[f"{i}_crudo"], f[f"{i}_v2"]
                if a is None or c is None or b is None:
                    continue
                r["n"] += 1; r["v1_pos"] += a; r["v2_pos"] += b
                r["crudo_ne_v1"] += (c != a); r["v2_ne_v1"] += (b != a)
                r["v1_a_v2"] += (a == 1 and b == 0); r["v2_a_v1"] += (a == 0 and b == 1)
    return out


def main():
    """Recalcula `cr1_veredicto_contradice_narracion` y `cl2_pnj_inactivo_actua` para las campañas de `pares.todos()`.

    Reanuda saltando los CSV existentes (`--forzar` los rehace). Escribe `fidelidad.json` y, si no se filtraron
    pares, `comparacion_booleanos.json` con el G1-vs-G2 antes/después de normalizar (HL, p Holm; `--B`, `--semilla`).
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", default="")
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--semilla", type=int, default=20260920)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    filtro = {p for p in a.pares.split(",") if p}
    pares = [p for p in _pares.todos() if not filtro or p["par"] in filtro]
    t0 = time.time()
    todas = {}
    with datos.abrir_conexion() as conn:
        for k, p in enumerate(pares, 1):
            for brazo in ("G1", "G2"):
                ruta = DESTINO / rc.nombre_csv(p["par"], brazo)
                if ruta.exists() and not a.forzar:
                    todas[(p["par"], brazo)] = rc.leer_csv(ruta)
                    continue
                t1 = time.time()
                filas = procesar(conn, p["par"], brazo, p["campaign_g1" if brazo == "G1" else "campaign_g2"])
                escribir(ruta, filas)
                todas[(p["par"], brazo)] = filas
                print(f"[{k:2}/{len(pares)}] par{p['par']} {brazo}: {len(filas)} turnos en {time.time() - t1:5.1f}s", flush=True)
    fid = fidelidad(todas)
    (DESTINO / "fidelidad.json").write_text(json.dumps(fid, indent=1), encoding="utf-8")
    print("\nFIDELIDAD (crudo recalculado vs guardado) y efecto de normalizar:")
    for k, r in fid.items():
        print(f"  {k:52} n={r['n']:6} crudo≠v1={r['crudo_ne_v1']:5} v1+={r['v1_pos']:5} v2+={r['v2_pos']:5} "
              f"(1→0: {r['v1_a_v2']}, 0→1: {r['v2_a_v1']})")
    if not filtro:
        res = cmp.analizar(DESTINO, pares, instrumentos=INSTR, semilla=a.semilla, B=a.B)
        (DESTINO / "comparacion_booleanos.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        print("\nG1 vs G2 (media por campaña = tasa de turnos con la marca; 21 parejas, HL de G1-G2):")
        for i, r in res["instrumentos"].items():
            c = r["cambio"]
            print(f"  {i:36} G1 {r['v1']['media_g1']:.4f}→{r['v2']['media_g1']:.4f}  G2 {r['v1']['media_g2']:.4f}→{r['v2']['media_g2']:.4f}"
                  f"  HL {r['v1']['hl']:+.4g}→{r['v2']['hl']:+.4g}  pHolm {r['v1']['p_holm']:.3g}→{r['v2']['p_holm']:.3g}  {c['titular']}")
    print(f"\n{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
