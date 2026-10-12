"""
LÍNEA BASE del arnés de sensibilidad por perturbación (A2).

Toma turnos REALES (muestra reproducible, semilla 20260920: 150 turnos por brazo de
10 pares de los dos lotes), les inyecta un defecto CONOCIDO (perturbaciones.py) y comprueba
si cada instrumento (instrumentos_texto.py) reacciona en la dirección PRE-ESPECIFICADA
(perturbaciones.ESPERADO, escrita antes de correr nada).

  PYTHONUTF8=1 py scripts/sensibilidad/correr_sensibilidad.py            # línea base completa
  PYTHONUTF8=1 py scripts/sensibilidad/correr_sensibilidad.py --rapido   # humo (pocas muestras)

Estadística (estadistica.py): booleanos -> tasa antes/después con IC de Wilson, diferencia
pareada con IC de Newcombe y McNemar exacta; numéricos -> diferencia pareada (después - antes)
mediana con IC bootstrap al 95 %, delta de Cliff (pareado y de dos muestras) y prueba de signos
exacta. Multiplicidad: Holm dentro de cada brazo y familia (confirmatorias = dirección
pre-especificada distinta de «sin cambio»; controles = «sin cambio»). Los pares
(perturbación, instrumento) sin expectativa pre-especificada son descriptivos: sin veredicto.

Solo SELECT. Sin LLM. Salidas: docs/reportes/sensibilidad_baseline.{md,csv}.
"""
import argparse
import csv
import hashlib
import platform
import random
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))

import datos                       # noqa: E402
import estadistica as es           # noqa: E402
import fidelidad                   # noqa: E402
import instrumentos_texto as it    # noqa: E402
import perturbaciones as pt        # noqa: E402

SEMILLA = 20260920
LT_PERTURBACIONES = {"P6", "P8", "P11a_inyeccion", "P11b_eliminacion", "P12"}   # LanguageTool es lento
FAMILIAS = ("confirmatoria", "control", "descriptivo")
GLIFO_ESP = {"se_dispara": "●", "sube": "▲", "baja": "▼", "sin_cambio": "="}
GLIFO_VER = {"responde": "✓", "no responde": "✗", "dirección opuesta": "↔",
             "cambio inesperado": "!", "no aplica": "–", "": "·"}


# ================================================================== celdas y evaluación
def _semilla_celda(semilla, *claves):
    return int(hashlib.sha1("|".join(map(str, (semilla,) + claves)).encode()).hexdigest()[:8], 16)


def estadisticos_celda(tipo, antes, despues, semilla=0):
    """Estadísticos de una celda (brazo, perturbación, instrumento) sobre pares antes/después."""
    if tipo == "bool":
        a_, d_ = [bool(x) for x in antes], [bool(x) for x in despues]
        t = es.contar_pareado(a_, d_)
        n = len(a_)
        dif, lo, hi = es.newcombe_pareado(**t)
        return {"tipo": "bool", "n": n, **t,
                "tasa_antes": (t["a"] + t["b"]) / n if n else float("nan"),
                "tasa_despues": (t["a"] + t["c"]) / n if n else float("nan"),
                "ic_antes": es.wilson(t["a"] + t["b"], n), "ic_despues": es.wilson(t["a"] + t["c"], n),
                "dif": dif, "ic_dif": (lo, hi), "p": es.mcnemar_exacta(t["b"], t["c"])}
    pares = [(x, y) for x, y in zip(antes, despues) if x is not None and y is not None]
    n = len(pares)
    if n == 0:
        nan = float("nan")
        return {"tipo": "num", "n": 0, "mediana_antes": nan, "mediana_despues": nan, "mediana_dif": nan,
                "ic_dif": (nan, nan), "delta_pareado": 0.0, "delta_cruzado": 0.0, "p": 1.0}
    xs, ys = [x for x, _ in pares], [y for _, y in pares]
    diffs = [y - x for x, y in pares]
    import numpy as np
    ic = (0.0, 0.0) if not any(diffs) else es.ic_bootstrap_mediana(diffs, semilla=semilla)
    return {"tipo": "num", "n": n, "mediana_antes": float(np.median(xs)), "mediana_despues": float(np.median(ys)),
            "mediana_dif": float(np.median(diffs)), "ic_dif": ic,
            "delta_pareado": es.delta_pareado(diffs), "delta_cruzado": es.cliff_delta(ys, xs),
            "p": es.prueba_signos(diffs)}


