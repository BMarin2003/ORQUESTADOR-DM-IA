"""
Prueba A2 de cl2_recall_semantico_v2 (nulo condicionado por mención; ver condicionado.py). Mismas convenciones
que sensibilidad_semantico.py: expectativas y parámetros sellados con SHA-256 ANTES de correr, perturbaciones
en memoria (nunca se escribe en la base), funciones reales del instrumento, estadística de
experimento/scripts/sensibilidad/estadistica.py. Mismas oraciones de perturbación que la v1 (se importan, no se copian).

Diferencia de diseño con la v1, fijada antes de correr: aquí se juzga la DECISIÓN (reconocido sí/no; McNemar
exacta sobre los pares discordantes, Holm por familia), no el margen. Motivo: condicionar el nulo no cambia
cuánto sube la similitud real al insertar una oración, solo el umbral que debe cruzar; el margen de SC2 subiría
igual en ambas versiones aunque la decisión no cambie. El margen se reporta como dato secundario.

  SQ1 paráfrasis sin lexema (evento hoy NO reconocido)  -> ESPERADO: se_dispara (0 -> 1)
  SQ2 ventana ajena (evento hoy reconocido)             -> ESPERADO: baja (1 -> 0)
  SC1 oración neutra, sin nombre (cualquier evento)     -> ESPERADO: sin_cambio
  SC2 nombre sin cambio de estado (cualquier evento)    -> ESPERADO: sin_cambio   <- la que falló en la v1
En SC1 y SC2 se calcula también la decisión de la v1 con la MISMA inserción (comparación descriptiva).

    $env:PYTHONUTF8="1"; py experimento/scripts/semantico/sensibilidad_semantico_v2.py
"""
import argparse
import csv
import hashlib
import json
import random
import sys
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
import sensibilidad_semantico as S1            # noqa: E402  (oraciones de perturbación de la v1)

N_DEF, SEMILLA_DEF = 40, 20261009
EXPECTATIVAS = {
    "SQ1|parafrasis_sin_lexema|reconocido": "se_dispara",
    "SQ2|texto_ajeno|reconocido": "baja",
    "SC1|oracion_neutra|reconocido": "sin_cambio",
    "SC2|nombre_sin_cambio|reconocido": "sin_cambio",
}
PARAMETROS = {"instrumento": "cl2_recall_semantico_v2", "nulo": "condicionado a oraciones que mencionan la entidad",
              "min_nulo": K.MIN_NULO, "ventana": C.VENTANA, "exclusion": C.EXCLUSION, "cuantil": C.CUANTIL,
              "criterio": "decision (McNemar exacta, Holm por familia)", "n_por_perturbacion": N_DEF,
              "semilla": SEMILLA_DEF, "alias": "palabras con mayuscula >=4 letras sin articulos; si no, frase completa"}
