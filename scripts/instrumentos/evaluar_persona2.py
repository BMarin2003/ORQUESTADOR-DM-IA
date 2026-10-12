#!/usr/bin/env python3
"""
evaluar_persona2.py -- evalúa persona2.py sobre transcripciones reales (SOLO SELECT).

PROCEDENCIA / CONGELAMIENTO (leer antes de tocar nada)
  Los turnos usados para construir léxicos, ajustar reglas y depurar el detector (los 810 de la muestra
  de exploración semilla 777, los 600 de evaluación y los 4 800 de reserva, más 3 turnos de sondeo manual)
  están listados en validacion/persona2_desarrollo_turnos.csv (scripts/instrumentos/procedencia_persona2.py).
  validacion/auditoria_persona2_*.csv es la muestra de DESARROLLO (construida con la versión 1 del
  detector): NO se regenera ni se edita (este script se niega a sobrescribirla).
  A PARTIR DE LA ITERACIÓN «regla de declarada v2» EL DETECTOR QUEDA CONGELADO: la auditoría de
  confirmación (scripts/instrumentos/confirmacion_persona2.py, semilla 20260921) usa solo turnos que
  NO están en persona2_desarrollo_turnos.csv, y no se ajusta nada después de mirarla.

(a) Muestra reproducible (semilla 20260920): 12 de los 21 pares de docs/ids_par07-17.json y
    docs/ids_par18-27.json; por par, 25 turnos (mismos turn_id en G1 y G2) -> 300 turnos por brazo.
(b) Métricas (IC 95 % de Wilson, % de turnos con >=1 hallazgo):
      PRIMARIA   = usurpación mental/verbal (VOLICION + COGNICION + EMOCION + HABLA): la regla de oro de
                   dm/prompt_g2.md (nunca describas pensamientos, emociones, diálogo ni decisiones del PJ).
      SECUNDARIA = ACCION_NO_DECLARADA, EXPERIMENTAL: depende de la equivalencia «declarada» (verbo,
                   sinónimo, contenido compartido, parte del cuerpo/movimiento genéricos), que es difícil.
    Se muestra ANTES (regla de declarada v1: solo verbo/sinónimo; persona2.CONFIG_V1) y DESPUÉS (v2).
(c) Comparación con el detector viejo (regex de 3.ª persona, orquestador/vertical_slice.py ~l.640-690).
(d) Velocidad (turnos/s).
(e) Opcional y desactivado por defecto: --escribir-auditoria-desarrollo reconstruye la muestra de desarrollo
    (solo si los CSV NO existen).

Etiquetas del etiquetado manual (columna etiqueta_manual):  USURPA | NO_USURPA | AMBIGUO
  - fila con categoria_detectada: ¿la frase marcada (⟦disparador⟧) narra acción/diálogo/pensamiento/emoción
    del PJ que el jugador NO declaró en accion_jugador?  NO_USURPA = falso positivo.
  - fila sin categoria_detectada (turno completo): ¿hay usurpación (mental/verbal o física) en el turno?

Uso:  PYTHONUTF8=1 py scripts/instrumentos/evaluar_persona2.py
"""
import argparse
import csv
import json
import math
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ / "orquestador"))

import db  # noqa: E402
import persona2 as P  # noqa: E402
import psycopg  # noqa: E402
import spacy  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402
from validacion_generar import prosa  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PRIMARIAS = ["VOLICION", "COGNICION", "EMOCION", "HABLA"]
SECUNDARIA = "ACCION_NO_DECLARADA"
CATS = PRIMARIAS + [SECUNDARIA]
MENTALES = {"EMOCION", "COGNICION", "VOLICION", "MENTAL"}
N_PARES = 12
TURNOS_POR_PAR = 25          # x 12 pares = 300 por brazo
RESERVA_POR_PAR = 200


# ═════════════════════ datos ═════════════════════