def evaluar(celdas, esperado, semilla=SEMILLA, n_min=es.N_MIN):
    """celdas: {(brazo, pid, instrumento): {"tipo", "antes", "despues"}} -> filas con veredicto."""
    filas = []
    for (brazo, pid, instr), c in sorted(celdas.items()):
        e = estadisticos_celda(c["tipo"], c["antes"], c["despues"], _semilla_celda(semilla, brazo, pid, instr))
        exp = esperado.get(pid, {}).get(instr)
        fam = "descriptivo" if exp is None else "control" if exp == "sin_cambio" else "confirmatoria"
        filas.append({"brazo": brazo, "perturbacion": pid, "instrumento": instr, "tipo": c["tipo"],
                      "familia": fam, "esperado": exp or "", **e, "p_holm": e["p"],
                      "observado": "", "veredicto": ""})
    for brazo in sorted({f["brazo"] for f in filas}):
        for fam in FAMILIAS:
            grupo = [f for f in filas if f["brazo"] == brazo and f["familia"] == fam and f["n"] >= n_min]
            for f, p in zip(grupo, es.holm([f["p"] for f in grupo])):
                f["p_holm"] = p
    for f in filas:
        if f["n"] < n_min:
            f["veredicto"] = "no aplica" if f["esperado"] else ""
            continue
        if f["tipo"] == "bool":
            f["observado"] = es.direccion_booleana(f["p_holm"], f["b"], f["c"])
        else:
            f["observado"] = es.direccion_numerica(f["p_holm"], f["delta_pareado"])
        f["veredicto"] = es.veredicto(f["esperado"], f["observado"], f["n"], n_min) if f["esperado"] else ""
    return filas


def completar_celdas_esperadas(celdas, esperado, brazos=("G1", "G2")):
    """Crea celdas vacías para cada (brazo, perturbación, instrumento) con expectativa
    pre-especificada que no llegó a calcularse (sin turnos elegibles): salen «no aplica»
    en vez de desaparecer del informe."""
    for pid, exps in esperado.items():
        for instr in exps:
            for brazo in brazos:
                celdas.setdefault((brazo, pid, instr),
                                  {"tipo": it.INSTRUMENTOS[instr].tipo, "antes": [], "despues": []})


# ================================================================== recolección
def _valores(texto, ctx, nombres):
    return it.calcular(texto, ctx, nombres=nombres)


def recolectar(plan, dc_por_campana, args, log):
    """Calcula antes/después de todas las perturbaciones. -> celdas, metadatos."""
    rng_lt = random.Random(f"{args.semilla}|lt")
    celdas = {}

    def anadir(brazo, pid, instr, tipo, a, d):
        c = celdas.setdefault((brazo, pid, instr), {"tipo": tipo, "antes": [], "despues": []})
        c["antes"].append(a)
        c["despues"].append(d)

    turno_instr = {n for n, i in it.INSTRUMENTOS.items() if i.ambito == "turno"}
    sin_lt = turno_instr - {"grammaticality_lt"}
    pids_turno = [p for p, x in pt.CATALOGO.items() if x.ambito == "turno"]
    donantes = {}       # brazo -> [(par, DatosCampana)]
    for p in plan["pares"]:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            donantes.setdefault(brazo, []).append((p["par"], dc_por_campana[p[k]]))
    tiempos, elegibles = {}, {}

    for brazo in ("G1", "G2"):
        items = [t for t in plan["turnos"] if t["brazo"] == brazo]
        datos_items = []
        for t in items:
            dc = dc_por_campana[t["campaign_id"]]
            datos_items.append((t, dc, dc.texto(t["turn"]), dc.contexto(t["turn"])))
        lt_idx = set(rng_lt.sample(range(len(items)), min(args.lt_n, len(items)))) if not args.sin_lt else set()
        t0 = time.perf_counter()
        base = []
        for i, (t, dc, texto, ctx) in enumerate(datos_items):
            base.append(_valores(texto, ctx, turno_instr if i in lt_idx else sin_lt))
        tiempos[f"baseline {brazo}"] = time.perf_counter() - t0
        for pid in pids_turno:
            t0 = time.perf_counter()
            n_el = 0
            for i, (t, dc, texto, ctx) in enumerate(datos_items):
                if not pt.elegible(pid, texto, ctx):
                    continue
                n_el += 1
                rng = random.Random(f"{args.semilla}|{pid}|{t['campaign_id']}|{t['turn']}")
                donante = None
                if pid == "P8":
                    otros = [d for par, d in donantes[brazo] if par != t["par"]]
                    while not donante:
                        dd = rng.choice(otros)
                        donante = dd.texto(rng.randint(2, 1400)).strip() or None
                r = pt.perturbar(pid, texto, ctx, rng, donante=donante)
                con_lt = pid in LT_PERTURBACIONES and i in lt_idx
                despues = _valores(r.texto, r.ctx, turno_instr if con_lt else sin_lt)
                for instr, v in despues.items():
                    anadir(brazo, pid, instr, it.INSTRUMENTOS[instr].tipo, base[i][instr], v)
            elegibles[(brazo, pid)] = n_el
            tiempos[f"{pid} {brazo}"] = time.perf_counter() - t0
            log(f"  {brazo} {pid}: {n_el} turnos elegibles ({tiempos[f'{pid} {brazo}']:.1f}s)")
        # ventanas (P9)
        t0 = time.perf_counter()
        vent = [v for v in plan["ventanas"] if v["brazo"] == brazo]
        for v in vent:
            dc = dc_por_campana[v["campaign_id"]]
            textos = [dc.texto(v["start"] + j) for j in range(v["k"])]
            ctx = dc.contexto(v["start"])
            antes = it.calcular_ventana(textos, ctx)
            rng = random.Random(f"{args.semilla}|P9|{v['campaign_id']}|{v['start']}")
            r = pt.perturbar_ventana("P9", textos, rng)
            despues = it.calcular_ventana(r.textos, ctx)
            for instr in antes:
                anadir(brazo, "P9", instr, "num", antes[instr], despues[instr])
        elegibles[(brazo, "P9")] = len(vent)
        tiempos[f"P9 {brazo}"] = time.perf_counter() - t0
        log(f"  {brazo} P9: {len(vent)} ventanas ({tiempos[f'P9 {brazo}']:.1f}s)")
    it.guardar_cache_lt()
    completar_celdas_esperadas(celdas, pt.ESPERADO)
    return celdas, elegibles, tiempos


