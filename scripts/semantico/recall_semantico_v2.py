"""
Medición completa de cl2_recall_semantico_v2 (nulo condicionado por mención; ver condicionado.py y
docs/especificaciones/spec_cl2_recall_semantico_v2.md). EXPLORATORIO. Solo lectura de la base.

Sobre los MISMOS eventos de Jericho-QA / v1 calcula, para cada evento: si la v2 lo puede evaluar, su
decisión v2, la decisión v1 y la de Jericho léxico. Compara las tres sobre el MISMO subconjunto
(eventos evaluables por la v2), para que las diferencias no vengan de comparar conjuntos distintos.

Salidas:
  datos_v2/semantico/eventos_v2.csv
  docs/reportes/semantico/cl2_recall_semantico_v2.md

    $env:PYTHONUTF8="1"; py scripts/semantico/recall_semantico_v2.py
"""
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comun as C                              # noqa: E402
import condicionado as K                       # noqa: E402
import db as bd                                # noqa: E402
import pares as _pares                         # noqa: E402
import estadistica as est                      # noqa: E402
import recall_semantico as RS                  # noqa: E402

FAMILIAS = RS.FAMILIAS


def evaluar_campana(camp, brazo, embedder):
    tpi, eventos = RS.cargar(camp, brazo)
    if not eventos:
        return []
    Q = embedder([C.consulta(e) for e in eventos])
    filas = []
    with camp._conn() as c:
        camp._tx(c)
        for e, q in zip(eventos, Q):
            d1 = C.evaluar_evento(C.max_por_turno(c, camp.campaign_id, q), e)
            if d1 is None:
                continue                         # la v1 tampoco lo evaluaba: fuera del universo de 790
            d2 = K.evaluar(K.max_por_turno_mencion(c, camp.campaign_id, q, K.patron_sql(e["entidad"], e["campo"])), e)
            filas.append({"turno": e["turno"], "campo": e["campo"], "estado": e["estado"], "entidad": e["entidad"],
                          "evaluable_v2": int(d2 is not None),
                          "rec_v2": "" if d2 is None else int(d2["reconocido"]),
                          "margen_v2": "" if d2 is None or d2["margen"] is None else d2["margen"],
                          "n_nulo_v2": "" if d2 is None else d2["n_nulo"],
                          "rec_v1": int(d1["reconocido"]), "jericho": RS._b(C.jericho_reconoce(e, tpi))})
    return filas


def _p(xs):
    return f"{np.mean(xs):.3f}" if xs else "—"


def _wilson(xs):
    if not xs:
        return "—"
    lo, hi = est.wilson(sum(xs), len(xs))
    return f"{np.mean(xs):.3f} [{lo:.3f}, {hi:.3f}]"


