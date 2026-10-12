"""
Prueba A2 (sensibilidad por perturbaciones) del instrumento EXPLORATORIO cl2_recall_semantico, con las
MISMAS convenciones del arnés de scripts/sensibilidad/: expectativas fijadas y selladas con SHA-256 ANTES
de correr; perturbaciones en memoria (nunca se escribe en la base); funciones REALES del instrumento
(comun.evaluar_evento / comun.jericho_reconoce); estadística de scripts/sensibilidad/estadistica.py
(diferencia pareada del margen, delta de Cliff pareado >= 0.147, prueba de signos exacta, Holm por familia).

Perturbaciones (por EVENTO; muestra con semilla fija):
  SQ1  paráfrasis sin lexema    evento HOY no reconocido -> se inserta en el turno del evento una oración
                                que expresa el mismo cambio SIN ningún lexema de Jericho («{n} ya no respira…»).
                                ESPERADO: el margen sube. (Se registra aparte el veredicto de Jericho con la
                                misma inserción: por construcción no debería cambiar; muestra la ceguera léxica.)
  SQ2  texto ajeno              evento HOY reconocido -> su ventana se sustituye por una ventana de OTRA pareja.
                                ESPERADO: el margen baja.
  SC1  oración neutra (control) cualquier evento -> se inserta una oración ambiental sin nombres ni cambios
                                de estado. ESPERADO: sin cambio.
  SC2  nombre sin cambio        cualquier evento -> se inserta una oración que nombra a la entidad SIN
       (control)                expresar el cambio («{n} camina por la plaza…»). ESPERADO: sin cambio. Si el
                                margen sube aquí, el instrumento responde al nombre y no al estado.
Lectura: el instrumento es informativo si SQ1 y SQ2 «responden» y SC1 y SC2 «responden» (sin cambio). Aun
así queda EXPLORATORIO en esta tesis: la clasificación de instrumentos se fijó antes del contraste de
hipótesis y no se reabre (apartado 5.8.5); el resultado orienta la recomendación de un estudio futuro.

    $env:PYTHONUTF8="1"; py scripts/semantico/sensibilidad_semantico.py [--n 40] [--semilla 20261008]
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
import db as bd                                # noqa: E402
import pares as _pares                         # noqa: E402
import estadistica as est                      # noqa: E402  (scripts/sensibilidad/estadistica.py)
import recall_semantico as RS                  # noqa: E402

EXPECTATIVAS = {
    "SQ1|parafrasis_sin_lexema|margen": "sube",
    "SQ2|texto_ajeno|margen": "baja",
    "SC1|oracion_neutra|margen": "sin_cambio",
    "SC2|nombre_sin_cambio|margen": "sin_cambio",
}
CONFIRMATORIAS, CONTROLES = ("SQ1", "SQ2"), ("SC1", "SC2")
HASH = hashlib.sha256(json.dumps(EXPECTATIVAS, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# Paráfrasis SIN ningún lexema de los léxicos de Jericho (lo verifica _assert_sin_lexema antes de correr).
PARAFRASIS = {
    ("npc.status", "dead"): "{n} ya no respira; su cuerpo quedó tendido e inmóvil sobre la tierra.",
    ("npc.status", "missing"): "Nadie sabe adónde fue {n}; su casa está vacía y nadie lo ha visto desde entonces.",
    ("npc.status", "captured"): "Unos guardias se llevaron a {n} maniatado y lo encerraron tras unos barrotes.",
    ("quest.status", "completed"): "Por fin, el encargo «{n}» quedó terminado con éxito.",
    ("quest.status", "failed"): "El encargo «{n}» se vino abajo y ya no hay forma de salvarlo.",
    ("quest.status", "abandoned"): "Dejan de lado el encargo «{n}» y no piensan volver a él.",
    ("npc.affinity", "hostile"): "{n} te mira con rabia y deja claro que te quiere lejos.",
    ("npc.affinity", "wary"): "{n} no se fía de ti y vigila cada uno de tus movimientos.",
    ("npc.affinity", "cold"): "{n} apenas te dirige la palabra y responde con sequedad.",
    ("npc.affinity", "cordial"): "{n} te recibe con una sonrisa y te ofrece asiento junto al fuego.",
    ("npc.affinity", "loyal"): "{n} jura que estará a tu lado pase lo que pase.",
    ("npc.affinity", "devoted"): "{n} daría la vida por ti sin dudarlo un instante.",
}
NEUTRAS = (
    "El viento agita las ramas de los árboles cercanos.",
    "A lo lejos se oye el murmullo de un arroyo.",
    "El cielo se cubre de nubes grises mientras cae la tarde.",
)
NOMBRE_SIN_CAMBIO = {
    "npc": "{n} camina por la plaza y saluda a unos vecinos.",
    "quest": "Alguien menciona el encargo «{n}» de pasada en la taberna.",
}


def _lexemas():
    todos = set()
    for tabla in (C.RV._KEYWORDS_NPC_STATUS, C.RV._KEYWORDS_QUEST_STATUS, C.RV._KEYWORDS_AFINIDAD_BANDA):
        for claves in tabla.values():
            todos.update(k.lower() for k in claves)
    return todos


def _assert_sin_lexema():
    """Ninguna oración insertada (sin el nombre) contiene un lexema de Jericho; si no, se detiene ANTES de perturbar."""
    lex = _lexemas()
    frases = list(PARAFRASIS.values()) + list(NEUTRAS) + list(NOMBRE_SIN_CAMBIO.values())
    malas = [(f, k) for f in frases for k in lex if k in f.replace("{n}", "").lower()]
    if malas:
        raise AssertionError(f"oraciones de la A2 con lexemas de Jericho: {malas}")
    faltan = set(C._CONSULTA) - set(PARAFRASIS)
    if faltan:
        raise AssertionError(f"estados sin paráfrasis: {faltan}")


def _insertar_en_turno(tpi, t, oracion):
    tpi2 = dict(tpi)
    tpi2[t] = (tpi.get(t, "") + " " + oracion).strip()
    return tpi2


def _ventana_ajena(conn, q, campaign_id, u):
    """{u, u+1} -> máxima similitud de q con las oraciones de esa ventana de OTRA campaña (búsqueda exacta)."""
    filas = conn.execute(C.SQL_MAX_POR_TURNO, (C.vec_literal(q), campaign_id, u, u + C.VENTANA)).fetchall()
    return {int(f["turn_id"]): float(f["s"]) for f in filas}


def candidatos(pares, embedder):
    """Todos los eventos evaluables del corpus con lo necesario para perturbarlos."""
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
                    s_turno = C.max_por_turno(c, camp.campaign_id, q)
                    base = C.evaluar_evento(s_turno, e)
                    if base is None:
                        continue
                    out.append({"par": p["par"], "brazo": brazo, "campaign_id": p[k], "camp": camp, "ev": e, "q": q,
                                "s_turno": s_turno, "tpi": tpi, "base": base})
    return out


def _fila(pid, x, despues, extra=None):
    f = {"perturbacion": pid, "par": x["par"], "brazo": x["brazo"], "turno": x["ev"]["turno"], "campo": x["ev"]["campo"],
         "estado": x["ev"]["estado"], "entidad": x["ev"]["entidad"], "margen_antes": x["base"]["margen"],
         "margen_despues": despues["margen"], "reconocido_antes": int(x["base"]["reconocido"]),
         "reconocido_despues": int(despues["reconocido"])}
    f.update(extra or {})
    return f


def _insercion(x, oracion, embedder):
    """Inserta `oracion` en el turno del evento: el máximo de ese turno pasa a max(actual, sim(q, oración))."""
    t = x["ev"]["turno"]
    sim = float(np.dot(x["q"], embedder([oracion])[0]))
    reemplazo = {u: x["s_turno"][u] for u in range(t, t + C.VENTANA + 1) if u in x["s_turno"]}
    reemplazo[t] = max(reemplazo.get(t, -1.0), sim)
    return C.evaluar_evento(x["s_turno"], x["ev"], reemplazo), sim


def correr(cands, n, semilla, embedder):
    rng = random.Random(semilla)
    no_rec = [x for x in cands if not x["base"]["reconocido"]]
    rec = [x for x in cands if x["base"]["reconocido"]]
    rng.shuffle(no_rec); rng.shuffle(rec)
    todos = list(cands); rng.shuffle(todos)
    filas = []
    for x in no_rec[:n]:                                                          # SQ1
        ev = x["ev"]
        oracion = PARAFRASIS[(ev["campo"], ev["estado"])].format(n=ev["entidad"])
        despues, sim = _insercion(x, oracion, embedder)
        jer_antes = C.jericho_reconoce(ev, x["tpi"])
        jer_despues = C.jericho_reconoce(ev, _insertar_en_turno(x["tpi"], ev["turno"], oracion))
        filas.append(_fila("SQ1", x, despues, {"oracion": oracion, "sim_oracion": sim,
                                               "jericho_antes": RS._b(jer_antes), "jericho_despues": RS._b(jer_despues)}))
    for x in rec[:n]:                                                             # SQ2
        otras = [y for y in cands if y["par"] != x["par"]]
        y = rng.choice(otras)
        turnos = sorted(y["s_turno"])
        u = rng.choice(turnos[:-1]) if len(turnos) > 1 else turnos[0]
        with x["camp"]._conn() as c:
            x["camp"]._tx(c)
            ajena = _ventana_ajena(c, x["q"], y["campaign_id"], u)
        t = x["ev"]["turno"]
        reemplazo = {t + (v - u): s for v, s in ajena.items()}
        despues = C.evaluar_evento(x["s_turno"], x["ev"], reemplazo)
        filas.append(_fila("SQ2", x, despues, {"ventana_ajena": f"Par{y['par']} {y['brazo']} t{u}"}))
    for x in todos[:n]:                                                           # SC1
        oracion = rng.choice(NEUTRAS)
        despues, sim = _insercion(x, oracion, embedder)
        filas.append(_fila("SC1", x, despues, {"oracion": oracion, "sim_oracion": sim}))
    for x in todos[n:2 * n] or todos[:n]:                                         # SC2 (otra muestra si alcanza)
        ev = x["ev"]
        oracion = NOMBRE_SIN_CAMBIO[ev["campo"].split(".")[0]].format(n=ev["entidad"])
        despues, sim = _insercion(x, oracion, embedder)
        filas.append(_fila("SC2", x, despues, {"oracion": oracion, "sim_oracion": sim}))
    return filas


def resumir(filas, semilla):
    res = {}
    for clave, esperado in EXPECTATIVAS.items():
        pid = clave.split("|")[0]
        sub = [f for f in filas if f["perturbacion"] == pid]
        diffs = [f["margen_despues"] - f["margen_antes"] for f in sub]
        b = sum(1 for f in sub if f["reconocido_antes"] and not f["reconocido_despues"])
        c = sum(1 for f in sub if not f["reconocido_antes"] and f["reconocido_despues"])
        lo, hi = est.ic_bootstrap_mediana(diffs, semilla=semilla) if diffs else (float("nan"), float("nan"))
        res[pid] = {"clave": clave, "esperado": esperado, "n": len(sub), "delta": est.delta_pareado(diffs),
                    "p": est.prueba_signos(diffs) if diffs else 1.0, "mediana": float(np.median(diffs)) if diffs else float("nan"),
                    "ic": (lo, hi), "se_apagan": b, "se_encienden": c}
    for familia in (CONFIRMATORIAS, CONTROLES):
        aj = est.holm([res[p]["p"] for p in familia])
        for p, pa in zip(familia, aj):
            r = res[p]
            r["p_holm"] = pa
            r["observado"] = est.direccion_numerica(pa, r["delta"])
            r["veredicto"] = est.veredicto(r["esperado"], r["observado"], r["n"])
    return res


def escribir(filas, res, semilla, n):
    C.SALIDA_DOCS.mkdir(parents=True, exist_ok=True)
    base = C.SALIDA_DOCS / "sensibilidad_semantico"
    campos = list(dict.fromkeys(k for f in filas for k in f))
    with open(base.with_suffix(".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    base.with_suffix(".json").write_text(json.dumps({"sha256_expectativas": HASH, "expectativas": EXPECTATIVAS,
                                                     "semilla": semilla, "n_por_perturbacion": n, "resultados": res},
                                                    indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    sq1 = [f for f in filas if f["perturbacion"] == "SQ1"]
    jer_cambia = sum(1 for f in sq1 if f.get("jericho_antes") != f.get("jericho_despues"))
    L = ["# Prueba A2 de CL-2 recall semántico", "",
         f"SHA-256 de las expectativas (fijadas antes de correr): `{HASH}`  ·  semilla {semilla}  ·  n por perturbación {n}", "",
         "| Perturbación | Esperado | n | Mdn Δ margen [IC 95 %] | δ Cliff pareado | p signos | p Holm | Observado | Veredicto | 0→1 | 1→0 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for pid in CONFIRMATORIAS + CONTROLES:
        r = res[pid]
        L.append(f"| {pid} {r['clave'].split('|')[1].replace('_', ' ')} | {r['esperado']} | {r['n']} | {r['mediana']:+.4f} [{r['ic'][0]:+.4f}, {r['ic'][1]:+.4f}] | "
                 f"{r['delta']:+.2f} | {r['p']:.4g} | {r['p_holm']:.4g} | {r['observado']} | **{r['veredicto']}** | {r['se_encienden']} | {r['se_apagan']} |")
    veredictos = [res[p]["veredicto"] for p in CONFIRMATORIAS + CONTROLES]
    ok = all(v == "responde" for v in veredictos)
    insuficiente = any(v == "no aplica" for v in veredictos)
    L += ["", f"Jericho-QA con la misma paráfrasis de SQ1: cambia su veredicto en {jer_cambia} de {len(sq1)} eventos "
          "(por construcción la paráfrasis no contiene sus lexemas).", "",
          "**Lectura:** " + ("las cuatro perturbaciones responden como se esperaba: el instrumento distingue el cambio de estado "
                             "parafraseado, cae ante texto ajeno y no reacciona a texto neutro ni al nombre solo." if ok else
                             f"muestra insuficiente (menos de {est.N_MIN} eventos en alguna perturbación): no hay veredicto." if insuficiente else
                             "al menos una perturbación no respondió como se esperaba (ver tabla): el instrumento no es informativo "
                             "en ese aspecto y se reporta como tal."),
          "", "Clasificación en esta tesis: EXPLORATORIO en cualquier caso (la clasificación de instrumentos se fijó antes del "
          "contraste de hipótesis). El resultado de esta prueba orienta la recomendación para un estudio futuro."]
    base.with_suffix(".md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None, embedder=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--semilla", type=int, default=20261008)
    ap.add_argument("--pares", help="solo para pruebas; la A2 real usa las 27")
    ap.add_argument("--dispositivo", default="cpu")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _assert_sin_lexema()
    print(f"SHA-256 de las expectativas (fijadas antes de correr): {HASH}", flush=True)
    if embedder is None:
        rev = C.revision_fijada()
        if rev is None:
            sys.exit("No hay manifiesto de embeddings: corre antes scripts/semantico/embeber_corpus.py")
        embedder = C.Embedder(revision=rev, dispositivo=a.dispositivo)
    pares = _pares.todos()
    if a.pares:
        pedidos = {p.strip().zfill(2) for p in a.pares.split(",")}
        pares = [p for p in pares if p["par"] in pedidos]
    cands = candidatos(pares, embedder)
    filas = correr(cands, a.n, a.semilla, embedder)
    res = resumir(filas, a.semilla)
    escribir(filas, res, a.semilla, a.n)
    for pid in CONFIRMATORIAS + CONTROLES:
        r = res[pid]
        print(f"{r['clave']}: esperado {r['esperado']}, observado {r['observado']} -> {r['veredicto']} (n={r['n']})")
    print(f"Informe: {C.SALIDA_DOCS / 'sensibilidad_semantico.md'}")
    return filas, res


if __name__ == "__main__":
    main()
