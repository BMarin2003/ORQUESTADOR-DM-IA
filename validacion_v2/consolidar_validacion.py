"""Validación humana v2 -- consolidación (plan del libro de códigos, secciones 4 y 5).

Entradas: respuestas/etiquetas_v2_*.csv, clave.csv, clave_cd.csv, controles_clave.csv, poblaciones.json,
          datos_v2/persona2_v3b (A se valida contra persona2 v3b), respuestas/auditoria_afinidad_respuestas.csv.
Salidas:  resultados_validacion_v2.md, resultados_validacion_v2.json, anexo_respuestas_v2.csv
    PYTHONUTF8=1 py validacion_v2/consolidar_validacion.py
"""
import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SEMILLA = 20261104
B = 2000
# código del formulario (semilla del orden) -> archivo
ARCHIVOS = {"E5": "etiquetas_v2_E5.csv", "E6": "etiquetas_v2_E6_rotuladoE3.csv", "E7": "etiquetas_v2_E7.csv",
            "E8": "etiquetas_v2_E8.csv", "E9": "etiquetas_v2_E9.csv"}
# rótulo con que se reporta cada evaluador
ROTULO = {"E5": "E1", "E6": "E2", "E7": "E3", "E8": "E4", "E9": "E5"}
PREG = {"persona2": "A", "pnj": "B", "jericho": "C", "accion": "D"}
TOPE_FALLOS = {"persona2": 2, "pnj": 2, "jericho": 1, "accion": 1}


def leer(p):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def fleiss(M):
    """M: lista de ítems, cada uno lista de 0/1 (sin faltantes)."""
    n = len(M[0])
    N = len(M)
    p1 = sum(sum(r) for r in M) / (N * n)
    P = [(sum(r) * (sum(r) - 1) + (n - sum(r)) * (n - sum(r) - 1)) / (n * (n - 1)) for r in M]
    Pbar = sum(P) / N
    Pe = p1 ** 2 + (1 - p1) ** 2
    return (Pbar - Pe) / (1 - Pe)


def kripp(M):
    """α de Krippendorff nominal, datos completos."""
    o = Counter()
    for r in M:
        m = len(r)
        c = Counter(r)
        for x in (0, 1):
            for y in (0, 1):
                o[(x, y)] += c[x] * (c[y] - (x == y)) / (m - 1)
    nt = sum(o.values())
    nx = {x: o[(x, 0)] + o[(x, 1)] for x in (0, 1)}
    Do = (o[(0, 1)] + o[(1, 0)]) / nt
    De = (2 * nx[0] * nx[1]) / (nt * (nt - 1))
    return 1 - Do / De


def auc(z, y):
    pos = [a for a, b in zip(z, y) if b == 1]
    neg = [a for a, b in zip(z, y) if b == 0]
    if not pos or not neg:
        return float("nan")
    s = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return s / (len(pos) * len(neg))


def pbis(z, y):
    n = len(z)
    mz = sum(z) / n
    sz = math.sqrt(sum((a - mz) ** 2 for a in z) / n)
    p = sum(y) / n
    if p in (0, 1) or sz == 0:
        return float("nan")
    m1 = sum(a for a, b in zip(z, y) if b) / sum(y)
    m0 = sum(a for a, b in zip(z, y) if not b) / (n - sum(y))
    return (m1 - m0) / sz * math.sqrt(p * (1 - p))