# ================================================================== informe
def _f(x, d=3):
    if x is None or x != x:
        return "—"
    return f"{x:.{d}f}"


def _pct(x):
    return "—" if x != x else f"{100 * x:.1f}%"


def _celda_resumen(f):
    """Glifos: esperado + veredicto (+ observado si no coincide)."""
    if not f["esperado"]:
        return ""
    s = GLIFO_ESP[f["esperado"]] + GLIFO_VER[f["veredicto"]]
    if f["veredicto"] in ("no responde", "dirección opuesta", "cambio inesperado") and f["observado"]:
        s += f"({GLIFO_ESP[f['observado']]})"
    if (f["veredicto"] == "responde" and f["esperado"] == "se_dispara" and f.get("tipo") == "bool"
            and f.get("tasa_despues", 1.0) < 0.5):
        s += "~"          # anotación de informe: responde, pero detecta menos de la mitad de lo inyectado
    return s


def _linea_detalle(f):
    if f["tipo"] == "bool":
        ant = f"{_pct(f['tasa_antes'])} [{_pct(f['ic_antes'][0])}, {_pct(f['ic_antes'][1])}]"
        des = f"{_pct(f['tasa_despues'])} [{_pct(f['ic_despues'][0])}, {_pct(f['ic_despues'][1])}]"
        dif = f"{100 * f['dif']:+.1f} pp [{100 * f['ic_dif'][0]:+.1f}, {100 * f['ic_dif'][1]:+.1f}]"
        extra = f"b={f['b']} c={f['c']}"
        delta = "—"
    else:
        ant, des = _f(f["mediana_antes"]), _f(f["mediana_despues"])
        dif = f"{_f(f['mediana_dif'])} [{_f(f['ic_dif'][0])}, {_f(f['ic_dif'][1])}]"
        delta = f"{f['delta_pareado']:+.2f} / {f['delta_cruzado']:+.2f}"
        extra = ""
    return (f"| {f['perturbacion']} | `{f['instrumento']}` | {GLIFO_ESP.get(f['esperado'], '')} {f['esperado']} | "
            f"{f['n']} | {ant} | {des} | {dif} {extra} | {delta} | {f['p_holm']:.3g} | "
            f"{f['observado'] or '—'} | **{f['veredicto'] or '—'}** |")


def _matriz(filas, brazo):
    """Matriz instrumento × perturbación con glifos esperado+veredicto."""
    fb = [f for f in filas if f["brazo"] == brazo and f["esperado"]]
    perts = [p for p in pt.CATALOGO if any(f["perturbacion"] == p for f in fb)]
    instrs = [i for i in it.INSTRUMENTOS if any(f["instrumento"] == i for f in fb)]
    idx = {(f["perturbacion"], f["instrumento"]): f for f in fb}
    cab = "| instrumento | " + " | ".join(p.replace("_", " ", 1) for p in perts) + " |"
    lin = "|---|" + "|".join("---" for _ in perts) + "|"
    out = [cab, lin]
    for i in instrs:
        out.append(f"| `{i}` | " + " | ".join(
            _celda_resumen(idx[(p, i)]) if (p, i) in idx else "" for p in perts) + " |")
    return "\n".join(out)