def cargar_pares():
    """Lee los 21 pares G1/G2 de los dos lotes de ids en docs/, ordenados por número de par."""
    pares = []
    for f in ("docs/ids_par07-17.json", "docs/ids_par18-27.json"):
        for e in json.loads((RAIZ / f).read_text(encoding="utf-8")):
            pares.append({"par": e["par"], "lugar": e.get("lugar"), "campaign_g1": e["campaign_g1"],
                          "campaign_g2": e["campaign_g2"], "lote": f.split("/")[-1]})
    pares.sort(key=lambda e: e["par"])
    return pares


def cargar_nombres():
    """Mapa id de personaje -> nombre del PJ jugador, para detectar su nombre en la narración."""
    d = json.loads((RAIZ / "jugador/personajes_jugadores.json").read_text(encoding="utf-8"))
    return {p["id"]: p["nombre"] for p in d["personajes"]}


def jugador(buf):
    """Texto de la acción del jugador a partir del player_buffer (une los fragmentos)."""
    return "\n".join((x.get("text", "") if isinstance(x, dict) else str(x)) for x in (buf or [])).strip()


def registro(brazo, e, cid, turn_id, f, nombres):
    """Registro de un turno-brazo: PJ, acción del jugador y narración del DM reducida a prosa."""
    buf = f["player_buffer"] or []
    pj = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
    return {"brazo": brazo, "par": e["par"], "lote": e["lote"], "campaign_id": cid, "turn_id": turn_id,
            "pj": pj, "nombre": nombres.get(pj), "accion": jugador(buf), "dm": prosa(f["dm_output"], brazo)}


def turno_valido(f):
    """Turno utilizable: narración de >= 20 caracteres y acción del jugador no vacía."""
    return len((f["dm_output"] or "").strip()) >= 20 and bool(jugador(f["player_buffer"]))


def muestrear(conn, seed, n_por_par, reserva_por_par, nombres):
    """SOLO SELECT. Devuelve (eval, reserva, pares_elegidos): registros por (par, turno, brazo)."""
    rnd = random.Random(seed)
    pares = cargar_pares()
    elegidos = rnd.sample(pares, N_PARES)
    elegidos.sort(key=lambda e: e["par"])
    ev, rs = [], []
    for e in elegidos:
        rt = random.Random(f"{seed}-par{e['par']}")
        cand = rt.sample(range(1, 1401), 560)
        por_brazo = {}
        for brazo, cid in (("G1", e["campaign_g1"]), ("G2", e["campaign_g2"])):
            filas = conn.execute(
                "SELECT turn_id, player_buffer, dm_output FROM turn_log "
                "WHERE campaign_id=%s AND turn_id = ANY(%s)", (cid, cand)).fetchall()
            por_brazo[brazo] = {f["turn_id"]: f for f in filas}
        validos = []
        for t in cand:
            f1, f2 = por_brazo["G1"].get(t), por_brazo["G2"].get(t)
            if f1 and f2 and turno_valido(f1) and turno_valido(f2):
                validos.append(t)
        for i, t in enumerate(validos[:n_por_par + reserva_por_par]):
            destino = ev if i < n_por_par else rs
            for brazo, cid in (("G1", e["campaign_g1"]), ("G2", e["campaign_g2"])):
                destino.append(registro(brazo, e, cid, t, por_brazo[brazo][t], nombres))
    return ev, rs, elegidos


# ═════════════════════ detector viejo (regex de 3.ª persona) ═════════════════════

def viejo(nombre, dm):
    """Las tres regex de orquestador/vertical_slice.py, sin la condición «not tiradas»."""
    if not nombre:
        return {"piensa": False, "accion": False, "muerte": False}
    n = re.escape(nombre)
    return {
        "piensa": bool(re.search(rf"\b{n}\s+(piensa|siente|decide|comprende)", dm, re.I)),
        "accion": bool(re.search(rf"\b{n}\s+(ataca|golpea|convence|esquiva|salta|derriba|desarma)\b", dm, re.I)),
        "muerte": bool(re.search(rf"\b{n}\s+(muere|cae muerto|fallece|pierde la vida)\b", dm, re.I)),
    }


