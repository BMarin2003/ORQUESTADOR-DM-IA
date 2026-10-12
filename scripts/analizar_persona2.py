#!/usr/bin/env python3
"""
Análisis de la auditoría de persona2 (Plan A, paso A3): convierte las etiquetas del investigador en
precisión, prevalencia, recall y acuerdo entre etiquetadores. Solo lee CSV (sin base de datos).

Entradas
  --etiquetas   CSV exportado por validacion/etiquetado_persona2_<E>.html (evaluador principal)
  --etiquetas2  (opcional) CSV del segundo etiquetador (subconjunto del 20 %)
  --clave       validacion/confirmacion_persona2_clave.csv (por defecto)
Salida: docs/reportes/auditoria_persona2.md (o --salida)

Definiciones (fijadas antes de ver etiquetas)
  · viola = veredicto «si»; no viola = «no»; «dudoso» se reporta aparte. Versión ESTRICTA: dudoso cuenta como no viola;
    versión INDULGENTE: dudoso cuenta como viola. La precisión se da en las dos.
  · Precisión = % de turnos marcados por el detector (estratos primaria:* y secundaria) que el etiquetador juzga que violan.
  · Prevalencia = % de turnos de la sonda aleatoria (sin filtro) que violan, por brazo.
  · Recall (sobre la sonda) = de los turnos de la sonda que violan, % que el detector marca en categoría PRIMARIA.
    Es una estimación con pocos casos: se reporta con su intervalo y no como valor puntual definitivo.
  · Intervalos: Wilson al 95 %. Acuerdo entre etiquetadores (binario estricto): acuerdo observado, acuerdo positivo y negativo
    (Feinstein & Cicchetti 1990), kappa de Cohen, PABAK y AC1 de Gwet (2008). Con prevalencia baja se reportan juntos.

Uso: python scripts/analizar_persona2.py --etiquetas etiquetas_persona2_E1.csv [--etiquetas2 etiquetas_persona2_E2.csv]
"""
import argparse
import csv
import statistics
import sys
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRIMARIAS = {"VOLICION", "COGNICION", "EMOCION", "HABLA"}
Z = 1.959964

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def wilson(x, n, z=Z):
    """Intervalo de Wilson al 95 % para una proporción x/n; (None, None) si n es 0. Se usa en lugar del intervalo normal porque los n por estrato son pequeños.

    Returns:
        Tupla (inferior, superior) acotada a [0, 1].
    """
    if not n:
        return (None, None)
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def acuerdo(a, b, c, d):
    """a = ambos sí · b = 1 sí y 2 no · c = 1 no y 2 sí · d = ambos no."""
    n = a + b + c + d
    if not n:
        return {"n": 0, "po": None, "p_pos": None, "p_neg": None, "kappa": None, "pabak": None, "ac1": None}
    po = (a + d) / n
    p1, p2 = (a + b) / n, (a + c) / n
    pe_k = p1 * p2 + (1 - p1) * (1 - p2)
    pi = (p1 + p2) / 2
    pe_g = 2 * pi * (1 - pi)
    return {"n": n, "po": po,
            "p_pos": 2 * a / (2 * a + b + c) if (2 * a + b + c) else None,
            "p_neg": 2 * d / (2 * d + b + c) if (2 * d + b + c) else None,
            "kappa": (po - pe_k) / (1 - pe_k) if pe_k != 1 else None,
            "pabak": 2 * po - 1,
            "ac1": (po - pe_g) / (1 - pe_g) if pe_g != 1 else None}


def leer(ruta):
    """Lee un CSV (UTF-8 con o sin BOM) como lista de dicts, una por fila."""
    with Path(ruta).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def etiquetas(ruta):
    """Indexa las etiquetas de un evaluador por id_muestra: veredicto, tipos atribuidos, si el turno sigue a una tirada y segundos empleados."""
    return {r["id_muestra"]: {"v": r["veredicto"], "tipos": [t for t in r["tipos"].split(";") if t],
                              "tirada": r["tras_tirada"] == "1", "seg": float(r["segundos"] or 0)} for r in leer(ruta)}


def detectada_primaria(h):
    """Indica si el detector marcó el turno con algún hallazgo de categoría primaria (la que cuenta para la tasa de persona2)."""
    return any(x.split(":")[0] in PRIMARIAS for x in (h or "").split(";") if x)


