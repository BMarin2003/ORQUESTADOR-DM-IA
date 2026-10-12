"""
Variante de cl2_recall_semantico_v2 con el nulo SOLO de ventanas ANTERIORES al evento (EXPLORATORIO).

Motivo (límite 2 declarado en resultados v2): el nulo de la v2 incluye ventanas posteriores al evento, que
pueden describir ya el estado cambiado (un PNJ muerto se sigue narrando muerto) y suben el umbral P95, lo
que hace a la v2 conservadora. Aquí, para cada evento, el nulo usa solo turnos < t (más la ventana real,
que no cambia). Todo lo demás es idéntico a la v2 (condicionado.py, comun.py): mismos eventos, consultas,
mención, cuantil, búsqueda exacta. Si el recall sube de forma clara, el límite era real; si no, la
conclusión de la v2 (la similitud apenas detecta cambios de estado) no dependía de él.

Salidas: datos_v2/semantico/eventos_v2_previo.csv · docs/reportes/semantico/cl2_recall_semantico_v2_previo.md

    $env:PYTHONUTF8="1"; py scripts/semantico/recall_semantico_v2_previo.py [--dispositivo cuda]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comun as C                              # noqa: E402
import condicionado as K                       # noqa: E402
import db as bd                                # noqa: E402
import estadistica as est                      # noqa: E402
import pares as _pares                         # noqa: E402
import recall_semantico as RS                  # noqa: E402


def solo_previas(s_turno, t):
    return {u: v for u, v in s_turno.items() if u < t or t <= u <= t + C.VENTANA}


def evaluar_campana(camp, brazo, embedder):
    tpi, eventos = RS.cargar(camp, brazo)
    if not eventos:
        return []
    Q = embedder([C.consulta(e) for e in eventos])
    filas = []
    with camp._conn() as c:
        camp._tx(c)
        for e, q in zip(eventos, Q):
            if C.evaluar_evento(C.max_por_turno(c, camp.campaign_id, q), e) is None:
                continue
            s = K.max_por_turno_mencion(c, camp.campaign_id, q, K.patron_sql(e["entidad"], e["campo"]))
            d2 = K.evaluar(s, e)
            dp = K.evaluar(solo_previas(s, e["turno"]), e)
            filas.append({"turno": e["turno"], "campo": e["campo"], "brazo": brazo,
                          "rec_v2": None if d2 is None else int(d2["reconocido"]),
                          "rec_previo": None if dp is None else int(dp["reconocido"]),
                          "q95_v2": None if d2 is None else d2["q95"], "q95_previo": None if dp is None else dp["q95"]})
    return filas


def _w(xs):
    if not xs:
        return "—"
    lo, hi = est.wilson(sum(xs), len(xs))
    return f"{np.mean(xs):.3f} [{lo:.3f}, {hi:.3f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dispositivo", default="cpu")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    embedder = C.Embedder(revision=C.revision_fijada(), dispositivo=a.dispositivo)
    todos = []
    for p in _pares.todos():
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            filas = evaluar_campana(bd.Campaña(p[k]), brazo, embedder)
            for f in filas:
                f["par"] = p["par"]
            todos += filas
            print(f"Par{p['par']} {brazo}: {len(filas)} eventos", flush=True)
    ambos = [f for f in todos if f["rec_v2"] is not None and f["rec_previo"] is not None]
    solo_v2 = [f for f in todos if f["rec_v2"] is not None]
    solo_p = [f for f in todos if f["rec_previo"] is not None]
    q = [(f["q95_v2"], f["q95_previo"]) for f in ambos]
    L = ["# cl2_recall_semantico_v2 con nulo solo de ventanas previas (EXPLORATORIO)", "",
         f"Universo: {len(todos)} eventos · evaluables v2: {len(solo_v2)} · evaluables variante previa: {len(solo_p)} · "
         f"evaluables en ambas: {len(ambos)}.", "",
         "| Familia | n (ambas) | recall v2 [IC95] | recall nulo previo [IC95] |", "|---|---|---|---|"]
    for fam in RS.FAMILIAS + ("todas",):
        s = ambos if fam == "todas" else [f for f in ambos if f["campo"] == fam]
        L.append(f"| {fam} | {len(s)} | {_w([f['rec_v2'] for f in s])} | {_w([f['rec_previo'] for f in s])} |")
    if q:
        L += ["", f"Umbral P95 medio: v2 {np.mean([x for x, _ in q]):.4f} · previo {np.mean([y for _, y in q]):.4f}. "
              f"Eventos que cambian de decisión: {sum(f['rec_v2'] != f['rec_previo'] for f in ambos)}.", "",
              "Azar de referencia del instrumento: 5 %. Exploratorio, sin sello previo: es la variante declarada como trabajo futuro."]
    (C.SALIDA_DOCS / "cl2_recall_semantico_v2_previo.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    RS.escribir_csv(C.SALIDA_DATOS / "eventos_v2_previo.csv",
                    [{k: ("" if f[k] is None else f[k]) for k in ("par", "brazo", "turno", "campo", "rec_v2", "rec_previo", "q95_v2", "q95_previo")}
                     for f in todos])
    print("\n".join(L))


if __name__ == "__main__":
    main()
