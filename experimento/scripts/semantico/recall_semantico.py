"""
Paso 2 del instrumento EXPLORATORIO cl2_recall_semantico (definición en comun.py). Requiere que
embeber_corpus.py haya llenado medicion_oraciones. Solo LECTURA de la base.

Por campaña: toma los eventos de Jericho-QA (deltas_narrables con su mismo filtro), calcula la
consulta de cada evento, pide a pgvector la máxima similitud por turno (búsqueda exacta), decide con
el nulo exacto de la campaña y guarda también el veredicto del Jericho léxico REAL para el mismo evento.

Salidas:
  datos/datos_v2/semantico/eventos.csv       un evento por fila (s_real, q95, margen, z, p_emp, reconocido, jericho)
  datos/datos_v2/semantico/por_campana.csv   recall semántico y léxico por campaña y por familia
  docs/reportes/semantico/cl2_recall_semantico.md   comparación pareada G1 - G2 (descriptiva, EXPLORATORIA)

    $env:PYTHONUTF8="1"; py experimento/scripts/semantico/recall_semantico.py [--pares 07,08]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comun as C                              # noqa: E402
import db as bd                                # noqa: E402
import pares as _pares                         # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

N_MIN_EVENTOS = 3        # una campaña con menos eventos evaluables no entra a la comparación pareada
FAMILIAS = ("npc.status", "npc.affinity", "quest.status")
SEMILLA, B = 20261008, 10000


def cargar(camp, brazo):
    """Carga los turnos de narración normalizados y los eventos narrables derivados de los deltas de una campaña, hasta el turno C.HASTA."""
    turnos = [t for t in camp.turnos_narracion() if t["turn_id"] <= C.HASTA]
    tpi = {t["turn_id"]: normalizar_turno(t["dm_output"], brazo) for t in turnos}
    deltas = [d for d in camp.deltas_narrables() if d["turn_id"] <= C.HASTA]
    eventos = [e for e in (C.evento_desde_delta(d) for d in deltas) if e is not None]
    return tpi, eventos


def evaluar_campana(camp, brazo, embedder):
    """Lista de filas (una por evento evaluable) de una campaña."""
    tpi, eventos = cargar(camp, brazo)
    if not eventos:
        return []
    Q = embedder([C.consulta(e) for e in eventos])
    filas = []
    with camp._conn() as c:
        camp._tx(c)
        n = c.execute(f"SELECT count(*) AS n FROM {C.TABLA} WHERE campaign_id=%s", (camp.campaign_id,)).fetchone()["n"]
        if not n:
            raise RuntimeError(f"{C.TABLA} vacía para {camp.campaign_id}: corre antes embeber_corpus.py")
        for e, q in zip(eventos, Q):
            s_turno = C.max_por_turno(c, camp.campaign_id, q)
            r = C.evaluar_evento(s_turno, e)
            if r is None:
                continue
            filas.append({"turno": e["turno"], "campo": e["campo"], "estado": e["estado"], "entidad": e["entidad"],
                          "consulta": C.consulta(e), **{k: r[k] for k in ("s_real", "q95", "margen", "z", "p_emp", "n_nulo")},
                          "reconocido": int(r["reconocido"]), "jericho": _b(C.jericho_reconoce(e, tpi))})
    return filas


def _b(x):
    """Convierte un booleano a entero; cadena vacía si es None (celda vacía en el CSV)."""
    return "" if x is None else int(x)


def resumen_campana(filas):
    """Resume una campaña: número de eventos, recall semántico y de Jericho, mediana de margen y de z, y recall por familia de evento."""
    out = {"n_eventos": len(filas)}
    if filas:
        out["recall_sem"] = float(np.mean([f["reconocido"] for f in filas]))
        jer = [f["jericho"] for f in filas if f["jericho"] != ""]
        out["recall_jericho"] = float(np.mean(jer)) if jer else ""
        out["margen_mediana"] = float(np.median([f["margen"] for f in filas]))
        out["z_mediana"] = float(np.median([f["z"] for f in filas]))
    for fam in FAMILIAS:
        sub = [f["reconocido"] for f in filas if f["campo"] == fam]
        out[f"n_{fam}"] = len(sub)
        out[f"recall_sem_{fam}"] = float(np.mean(sub)) if sub else ""
    return out


def comparacion(por_campana, campo):
    """Diferencias G1 - G2 por pareja (solo parejas con >= N_MIN_EVENTOS en ambos brazos)."""
    import comparar_v1_v2 as cp      # experimento/scripts/reporte_v2: Wilcoxon exacto, Hodges-Lehmann, rank-biserial (Kerby), IC bootstrap
    por_par = defaultdict(dict)
    for r in por_campana:
        por_par[r["par"]][r["brazo"]] = r
    g1, g2, d = [], [], []
    for par in sorted(por_par):
        x = por_par[par]
        if all(b in x and x[b]["n_eventos"] >= N_MIN_EVENTOS and x[b].get(campo, "") != "" for b in ("G1", "G2")):
            g1.append(x["G1"][campo]); g2.append(x["G2"][campo]); d.append(x["G1"][campo] - x["G2"][campo])
    if not d:
        return None
    d = np.asarray(d, dtype=float)
    lo, hi = cp.ic_bootstrap_pares(d, cp.hodges_lehmann, semilla=SEMILLA, B=B)
    w = cp.wilcoxon_exacto(d)
    return {"n_pares": int(d.size), "mdn_g1": float(np.median(g1)), "mdn_g2": float(np.median(g2)),
            "hl": cp.hodges_lehmann(d), "ic": (lo, hi), "r": cp.rank_biserial_pareada(d), "p": w["p"], "n_efectivo": w["n_efectivo"]}


def acuerdo(filas):
    """Tabla 2x2 semántico vs Jericho sobre los eventos que ambos evalúan."""
    t = {"ambos": 0, "solo_sem": 0, "solo_jericho": 0, "ninguno": 0}
    for f in filas:
        if f["jericho"] == "":
            continue
        s, j = f["reconocido"], f["jericho"]
        t["ambos" if s and j else "solo_sem" if s else "solo_jericho" if j else "ninguno"] += 1
    return t


def escribir_csv(ruta, filas):
    """Escribe filas (dicts) a CSV; las columnas son la unión de claves en orden de aparición."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    campos = list(dict.fromkeys(k for f in filas for k in f))
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