# ═════════════════════ utilidades ═════════════════════

def wilson(k, n, z=1.96):
    """Intervalo de Wilson al 95 % (en %) para k aciertos de n; (0, 0) si n es 0."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def celda(k, n):
    """Texto de tabla: conteo, porcentaje e IC de Wilson."""
    lo, hi = wilson(k, n)
    return f"{k:3d} ({100*k/max(n,1):5.1f}%) [{lo:4.1f}-{hi:4.1f}]"


class CacheNlp:
    """envuelve nlp para reutilizar el Doc (el detector lo llama una vez por texto)."""
    def __init__(self, nlp):
        """Envuelve `nlp` con un caché de Docs por texto."""
        self.nlp, self.docs = nlp, {}

    def __call__(self, texto):
        """Devuelve el Doc del texto, procesándolo con spaCy solo la primera vez."""
        if texto not in self.docs:
            self.docs[texto] = self.nlp(texto)
        return self.docs[texto]


def analizar(recs, nlp, config=None, sufijo=""):
    """guarda r['hall'+sufijo], r['excl'+sufijo] (y la muerte solo en la versión por defecto)."""
    for r in recs:
        hall, excl = P.analizar_completo(r["dm"], r["accion"], nlp, r["nombre"], config)
        r["hall" + sufijo], r["excl" + sufijo] = hall, excl
        if not sufijo:
            r["muerte"] = P.narra_muerte_pj(r["dm"], nlp, r["nombre"])
            r["muerte_sin_nombre"] = P.narra_muerte_pj(r["dm"], nlp)


def turnos_con(rs, cats, clave="hall", estricto=False):
    """Nº de turnos con >= 1 hallazgo de las categorías `cats`; con `estricto` ignora los hallazgos con eco declarado."""
    def ok(h):
        """Hallazgo contable: de la categoría pedida y, si `estricto`, no declarado."""
        return h["categoria"] in cats and (not estricto or not h["declarada"])
    return sum(1 for r in rs if any(ok(h) for h in r[clave]))


# ═════════════════════ informe ═════════════════════

def informe(ev):
    """Imprime las métricas primaria y secundaria (antes v1 / después v2 de la regla de declarada), la comparación con el detector viejo y exclusiones, con IC de Wilson."""
    por = {b: [r for r in ev if r["brazo"] == b] for b in ("G1", "G2")}
    print("\n" + "=" * 92)
    print("(b1) MÉTRICA PRIMARIA: usurpación mental/verbal (VOLICION+COGNICION+EMOCION+HABLA)")
    print("     % de turnos con >=1 hallazgo, [IC 95 % Wilson]. La regla de declarada v2 NO cambia estas cifras.")
    print("=" * 92)
    print(f"  n turnos: G1={len(por['G1'])}  G2={len(por['G2'])}   pares: {sorted({r['par'] for r in ev})}")
    print(f"  {'':34s}{'G1 antes(v1)':26s}{'G1 después(v2)':26s}{'G2 antes(v1)':26s}{'G2 después(v2)':26s}")
    filas = [(c, {c}, False) for c in PRIMARIAS]
    filas += [("PRIMARIA (cualquiera de las 4)", set(PRIMARIAS), False),
              ("PRIMARIA sin eco declarado", set(PRIMARIAS), True)]
    for nombre, cats, estricto in filas:
        celdas = []
        for b in ("G1", "G2"):
            n = len(por[b])
            celdas.append(celda(turnos_con(por[b], cats, "hall_v1", estricto), n))
            celdas.append(celda(turnos_con(por[b], cats, "hall", estricto), n))
        print(f"  {nombre:34s}" + "".join(f"{c:26s}" for c in celdas))
    n_h = {b: sum(1 for r in por[b] for h in r["hall"] if h["categoria"] in PRIMARIAS) for b in por}
    print(f"  hallazgos primarios: G1={n_h['G1']}  G2={n_h['G2']}")
    print("  (tirada_declarada es True en el %.1f %% de los turnos: los jugadores casi siempre llevan tag {Habilidad}.)"
          % (100 * sum(1 for r in ev if "{" in r["accion"]) / len(ev)))

    print("\n" + "=" * 92)
    print("(b2) MÉTRICA SECUNDARIA EXPERIMENTAL: ACCION_NO_DECLARADA")
    print("=" * 92)
    print(f"  {'':34s}{'G1 antes(v1)':26s}{'G1 después(v2)':26s}{'G2 antes(v1)':26s}{'G2 después(v2)':26s}")
    celdas = []
    for b in ("G1", "G2"):
        n = len(por[b])
        celdas.append(celda(turnos_con(por[b], {SECUNDARIA}, "hall_v1"), n))
        celdas.append(celda(turnos_con(por[b], {SECUNDARIA}, "hall"), n))
    print(f"  {'ACCION_NO_DECLARADA':34s}" + "".join(f"{c:26s}" for c in celdas))
    for b in ("G1", "G2"):
        a = sum(1 for r in por[b] for h in r["hall_v1"] if h["categoria"] == SECUNDARIA)
        d = sum(1 for r in por[b] for h in r["hall"] if h["categoria"] == SECUNDARIA)
        vias = Counter(e.get("via") for r in por[b] for e in r["excl"]
                       if e["motivo"] == "declarada")
        vias1 = Counter(e.get("via") for r in por[b] for e in r["excl_v1"] if e["motivo"] == "declarada")
        print(f"   {b}: hallazgos ACCION antes={a}  después={d}  (quitados por la regla v2: {a-d});"
              f" candidatos declarados por vía  v1={dict(vias1)}  v2={dict(vias)}")

    print("\n  Verbos más frecuentes (v2, ambos brazos):")
    for cat in CATS:
        c = Counter(h["verbo_lema"] for r in ev for h in r["hall"] if h["categoria"] == cat)
        print(f"   {cat:20s} " + (", ".join(f"{l}:{n}" for l, n in c.most_common(7)) or "-"))

    print("\n  Persona 3 (control positivo con el nombre del PJ), hallazgos v2:")
    for b in ("G1", "G2"):
        h3 = [h for r in por[b] for h in r["hall"] if h["persona"] == "3"]
        h_all = [h for r in por[b] for h in r["hall"]]
        print(f"   {b}: persona 3 = {len(h3)} de {len(h_all)} hallazgos "
              f"({', '.join(h['categoria'] + ':' + h['verbo_lema'] for h in h3) or '-'})")

    print("\n  Exclusiones registradas (v2, verbos descartados por motivo):")
    for b in ("G1", "G2"):
        c = Counter(e["motivo"] for r in por[b] for e in r["excl"])
        print(f"   {b}: " + ", ".join(f"{k}={v}" for k, v in c.most_common()))

    print("\n  Muerte del PJ (narra_muerte_pj):")
    for b in ("G1", "G2"):
        print(f"   {b}: con nombre_pj = {sum(1 for r in por[b] if r['muerte'])}; "
              f"sin nombre_pj = {sum(1 for r in por[b] if r['muerte_sin_nombre'])}")

    print("\n" + "=" * 92)
    print("(c) DETECTOR VIEJO (regex 3.ª persona + nombre del PJ) vs NUEVO, mismos turnos")
    print("=" * 92)
    for b in ("G1", "G2"):
        rs = por[b]
        v = [viejo(r["nombre"], r["dm"]) for r in rs]
        nombra = sum(1 for r in rs if r["nombre"] and re.search(rf"\b{re.escape(r['nombre'])}\b", r["dm"], re.I))
        viejo_any = sum(1 for x in v if x["piensa"] or x["accion"])
        n3 = sum(1 for r in rs if any(h["persona"] == "3" for h in r["hall"]))
        print(f"  {b}: turnos={len(rs)} nombra al PJ={nombra} ({100*nombra/len(rs):.1f}%)  "
              f"viejo: piensa={sum(x['piensa'] for x in v)} accion={sum(x['accion'] for x in v)} "
              f"muerte={sum(x['muerte'] for x in v)} -> turnos marcados={viejo_any}  |  nuevo: persona 3={n3} turnos, "
              f"primaria={turnos_con(rs, set(PRIMARIAS))}, secundaria={turnos_con(rs, {SECUNDARIA})}")


# ═════════════════════ velocidad ═════════════════════

def velocidad(ev, nlp_completo, nlp_reducido):
    """Mide turnos/s del detector sin spaCy, con spaCy reducido y con pipeline completo; comprueba que reducido y completo dan la misma salida."""
    textos = [(r["dm"], r["accion"], r["nombre"]) for r in ev]
    palabras = sum(len(t[0].split()) for t in textos)
    print("\n" + "=" * 92)
    print("(d) VELOCIDAD  (%d turnos, %d palabras)" % (len(textos), palabras))
    print("=" * 92)
    res = {}
    for nombre, nlp in (("sin spaCy (nlp=None, solo léxico)", None),
                        ("spaCy es_core_news_sm SIN parser/ner", nlp_reducido),
                        ("spaCy es_core_news_sm pipeline completo", nlp_completo)):
        t0 = time.perf_counter()
        out = [P.detectar_usurpacion(d, a, nlp, n) for d, a, n in textos]
        dt = time.perf_counter() - t0
        res[nombre] = out
        print(f"  {nombre:42s} {dt:7.2f} s  -> {len(textos)/dt:7.1f} turnos/s  ({palabras/dt:8.0f} palabras/s)")
    a, b, c = (res["spaCy es_core_news_sm SIN parser/ner"], res["spaCy es_core_news_sm pipeline completo"],
               res["sin spaCy (nlp=None, solo léxico)"])
    print(f"  salida idéntica reducido vs completo: {a == b};  turnos donde nlp=None difiere del reducido: "
          f"{sum(1 for x, y in zip(a, c) if x != y)}")


# ═════════════════════ (opcional) auditoría de desarrollo ═════════════════════

def marcar(evid, dm, ini, fin):
    """Marca con ⟦ ⟧ el disparador dentro de la frase de evidencia; devuelve la frase intacta si no se localiza."""
    idx = dm.find(evid)
    if idx < 0 or not (idx <= ini < idx + len(evid)):
        return evid
    a, b = ini - idx, fin - idx
    return evid[:a] + "⟦" + evid[a:b] + "⟧" + evid[b:]


def construir_auditoria(pool, seed, n_con=100, n_sin=100):
    """Construye la muestra de DESARROLLO (v1 del detector): cuota equilibrada por categoría entre turnos con hallazgo más turnos sin hallazgo con verbo mental descartado."""
    rnd = random.Random(seed + 1)

    def cats_turno(r):
        """Categorías de hallazgo del turno (incluye MUERTE_PJ)."""
        s = {h["categoria"] for h in r["hall"]}
        if r["muerte"]:
            s.add("MUERTE_PJ")
        return s
    con = [r for r in pool if cats_turno(r)]
    freq = Counter(c for r in con for c in cats_turno(r))
    asignado = defaultdict(list)
    for r in con:
        c = min(cats_turno(r), key=lambda x: (freq[x], x))
        asignado[c].append(r)
    cats = sorted(asignado)
    cuota = {c: 0 for c in cats}
    restante = n_con
    while restante > 0 and any(cuota[c] < len(asignado[c]) for c in cats):
        for c in cats:
            if restante > 0 and cuota[c] < len(asignado[c]):
                cuota[c] += 1
                restante -= 1
    filas = []
    for c in cats:
        for r in rnd.sample(sorted(asignado[c], key=lambda r: (r["campaign_id"], r["turn_id"])), cuota[c]):
            if c == "MUERTE_PJ":
                m = r["muerte"]
                cand = (m["evidencia"], m["inicio"], m["fin"])
            else:
                h = sorted((h for h in r["hall"] if h["categoria"] == c),
                           key=lambda h: (h["confianza"] != "alta", h["inicio"]))[0]
                cand = (h["evidencia"], h["inicio"], h["fin"])
            filas.append({"rec": r, "estrato": "con_hallazgo", "cat": c, "texto": marcar(cand[0], r["dm"], cand[1], cand[2])})
    sin = sorted([r for r in pool if not r["hall"] and not r["muerte"]
                  and any(e["categoria_potencial"] in MENTALES for e in r["excl"])],
                 key=lambda r: (r["campaign_id"], r["turn_id"]))
    for r in rnd.sample(sin, min(n_sin, len(sin))):
        filas.append({"rec": r, "estrato": "sin_hallazgo", "cat": "", "texto": r["dm"]})
    rnd.shuffle(filas)
    for f, i in zip(filas, rnd.sample(range(100000, 1000000), len(filas))):
        f["id"] = f"M{i}"
    return filas


def escribir_csv_ciego(filas, ruta_muestra, ruta_clave):
    """Escribe la muestra ciega (sin categoría real ni procedencia) y su clave en dos CSV."""
    with open(ruta_muestra, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["id_muestra", "frase_evidencia_o_turno_completo", "accion_jugador",
                    "categoria_detectada", "etiqueta_manual", "nota"])
        for f in filas:
            w.writerow([f["id"], f["texto"], f["rec"]["accion"], f["cat"], "", ""])
    with open(ruta_clave, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["id_muestra", "campaign_id", "turn_id", "brazo", "estrato"])
        for f in sorted(filas, key=lambda f: f["id"]):
            w.writerow([f["id"], f["rec"]["campaign_id"], f["rec"]["turn_id"], f["rec"]["brazo"], f["estrato"]])


def main():
    """CLI de la evaluación sobre transcripciones reales (solo SELECT); se niega a sobrescribir la auditoría de desarrollo congelada."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260920)
    ap.add_argument("--n-por-par", type=int, default=TURNOS_POR_PAR)
    ap.add_argument("--escribir-auditoria-desarrollo", action="store_true",
                    help="reconstruye validacion/auditoria_persona2_*.csv (solo si NO existen; están congelados)")
    args = ap.parse_args()

    dir_val = RAIZ / "validacion"
    rutas = (dir_val / "auditoria_persona2_muestra.csv", dir_val / "auditoria_persona2_clave.csv")
    if args.escribir_auditoria_desarrollo and any(r.exists() for r in rutas):
        sys.exit("ERROR: validacion/auditoria_persona2_*.csv ya existen y están CONGELADOS (muestra de desarrollo v1). "
                 "No se sobrescriben.")

    nombres = cargar_nombres()
    reserva = RESERVA_POR_PAR if args.escribir_auditoria_desarrollo else 0
    with psycopg.connect(db.DSN, row_factory=dict_row) as conn:      # SOLO SELECT
        ev, rs, elegidos = muestrear(conn, args.seed, args.n_por_par, reserva, nombres)
    print(f"Muestra: {len(elegidos)} pares {[e['par'] for e in elegidos]} "
          f"(lote1={sum(1 for e in elegidos if '07-17' in e['lote'])}, lote2={sum(1 for e in elegidos if '18-27' in e['lote'])}); "
          f"eval={len(ev)} registros (={len(ev)//2} por brazo)")

    nlp_full = spacy.load("es_core_news_sm")
    nlp_red = spacy.load("es_core_news_sm", exclude=["ner", "parser"])
    cache = CacheNlp(nlp_red)
    analizar(ev, cache, P.CONFIG_V1, "_v1")     # ANTES: declarada v1 (solo verbo/sinónimo)
    analizar(ev, cache)                          # DESPUÉS: declarada v2 (defecto)
    informe(ev)
    velocidad(ev, nlp_full, nlp_red)

    if args.escribir_auditoria_desarrollo:
        analizar(rs, cache)
        filas = construir_auditoria(ev + rs, args.seed)
        escribir_csv_ciego(filas, *rutas)
        print(f"\nauditoría de desarrollo escrita: {len(filas)} filas")


if __name__ == "__main__":
    main()