def _seccion_3a_persona(filas, brazo):
    idx = {(f["perturbacion"], f["instrumento"]): f for f in filas if f["brazo"] == brazo}
    casos = [("qn2_pj_piensa_narrado", c) for c in ("decision", "pensamiento", "emocion")] + \
            [("qn2_pj_accion_revisar", "accion"), ("qn2_pj_accion_revisar", "accion_sin_tirada")]
    out = ["| detector | categoría | control 3.ª persona con nombre: antes → después | veredicto | "
           "usurpación 2.ª persona: antes → después | veredicto |", "|---|---|---|---|---|---|"]

    def cel(p, i):
        f = idx.get((p, i))
        if not f or f["n"] == 0:
            return "n/a", "no aplica"
        if f["tipo"] == "bool":
            return f"{_pct(f['tasa_antes'])} → {_pct(f['tasa_despues'])} (n={f['n']})", f["veredicto"] or "—"
        return "—", f["veredicto"]
    for instr, cat in casos:
        a, va = cel(f"P2_{cat}", instr)
        b, vb = cel(f"P1_{cat}", instr)
        out.append(f"| `{instr}` | {cat} | {a} | {va} | {b} | {vb} |")
    for instr, p3, p2 in (("cl2_pc_hp_contradice_narracion", "P4_3p", "P4_2p"),):
        a, va = cel(p3, instr)
        b, vb = cel(p2, instr)
        out.append(f"| `{instr}` | muerte del PJ con HP>0 | {a} | {va} | {b} | {vb} |")
    return "\n".join(out)


def _hallazgos(filas):
    """Lista automática: confirmatorias que no responden / responden al revés y controles rotos."""
    out = []
    for brazo in ("G2", "G1"):
        for ver, titulo in (("no responde", "no responde"), ("dirección opuesta", "dirección opuesta")):
            por_instr = {}
            for f in filas:
                if f["brazo"] == brazo and f["familia"] == "confirmatoria" and f["veredicto"] == ver:
                    por_instr.setdefault(f["instrumento"], []).append(f["perturbacion"])
            for instr, ps in por_instr.items():
                out.append(f"- **{brazo}** · `{instr}` **{titulo}** ante: {', '.join(ps)}")
        por_instr = {}
        for f in filas:
            if f["brazo"] == brazo and f["familia"] == "control" and f["veredicto"] == "cambio inesperado":
                por_instr.setdefault(f["instrumento"], []).append(f["perturbacion"])
        for instr, ps in por_instr.items():
            out.append(f"- **{brazo}** · `{instr}` **cambia sin que debiera** (control roto) ante: {', '.join(ps)}")
        na = sorted({f["perturbacion"] for f in filas if f["brazo"] == brazo and f["veredicto"] == "no aplica"})
        if na:
            out.append(f"- **{brazo}** · con expectativas «no aplica» (menos de 10 pares válidos): {', '.join(na)}")
    return out


def _prevalencia(conn, plan):
    """Tasa de marca guardada en turn_validation (todas las campañas de los dos lotes)."""
    pares = datos.cargar_pares()
    out = {}
    for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
        ids = [p[k] for p in pares]
        r = conn.execute("""
            SELECT count(*) AS n, sum(cl2_pnj_inactivo_actua::int) AS cl2_pnj, sum(qn2_pj_piensa_narrado::int) AS piensa,
                   sum(qn2_pj_accion_revisar::int) AS accion, sum(cl2_pc_hp_contradice_narracion::int) AS hp,
                   sum(cr1_veredicto_contradice_narracion::int) AS cr1,
                   sum((cardinality(cr2_nombres_no_reconocidos) > 0)::int) AS cr2,
                   sum((raw_flags ? 'meta_comentario')::int) AS meta, sum((raw_flags ? 'comenta_reglas')::int) AS reglas
              FROM turn_validation WHERE campaign_id = ANY(%s)""", (ids,)).fetchone()
        out[brazo] = r
    return out


