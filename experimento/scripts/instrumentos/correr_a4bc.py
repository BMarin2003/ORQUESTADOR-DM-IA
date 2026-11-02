"""
Corredor de A4b/c: enchufa respuesta_accion.py y anclaje_escenario.py al arnés de sensibilidad
(experimento/scripts/sensibilidad, sin editarlo), corre las perturbaciones de la matriz pre-especificada
(matriz_a4bc.py) y escribe el informe esperado-vs-observado. Solo SELECT; sin LLM.

  PYTHONUTF8=1 py experimento/scripts/instrumentos/correr_a4bc.py --precalentar    # llena la caché de lemas (~15 min)
  PYTHONUTF8=1 py experimento/scripts/instrumentos/correr_a4bc.py --desarrollo     # pares de DESARROLLO (calibra min)
  PYTHONUTF8=1 py experimento/scripts/instrumentos/correr_a4bc.py                  # EVALUACIÓN (muestra del arnés)

Evaluación = datos.plan_muestra(semilla 20260920): 150 turnos por brazo + 60 ventanas de 8; pares
09, 11, 13, 14, 16, 20, 21, 23, 24, 25. Desarrollo = los otros 11 pares (semilla 20260919).
Documento de diseño: docs/research/a4bc_diseno_instrumentos.md.
"""
import argparse
import csv
import hashlib
import json
import platform
import random
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
for _p in (AQUI, RAIZ / "experimento" / "scripts" / "sensibilidad"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import anclaje_escenario as ae     # noqa: E402
import contexto_a4bc as cx         # noqa: E402
import correr_sensibilidad as cs   # noqa: E402
import datos                       # noqa: E402
import estadistica as es           # noqa: E402
import instrumentos_texto as it    # noqa: E402
import lemas_es as le              # noqa: E402
import matriz_a4bc_v2 as mx        # noqa: E402  (a4bc-2: solo cambian 5 magnitudes mínimas; ver doc §9)
import perturbaciones as pt        # noqa: E402
import perturbaciones_a4bc as pa   # noqa: E402
import respuesta_accion as ra      # noqa: E402

SEM_EVAL, SEM_DEV = 20260920, 20260919
DEV_PARES = ("07", "08", "10", "12", "15", "17", "18", "19", "22", "26", "27")
INSTR_TURNO = ["cr2a_z", "cr2a_crudo", "cr2b_cos_turno", "cr2b_cos_turno_sn"]
INSTR_VENT = ["cr2a_z_ventana8", "cr2b_cos_ventana8", "cr2b_cos_ventana8_sn"]
PERT_TURNO = ["X1_misma_campana_lejana", "X2_misma_campana_cercana", "P8", "P5", "P6", "C1_reorden_oraciones",
              "C2_minusculas", "C3_sin_tildes", "P11a_inyeccion", "P11b_eliminacion", "S1_sinonimos"]
PERT_VENT = ["P9", "W1_ventana_otro_par"]
CELDAS_CALIBRADAS = {(i, p) for i in ("cr2a_z", "cr2a_crudo")
                     for p in ("X1_misma_campana_lejana", "X2_misma_campana_cercana", "P8")} | {
    ("cr2b_cos_turno", "P8"), ("cr2b_cos_turno_sn", "P8"),
    ("cr2b_cos_ventana8", "W1_ventana_otro_par"), ("cr2b_cos_ventana8_sn", "W1_ventana_otro_par"),
    # a4bc-2: la regla se extendió a las celdas direccionales que el borrador no había medido
    ("cr2b_cos_turno", "P5"), ("cr2a_z_ventana8", "P9"), ("cr2a_z_ventana8", "W1_ventana_otro_par")}
GLIFO = {"baja": "▼", "sube": "▲", "sin_cambio": "="}
GLIFO_APR = {"aprobada": "✓", "falla": "✗", "descriptiva": "·", "no aplica": "–"}


# ================================================================== piezas puras
def hash_matriz_activa():
    """SHA-256 de la matriz pre-especificada vigente (a4bc-2), para sellarla en el informe."""
    return mx.hash_matriz(mx.MATRIZ)


def bloques(n=1400, tam=200):
    """Bloques consecutivos de `tam` turnos (inicio, fin) que cubren 1..n, para la distribución por tramos de campaña."""
    return [(i, min(i + tam - 1, n)) for i in range(1, n + 1, tam)]


def regex_nombres(nombres):
    """Proxy crudo: nombre completo o palabra capitalizada de >= 4 letras de un nombre propio del escenario
    (sensible a mayúsculas)."""
    alts = set()
    for n in nombres:
        alts.add(n)
        for w in re.findall(r"[^\W\d_]+", n):
            if w[0].isupper() and len(w) >= 4:
                alts.add(w)
    return re.compile(r"(?<!\w)(?:" + "|".join(sorted(map(re.escape, alts), key=len, reverse=True)) + r")(?!\w)")


def menciona_nombre(texto, rx):
    """True si el texto (ya limpiado) contiene algún nombre propio del escenario según el proxy `rx`."""
    return bool(rx.search(le.limpiar(texto)))


def aprobacion(cel, fila, todas_cero):
    """Criterio de aprobación de una celda fijado de antemano: veredicto del arnés «responde» y, si hay dirección, |mediana| >= min; las celdas exactas exigen diferencia 0 en todos los pares; sin n suficiente no aplica."""
    if cel["descriptivo"]:
        return "descriptiva"
    if fila["n"] < es.N_MIN:
        return "no aplica"
    if cel["exacto"]:
        return "aprobada" if todas_cero else "falla"
    if cel["dir"] == "sin_cambio":
        return "aprobada" if fila["veredicto"] == "responde" else "falla"
    signo = -1 if cel["dir"] == "baja" else 1
    ok = fila["veredicto"] == "responde" and signo * fila["mediana_dif"] >= cel["min"]
    return "aprobada" if ok else "falla"


TOL_REL = 0.02   # lectura POST HOC (no cambia el criterio): un «cambio inesperado» de < 2 % de la mediana previa se etiqueta despreciable


def rel_dif(mediana_antes, mediana_dif):
    """Diferencia mediana relativa a |mediana previa|; None si la mediana previa es nula o NaN."""
    if mediana_antes is None or mediana_antes != mediana_antes or mediana_antes == 0:
        return None
    return mediana_dif / abs(mediana_antes)


def despreciable(rel):
    """Lectura post hoc (no altera el criterio): True si el cambio relativo es menor que TOL_REL."""
    return rel is not None and abs(rel) < TOL_REL


def min_cumple_regla(cel, mediana_dev):
    """Regla de calibración (doc §5): min <= 0,5 x |mediana del efecto en desarrollo| y mismo signo."""
    if cel["dir"] == "sin_cambio" or cel["descriptivo"]:
        return None
    signo = -1 if cel["dir"] == "baja" else 1
    return signo * mediana_dev > 0 and cel["min"] <= 0.5 * abs(mediana_dev)


# ================================================================== datos
class Camp:
    """Datos cargados de una campaña: textos, acciones, tokens de respuesta, pool de acciones y conteo de clases de acción."""
    def __init__(self, cid, brazo, par):
        """Inicializa la campaña con contenedores vacíos que `cargar_campanas` rellena."""
        self.cid, self.brazo, self.par = str(cid), brazo, par
        self.textos, self.acciones, self.tokR, self.pool, self.clases = {}, {}, {}, None, Counter()


def cargar_campanas(conn, pares, log):
    """Carga (solo SELECT) las campañas G1/G2 de los pares: textos, acciones, tokens con caché de lemas y pool de acciones; devuelve (camps, lores del turno 0)."""
    camps, lores = {}, {}
    t0 = time.perf_counter()
    for p in pares:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            cid = p[k]
            rs = conn.execute("SELECT turn_id, player_buffer, dm_output FROM turn_log WHERE campaign_id=%s "
                              "ORDER BY turn_id", (cid,)).fetchall()
            c = Camp(cid, brazo, p["par"])
            ts = [r["turn_id"] for r in rs if r["turn_id"] >= 1]
            por_t = {r["turn_id"]: r for r in rs}
            lores[(p["par"], brazo)] = (por_t.get(0) or {}).get("dm_output") or ""
            c.textos = {t: por_t[t]["dm_output"] or "" for t in ts}
            c.acciones = {t: por_t[t]["player_buffer"] for t in ts}
            toks = le.tokens_lote_cacheado(f"R_{cid}", [c.textos[t] for t in ts])
            c.tokR = dict(zip(ts, toks))
            clases = {t: ra.clasificar_accion(c.acciones[t]) for t in ts}
            tokA = le.tokens_lote_cacheado(
                f"A_{cid}", [ra.texto_accion(c.acciones[t]) if clases[t] != "solo_tag" else "" for t in ts])
            c.clases = Counter(clases.values())
            c.pool = ra.PoolAcciones(cid, {t: le.filtrar(tk) for t, tk in zip(ts, tokA)}, clases)
            camps[cid] = c
        log(f"  par {p['par']}: campañas cargadas ({time.perf_counter() - t0:.0f}s)")
    return camps, lores


def construir_escenarios(pares, lores, log):
    """Construye el Escenario de cada par con el lore de G1; avisa si el lore difiere entre brazos."""
    esc, difieren = {}, []
    for p in pares:
        w, per = ae.cargar_fixtures(p["par"])
        if lores[(p["par"], "G1")] != lores[(p["par"], "G2")]:
            difieren.append(p["par"])
        esc[p["par"]] = ae.Escenario.de_fixtures(p["par"], lores[(p["par"], "G1")], w, per)
    if difieren:
        log(f"  aviso: el lore (turno 0) difiere entre G1 y G2 en los pares {difieren}; se usa el de G1")
    return esc


# ================================================================== recolección de celdas
def _semilla(sem, *claves):
    """Generador aleatorio determinista derivado de la semilla y de las claves de la unidad perturbada."""
    return random.Random(f"{sem}|" + "|".join(map(str, claves)))


def recolectar(plan, camps, esc, modelo, sem, log):
    """Aplica cada perturbación de la matriz a los turnos y ventanas del plan y reúne los pares (antes, después) por (brazo, perturbación, instrumento); devuelve (celdas, elegibles, extras)."""
    celdas, elegibles, tiempos = {}, {}, {}
    extras = {}

    def anadir(brazo, pid, instr, a, d):
        """Acumula un par (antes, después) en la celda (brazo, perturbación, instrumento)."""
        c = celdas.setdefault((brazo, pid, instr), {"tipo": "num", "antes": [], "despues": []})
        c["antes"].append(a)
        c["despues"].append(d)

    for brazo in ("G1", "G2"):
        items = [t for t in plan["turnos"] if t["brazo"] == brazo]
        base = []
        for t in items:
            c = camps[t["campaign_id"]]
            ctx = cx.crear(pool=c.pool, turno=t["turn"], escenario=esc[c.par], modelo=modelo, brazo=brazo)
            base.append((c, ctx, c.textos[t["turn"]], it.calcular(c.textos[t["turn"]], ctx, nombres=INSTR_TURNO)))
        for pid in PERT_TURNO:
            t0, n_el = time.perf_counter(), 0
            for (c, ctx, texto, v0), t in zip(base, items):
                if not pa.elegible(pid, texto, ctx):
                    continue
                n_el += 1
                rng = _semilla(sem, pid, c.cid, t["turn"])
                donante = None
                if pid in ("X1_misma_campana_lejana", "X2_misma_campana_cercana"):
                    dmin, dmax = (50, None) if pid.startswith("X1") else (3, 10)
                    donante = c.textos[pa.elegir_donante_misma_campana(c.textos, t["turn"], rng, dmin, dmax)]
                elif pid == "P8":
                    otros = sorted((x for x in camps.values() if x.brazo == brazo and x.par != c.par), key=lambda x: x.cid)
                    while not donante:
                        dd = rng.choice(otros)
                        donante = dd.textos.get(rng.randint(2, 1400), "").strip() or None
                r = pa.aplicar(pid, texto, ctx, rng, donante=donante)
                v1 = it.calcular(r.texto, r.ctx, nombres=INSTR_TURNO)
                for instr in INSTR_TURNO:
                    anadir(brazo, pid, instr, v0[instr], v1[instr])
                if pid == "S1_sinonimos":
                    extras.setdefault(brazo, []).append(r.info.get("n_sustituciones", 0))
            elegibles[(brazo, pid)] = n_el
            log(f"  {brazo} {pid}: {n_el} turnos elegibles ({time.perf_counter() - t0:.1f}s)")
        # ventanas
        t0 = time.perf_counter()
        vent = [v for v in plan["ventanas"] if v["brazo"] == brazo]
        for v in vent:
            c = camps[v["campaign_id"]]
            textos = [c.textos.get(v["start"] + j, "") for j in range(v["k"])]
            ctx = cx.crear(pool=c.pool, turno=v["start"], escenario=esc[c.par], modelo=modelo, brazo=brazo)
            antes = it.calcular_ventana(textos, ctx, nombres=INSTR_VENT)
            rng = _semilla(sem, "P9", c.cid, v["start"])
            d9 = it.calcular_ventana(pt.perturbar_ventana("P9", textos, rng).textos, ctx, nombres=INSTR_VENT)
            rng = _semilla(sem, "W1", c.cid, v["start"])
            otros = sorted((x for x in camps.values() if x.brazo == brazo and x.par != c.par), key=lambda x: x.cid)
            donantes = None
            while not donantes:
                dd = rng.choice(otros)
                s0 = rng.randint(2, 1393)
                cand = [dd.textos.get(s0 + j, "") for j in range(v["k"])]
                donantes = cand if all(x.strip() for x in cand) else None
            dw = it.calcular_ventana(pa.perturbar_ventana_w1(textos, donantes).textos, ctx, nombres=INSTR_VENT)
            for instr in INSTR_VENT:
                anadir(brazo, "P9", instr, antes[instr], d9[instr])
                anadir(brazo, "W1_ventana_otro_par", instr, antes[instr], dw[instr])
        tiempos[f"ventanas {brazo}"] = time.perf_counter() - t0
        log(f"  {brazo} ventanas: {len(vent)} ({tiempos[f'ventanas {brazo}']:.1f}s)")
    return celdas, elegibles, extras


def evaluar(celdas, sem):
    """Evalúa las celdas con el arnés de sensibilidad, las cruza con la matriz y añade control exacto, fracción de cambio, cambio relativo y aprobación; descarta filas sin celda en la matriz."""
    filas = cs.evaluar(celdas, mx.esperado_arnes(), sem)
    for f in filas:
        cel = mx.MATRIZ["celdas"].get(f["instrumento"], {}).get(f["perturbacion"])
        c = celdas[(f["brazo"], f["perturbacion"], f["instrumento"])]
        pares = [(a, d) for a, d in zip(c["antes"], c["despues"])]
        f["todas_cero"] = all(a == d for a, d in pares)
        con = [(a, d) for a, d in pares if a is not None and d is not None]
        f["frac_cambio"] = sum(1 for a, d in con if a != d) / len(con) if con else float("nan")
        f["cel"] = cel
        f["rel"] = rel_dif(f["mediana_antes"], f["mediana_dif"])
        f["aprobacion"] = aprobacion(cel, f, f["todas_cero"]) if cel else ""
    return [f for f in filas if f["cel"]]


# ================================================================== distribución real (paso 5)
def _spearman(x, y):
    """Correlación de Spearman por rangos; NaN si hay menos de 3 puntos o varianza nula."""
    import numpy as np
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return float("nan")
    rx, ry = x.argsort().argsort().astype(float), y.argsort().argsort().astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def _media(xs):
    """Media ignorando None; NaN si no hay valores."""
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def distribucion(camps, esc, modelo, log):
    """Descriptivo (sin veredicto): medias por bloque de 200 turnos de las métricas CR-2a/CR-2b, el proxy de nombres y la identificación del escenario, por campaña."""
    filas, clases = [], Counter()
    for c in sorted(camps.values(), key=lambda x: (x.brazo, x.par)):
        e = esc[c.par]
        rx = regex_nombres(e.nombres)
        ts = sorted(c.tokR)
        clases.update(c.clases)
        r = {t: ra.medir(c.pool, t, None, tokens_respuesta=c.tokR[t]) for t in ts}
        ct = {v: {t: ae.cos_tokens(modelo, e, [c.tokR[t]], v) for t in ts} for v in ae.VARIANTES}
        toks = [c.tokR[t] for t in ts]
        rod = {v: dict(zip(ts[ae.K_VENTANA - 1:], ae.serie_rodante(modelo, e, toks, v))) for v in ae.VARIANTES}
        prox = {t: menciona_nombre(c.textos[t], rx) for t in ts}
        for a, b in bloques(len(ts)):
            rango = [t for t in ts if a <= t <= b]
            fin = [t for t in rango if t >= a + ae.K_VENTANA - 1]
            ident = [ae.identificar(modelo, ESC_TODOS, toks[ts.index(t) - ae.K_VENTANA + 1: ts.index(t) + 1], "con")[0] == c.par
                     for t in fin[ae.K_VENTANA - 1::ae.K_VENTANA]]
            filas.append({"brazo": c.brazo, "par": c.par, "ini": a, "fin": b,
                          "n_z": sum(1 for t in rango if r[t]["z"] is not None),
                          "z": _media(r[t]["z"] for t in rango), "crudo": _media(r[t]["crudo"] for t in rango),
                          "cos_turno": _media(ct["con"][t] for t in rango), "cos_turno_sn": _media(ct["sn"][t] for t in rango),
                          "cos_v8": _media(rod["con"][t] for t in fin), "cos_v8_sn": _media(rod["sn"][t] for t in fin),
                          "prox_nombres": _media(float(prox[t]) for t in rango),
                          "top1_v8": _media(float(x) for x in ident)})
        log(f"  {c.brazo} par {c.par}: distribución calculada")
    return filas, clases


ESC_TODOS = {}


# ================================================================== informe
def _f(x, d=3):
    """Formatea un número con d decimales; «—» si es None o NaN."""
    return "—" if x is None or x != x else f"{x:.{d}f}"


def _celda_txt(f):
    """Texto de una celda de la tabla resumen: glifo esperado, aprobación, lo observado si discrepa y mediana de la diferencia."""
    cel = f["cel"]
    s = f"{GLIFO[cel['dir']]}{GLIFO_APR.get(f['aprobacion'], '')}"
    if f["veredicto"] in ("no responde", "dirección opuesta", "cambio inesperado") and f["observado"]:
        s += f"({GLIFO.get(f['observado'], '')})"
    return s + (" exacto" if cel["exacto"] else "") + f" {_f(f['mediana_dif'], 3)}"


def tabla_matriz(filas, brazo):
    """Tabla Markdown perturbación x instrumento de un brazo."""
    fb = [f for f in filas if f["brazo"] == brazo]
    instrs = [i for i in mx.MATRIZ["celdas"] if any(f["instrumento"] == i for f in fb)]
    perts = list(dict.fromkeys(f["perturbacion"] for f in fb))
    idx = {(f["perturbacion"], f["instrumento"]): f for f in fb}
    out = ["| perturbación | " + " | ".join(f"`{i}`" for i in instrs) + " |", "|---|" + "|".join("---" for _ in instrs) + "|"]
    for p in perts:
        out.append(f"| {p} | " + " | ".join(_celda_txt(idx[(p, i)]) if (p, i) in idx else "" for i in instrs) + " |")
    return "\n".join(out)


def linea_detalle(f):
    """Fila Markdown del detalle de una celda (esperado, medianas, IC, delta, p de Holm, veredicto, criterio)."""
    return (f"| {f['perturbacion']} | `{f['instrumento']}` | {GLIFO[f['cel']['dir']]} {f['cel']['dir']}"
            f"{'' if f['cel']['min'] is None else f' ≥{f['cel']['min']:g}'} | {f['n']} | {_f(f['mediana_antes'])} | "
            f"{_f(f['mediana_despues'])} | {_f(f['mediana_dif'])} [{_f(f['ic_dif'][0])}, {_f(f['ic_dif'][1])}] | "
            f"{f['delta_pareado']:+.2f} | {f['p_holm']:.3g} | {f['observado'] or '—'} | {f['veredicto'] or '—'} | "
            f"**{f['aprobacion']}** |")


CAB_DETALLE = ("| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | "
               "p Holm | observado | veredicto arnés | criterio |\n|---|---|---|---|---|---|---|---|---|---|---|---|")


def escribir_informe(ruta_md, ruta_csv, filas, meta, dist=None, clases=None):
    """Escribe el CSV de celdas y el informe Markdown esperado-vs-observado; los hallazgos que fallan se reportan sin modificar la expectativa."""
    campos = ["brazo", "perturbacion", "instrumento", "familia", "esperado", "n", "mediana_antes", "mediana_despues",
              "mediana_dif", "delta_pareado", "delta_cruzado", "p", "p_holm", "observado", "veredicto", "todas_cero",
              "frac_cambio", "aprobacion"]
    with open(ruta_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    L, ap = [], None
    L_ap = L.append
    ap = L_ap
    dev = meta["modo"] == "desarrollo"
    ap(f"# Sensibilidad A4b/c — {'CORRIDA DE DESARROLLO (calibración de min)' if dev else 'evaluación'}: respuesta a la acción (CR-2a) y anclaje al escenario (CR-2b)\n")
    ap(f"- Generado: {meta['fecha']} · commit `{meta['commit']}` · Python {platform.python_version()} · {le.version_modelo()}")
    ap(f"- Modo: **{meta['modo']}** · semilla de muestreo **{meta['semilla']}** · pares: {', '.join(p['par'] + ' (' + p['lote'] + ')' for p in meta['plan']['pares'])}")
    ap(f"- Muestra: {meta['n_por_brazo']} turnos por brazo + {meta['n_ventanas']} ventanas de 8 turnos por brazo. Solo SELECT, sin LLM.")
    ap(f"- **Matriz pre-especificada `{mx.VERSION}` ({mx.FECHA}): SHA-256 `{hash_matriz_activa()}`** (verificado por `test_matriz_a4bc_v2.py`; deriva de a4bc-1 `67e6133a…c54e` y solo cambió 5 `min` en desarrollo, doc §9.1; "
       f"ninguna dirección esperada se modificó tras ver resultados).")
    ap("- Tiempos: " + "; ".join(f"{k} {v:.0f}s" for k, v in meta["tiempos"].items()) + "\n")
    ap("## 0. Cómo leer\n")
    ap("Criterio de aprobación por celda (fijado antes; ver `docs/research/a4bc_diseno_instrumentos.md` §4): veredicto del arnés «responde» "
       "(Holm p<0,05 y |delta de Cliff pareado| ≥ 0,147 en la dirección esperada; para «=» ninguno de los dos) **y**, si hay dirección, "
       "|mediana de la diferencia pareada| ≥ `min`; celdas «exacto»: diferencia 0 en el 100 % de los pares. Glifos: ▼ baja, ▲ sube, = sin cambio; "
       "✓ aprobada, ✗ falla, · descriptiva (sin veredicto); entre paréntesis lo observado si no coincide; el número es la mediana de la diferencia "
       "pareada (después − antes).\n")
    ap("## 1. Resumen esperado-vs-observado\n")
    for brazo, nombre in (("G2", "G2 (monolítico)"), ("G1", "G1 (multiagente)")):
        ap(f"### {nombre}\n")
        ap(tabla_matriz(filas, brazo))
        ap("")
    ap("## 2. Recuento y hallazgos\n")
    ap("| brazo | instrumento | aprobadas | fallan | no aplica |\n|---|---|---|---|---|")
    for brazo in ("G2", "G1"):
        for i in mx.MATRIZ["celdas"]:
            fs = [f for f in filas if f["brazo"] == brazo and f["instrumento"] == i]
            ap(f"| {brazo} | `{i}` | {sum(f['aprobacion'] == 'aprobada' for f in fs)} | {sum(f['aprobacion'] == 'falla' for f in fs)} | "
               f"{sum(f['aprobacion'] == 'no aplica' for f in fs)} |")
    ap("\n**Celdas que NO cumplen (hallazgos; no se cambia la expectativa):**\n")
    malas = [f for f in filas if f["aprobacion"] == "falla"]
    if not malas:
        ap("- (ninguna)")
    for f in malas:
        ap(f"- **{f['brazo']}** · `{f['instrumento']}` ante **{f['perturbacion']}**: esperado {f['cel']['dir']}"
           f"{'' if f['cel']['min'] is None else f' (min {f['cel']['min']:g})'}, mediana antes {_f(f['mediana_antes'])} → después {_f(f['mediana_despues'])}, "
           f"Δ {_f(f['mediana_dif'])}, δ {f['delta_pareado']:+.2f}, observado {f['observado'] or '—'}, veredicto arnés «{f['veredicto']}»"
           f"{'' if not f['cel']['exacto'] else ('; diferencia distinta de 0 en algún par' if not f['todas_cero'] else '')}"
           f"{'; [lectura post hoc] Δ relativo ' + _f(100 * f['rel'], 2) + ' %' + (' = despreciable (< 2 %)' if despreciable(f['rel']) else ' = NO despreciable') if f['cel']['dir'] == 'sin_cambio' and f['rel'] is not None else ''}.")
    ctl_mal = [f for f in malas if f["cel"]["dir"] == "sin_cambio" and not f["cel"]["exacto"]]
    ap(f"**Lectura post hoc de los controles «=» que fallan por la regla del arnés** (no cambia el criterio ni los conteos; la regla cuenta signos, "
       f"no magnitudes): de {len(ctl_mal)} controles «=» con «cambio inesperado», {sum(despreciable(f['rel']) for f in ctl_mal)} tienen |Δ mediana| < "
       f"{100 * TOL_REL:.0f} % de la mediana previa (despreciables en magnitud) y {sum(not despreciable(f['rel']) for f in ctl_mal)} no.\n")
    if dev:
        ap("## 3. Regla de calibración de `min` (doc §5): min ≤ 0,5 × |mediana del efecto en desarrollo|\n")
        ap("| brazo | instrumento | perturbación | min | mediana desarrollo | ¿cumple la regla? |\n|---|---|---|---|---|---|")
        peor = []
        for f in filas:
            if (f["instrumento"], f["perturbacion"]) in CELDAS_CALIBRADAS:
                ok = min_cumple_regla(f["cel"], f["mediana_dif"])
                ap(f"| {f['brazo']} | `{f['instrumento']}` | {f['perturbacion']} | {f['cel']['min']:g} | {_f(f['mediana_dif'], 4)} | {'sí' if ok else 'NO'} |")
                if not ok:
                    peor.append(f)
        ap(f"\n**Resultado de la regla: {'TODAS las celdas calibradas cumplen; el hash queda ' + mx.VERSION if not peor else str(len(peor)) + ' celda(s) NO cumplen: registrar una versión a4bc-2 con fecha y hora ANTES de la evaluación'}.**\n")
    ap(f"## {4 if dev else 3}. Detalle por brazo\n")
    for brazo in ("G2", "G1"):
        ap(f"### {brazo}\n")
        ap(CAB_DETALLE)
        for f in [f for f in filas if f["brazo"] == brazo and f["cel"]["dir"] != "sin_cambio"]:
            ap(linea_detalle(f))
        ap(f"\n**Controles «sin cambio» ({brazo}):**\n")
        ap(CAB_DETALLE)
        for f in [f for f in filas if f["brazo"] == brazo and f["cel"]["dir"] == "sin_cambio"]:
            ap(linea_detalle(f))
        ap("")
    ap(f"## {5 if dev else 4}. Límite léxico (S1, descriptivo)\n")
    for brazo in ("G2", "G1"):
        for f in [f for f in filas if f["brazo"] == brazo and f["perturbacion"] == "S1_sinonimos"]:
            ap(f"- {brazo} · `{f['instrumento']}`: mediana antes {_f(f['mediana_antes'])} → después {_f(f['mediana_despues'])} "
               f"(Δ mediana {_f(f['mediana_dif'])}); cambió en el {100 * f['frac_cambio']:.0f} % de los turnos; n={f['n']}.")
        ns = meta["extras"].get(brazo, [])
        if ns:
            ap(f"- {brazo}: sustituciones por turno (diccionario mínimo): media {sum(ns) / len(ns):.1f}, "
               f"turnos sin ninguna {100 * sum(1 for x in ns if x == 0) / len(ns):.0f} %.")
    ap("")
    if dist:
        ap("## 5. Distribución real: ventanas de 200 turnos (descriptivo, 42 campañas, sin veredicto)\n")
        ap(seccion_distribucion(dist, clases))
    Path(ruta_md).write_text("\n".join(L), encoding="utf-8")


def seccion_distribucion(dist, clases):
    """Sección Markdown de la distribución real por bloques: medias por brazo y, por campaña, caída primero-último y Spearman contra el proxy de nombres."""
    out = []
    tot = sum(clases.values())
    out.append("Clases de acción en los " + f"{tot} turnos: " + ", ".join(f"{k} {v} ({100 * v / tot:.2f} %)" for k, v in clases.most_common()) + ".\n")
    metricas = [("z", "cr2a_z (media)"), ("crudo", "cr2a_crudo (Ochiai)"), ("cos_turno", "cos por turno"), ("cos_turno_sn", "cos por turno sin nombres"),
                ("cos_v8", "cos ventana 8"), ("cos_v8_sn", "cos ventana 8 sin nombres"), ("prox_nombres", "proxy: % turnos con nombre propio"),
                ("top1_v8", "identifica su escenario (ventana 8, argmax de 21)")]
    bl = sorted({(f["ini"], f["fin"]) for f in dist})
    for brazo in ("G2", "G1"):
        out.append(f"### {brazo}: media por bloque de 200 turnos (media de las medias por campaña)\n")
        out.append("| métrica | " + " | ".join(f"{a}-{b}" for a, b in bl) + " | Δ último − primero |\n|---|" + "---|" * (len(bl) + 1))
        for k, nombre in metricas:
            vals = []
            for a, b in bl:
                xs = [f[k] for f in dist if f["brazo"] == brazo and f["ini"] == a and f[k] == f[k]]
                vals.append(sum(xs) / len(xs) if xs else float("nan"))
            esc = 100 if k in ("prox_nombres", "top1_v8") else 1
            out.append(f"| {nombre} | " + " | ".join(_f(v * esc, 2 if esc == 1 else 1) for v in vals) + f" | {_f((vals[-1] - vals[0]) * esc, 2 if esc == 1 else 1)} |")
        out.append("")
    out.append("### Por campaña: ¿cae cada métrica del primer al último bloque, y cuánto acompaña al proxy de nombres?\n")
    out.append("| brazo | métrica | campañas donde cae (último < primero) | ρ de Spearman con el proxy (mediana entre campañas, 7 bloques) |\n|---|---|---|---|")
    for brazo in ("G2", "G1"):
        for k, nombre in metricas:
            if k == "prox_nombres":
                continue
            caen, rhos, n = 0, [], 0
            for par in sorted({f["par"] for f in dist if f["brazo"] == brazo}):
                fs = sorted([f for f in dist if f["brazo"] == brazo and f["par"] == par], key=lambda f: f["ini"])
                if fs[0][k] != fs[0][k] or fs[-1][k] != fs[-1][k]:
                    continue
                n += 1
                caen += fs[-1][k] < fs[0][k]
                rhos.append(_spearman([f[k] for f in fs], [f["prox_nombres"] for f in fs]))
            rhos = sorted(r for r in rhos if r == r)
            out.append(f"| {brazo} | {nombre} | {caen}/{n} | {_f(rhos[len(rhos) // 2] if rhos else float('nan'), 2)} |")
    out.append("")
    return "\n".join(out)


# ================================================================== main
def main(argv=None):
    """CLI del corredor: carga las 42 campañas, construye el modelo idf, corre la matriz sobre la muestra (desarrollo o evaluación) y escribe el informe."""
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--desarrollo", action="store_true")
    ap_.add_argument("--precalentar", action="store_true")
    ap_.add_argument("--rapido", action="store_true", help="humo: 2 turnos por par, 1 ventana, sin distribución")
    ap_.add_argument("--sin-distribucion", action="store_true")
    ap_.add_argument("--salida", default=None)
    args = ap_.parse_args(argv)
    modo = "desarrollo" if args.desarrollo else "evaluación"
    sem = SEM_DEV if args.desarrollo else SEM_EVAL
    salida = args.salida or str(RAIZ / "docs" / "reportes" / ("sensibilidad_a4bc_desarrollo" if args.desarrollo else "sensibilidad_a4bc"))
    log = lambda s: print(s, flush=True)  # noqa: E731
    T0 = time.perf_counter()
    conn = datos.abrir_conexion()
    pares = datos.cargar_pares()
    log(f"a4bc {modo}: cargando 42 campañas (lemas con caché)...")
    camps, lores = cargar_campanas(conn, pares, log)
    esc = construir_escenarios(pares, lores, log)
    ESC_TODOS.update(esc)
    modelo = ae.ModeloAnclaje.desde_campanas([{"nombres": esc[c.par].nombres_lemas, "turnos": [c.tokR[t] for t in sorted(c.tokR)]}
                                              for c in camps.values()])
    log(f"modelo idf: {modelo.n_docs} campañas · t={time.perf_counter() - T0:.0f}s")
    if args.precalentar:
        return
    ra.registrar_en_arnes()
    ae.registrar_en_arnes()
    n_por_par, n_vent = (2, 1) if args.rapido else (15, 6)
    base_pares = [p for p in pares if p["par"] in DEV_PARES] if args.desarrollo else pares
    if args.desarrollo:
        assert not {p["par"] for p in base_pares} & {"09", "11", "13", "14", "16", "20", "21", "23", "24", "25"}
    plan = datos.plan_muestra(base_pares, sem, 10, n_por_par, n_vent)
    if not args.desarrollo:
        assert [p["par"] for p in plan["pares"]] == ["09", "11", "13", "14", "16", "20", "21", "23", "24", "25"], "la muestra de evaluación cambió"
    log(f"plan: pares {[p['par'] for p in plan['pares']]}")
    t = time.perf_counter()
    celdas, elegibles, extras = recolectar(plan, camps, esc, modelo, sem, log)
    tiempos = {"carga": t - T0, "perturbaciones + instrumentos": time.perf_counter() - t}
    filas = evaluar(celdas, sem)
    dist = clases = None
    if not args.desarrollo and not args.sin_distribucion and not args.rapido:
        t = time.perf_counter()
        dist, clases = distribucion(camps, esc, modelo, log)
        tiempos["distribución"] = time.perf_counter() - t
    tiempos["total"] = time.perf_counter() - T0
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True, timeout=10).stdout.strip() or "?"
    except Exception:
        commit = "?"
    meta = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "commit": commit, "semilla": sem, "plan": plan, "modo": modo,
            "n_por_brazo": len([x for x in plan["turnos"] if x["brazo"] == "G1"]),
            "n_ventanas": len([x for x in plan["ventanas"] if x["brazo"] == "G1"]), "tiempos": tiempos, "extras": extras}
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    escribir_informe(salida + ".md", salida + ".csv", filas, meta, dist, clases)
    if dist:
        with open(salida + "_distribucion.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(dist[0]))
            w.writeheader()
            w.writerows(dist)
    conn.close()
    log(f"escrito {salida}.md · {len(filas)} celdas · total {tiempos['total']:.0f}s")
    return filas


if __name__ == "__main__":
    main()