def pct(v, q):
    v = sorted(x for x in v if not math.isnan(x))
    if not v:
        return float("nan")
    k = (len(v) - 1) * q
    f = math.floor(k)
    return v[f] + (v[min(f + 1, len(v) - 1)] - v[f]) * (k - f)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = random.Random(SEMILLA)
    pobl = json.loads((AQUI / "poblaciones.json").read_text(encoding="utf-8"))
    clave = {r["id"]: r for r in leer(AQUI / "clave.csv") + leer(AQUI / "clave_cd.csv")}
    ctl = {r["id"]: r for r in leer(AQUI / "controles_clave.csv")}
    resp = {}
    for cod, f in ARCHIVOS.items():
        filas = leer(AQUI / "respuestas" / f)
        assert len(filas) == 982 and len({r["id"] for r in filas}) == 982, f
        resp[cod] = {r["id"]: int(r["respuesta"] == "Sí") for r in filas}
    evs = list(ARCHIVOS)

    # persona2 v3b por turno
    v3b = {}
    for r in clave.values():
        if r["tipo"] == "persona2":
            k = (r["par"], r["brazo"])
            if k not in v3b:
                v3b[k] = {int(x["turn_id"]): int(x["primaria"]) for x in leer(RAIZ / "datos_v2" / "persona2_v3b" / f"par{r['par']}_{r['brazo']}.csv")}

    # 1. controles y exclusiones
    controles, retenidos, constantes = {}, {}, {}
    for t in PREG:
        ids_t = [i for i, c in ctl.items() if c["tipo"] == t]
        items_t = [i for i, c in clave.items() if c["tipo"] == t]
        retenidos[t] = []
        for e in evs:
            ok = sum(resp[e][i] == (ctl[i]["esperada"] == "Sí") for i in ids_t)
            const = len({resp[e][i] for i in items_t}) == 1
            controles[(t, e)] = (ok, len(ids_t))
            constantes[(t, e)] = const
            if len(ids_t) - ok <= TOPE_FALLOS[t] and not const:
                retenidos[t].append(e)

    def referencia(t, quienes):
        ref = {}
        for i, c in clave.items():
            if c["tipo"] != t:
                continue
            v = [resp[e][i] for e in quienes]
            s = sum(v)
            ref[i] = None if 2 * s == len(v) else int(2 * s > len(v))
        return ref

    def detector(t, i):
        c = clave[i]
        if t == "persona2":
            return v3b[(c["par"], c["brazo"])][int(c["turn_id"])]
        return int(c["detector"])

    def bloque_detector(t, quienes, filtro=None, pob=None):
        ref = referencia(t, quienes)
        ids = [i for i in ref if ref[i] is not None and (filtro is None or filtro(clave[i]))]
        d = [detector(t, i) for i in ids]
        h = [ref[i] for i in ids]
        est = [clave[i]["estrato"] for i in ids]
        tp = sum(a and b for a, b in zip(d, h))
        fp = sum(a and not b for a, b in zip(d, h))
        fn = sum((not a) and b for a, b in zip(d, h))
        tn = sum((not a) and (not b) for a, b in zip(d, h))
        po, k = kappa(d, h)
        prec = wilson(tp, tp + fp)
        rec_s = wilson(tp, tp + fn)
        # exhaustividad ponderada por estrato (peso = N_estrato / n_estrato muestreado)
        nmu = Counter(clave[i]["estrato"] for i in clave if clave[i]["tipo"] == t and (filtro is None or filtro(clave[i])))
        W = {s: (pob or pobl[t])[s] / nmu[s] for s in nmu}

        def rec_w(idx):
            num = sum(W[est[j]] for j in idx if d[j] and h[j])
            den = sum(W[est[j]] for j in idx if h[j])
            return num / den if den else float("nan")

        def kap_idx(idx):
            return kappa([d[j] for j in idx], [h[j] for j in idx])[1]

        porest = defaultdict(list)
        for j, s in enumerate(est):
            porest[s].append(j)
        bw, bk = [], []
        for _ in range(B):
            idx = [j for s, v in porest.items() for j in (rng.choice(v) for _ in v)]
            bw.append(rec_w(idx))
            bk.append(kap_idx(idx))
        rw = rec_w(range(len(ids)))
        return {"n": len(ids), "empates": sum(v is None for v in ref.values()), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "acuerdo": po, "kappa": k, "kappa_ic": (pct(bk, .025), pct(bk, .975)),
                "precision": prec, "exh_muestra": rec_s, "exh_pond": (rw, pct(bw, .025), pct(bw, .975)),
                "ref_si": sum(h), "por_estrato": {s: (sum(h[j] for j in v), len(v)) for s, v in porest.items()}}

    def entre(t, quienes):
        ids = [i for i, c in clave.items() if c["tipo"] == t]
        M = [[resp[e][i] for e in quienes] for i in ids]
        return {"fleiss": fleiss(M), "kripp": kripp(M), "n_items": len(ids), "n_ev": len(quienes),
                "unanimes": sum(len(set(r)) == 1 for r in M) / len(M)}

    R = {"retenidos": retenidos, "controles": {f"{t}|{e}": v for (t, e), v in controles.items()}}
    for t in ("persona2", "pnj", "jericho"):
        R[t] = {"principal": bloque_detector(t, retenidos[t]), "todos": bloque_detector(t, evs)}
    R["persona2"]["sin_E9"] = bloque_detector("persona2", [e for e in retenidos["persona2"] if e != "E9"]) \
        if len([e for e in retenidos["persona2"] if e != "E9"]) >= 2 else None
    R["jericho"]["estado"] = bloque_detector("jericho", retenidos["jericho"], lambda c: c["campo"] == "npc.status", {s: pobl["jericho_campo"][s]["npc.status"] for s in ("si", "no")})
    R["jericho"]["afinidad"] = bloque_detector("jericho", retenidos["jericho"], lambda c: c["campo"] == "npc.affinity", {s: pobl["jericho_campo"][s]["npc.affinity"] for s in ("si", "no")})

    # D
    def bloque_d(quienes):
        ref = referencia("accion", quienes)
        al = [i for i in ref if clave[i]["estrato"] == "aleatorio" and ref[i] is not None]
        z = [float(clave[i]["z"]) for i in al]
        y = [ref[i] for i in al]
        a = auc(z, y)
        bs = []
        for _ in range(B):
            idx = [rng.randrange(len(al)) for _ in al]
            bs.append(auc([z[j] for j in idx], [y[j] for j in idx]))
        cb = [i for i in ref if clave[i]["estrato"] == "cola_baja" and ref[i] is not None]
        no_cb = sum(1 - ref[i] for i in cb)
        no_al = sum(1 - v for v in y)
        return {"n_al": len(al), "no_al": no_al, "auc": a, "auc_ic": (pct(bs, .025), pct(bs, .975)), "rpb": pbis(z, y),
                "n_cb": len(cb), "no_cb": no_cb, "prop_no_cb": wilson(no_cb, len(cb)), "prop_no_al": wilson(no_al, len(al)),
                "z_med_si": sorted(a for a, b in zip(z, y) if b)[len([1 for b in y if b]) // 2] if any(y) else float("nan"),
                "z_med_no": sorted(a for a, b in zip(z, y) if not b)[no_al // 2] if no_al else float("nan")}

    R["accion"] = {"principal": bloque_d(retenidos["accion"]), "todos": bloque_d(evs)}
    R["entre"] = {t: {"principal": entre(t, retenidos[t]), "todos": entre(t, evs)} for t in PREG}

    # A contra v2b (lo que se congeló al muestrear): sólo como comparación
    ref_a = referencia("persona2", retenidos["persona2"])
    ids_a = [i for i in ref_a if ref_a[i] is not None]
    R["persona2"]["v2b_matriz"] = Counter((int(clave[i]["detector"]), ref_a[i]) for i in ids_a)
    R["persona2"]["v2b_matriz"] = {f"{k[0]}{k[1]}": v for k, v in R["persona2"]["v2b_matriz"].items()}

    # auditoría de afinidad
    aud = leer(AQUI / "respuestas" / "auditoria_afinidad_respuestas.csv")
    k = sum(r["respuesta"] == "Sí" for r in aud)
    R["auditoria"] = {"si": k, "n": len(aud), "wilson": wilson(k, len(aud))}

    # anexo crudo
    with open(AQUI / "anexo_respuestas_v2.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "pregunta", "estrato", "control"] + [ROTULO[e] for e in evs])
        for i in sorted(set(resp["E5"])):
            c = clave.get(i) or ctl[i]
            w.writerow([i, PREG[c["tipo"]], c.get("estrato", ""), int(i in ctl)] + ["Sí" if resp[e][i] else "No" for e in evs])

    (AQUI / "resultados_validacion_v2.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    escribir_md(R, evs)
    print("listo")


def f2(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.2f}"


def pc(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.1f}"


def escribir_md(R, evs):
    L = ["# Validación humana v2 — resultados consolidados", "",
         f"Evaluadores: {', '.join(ROTULO[e] for e in evs)}. Referencia por ítem = mayoría de los evaluadores retenidos en cada pregunta. "
         "Los ítems de control no entran en el análisis.", "", "## 1. Controles y retención", "",
         "| Evaluador | A | B | C | D |", "|---|---|---|---|---|"]
    for e in evs:
        celdas = []
        for t in PREG:
            ok, n = R["controles"][f"{t}|{e}"]
            celdas.append(f"{ok}/{n}" + ("" if e in R["retenidos"][t] else " (excluido)"))
        L.append(f"| {ROTULO[e]} | " + " | ".join(celdas) + " |")
    L += ["", "| Pregunta | Retenidos |", "|---|---|"]
    for t, q in PREG.items():
        L.append(f"| {q} | {', '.join(ROTULO[e] for e in R['retenidos'][t])} ({len(R['retenidos'][t])}) |")
    nombres = {"persona2": "A · persona2 v3b", "pnj": "B · PNJ inactivo refinado", "jericho": "C · Jericho-QA"}
    L += ["", "## 2. Detector frente a la referencia humana (A, B, C)", "",
          "| Instrumento | Análisis | n | VP | FP | FN | VN | % acuerdo | κ [IC 95 %] | Precisión [IC Wilson] | Exhaustividad ponderada [IC 95 %] |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]

    def fila(nom, an, b):
        if b is None:
            return
        p, pl, ph = b["precision"]
        r, rl, rh = b["exh_pond"]
        kl, kh = b["kappa_ic"]
        L.append(f"| {nom} | {an} | {b['n']} | {b['tp']} | {b['fp']} | {b['fn']} | {b['tn']} | {pc(b['acuerdo'])} | "
                 f"{f2(b['kappa'])} [{f2(kl)}, {f2(kh)}] | {pc(p)} [{pc(pl)}, {pc(ph)}] | {pc(r)} [{pc(rl)}, {pc(rh)}] |")

    for t in ("persona2", "pnj", "jericho"):
        fila(nombres[t], "principal", R[t]["principal"])
        if t == "persona2" and R[t].get("sin_E9"):
            fila(nombres[t], "sin E5 (límite en controles)", R[t]["sin_E9"])
        if t == "jericho":
            fila(nombres[t], "solo estado (npc.status)", R[t]["estado"])
            fila(nombres[t], "solo afinidad (npc.affinity)", R[t]["afinidad"])
        fila(nombres[t], "sensibilidad: 5 evaluadores", R[t]["todos"])
    L += ["", "Exhaustividad ponderada: cada ítem pesa N_estrato / n_estrato (poblaciones en `poblaciones.json`); "
          "IC por bootstrap estratificado (2 000 réplicas). κ con IC por el mismo bootstrap.", ""]
    a = R["auditoria"]
    L += [f"Auditoría de afinidad (autores, 30 cambios): la narración refleja el cambio en {a['si']}/{a['n']} "
          f"({pc(a['wilson'][0])} %, IC Wilson {pc(a['wilson'][1])}–{pc(a['wilson'][2])} %).", "",
          f"persona2 v2b (versión con que se estratificó) frente a la misma referencia: {R['persona2']['v2b_matriz']} "
          "(clave «detector,referencia»).", "", "## 3. Pregunta D · respuesta a la acción (z continuo)", "",
          "| Análisis | n al azar | Ref. «No» | AUC [IC 95 %] | r biserial | Cola baja: «No» / n [IC Wilson] |", "|---|---|---|---|---|---|"]
    for an, k in (("principal", "principal"), ("sensibilidad: 5 evaluadores", "todos")):
        d = R["accion"][k]
        p, pl, ph = d["prop_no_cb"]
        L.append(f"| {an} | {d['n_al']} | {d['no_al']} | {f2(d['auc'])} [{f2(d['auc_ic'][0])}, {f2(d['auc_ic'][1])}] | "
                 f"{f2(d['rpb'])} | {d['no_cb']}/{d['n_cb']} = {pc(p)} % [{pc(pl)}, {pc(ph)}] |")
    L += ["", "## 4. Acuerdo entre evaluadores", "",
          "| Pregunta | Análisis | Evaluadores | κ de Fleiss | α de Krippendorff | % ítems unánimes |", "|---|---|---|---|---|---|"]
    for t, q in PREG.items():
        for an, k in (("principal", "principal"), ("5 evaluadores", "todos")):
            x = R["entre"][t][k]
            L.append(f"| {q} | {an} | {x['n_ev']} | {f2(x['fleiss'])} | {f2(x['kripp'])} | {pc(x['unanimes'])} |")
    (AQUI / "resultados_validacion_v2.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