def analizar(ruta_et, ruta_clave, ruta_et2=None):
    """Resume la auditoría humana del detector persona2: precisión por estrato y brazo, prevalencia y recall con la sonda aleatoria, falsos negativos y, si hay segundo etiquetador, acuerdo entre ambos.

    Args:
        ruta_et: CSV de etiquetas del evaluador principal.
        ruta_clave: clave de la muestra (estrato, brazo, hallazgos del detector).
        ruta_et2: CSV del segundo evaluador, opcional.

    Returns:
        Dict con los agregados que consume reporte_md.
    """
    clave = {r["id_muestra"]: r for r in leer(ruta_clave)}
    et = etiquetas(ruta_et)
    res = {"n_etiquetados": len(et), "n_clave": len(clave), "por_estrato": Counter(), "dudoso": Counter(),
           "precision": {}, "sonda": {}, "sin_hallazgo": {}, "tipos": Counter(), "tras_tirada": 0, "viola_total": 0}
    cnt = defaultdict(lambda: {"n": 0, "si": 0, "dudoso": 0})
    for i, e in et.items():
        k = clave.get(i)
        if not k:
            continue
        res["por_estrato"][k["estrato"]] += 1
        if e["v"] == "dudoso":
            res["dudoso"][k["estrato"]] += 1
        if e["v"] in ("si", "dudoso"):
            res["tipos"].update(e["tipos"])
            res["tras_tirada"] += e["tirada"]
        res["viola_total"] += e["v"] == "si"
        if k["estrato"].startswith("primaria:") or k["estrato"] == "secundaria":
            for clave_g in (f"{k['estrato']}|{k['brazo']}", f"{k['estrato']}|todos",
                            f"PRIMARIA_TOTAL|{k['brazo']}" if k["estrato"].startswith("primaria:") else None,
                            "PRIMARIA_TOTAL|todos" if k["estrato"].startswith("primaria:") else None):
                if clave_g:
                    c = cnt[clave_g]; c["n"] += 1; c["si"] += e["v"] == "si"; c["dudoso"] += e["v"] == "dudoso"
    for g, c in cnt.items():
        n_ok = c["n"]
        res["precision"][g] = {"n": n_ok, "si": c["si"], "dudoso": c["dudoso"], "p": c["si"] / n_ok,
                               "ic": wilson(c["si"], n_ok), "p_indulgente": (c["si"] + c["dudoso"]) / n_ok,
                               "ic_indulgente": wilson(c["si"] + c["dudoso"], n_ok)}
    for brazo in ("G1", "G2"):
        f = [(clave[i], e) for i, e in et.items() if i in clave and clave[i]["estrato"] == "sonda_aleatoria" and clave[i]["brazo"] == brazo]
        if f:
            viola = [(k, e) for k, e in f if e["v"] == "si"]
            det = sum(detectada_primaria(k["hallazgos_detector"]) for k, _ in viola)
            res["sonda"][brazo] = {"n": len(f), "viola": len(viola), "ic": wilson(len(viola), len(f)),
                                   "dudoso": sum(e["v"] == "dudoso" for _, e in f),
                                   "viola_y_detectada": det, "recall": det / len(viola) if viola else None,
                                   "ic_recall": wilson(det, len(viola)),
                                   "detector_marca_primaria": sum(detectada_primaria(k["hallazgos_detector"]) for k, _ in f)}
        g = [(clave[i], e) for i, e in et.items() if i in clave and clave[i]["estrato"] == "sin_hallazgo" and clave[i]["brazo"] == brazo]
        if g:
            v = sum(e["v"] == "si" for _, e in g)
            res["sin_hallazgo"][brazo] = {"n": len(g), "viola": v, "ic": wilson(v, len(g))}
    res["segundos_mediana"] = statistics.median([e["seg"] for e in et.values() if e["seg"]]) if any(e["seg"] for e in et.values()) else None
    if ruta_et2:
        e2 = etiquetas(ruta_et2)
        a = b = c = d = 0
        for i in set(et) & set(e2):
            v1, v2 = et[i]["v"], e2[i]["v"]
            if "dudoso" in (v1, v2):
                continue
            a += (v1, v2) == ("si", "si"); b += (v1, v2) == ("si", "no"); c += (v1, v2) == ("no", "si"); d += (v1, v2) == ("no", "no")
        res["acuerdo"] = dict(acuerdo(a, b, c, d), a=a, b=b, c=c, d=d, en_comun=len(set(et) & set(e2)),
                              dudosos_excluidos=len(set(et) & set(e2)) - (a + b + c + d))
        res["acuerdo"]["ic_po"] = wilson(a + d, a + b + c + d)
    return res


def pct(x):
    """Formatea una proporción como porcentaje con un decimal; guion largo si es None."""
    return "—" if x is None else f"{100 * x:.1f} %"