SELLO = {"expectativas": EXPECTATIVAS, "parametros": PARAMETROS}
HASH = hashlib.sha256(json.dumps(SELLO, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
CONFIRMATORIAS, CONTROLES = ("SQ1", "SQ2"), ("SC1", "SC2")


def candidatos(pares, embedder):
    """Eventos evaluables por la v2, con sus puntuaciones v1 (sin condicionar) y v2 (condicionadas)."""
    out = []
    for p in pares:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            camp = bd.Campaña(p[k])
            tpi, eventos = RS.cargar(camp, brazo)
            if not eventos:
                continue
            Q = embedder([C.consulta(e) for e in eventos])
            with camp._conn() as c:
                camp._tx(c)
                for e, q in zip(eventos, Q):
                    patron = K.patron_sql(e["entidad"], e["campo"])
                    s2 = K.max_por_turno_mencion(c, camp.campaign_id, q, patron)
                    base2 = K.evaluar(s2, e)
                    if base2 is None:
                        continue
                    s1 = C.max_por_turno(c, camp.campaign_id, q)
                    out.append({"par": p["par"], "brazo": brazo, "campaign_id": p[k], "camp": camp, "ev": e,
                                "q": q, "patron": patron, "s1": s1, "s2": s2,
                                "base1": C.evaluar_evento(s1, e), "base2": base2})
            print(f"Par{p['par']} {brazo}: {sum(1 for x in out if x['campaign_id'] == p[k])} eventos evaluables (v2)", flush=True)
    return out


def _ventana(s, t):
    """Recorta las similitudes por turno a la ventana que empieza en t y dura C.VENTANA turnos."""
    return {u: s[u] for u in range(t, t + C.VENTANA + 1) if u in s}


def _insertar(x, oracion, embedder):
    """Inserta `oracion` en el turno del evento. v1: siempre cuenta. v2: solo si la oración menciona a la entidad."""
    ev, t = x["ev"], x["ev"]["turno"]
    sim = float(np.dot(x["q"], embedder([oracion])[0]))
    r1 = _ventana(x["s1"], t)
    r1[t] = max(r1.get(t, -1.0), sim)
    menc = K.menciona(oracion, ev["entidad"], ev["campo"])
    if menc:
        r2 = _ventana(x["s2"], t)
        r2[t] = max(r2.get(t, -1.0), sim)
        d2 = K.evaluar(x["s2"], ev, r2)
    else:
        d2 = x["base2"]
    return C.evaluar_evento(x["s1"], ev, r1), d2, sim, menc


def _rec(d):
    """Convierte una decisión a booleano; None si el evento no era evaluable."""
    return None if d is None else bool(d["reconocido"])


def _fila(pid, x, d2, d1=None, extra=None):
    """Fila de resultados de una perturbación: decisión y margen de la v2 antes y después, y de la v1 como contraste."""
    f = {"perturbacion": pid, "par": x["par"], "brazo": x["brazo"], "turno": x["ev"]["turno"],
         "campo": x["ev"]["campo"], "estado": x["ev"]["estado"], "entidad": x["ev"]["entidad"],
         "rec_antes": int(x["base2"]["reconocido"]), "rec_despues": int(d2["reconocido"]),
         "margen_antes": x["base2"]["margen"], "margen_despues": d2["margen"],
         "v1_rec_antes": "" if _rec(x["base1"]) is None else int(_rec(x["base1"])),
         "v1_rec_despues": "" if _rec(d1) is None else int(_rec(d1))}
    f.update(extra or {})
    return f


def correr(cands, n, semilla, embedder):
    """Aplica las perturbaciones de la prueba A2 de la v2 (SQ1, SQ2, SC1 y siguientes), en memoria y con semilla fija, y devuelve las filas de resultados."""
    rng = random.Random(semilla)
    no_rec = [x for x in cands if not x["base2"]["reconocido"]]
    rec = [x for x in cands if x["base2"]["reconocido"]]
    rng.shuffle(no_rec)
    rng.shuffle(rec)
    todos = list(cands)
    rng.shuffle(todos)
    filas = []
    for x in no_rec[:n]:                                                              # SQ1
        ev = x["ev"]
        oracion = S1.PARAFRASIS[(ev["campo"], ev["estado"])].format(n=ev["entidad"])
        d1, d2, sim, menc = _insertar(x, oracion, embedder)
        filas.append(_fila("SQ1", x, d2, d1, {"oracion": oracion, "sim_oracion": sim, "menciona": int(menc)}))
    for x in rec[:n]:                                                                 # SQ2
        otras = [y for y in cands if y["par"] != x["par"]]
        y = rng.choice(otras)
        turnos = sorted(y["s1"])
        u = rng.choice(turnos[:-1]) if len(turnos) > 1 else turnos[0]
        t = x["ev"]["turno"]
        with x["camp"]._conn() as c:
            x["camp"]._tx(c)
            ajena = K.max_por_turno_mencion(c, y["campaign_id"], x["q"], x["patron"], u, u + C.VENTANA)
        d2 = K.evaluar(x["s2"], x["ev"], {t + (v - u): s for v, s in ajena.items()})
        filas.append(_fila("SQ2", x, d2, None, {"ventana_ajena": f"Par{y['par']} {y['brazo']} t{u}",
                                                "menciones_en_ajena": len(ajena)}))
    for x in todos[:n]:                                                               # SC1
        oracion = rng.choice(S1.NEUTRAS)
        d1, d2, sim, menc = _insertar(x, oracion, embedder)
        filas.append(_fila("SC1", x, d2, d1, {"oracion": oracion, "sim_oracion": sim, "menciona": int(menc)}))
    for x in todos[n:2 * n] or todos[:n]:                                             # SC2
        ev = x["ev"]
        oracion = S1.NOMBRE_SIN_CAMBIO[ev["campo"].split(".")[0]].format(n=ev["entidad"])
        d1, d2, sim, menc = _insertar(x, oracion, embedder)
        filas.append(_fila("SC2", x, d2, d1, {"oracion": oracion, "sim_oracion": sim, "menciona": int(menc)}))
    return filas


def _decision(antes, despues):
    """Cuenta los pares discordantes (1 a 0, 0 a 1) y su p de McNemar exacta.

    Returns:
        Tupla (b, c, p).
    """
    t = est.contar_pareado(antes, despues)
    return t["b"], t["c"], est.mcnemar_exacta(t["b"], t["c"])


def resumir(filas):
    """Resume cada perturbación con McNemar exacta sobre la decisión y Holm por familia; el margen queda como medida secundaria y la v1 se reporta como contraste en los controles."""
    res = {}
    for clave, esperado in EXPECTATIVAS.items():
        pid = clave.split("|")[0]
        sub = [f for f in filas if f["perturbacion"] == pid]
        b, c, p = _decision([f["rec_antes"] for f in sub], [f["rec_despues"] for f in sub])
        dm = [f["margen_despues"] - f["margen_antes"] for f in sub
              if f["margen_antes"] is not None and f["margen_despues"] is not None]
        v1 = [f for f in sub if f["v1_rec_antes"] != "" and f["v1_rec_despues"] != ""]
        b1, c1, p1 = _decision([f["v1_rec_antes"] for f in v1], [f["v1_rec_despues"] for f in v1]) if v1 else (0, 0, 1.0)
        res[pid] = {"clave": clave, "esperado": esperado, "n": len(sub), "b_1a0": b, "c_0a1": c, "p": p,
                    "mdn_delta_margen": float(np.median(dm)) if dm else None, "n_margen": len(dm),
                    "v1": {"n": len(v1), "b_1a0": b1, "c_0a1": c1, "p": p1,
                           "observado": est.direccion_booleana(p1, b1, c1)} if pid in CONTROLES else None}
    for familia in (CONFIRMATORIAS, CONTROLES):
        for pid, pa in zip(familia, est.holm([res[x]["p"] for x in familia])):
            r = res[pid]
            r["p_holm"] = pa
            r["observado"] = est.direccion_booleana(pa, r["b_1a0"], r["c_0a1"])
            r["veredicto"] = est.veredicto(r["esperado"], r["observado"], r["n"])
    return res


def _fmt(x, d=4):
    """Formatea un número con signo y d decimales; guion largo si es None."""
    return "—" if x is None else f"{x:+.{d}f}"


def escribir(filas, res, n_cands, semilla, n):
    """Escribe el CSV, el JSON (con el sello SHA-256) y el informe Markdown de la prueba A2 de la v2."""
    C.SALIDA_DOCS.mkdir(parents=True, exist_ok=True)
    base = C.SALIDA_DOCS / "sensibilidad_semantico_v2"
    campos = list(dict.fromkeys(k for f in filas for k in f))
    with open(base.with_suffix(".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    base.with_suffix(".json").write_text(json.dumps({"sha256": HASH, "sello": SELLO, "semilla": semilla, "n": n,
                                                     "eventos_evaluables_v2": n_cands, "resultados": res},
                                                    indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    L = ["# Prueba A2 de cl2_recall_semantico_v2 (nulo condicionado por mención)", "",
         f"SHA-256 de expectativas y parámetros (fijados antes de correr): `{HASH}`  ·  semilla {semilla}  ·  "
         f"n por perturbación {n}  ·  eventos evaluables por la v2: {n_cands}", "",
         "Criterio: decisión (reconocido sí/no), McNemar exacta sobre pares discordantes, Holm por familia.", "",
         "| Perturbación | Esperado | n | 0→1 | 1→0 | p | p Holm | Observado | Veredicto | Mdn Δ margen (secundario) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for pid in CONFIRMATORIAS + CONTROLES:
        r = res[pid]
        L.append(f"| {pid} {r['clave'].split('|')[1].replace('_', ' ')} | {r['esperado']} | {r['n']} | {r['c_0a1']} | "
                 f"{r['b_1a0']} | {r['p']:.4g} | {r['p_holm']:.4g} | {r['observado']} | **{r['veredicto']}** | "
                 f"{_fmt(r['mdn_delta_margen'])} (n={r['n_margen']}) |")
    L += ["", "## La misma inserción, decidida por la v1 (sin condicionar)", "",
          "| Control | n | 0→1 | 1→0 | p | Observado v1 |", "|---|---|---|---|---|---|"]
    for pid in CONTROLES:
        v = res[pid]["v1"]
        L.append(f"| {pid} | {v['n']} | {v['c_0a1']} | {v['b_1a0']} | {v['p']:.4g} | {v['observado']} |")
    ok = all(res[p]["veredicto"] == "responde" for p in CONFIRMATORIAS + CONTROLES)
    L += ["", "**Lectura:** " + ("las cuatro perturbaciones responden como se esperaba." if ok else
                                 "al menos una perturbación no respondió como se esperaba (ver tabla); se reporta como tal."),
          "", "Clasificación: EXPLORATORIO en cualquier caso (instrumento posterior al contraste de hipótesis)."]
    base.with_suffix(".md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None, embedder=None):
    """Corre la prueba A2 de la v2 con los valores sellados (n y semilla); con --solo-sello solo imprime el hash.

    Con --pares es prueba de humo y no escribe informes.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N_DEF)
    ap.add_argument("--semilla", type=int, default=SEMILLA_DEF)
    ap.add_argument("--pares", help="solo para pruebas de humo; la A2 real usa las 27")
    ap.add_argument("--solo-sello", action="store_true", help="imprime el hash y sale sin correr nada")
    ap.add_argument("--dispositivo", default="cpu")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"SHA-256 de expectativas y parámetros (fijados antes de correr): {HASH}", flush=True)
    if a.solo_sello:
        return None
    if (a.n, a.semilla) != (N_DEF, SEMILLA_DEF) and not a.pares:
        sys.exit("n o semilla distintos de los sellados: la A2 real se corre con los valores fijados.")
    S1._assert_sin_lexema()
    if embedder is None:
        rev = C.revision_fijada()
        if rev is None:
            sys.exit("No hay manifiesto de embeddings: corre antes experimento/scripts/semantico/embeber_corpus.py")
        embedder = C.Embedder(revision=rev, dispositivo=a.dispositivo)
    pares = _pares.todos()
    if a.pares:
        pedidos = {p.strip().zfill(2) for p in a.pares.split(",")}
        pares = [p for p in pares if p["par"] in pedidos]
    cands = candidatos(pares, embedder)
    filas = correr(cands, a.n, a.semilla, embedder)
    res = resumir(filas)
    if a.pares:
        print("Prueba de humo: no se escriben informes.")
    else:
        escribir(filas, res, len(cands), a.semilla, a.n)
    for pid in CONFIRMATORIAS + CONTROLES:
        r = res[pid]
        extra = f" | v1 con la misma inserción: {r['v1']['observado']} (0→1: {r['v1']['c_0a1']})" if r["v1"] else ""
        print(f"{r['clave']}: esperado {r['esperado']}, observado {r['observado']} -> {r['veredicto']} "
              f"(n={r['n']}, 0→1={r['c_0a1']}, 1→0={r['b_1a0']}){extra}")
    if not a.pares:
        print(f"Informe: {C.SALIDA_DOCS / 'sensibilidad_semantico_v2.md'}")
    return filas, res


if __name__ == "__main__":
    main()