def informe(todos, por_campana):
    ev = [f for f in todos if f["evaluable_v2"]]
    L = ["# cl2_recall_semantico_v2 (EXPLORATORIO, nulo condicionado por mención)", "",
         "Mismos eventos que Jericho-QA y la v1. Solo cuentan las oraciones que mencionan a la entidad, en la ventana real "
         "y en el nulo. Spec y A2 sellada: docs/especificaciones/spec_cl2_recall_semantico_v2.md y sensibilidad_semantico_v2.md.", "",
         f"Universo (eventos que la v1 evaluaba): {len(todos)} · evaluables por la v2: {len(ev)} "
         f"({100 * len(ev) / max(1, len(todos)):.1f} %).", "",
         "## Evaluabilidad por brazo y familia", "", "| Brazo | Familia | Universo | Evaluables v2 |", "|---|---|---|---|"]
    for b in ("G1", "G2"):
        for fam in FAMILIAS:
            u = [f for f in todos if f["brazo"] == b and f["campo"] == fam]
            L.append(f"| {b} | {fam} | {len(u)} | {sum(f['evaluable_v2'] for f in u)} |")
    L += ["", "## Recall sobre el MISMO subconjunto (evaluables por la v2)", "",
          "| Familia | n | v2 [IC Wilson 95 %] | v1 | Jericho |", "|---|---|---|---|---|"]
    for fam in FAMILIAS + ("todas",):
        s = ev if fam == "todas" else [f for f in ev if f["campo"] == fam]
        L.append(f"| {fam} | {len(s)} | {_wilson([f['rec_v2'] for f in s])} | {_p([f['rec_v1'] for f in s])} | "
                 f"{_p([f['jericho'] for f in s if f['jericho'] != ''])} |")
    t = Counter(("v1" if f["rec_v1"] else "-") + "/" + ("v2" if f["rec_v2"] else "-") for f in ev)
    a = Counter(("sem" if f["rec_v2"] else "-") + "/" + ("jer" if f["jericho"] else "-") for f in ev if f["jericho"] != "")
    L += ["", "## Qué cambió respecto de la v1 (mismos eventos)", "",
          "| v1 y v2 | solo v1 | solo v2 | ninguno |", "|---|---|---|---|",
          f"| {t['v1/v2']} | {t['v1/-']} | {t['-/v2']} | {t['-/-']} |", "",
          "«Solo v1» son reconocimientos que dependían de nombrar a la entidad: la v2 los descarta.", "",
          "## Acuerdo v2 con Jericho-QA", "", "| Ambos | Solo v2 | Solo Jericho | Ninguno |", "|---|---|---|---|",
          f"| {a['sem/jer']} | {a['sem/-']} | {a['-/jer']} | {a['-/-']} |", "",
          "## Por brazo (descriptivo; los eventos evaluables por campaña son pocos)", "",
          "| Brazo | n evaluables | recall v2 [IC Wilson 95 %] |", "|---|---|---|"]
    for b in ("G1", "G2"):
        s = [f["rec_v2"] for f in ev if f["brazo"] == b]
        L.append(f"| {b} | {len(s)} | {_wilson(s)} |")
    comp = RS.comparacion(por_campana, "recall_sem")
    L += ["", "Comparación pareada G1 - G2 por par (mínimo 3 eventos evaluables en ambos brazos): " +
          ("sin pares suficientes." if comp is None else
           f"n = {comp['n_pares']} pares · Mdn G1 {comp['mdn_g1']:.3f} · Mdn G2 {comp['mdn_g2']:.3f} · "
           f"HL {comp['hl']:+.3f} [{comp['ic'][0]:+.3f}, {comp['ic'][1]:+.3f}] · p = {comp['p']:.4f}. Descriptivo, sin Holm."),
          "", "Uso: EXPLORATORIO. No decide H1e (regla del apartado 5.8.5). Sin validación humana: brecha declarada."]
    C.SALIDA_DOCS.mkdir(parents=True, exist_ok=True)
    (C.SALIDA_DOCS / "cl2_recall_semantico_v2.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def main(argv=None, embedder=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", help="lista separada por comas; por defecto las 27")
    ap.add_argument("--dispositivo", default="cpu")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if embedder is None:
        rev = C.revision_fijada()
        if rev is None:
            sys.exit("No hay manifiesto de embeddings: corre antes scripts/semantico/embeber_corpus.py")
        embedder = C.Embedder(revision=rev, dispositivo=a.dispositivo)
    pares = _pares.todos()
    if a.pares:
        pedidos = {p.strip().zfill(2) for p in a.pares.split(",")}
        pares = [p for p in pares if p["par"] in pedidos]
    todos, por_campana = [], []
    for p in pares:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            filas = evaluar_campana(bd.Campaña(p[k]), brazo, embedder)
            for f in filas:
                f.update(par=p["par"], brazo=brazo)
            todos += filas
            ev = [f["rec_v2"] for f in filas if f["evaluable_v2"]]
            por_campana.append({"par": p["par"], "brazo": brazo, "n_eventos": len(ev),
                                "recall_sem": float(np.mean(ev)) if ev else ""})
            print(f"Par{p['par']} {brazo}: {len(filas)} eventos, {len(ev)} evaluables v2", flush=True)
    orden = ["par", "brazo", "turno", "campo", "estado", "entidad", "evaluable_v2", "rec_v2", "margen_v2",
             "n_nulo_v2", "rec_v1", "jericho"]
    RS.escribir_csv(C.SALIDA_DATOS / "eventos_v2.csv", [{k: f[k] for k in orden} for f in todos])
    informe(todos, por_campana)
    return todos, por_campana


if __name__ == "__main__":
    main()