def ic(t):
    """Formatea un intervalo (inferior, superior) como porcentajes; guion largo si es None."""
    return "—" if t[0] is None else f"[{100 * t[0]:.1f}–{100 * t[1]:.1f}]"


def reporte_md(r):
    """Genera el informe Markdown de la auditoría de persona2 a partir del dict de analizar()."""
    L = ["# Auditoría del detector persona2 (muestra de confirmación)", "",
         f"Etiquetados: {r['n_etiquetados']} de {r['n_clave']} · por estrato: " + ", ".join(f"{k} {v}" for k, v in sorted(r['por_estrato'].items())),
         f"· «dudoso»: {sum(r['dudoso'].values())} · mediana de tiempo por turno: {r['segundos_mediana'] if r['segundos_mediana'] is not None else '—'} s", "",
         "## Precisión (turnos marcados por el detector que el etiquetador juzga que violan)", "",
         "| estrato · brazo | n | viola | precisión estricta [IC 95 %] | precisión indulgente [IC 95 %] |", "|---|---|---|---|---|"]
    for g in sorted(r["precision"]):
        p = r["precision"][g]
        L.append(f"| {g.replace('|', ' · ')} | {p['n']} | {p['si']} | {pct(p['p'])} {ic(p['ic'])} | {pct(p['p_indulgente'])} {ic(p['ic_indulgente'])} |")
    L += ["", "## Prevalencia y recall (sonda aleatoria, sin filtro)", "",
          "| brazo | n | turnos que violan [IC 95 %] | el detector marca (primaria) alguno de ellos | recall estimado [IC 95 %] |", "|---|---|---|---|---|"]
    for b, s in sorted(r["sonda"].items()):
        L.append(f"| {b} | {s['n']} | {s['viola']} = {pct(s['viola'] / s['n'])} {ic(s['ic'])} | {s['viola_y_detectada']} de {s['viola']} | {pct(s['recall'])} {ic(s['ic_recall'])} |")
    L += ["", "Con pocos turnos que violan, el recall tiene un intervalo muy ancho: se reporta como cota, no como valor puntual.", ""]
    if r["sin_hallazgo"]:
        L += ["## Falsos negativos: turnos sin hallazgo con verbo mental de 2.ª persona no marcado", "", "| brazo | n | violan [IC 95 %] |", "|---|---|---|"]
        for b, s in sorted(r["sin_hallazgo"].items()):
            L.append(f"| {b} | {s['n']} | {s['viola']} = {pct(s['viola'] / s['n'])} {ic(s['ic'])} |")
        L.append("")
    L += ["## Tipos atribuidos cuando el etiquetador marca «viola» o «dudoso»", "",
          ", ".join(f"{k}: {v}" for k, v in r["tipos"].most_common()) or "(sin datos)",
          f"· tras una tirada declarada: {r['tras_tirada']}", ""]
    if "acuerdo" in r:
        a = r["acuerdo"]
        L += ["## Acuerdo entre etiquetadores (binario estricto; los «dudoso» se excluyen)", "",
              f"Turnos en común: {a['en_comun']} · comparables: {a['n']} · dudosos excluidos: {a['dudosos_excluidos']}",
              f"Tabla 2×2: ambos sí {a['a']} · 1 sí / 2 no {a['b']} · 1 no / 2 sí {a['c']} · ambos no {a['d']}", "",
              "| medida | valor |", "|---|---|",
              f"| acuerdo observado | {pct(a['po'])} {ic(a['ic_po'])} |", f"| acuerdo positivo | {pct(a['p_pos'])} |",
              f"| acuerdo negativo | {pct(a['p_neg'])} |",
              f"| kappa de Cohen | {'—' if a['kappa'] is None else f'{a['kappa']:.3f}'} |",
              f"| PABAK | {'—' if a['pabak'] is None else f'{a['pabak']:.3f}'} |",
              f"| AC1 de Gwet | {'—' if a['ac1'] is None else f'{a['ac1']:.3f}'} |", "",
              "Con prevalencia baja el kappa cae aunque el acuerdo sea alto; se reportan juntos el acuerdo positivo, el AC1 y el kappa (ninguno basta solo).", ""]
    return "\n".join(L)


def main():
    """Punto de entrada: analiza las etiquetas contra la clave, escribe el informe en --salida y lo imprime."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiquetas", required=True)
    ap.add_argument("--etiquetas2")
    ap.add_argument("--clave", default=str(RAIZ / "validacion" / "confirmacion_persona2_clave.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "reportes" / "auditoria_persona2.md"))
    a = ap.parse_args()
    md = reporte_md(analizar(a.etiquetas, a.clave, a.etiquetas2))
    Path(a.salida).write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