def escribir_informe(ruta_md, ruta_csv, filas, meta):
    campos = ["brazo", "perturbacion", "instrumento", "tipo", "familia", "esperado", "n", "a", "b", "c", "d",
              "tasa_antes", "tasa_despues", "dif", "mediana_antes", "mediana_despues", "mediana_dif",
              "ic_dif_bajo", "ic_dif_alto", "delta_pareado", "delta_cruzado", "p", "p_holm",
              "observado", "veredicto"]
    with open(ruta_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for f in filas:
            r = dict(f)
            r["ic_dif_bajo"], r["ic_dif_alto"] = f["ic_dif"]
            w.writerow(r)

    L = []
    ap = L.append
    ap("# Sensibilidad por perturbación — línea base (instrumentos deterministas tal como están hoy)\n")
    ap(f"- Generado: {meta['fecha']} · commit `{meta['commit']}` (árbol de trabajo con cambios sin confirmar en "
       f"`orquestador/`: los instrumentos se leen del árbol tal cual) · Python {platform.python_version()}")
    ap(f"- Semilla de muestreo: **{meta['semilla']}** · pares: {', '.join(p['par'] + ' (' + p['lote'] + ')' for p in meta['plan']['pares'])}")
    ap(f"- Muestra: {meta['n_por_brazo']} turnos por brazo (turnos 2–1400) + {meta['n_ventanas']} ventanas de 8 turnos por brazo para P9; "
       f"LanguageTool sobre {meta['lt_n']} turnos por brazo y solo en P6, P8, P11a/b, P12 (lento).")
    ap(f"- **Hash SHA-256 de la tabla ESPERADO pre-especificada** (perturbaciones.py, escrita antes de correr nada): "
       f"`{pt.hash_esperado(original=True)}` (verificado por un test). Tras un primer humo con pocas muestras se añadieron "
       f"solo dos variantes, {', '.join(pt.POSTERIORES_AL_HUMO)} (149 de 150 turnos reales llevan tirada y "
       f"`qn2_pj_accion_revisar` solo mira turnos sin ella); hash de la tabla completa: `{pt.hash_esperado()}`. "
       f"Ninguna expectativa se modificó tras ver resultados.")
    ap("- Tiempos: " + "; ".join(f"{k} {v:.0f}s" for k, v in meta["tiempos_gruesos"].items()) + "\n")
    ap("## 0. Cómo leer este informe\n")
    ap("Dirección esperada = la de un instrumento **válido para su constructo** (p. ej. un detector de usurpación debe "
       "dispararse ante usurpación, sea en 3.ª o en 2.ª persona; barajar palabras no debe cambiar el TTR). "
       "Veredictos: **responde** (observado = esperado), **no responde** (se esperaba cambio y no se detecta), "
       "**dirección opuesta**, **cambio inesperado** (control «sin cambio» que se mueve: artefacto del instrumento) y "
       "**no aplica** (menos de 10 pares válidos, o el instrumento depende de datos que no son texto: "
       "`cl1_campo_inmutable_alterado` depende de los deltas del extractor). "
       "Reglas de decisión fijadas de antemano: numérico «cambia» si p ajustado (Holm) < 0,05 **y** |delta de Cliff pareado| ≥ 0,147 "
       "(Romano et al. 2006); booleano «cambia» si p McNemar exacta ajustada (Holm) < 0,05. "
       "Holm por brazo dentro de cada familia (confirmatoria = dirección pre-especificada ≠ «sin cambio»; control = «sin cambio»). "
       "Los pares sin expectativa son descriptivos (solo en el CSV).\n")
    ap("Glifos de las matrices: esperado ● se dispara · ▲ sube · ▼ baja · = sin cambio; veredicto ✓ responde · ✗ no responde · "
       "↔ dirección opuesta · ! cambio inesperado · – no aplica; entre paréntesis lo observado cuando no coincide; "
       "«~» tras ✓ = responde pero detecta menos de la mitad de los casos inyectados (anotación añadida al ver los "
       "resultados; no cambia el veredicto).\n")

    ap("## 1. Prueba de fidelidad (recálculo sobre texto vs. `turn_validation`)\n")
    fid = meta["fidelidad"]
    ap(f"Turnos recalculados: **{fid['n_turnos']['muestra']}** de la muestra aleatoria + **{fid['n_turnos']['positivos']}** "
       f"turnos con marca positiva guardada (ambos lotes y brazos). Numéricos a 3 decimales (`qn1_legibilidad_fh` es "
       f"`numeric(6,2)`: 2 decimales); booleanos y `cr2_nombres_no_reconocidos` por igualdad exacta.\n")
    ap("| columna | muestra: coinciden | positivos: coinciden |\n|---|---|---|")
    for col in list(fidelidad.NUMERICOS) + fidelidad.BOOLEANOS + ["cr2_nombres_no_reconocidos"] + fidelidad.RAW_FLAGS:
        m = fid["resumen"]["muestra"].get(col, {"n": 0, "ok": 0})
        p = fid["resumen"]["positivos"].get(col, {"n": 0, "ok": 0})
        ap(f"| `{col}` | {m['ok']}/{m['n']} | {p['ok']}/{p['n']} |")
    malas = [x for x in fid["filas"] if not x["ok"]]
    ap(f"\nDiscrepancias totales: **{len(malas)}**." + ("" if not malas else " Primeras:"))
    for x in malas[:15]:
        ap(f"- par {x['par']} {x['brazo']} t{x['turn']} `{x['columna']}`: recalculado {x['recalculado']!r} vs guardado {x['guardado']!r}")
    mu = fid["mutaciones"]
    ap("\nControl de la propia prueba (mutaciones deliberadas del contexto en "
       f"{mu['escena_erronea']['n']} turnos): con la escena anterior equivocada (turno t−2) el Jaccard deja de coincidir en "
       f"{mu['escena_erronea']['discrepancias']}/{mu['escena_erronea']['n']}; sin los PNJ en el gazetteer el grafo de entidades "
       f"deja de coincidir en {mu['sin_pnj_en_gazetteer']['discrepancias']}/{mu['sin_pnj_en_gazetteer']['n']}. "
       "Es decir, la coincidencia no es trivial.\n")
    if meta.get("prevalencia"):
        ap("Prevalencia de marcas guardadas (todas las campañas de los dos lotes; contexto para la potencia de los booleanos):\n")
        ap("| brazo | turnos | cl2_pnj_inactivo_actua | qn2_pj_piensa_narrado | qn2_pj_accion_revisar | cl2_pc_hp | cr1 | cr2 (≥1 nombre) | meta_comentario | comenta_reglas |\n|---|---|---|---|---|---|---|---|---|---|")
        for b, r in meta["prevalencia"].items():
            ap(f"| {b} | {r['n']} | {r['cl2_pnj']} | {r['piensa']} | {r['accion']} | {r['hp']} | {r['cr1']} | {r['cr2']} | {r['meta']} | {r['reglas']} |")
        ap("")

    ap("## 2. Resumen: instrumento × perturbación (esperado, veredicto)\n")
    for brazo, nombre in (("G2", "G2 (monolítico, narra en 2.ª persona)"), ("G1", "G1 (multiagente, con etiquetas de formato)")):
        ap(f"### {nombre}\n")
        ap(_matriz(filas, brazo))
        ap("")

    ap("## 3. Los detectores de 3.ª persona\n")
    ap("Los tres detectores que buscan «‹Nombre del PJ› decide/muere/ataca…»: control positivo en 3.ª persona (P2, P4_3p) frente a "
       "la misma usurpación en 2.ª persona (P1, P4_2p). Tasas de marca antes → después de la inyección.\n")
    for brazo in ("G2", "G1"):
        ap(f"**{brazo}**\n")
        ap(_seccion_3a_persona(filas, brazo))
        ap("")

    ap("## 3b. Hallazgos automáticos (lo que NO cumplió la expectativa pre-especificada)\n")
    for linea in _hallazgos(filas):
        ap(linea)
    ap("")
    ap("## 3c. Lectura de la corrida del 2026-09-20 (redactada a mano sobre estas tablas; no se regenera al volver a correr)\n")
    for linea in LECTURA_2026_09_20:
        ap(f"- {linea}")
    ap("")

    for brazo, titulo in (("G2", "G2 (monolítico)"), ("G1", "G1 (multiagente)")):
        ap(f"## 4{'a' if brazo == 'G2' else 'b'}. Detalle por brazo — {titulo}\n")
        ap("Comparaciones **confirmatorias** (dirección pre-especificada). `Antes/Después`: tasa de marca con IC de Wilson (booleanos) "
           "o mediana (numéricos); `Δ`: diferencia pareada con IC (Newcombe / bootstrap); `δ`: delta de Cliff pareado / de dos muestras; "
           "`p Holm`: p ajustado.\n")
        ap("| perturbación | instrumento | esperado | n | antes | después | Δ [IC95] | δ | p Holm | observado | veredicto |\n|---|---|---|---|---|---|---|---|---|---|---|")
        for f in [f for f in filas if f["brazo"] == brazo and f["familia"] == "confirmatoria"]:
            ap(_linea_detalle(f))
        ap("")
        ctl = [f for f in filas if f["brazo"] == brazo and f["familia"] == "control"]
        malos = [f for f in ctl if f["veredicto"] == "cambio inesperado"]
        ap(f"**Controles «sin cambio»** ({brazo}): {sum(f['veredicto'] == 'responde' for f in ctl)} conformes, "
           f"{len(malos)} con cambio inesperado, {sum(f['veredicto'] == 'no aplica' for f in ctl)} no aplica.\n")
        if malos:
            ap("| perturbación | instrumento | esperado | n | antes | después | Δ [IC95] | δ | p Holm | observado | veredicto |\n|---|---|---|---|---|---|---|---|---|---|---|")
            for f in malos:
                ap(_linea_detalle(f))
            ap("")

    ap("## 5. Limitaciones y decisiones de diseño\n")
    for s in meta["limitaciones"]:
        ap(f"- {s}")
    ap("")
    Path(ruta_md).write_text("\n".join(L), encoding="utf-8")


LECTURA_2026_09_20 = [
    "**Detectores de 3.ª persona (qn2_pj_piensa_narrado, qn2_pj_accion_revisar, cl2_pc_hp_contradice_narracion): ciegos en 2.ª persona, en los dos brazos.** "
    "Con el nombre del PJ (P2, P4_3p) marcan 150/150 (135/135 en G2 para P4 por elegibilidad); con la misma usurpación en 2.ª persona (P1, P4_2p) marcan 0/150. "
    "Es el fallo conocido, ahora medido; el arnés lo detecta y sirve para verificar los detectores corregidos.",
    "**qn2_pj_accion_revisar y cl2_pc_hp_contradice_narracion están inertes en los datos reales aunque se corrijan:** 0 marcas guardadas en 58 800 turnos. "
    "En el primer caso la puerta `not tiradas` casi nunca se abre (149 de 150 turnos muestreados llevan tirada: P1_accion/P2_accion quedan «no aplica»; "
    "solo el turno simulado sin tirada permite ejercitar el regex).",
    "**cr2_nombres_no_reconocidos está saturado en G1 por el formato:** 29 357 de 29 400 turnos G1 guardados tienen algún «nombre no reconocido» (99,9 %; G2: 5,7 %), "
    "porque la línea de tirada («Percepción: Éxito…») y sus mayúsculas cuentan como nombres propios. En la muestra 100 % antes de la perturbación, por eso no puede subir ante nombres inventados (P5 «no responde» en G1); "
    "al quitar el formato (P11b) cae a 9,3 %. Con P11a en G2 sube de 6,0 % a 100 %.",
    "**Artefacto de formato (P11) en todos los numéricos de contenido:** TTR, n-gramas, Fernández-Huerta, Jaccard, densidad de grafo y gramaticalidad cambian de forma significativa al añadir/quitar etiquetas y línea mecánica (7 de 9 controles rotos al inyectar el formato en G2, 6 de 9 al quitarlo en G1; solo meta_comentario y comenta_reglas, y FH en G1, quedan quietos). "
    "Las comparaciones G1 vs G2 con estos instrumentos sobre el texto crudo mezclan estilo con formato.",
    "**pnj_inactivo_refinado (spaCy) detecta ~10 % (G2) y ~2 % (G1) de los PNJ inactivos inyectados como sujeto:** solo cuenta nombres de una palabra (`nombre in tok.text`); los PNJ de varias palabras («Sargento Brea») nunca. "
    "El detector crudo `cl2_pnj_inactivo_actua` sí responde (100 % tras la inyección; marca base 4,7 % en G2, 14,0 % en G1).",
    "**Gramaticalidad (LanguageTool):** techo en ~1,00; baja con P6 (barajar) pero no ve palabras de otro alfabeto (P12 «no responde»): la categoría TYPOS está excluida.",
    "**Coherencia local:** `ventana_jaccard_medio` baja al permutar (efecto pequeño, −0,015) y `ventana_consistencia_V`/`coherencia_C`/`entity_coreference` se comportan como controles invariantes; "
    "`detector_bucles` (visitas/ciclos) no reacciona a la permutación. `cr2_entidad_grafo_densidad` y `grafo_lema_densidad` no distinguen una narración de otro par (P8: diferencias pareadas casi siempre 0; mediana ~0).",
    "**P8 sobre cl2_pnj_inactivo_actua en G1 figura como «cambio inesperado»** porque mi expectativa «sin cambio» olvidó que sustituir el texto elimina las marcas reales de base (14 % de los turnos G1): "
    "21 marcas desaparecen y ninguna aparece (b=21, c=0). Es un error de la pre-especificación, se conserva y se reporta.",
    "Instrumentos que SÍ se comportan como se pre-especificó: `cr1` ante pifia+éxito, TTR/n-gramas ante párrafo duplicado, Jaccard ante otro par, gramaticalidad ante barajar, controles exactos de P6 (TTR, FH, Jaccard invariantes) y de P9 (V invariante).",
]


LIMITACIONES = [
    "Un defecto sintético insertado en una oración no es un defecto natural del DM: mide la capacidad de detección del instrumento "
    "ante ese patrón, no su tasa de falsos negativos en la naturaleza.",
    "P1/P2 (usurpación) se inserta al inicio de un párrafo elegido al azar, con una plantilla por categoría; el léxico de las "
    "plantillas está fijado (repertorio de 2–5 oraciones por categoría): un detector nuevo puede reaccionar al repertorio y no a la categoría.",
    "El estado de PNJ es histórico (reconstruido desde `state_deltas`); el HP del PJ es el ACTUAL (no hay historia de HP en la base) "
    "y las tiradas se recalculan con `jugador/dados.py` de hoy. En P3/P4/P10 el contexto se manipula explícitamente (estado del PNJ, tirada) "
    "porque en los datos reales casi no hay PNJ muertos activos, muertes de PJ ni pifias narradas como éxito: son controles positivos "
    "casi tautológicos para regex (validan el arnés y la ceguera de 2.ª persona, no la calidad del DM).",
    "P6 baraja solo palabras en minúscula (mayúsculas, cifras y puntuación quedan fijas) para no introducir artefactos de capitalización "
    "en el detector de nombres; por construcción TTR, Fernández-Huerta y Jaccard son invariantes (sirven de control de exactitud).",
    "P8 usa como donante un turno aleatorio (2–1400) de OTRO par del mismo brazo de la muestra (formato G1 con G1, G2 con G2).",
    "P9: una permutación aleatoria (≠ identidad) por ventana de 8 turnos, no todas las permutaciones (Barzilay & Lapata usan varias). "
    "`ventana_consistencia_V` es invariante al orden por construcción (control exacto).",
    "P11a inyecta «narrativa/mecanica» + una línea «Habilidad: Éxito|Fallo (N vs CD M).»; P11b usa `prosa()` de `validacion_generar.py`. "
    "Cualquier cambio en un instrumento que debería mirar solo el contenido es artefacto de formato (p. ej. `cr2_nombres_no_reconocidos` "
    "marca «Éxito»/«Percepción» de la línea mecánica).",
    "`jericho_qa_recall` y `relojes_no_reconocidos` (reporte_validacion.py) dependen de deltas y relojes de la base, no de texto arbitrario: "
    "no están en este arnés v1. `cl1_campo_inmutable_alterado` depende de los deltas del extractor. `coherencia_entidad_C`, "
    "`consistencia_atributos_V` y `detector_bucles` se evalúan por ventana de 8 turnos (son agregados de campaña: la ventana es una adaptación).",
    "`entity_coreference_rate` por turno usa como «ya conocidas» las entidades mencionadas en turnos previos (recomputadas desde el texto) "
    "con la lista de entidades del turno; el reporte agrega por campaña con la lista final.",
    "Tamaños de efecto y umbrales (|δ| ≥ 0,147, α = 0,05, n mínimo 10) son convenciones publicadas fijadas antes de ver resultados; "
    "con n = 150 y muchas comparaciones el control de multiplicidad (Holm) es por brazo y familia, no global.",
    "Los detectores de 2.ª persona nuevos se enchufan con `instrumentos_texto.registrar_instrumento(...)` y "
    "`perturbaciones.registrar_esperado(...)` ANTES de correrlos; el arnés vuelve a correrse con este mismo script.",
]


# ================================================================== main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=SEMILLA)
    ap.add_argument("--n-pares", type=int, default=10)
    ap.add_argument("--n-por-par", type=int, default=15)
    ap.add_argument("--ventanas-por-par", type=int, default=6)
    ap.add_argument("--lt-n", type=int, default=50, help="turnos por brazo con LanguageTool")
    ap.add_argument("--sin-lt", action="store_true")
    ap.add_argument("--rapido", action="store_true", help="humo: 2 turnos por par, 1 ventana, 4 LT")
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "reportes" / "sensibilidad_baseline"))
    args = ap.parse_args(argv)
    if args.rapido:
        args.n_por_par, args.ventanas_por_par, args.lt_n = 2, 1, 4
    T0 = time.perf_counter()
    tiempos_gruesos = {}

    def log(s):
        print(s, flush=True)

    conn = datos.abrir_conexion()
    plan = datos.plan_muestra(datos.cargar_pares(), args.semilla, args.n_pares, args.n_por_par,
                              args.ventanas_por_par)
    t = time.perf_counter()
    dc = {}
    for p in plan["pares"]:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            dc[p[k]] = datos.DatosCampana(conn, p[k], brazo, p["par"])
    tiempos_gruesos["carga de datos"] = time.perf_counter() - t
    log(f"datos cargados: {len(dc)} campañas ({tiempos_gruesos['carga de datos']:.1f}s)")

    t = time.perf_counter()
    fid = fidelidad.correr(conn, plan, dc, args.semilla)
    tiempos_gruesos["fidelidad"] = time.perf_counter() - t
    log(f"fidelidad: {fid['n_turnos']} discrepancias={sum(not f['ok'] for f in fid['filas'])}")

    t = time.perf_counter()
    celdas, elegibles, tiempos = recolectar(plan, dc, args, log)
    tiempos_gruesos["perturbaciones + instrumentos"] = time.perf_counter() - t

    t = time.perf_counter()
    filas = evaluar(celdas, pt.ESPERADO, args.semilla)
    tiempos_gruesos["estadística"] = time.perf_counter() - t
    tiempos_gruesos["total"] = time.perf_counter() - T0

    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                                text=True, timeout=10).stdout.strip() or "?"
    except Exception:
        commit = "?"
    meta = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "commit": commit, "semilla": args.semilla, "plan": plan,
            "n_por_brazo": len([x for x in plan["turnos"] if x["brazo"] == "G1"]),
            "n_ventanas": len([x for x in plan["ventanas"] if x["brazo"] == "G1"]), "lt_n": 0 if args.sin_lt else args.lt_n,
            "tiempos_gruesos": tiempos_gruesos, "fidelidad": fid, "limitaciones": LIMITACIONES,
            "prevalencia": _prevalencia(conn, plan)}
    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    escribir_informe(args.salida + ".md", args.salida + ".csv", filas, meta)
    conn.close()
    log(f"escrito {args.salida}.md y .csv · {len(filas)} celdas · total {tiempos_gruesos['total']:.0f}s")
    return filas


if __name__ == "__main__":
    main()
