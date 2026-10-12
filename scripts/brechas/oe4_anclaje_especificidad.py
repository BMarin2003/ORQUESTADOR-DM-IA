"""
Brecha OE-4, segunda parte: las otras dos versiones crudas (CR-2b, anclaje al escenario por coseno, con
y sin nombres propios) también favorecen a G1. ¿Es anclaje al escenario PROPIO o vocabulario genérico
del género que se parece a cualquier escenario? (solo lectura)

Misma lógica que la descomposición de CR-2a: para cada ventana de 8 turnos (la del instrumento cos_v8,
aquí sin solapamiento) se calcula el coseno con el escenario propio y con los otros 26 escenarios.
  propio      coseno con la referencia del escenario de la campaña (lo que reporta el instrumento)
  ajenos      media del coseno con los escenarios de las otras campañas (lo genérico)
  exceso      propio − ajenos (lo específico de ESTE escenario)
Mismo modelo TF-IDF y mismos escenarios que distribucion_a4bc_27.py. Wilcoxon bilateral G1 − G2 por par.

    $env:PYTHONUTF8="1"; py scripts/brechas/oe4_anclaje_especificidad.py
"""
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ / "scripts" / "instrumentos", RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts" / "sensibilidad",
           RAIZ / "scripts", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import anclaje_escenario as ae          # noqa: E402
import correr_a4bc as C                 # noqa: E402
import datos                            # noqa: E402
import distribucion_a4bc_27 as D        # noqa: E402
import pares as _pares                  # noqa: E402

SALIDA = RAIZ / "docs" / "reportes" / "brechas"
K = ae.K_VENTANA


def main():
    """Mide la especificidad del anclaje al escenario (CR-2b): similitud de cada ventana con su propio escenario frente a los 26 ajenos, por variante, y compara G1 y G2 por pares."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.perf_counter()
    pares = _pares.todos()
    conn = D.ConnRecortada(datos.abrir_conexion())
    camps, lores = C.cargar_campanas(conn, pares, lambda s: None)
    esc = C.construir_escenarios(pares, lores, lambda s: None)
    modelo = ae.ModeloAnclaje.desde_campanas([{"nombres": esc[c.par].nombres_lemas, "turnos": [c.tokR[t] for t in sorted(c.tokR)]}
                                              for c in camps.values()])
    print(f"modelo listo · {time.perf_counter() - t0:.0f}s", flush=True)
    medias = {}
    for c in camps.values():
        toks = [c.tokR[t] for t in sorted(c.tokR)]
        ventanas = [toks[i:i + K] for i in range(0, len(toks) - K + 1, K)]
        fila = {}
        for v in ae.VARIANTES:
            propio, ajenos = [], []
            for w in ventanas:
                propio.append(ae.cos_tokens(modelo, esc[c.par], w, v))
                ajenos.append(float(np.mean([ae.cos_tokens(modelo, e, w, v) for q, e in esc.items() if q != c.par])))
            fila[f"propio_{v}"] = float(np.mean(propio))
            fila[f"ajenos_{v}"] = float(np.mean(ajenos))
            fila[f"exceso_{v}"] = fila[f"propio_{v}"] - fila[f"ajenos_{v}"]
        medias[(c.brazo, f"{int(c.par):02d}")] = fila
        print(f"  {c.brazo} par {c.par} · {time.perf_counter() - t0:.0f}s", flush=True)
    claves = sorted({p for _, p in medias if ("G1", p) in medias and ("G2", p) in medias})
    L = ["# Brecha OE-4 (b): especificidad del anclaje al escenario (CR-2b)", "",
         f"Pares: {len(claves)} · ventanas de {K} turnos sin solapamiento · 26 escenarios ajenos por ventana.", "",
         "| Componente | mediana G1 | mediana G2 | G1>G2 | mediana dif | p bilateral |", "|---|---|---|---|---|---|"]
    for v in ae.VARIANTES:
        for comp in ("propio", "ajenos", "exceso"):
            k = f"{comp}_{v}"
            g1 = [medias[("G1", p)][k] for p in claves]
            g2 = [medias[("G2", p)][k] for p in claves]
            d = [a - b for a, b in zip(g1, g2)]
            L.append(f"| {k} | {np.median(g1):.4f} | {np.median(g2):.4f} | {sum(x > 0 for x in d)}/{len(d)} | "
                     f"{np.median(d):+.4f} | {wilcoxon(d).pvalue:.3g} |")
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "oe4_anclaje.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
