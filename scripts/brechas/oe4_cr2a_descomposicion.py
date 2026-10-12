"""
Brecha OE-4: ¿por qué CR-2a normalizado (z) favorece a G2 y la versión cruda a G1? (solo lectura)

z = (crudo − media_nulo) / sd_nulo, donde el nulo es la MISMA respuesta del DM emparejada con
acciones de otros turnos de la campaña. Si crudo = media_nulo + z·sd, la discordancia se puede
descomponer por turno:

  crudo       solapamiento léxico (Ochiai) entre la acción del jugador y la respuesta
  media_nulo  solapamiento de esa misma respuesta con acciones AJENAS (lo genérico de la respuesta)
  exceso      crudo − media_nulo: lo que la respuesta comparte con ESTA acción y no con cualquiera
  sd_nulo, z, nR (lemas de la respuesta), nA (lemas de la acción)

Se promedia por campaña (turnos con z computable, 1..1400) y se compara G1 − G2 por par (Wilcoxon
bilateral). Control adicional: residuo de crudo tras regresión sobre log(nR) y log(nA).

    $env:PYTHONUTF8="1"; py scripts/brechas/oe4_cr2a_descomposicion.py
"""
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ / "scripts" / "instrumentos", RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts" / "sensibilidad",
           RAIZ / "scripts", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import correr_a4bc as C                 # noqa: E402
import datos                            # noqa: E402
import distribucion_a4bc_27 as D        # noqa: E402
import lemas_es as le                   # noqa: E402
import pares as _pares                  # noqa: E402
import respuesta_accion as ra           # noqa: E402

SALIDA = RAIZ / "docs" / "reportes" / "brechas"
VARS = ["crudo", "media_nulo", "exceso", "sd_nulo", "z", "nR", "nA"]


def por_turno(c):
    out = []
    for t in sorted(c.tokR):
        A = c.pool.lemas.get(t, frozenset())
        if c.pool.clases.get(t) == "solo_tag" or len(A) < ra.MIN_LEMAS:
            continue
        R = le.filtrar(c.tokR[t])
        if len(R) < ra.MIN_LEMAS:
            continue
        nulo = [ra.ochiai(c.pool.lemas[x], R) for x in ra.candidatos_nulo(c.pool, t, len(A))]
        if not nulo:
            continue
        crudo = ra.ochiai(A, R)
        m = sum(nulo) / len(nulo)
        sd = math.sqrt(sum((v - m) ** 2 for v in nulo) / len(nulo))
        out.append({"crudo": crudo, "media_nulo": m, "exceso": crudo - m, "sd_nulo": sd,
                    "z": (crudo - m) / max(sd, ra.PISO_SD), "nR": len(R), "nA": len(A)})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    conn = D.ConnRecortada(datos.abrir_conexion())
    camps, _ = C.cargar_campanas(conn, _pares.todos(), lambda s: print(s, flush=True))
    turnos = {}
    for c in camps.values():
        turnos[(c.brazo, f"{int(c.par):02d}")] = por_turno(c)
    # control por longitud: OLS agrupado crudo ~ log nR + log nA (todas las campañas)
    X, y = [], []
    for filas in turnos.values():
        for f in filas:
            X.append([1.0, math.log(f["nR"]), math.log(f["nA"])])
            y.append(f["crudo"])
    beta, *_ = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)
    medias = {}
    for k, filas in turnos.items():
        m = {v: float(np.mean([f[v] for f in filas])) for v in VARS}
        m["crudo_resid"] = float(np.mean([f["crudo"] - (beta[0] + beta[1] * math.log(f["nR"]) + beta[2] * math.log(f["nA"]))
                                          for f in filas]))
        m["n"] = len(filas)
        medias[k] = m
    pares = sorted({p for _, p in medias if ("G1", p) in medias and ("G2", p) in medias})
    L = ["# Brecha OE-4: descomposición de CR-2a (crudo = media_nulo + z·sd)", "",
         f"Pares: {len(pares)} · turnos computables G1 {sum(medias[('G1', p)]['n'] for p in pares)}, "
         f"G2 {sum(medias[('G2', p)]['n'] for p in pares)} · OLS crudo ~ log nR + log nA: "
         f"b0={beta[0]:.4f}, b_logR={beta[1]:.4f}, b_logA={beta[2]:.4f}", "",
         "| Componente | mediana G1 | mediana G2 | G1>G2 (pares) | mediana dif | p bilateral |", "|---|---|---|---|---|---|"]
    for v in VARS + ["crudo_resid"]:
        g1 = [medias[("G1", p)][v] for p in pares]
        g2 = [medias[("G2", p)][v] for p in pares]
        d = [a - b for a, b in zip(g1, g2)]
        L.append(f"| {v} | {np.median(g1):.4f} | {np.median(g2):.4f} | {sum(x > 0 for x in d)}/{len(d)} | "
                 f"{np.median(d):+.4f} | {wilcoxon(d).pvalue:.3g} |")
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "oe4_cr2a.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