def _f(x, d=3):
    """Formatea un número con d decimales; guion largo si está vacío o es None."""
    return "—" if x == "" or x is None else f"{x:.{d}f}"


def informe(todos, por_campana):
    """Escribe el informe Markdown de CL-2 (exploratorio): recall por familia, acuerdo con Jericho-QA y comparación pareada G1-G2 con Wilcoxon exacto.

    Returns:
        Tupla (comparaciones, acuerdo).
    """
    comp = {campo: comparacion(por_campana, campo) for campo in ("recall_sem", "z_mediana", "recall_jericho")}
    ac = acuerdo(todos)
    fam = {f: [x["reconocido"] for x in todos if x["campo"] == f] for f in FAMILIAS}
    L = ["# CL-2 recall semántico (EXPLORATORIO)", "",
         "Instrumento nuevo de medición sobre el corpus ya generado: no cambia la generación ni regenera campañas. "
         "Mismos eventos que Jericho-QA; reconoce paráfrasis por similitud (bge-m3, pgvector, búsqueda exacta) y decide "
         f"contra el nulo exacto de cada campaña (percentil {int(C.CUANTIL * 100)} de todas sus ventanas a más de {C.EXCLUSION} turnos). "
         "Tasa de reconocimiento esperada por azar: ~5 %. Hasta que pase su prueba A2 (sensibilidad_semantico.py) no decide hipótesis.", "",
         f"Eventos evaluados: {len(todos)} en {len(por_campana)} campañas.", "",
         "## Recall por familia (todas las campañas)", "", "| Familia | n | recall semántico | recall Jericho (mismos eventos) |", "|---|---|---|---|"]
    for f in FAMILIAS:
        jer = [x["jericho"] for x in todos if x["campo"] == f and x["jericho"] != ""]
        L.append(f"| {f} | {len(fam[f])} | {_f(np.mean(fam[f]) if fam[f] else '')} | {_f(np.mean(jer) if jer else '')} |")
    L += ["", "## Acuerdo con Jericho-QA (mismos eventos)", "", "| Ambos | Solo semántico | Solo Jericho | Ninguno |", "|---|---|---|---|",
          f"| {ac['ambos']} | {ac['solo_sem']} | {ac['solo_jericho']} | {ac['ninguno']} |", "",
          "«Solo semántico» son eventos narrados sin el lexema que Jericho busca (paráfrasis) o falsos positivos; "
          "la prueba A2 y una revisión humana de una muestra deben decir cuál de los dos predomina.", "",
          f"## Comparación pareada G1 - G2 (parejas con al menos {N_MIN_EVENTOS} eventos en ambos brazos)", "",
          "| Medida | n pares | Mdn G1 | Mdn G2 | HL [IC 95 %] | r | p bilateral (Wilcoxon exacto) |", "|---|---|---|---|---|---|---|"]
    for campo, r in comp.items():
        if r is None:
            L.append(f"| {campo} | 0 | — | — | — | — | — |")
            continue
        L.append(f"| {campo} | {r['n_pares']} | {_f(r['mdn_g1'])} | {_f(r['mdn_g2'])} | {r['hl']:+.3f} [{r['ic'][0]:+.3f}, {r['ic'][1]:+.3f}] | {r['r']:+.2f} | {r['p']:.4f} |")
    L += ["", "Uso: EXPLORATORIO. Sin corrección de Holm y sin decisión sobre H1e (regla del apartado 5.8.5 de la tesis).", "",
          "Límites declarados: (1) depende de un modelo de embeddings (versión fijada en el manifiesto); (2) la consulta incluye "
          "el nombre de la entidad, así que parte de la similitud puede venir del nombre y no del cambio de estado (la A2 lo controla con SC2); "
          "(3) solo recall, igual que Jericho: no mide afirmaciones de estado no respaldadas por la base."]
    C.SALIDA_DOCS.mkdir(parents=True, exist_ok=True)
    (C.SALIDA_DOCS / "cl2_recall_semantico.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return comp, ac


def main(argv=None, embedder=None):
    """Evalúa el recall semántico de todos los eventos de las campañas (o --pares), escribe los CSV y el informe.

    Exige el manifiesto de embeddings; el embedder es inyectable para pruebas.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", help="lista separada por comas; por defecto las 27")
    ap.add_argument("--dispositivo", default="cpu")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if embedder is None:
        rev = C.revision_fijada()
        if rev is None:
            sys.exit("No hay manifiesto de embeddings: corre antes experimento/scripts/semantico/embeber_corpus.py")
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
            por_campana.append({"par": p["par"], "brazo": brazo, **resumen_campana(filas)})
            print(f"Par{p['par']} {brazo}: {len(filas)} eventos, recall semántico "
                  f"{_f(por_campana[-1].get('recall_sem', ''))}, Jericho {_f(por_campana[-1].get('recall_jericho', ''))}", flush=True)
    orden = ["par", "brazo", "turno", "campo", "estado", "entidad", "consulta", "s_real", "q95", "margen", "z", "p_emp", "n_nulo", "reconocido", "jericho"]
    escribir_csv(C.SALIDA_DATOS / "eventos.csv", [{k: f[k] for k in orden} for f in todos])
    escribir_csv(C.SALIDA_DATOS / "por_campana.csv", por_campana)
    comp, ac = informe(todos, por_campana)
    print(f"Informe: {C.SALIDA_DOCS / 'cl2_recall_semantico.md'}")
    return todos, por_campana, comp, ac


if __name__ == "__main__":
    main()
