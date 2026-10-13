#!/usr/bin/env python3
"""
Análisis de la validación brecha 4 (OE-5/H1e): acuerdo entre evaluadores (kappa de Fleiss,
N evaluadores) y comparación contra los candidatos automáticos (cl2_pnj_inactivo_actua
refinado, y Jericho recall donde aplica). Solo lee CSV (sin base de datos), mismo patrón que
experimento/scripts/analizar_persona2.py -- kappa/PABAK/AC1 implementados a mano, sin scipy, mismas
fórmulas (Cohen para pares, Wilson para los IC) documentadas ahí.

Entradas
  --etiquetas   1 o más CSV exportados por datos/validacion/validacion_brecha4_<E>.html (uno por evaluador)
  --clave       datos/validacion/brecha4_clave.csv (por defecto) -- estrato real de cada caso, NO se le
                muestra nunca a los evaluadores, solo se usa aquí para comparar.
Salida: docs/reportes/validacion_brecha4.md (o --salida)

Definiciones (fijadas en experimento/scripts/validacion_brecha4_generar.py, antes de ver las respuestas):
  · Verdad de referencia para cl2_pnj_inactivo_actua refinado = el estrato del caso: 'actuando' es
    positivo (el refinamiento sintáctico dice que SÍ hay error de continuidad), 'solo_referenciado'
    es negativo. 'flagged_sin_refinar' aparece solo si spaCy no estaba disponible al generar la
    muestra -- se reporta aparte, sin verdad de referencia de ese instrumento.
  · Verdad de referencia para Jericho recall = solo el estrato 'silencio' tiene una (por
    construcción, todos son jericho_qa_recall()=no_reconocido para la transición de estado
    original) -- 'actuando'/'solo_referenciado' NO tienen un veredicto de Jericho comparable,
    porque Jericho valida si la TRANSICIÓN se narró, no si una mención posterior es un error de
    continuidad -- son constructos relacionados pero distintos, no se fuerza un número ahí.
  · Verdad humana por caso = veredicto MAYORITARIO entre evaluadores (activo/retrospectivo/no_aplica);
    empate a 2 se reporta como 'sin_mayoria' y se excluye de precisión/recall (no de kappa).
  · «Error de continuidad» (para precisión/recall) = veredicto humano 'activo'. 'retrospectivo' y
    'no_aplica' cuentan como «no es error».

Uso: python experimento/scripts/analizar_brecha4.py --etiquetas validacion_brecha4_E1.csv validacion_brecha4_E2.csv validacion_brecha4_E3.csv
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
Z = 1.959964
CATEGORIAS = ["activo", "retrospectivo", "no_aplica"]

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


def cohen_binario(a, b, c, d):
    """a=ambos sí · b=1 sí 2 no · c=1 no 2 sí · d=ambos no -- misma fórmula que
    experimento/scripts/analizar_persona2.py:acuerdo(), duplicada a propósito (documentado, mismo criterio
    que el resto del proyecto) para no acoplar este script a la ubicación exacta de ese otro."""
    n = a + b + c + d
    if not n:
        return {"n": 0, "po": None, "kappa": None, "pabak": None, "ac1": None}
    po = (a + d) / n
    p1, p2 = (a + b) / n, (a + c) / n
    pe_k = p1 * p2 + (1 - p1) * (1 - p2)
    pi = (p1 + p2) / 2
    pe_g = 2 * pi * (1 - pi)
    return {"n": n, "po": po,
            "kappa": (po - pe_k) / (1 - pe_k) if pe_k != 1 else None,
            "pabak": 2 * po - 1,
            "ac1": (po - pe_g) / (1 - pe_g) if pe_g != 1 else None}


def fleiss_kappa(tabla, categorias):
    """tabla: {id_caso: {categoria: conteo}}. Fórmula estándar (Fleiss 1971): kappa de Fleiss
    para N evaluadores/caso (N puede variar por caso si falta alguna respuesta -- se excluyen
    los casos con menos de 2 respuestas)."""
    filas = [(cid, {cat: r.get(cat, 0) for cat in categorias})
             for cid, r in tabla.items() if sum(r.values()) >= 2]
    if not filas:
        return None
    n_por_fila = [sum(r.values()) for _, r in filas]
    N = len(filas)
    n_bar = sum(n_por_fila) / N
    p_j = {cat: sum(r[cat] for _, r in filas) / (N * n_bar) for cat in categorias}
    Pe = sum(p_j[cat] ** 2 for cat in categorias)
    Pi_por_fila = []
    for (_, r), n_i in zip(filas, n_por_fila):
        if n_i < 2:
            continue
        Pi_por_fila.append((sum(v * v for v in r.values()) - n_i) / (n_i * (n_i - 1)))
    P_bar = sum(Pi_por_fila) / len(Pi_por_fila)
    if Pe == 1:
        return None
    return (P_bar - Pe) / (1 - Pe)


def leer(ruta):
    """Lee un CSV (UTF-8 con o sin BOM) como lista de dicts, una por fila."""
    with Path(ruta).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    """Calcula el acuerdo entre evaluadores humanos (Fleiss) sobre la validación de la brecha 4 y lo contrasta con la clave del detector.

    Lee los CSV de etiquetas (--etiquetas), cruza con la clave y escribe el informe Markdown en --salida.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiquetas", nargs="+", required=True)
    ap.add_argument("--clave", default=str(RAIZ / "datos" / "validacion" / "brecha4_clave.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "reportes" / "validacion_brecha4.md"))
    args = ap.parse_args()

    clave = {r["id"]: r for r in leer(args.clave)}
    por_evaluador = {}
    for ruta in args.etiquetas:
        filas = leer(ruta)
        ev = filas[0]["evaluador"] if filas else Path(ruta).stem
        por_evaluador[ev] = {r["id_caso"]: r["veredicto"] for r in filas}

    evaluadores = sorted(por_evaluador)
    ids = sorted(clave)
    faltantes = {ev: [i for i in ids if i not in por_evaluador[ev]] for ev in evaluadores}

    # --- tabla para Fleiss: {id: {categoria: conteo}}
    tabla = {}
    for i in ids:
        conteo = Counter()
        for ev in evaluadores:
            v = por_evaluador[ev].get(i)
            if v in CATEGORIAS:
                conteo[v] += 1
        if conteo:
            tabla[i] = dict(conteo)
    kappa_fleiss = fleiss_kappa(tabla, CATEGORIAS)

    # --- veredicto mayoritario humano (binarizado: activo = error de continuidad)
    mayoria = {}
    for i in ids:
        conteo = Counter(por_evaluador[ev].get(i) for ev in evaluadores if i in por_evaluador[ev])
        conteo.pop(None, None)
        if not conteo:
            continue
        top, n_top = conteo.most_common(1)[0]
        empatados = [c for c, n in conteo.items() if n == n_top]
        mayoria[i] = top if len(empatados) == 1 else "sin_mayoria"

    # --- pares de evaluadores: Cohen binario (activo vs no) sobre casos que ambos respondieron
    lineas_pares = []
    for a in range(len(evaluadores)):
        for b in range(a + 1, len(evaluadores)):
            e1, e2 = evaluadores[a], evaluadores[b]
            comunes = [i for i in ids if i in por_evaluador[e1] and i in por_evaluador[e2]]
            aa = sum(por_evaluador[e1][i] == "activo" and por_evaluador[e2][i] == "activo" for i in comunes)
            bb = sum(por_evaluador[e1][i] == "activo" and por_evaluador[e2][i] != "activo" for i in comunes)
            cc = sum(por_evaluador[e1][i] != "activo" and por_evaluador[e2][i] == "activo" for i in comunes)
            dd = sum(por_evaluador[e1][i] != "activo" and por_evaluador[e2][i] != "activo" for i in comunes)
            r = cohen_binario(aa, bb, cc, dd)
            lineas_pares.append((e1, e2, r))

    # --- comparación contra cl2_pnj_inactivo_actua refinado (estrato actuando/solo_referenciado)
    tp = fp = tn = fn = 0
    for i in ids:
        estrato = clave[i]["estrato"]
        if estrato not in ("actuando", "solo_referenciado") or i not in mayoria or mayoria[i] == "sin_mayoria":
            continue
        pred_positivo = estrato == "actuando"
        humano_positivo = mayoria[i] == "activo"
        tp += pred_positivo and humano_positivo
        fp += pred_positivo and not humano_positivo
        fn += (not pred_positivo) and humano_positivo
        tn += (not pred_positivo) and (not humano_positivo)
    n_refinado = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None

    # --- comparación contra Jericho (solo estrato 'silencio': todos son 'no_reconocido' por
    # construcción, así que aquí solo se puede medir si el humano CONFIRMA que efectivamente no
    # hay error -- Jericho predice implícitamente "no_aplica"/consistente para todos estos).
    n_silencio = sum(1 for i in ids if clave[i]["estrato"] == "silencio")
    silencio_confirmado = sum(1 for i in ids if clave[i]["estrato"] == "silencio"
                              and mayoria.get(i) in ("retrospectivo", "no_aplica"))
    silencio_activo = sum(1 for i in ids if clave[i]["estrato"] == "silencio"
                          and mayoria.get(i) == "activo")

    out = [
        "# Validación brecha 4 (OE-5/H1e) — resultado\n",
        f"Evaluadores: {', '.join(evaluadores)}. Casos en la clave: {len(ids)}.\n",
    ]
    for ev in evaluadores:
        if faltantes[ev]:
            out.append(f"- ⚠ {ev} no respondió {len(faltantes[ev])} de {len(ids)} casos "
                       f"todavía (export parcial).")
    out.append("")
    out.append("## Acuerdo entre evaluadores")
    out.append(f"- Kappa de Fleiss ({len(evaluadores)} evaluadores, 3 categorías): "
               f"**{'—' if kappa_fleiss is None else f'{kappa_fleiss:.3f}'}**  "
               f"(precedente citable: Chen, Wang, Yu & Zhang 2023, AAAI, Fleiss' Kappa=0.671, "
               f"4 evaluadores, escala 1-3, consistencia de persona.)")
    out.append("")
    out.append("| Par | n común | % acuerdo | kappa Cohen (bin. activo/no) | AC1 de Gwet |")
    out.append("|---|---|---|---|---|")
    for e1, e2, r in lineas_pares:
        po_txt = "—" if r["po"] is None else f"{r['po']:.1%}"
        kappa_txt = "—" if r["kappa"] is None else f"{r['kappa']:.3f}"
        ac1_txt = "—" if r["ac1"] is None else f"{r['ac1']:.3f}"
        out.append(f"| {e1}–{e2} | {r['n']} | {po_txt} | {kappa_txt} | {ac1_txt} |")
    out.append("")
    out.append("## cl2_pnj_inactivo_actua refinado vs. veredicto humano mayoritario")
    out.append(f"n={n_refinado} (estratos actuando/solo_referenciado con mayoría humana clara). "
               f"TP={tp} FP={fp} TN={tn} FN={fn}.")
    if precision is not None:
        lo, hi = wilson(tp, tp + fp)
        out.append(f"- Precisión: {precision:.1%} (IC95% Wilson {lo:.1%}–{hi:.1%})")
    if recall is not None:
        lo, hi = wilson(tp, tp + fn)
        out.append(f"- Recall: {recall:.1%} (IC95% Wilson {lo:.1%}–{hi:.1%})")
    out.append("")
    out.append("## Jericho recall (estrato 'silencio' — casos donde no reconoció nada)")
    out.append(f"n={n_silencio}. De estos, el humano confirma «no hay error» (retrospectivo/no_aplica) "
              f"en {silencio_confirmado} y encuentra «lo narra activo» en {silencio_activo} — "
              f"este último grupo son falsos negativos de Jericho (silencio que SÍ escondía un "
              f"error de continuidad no detectado por el vocabulario léxico).")
    out.append("")
    out.append("## Nota metodológica")
    out.append("Jericho recall valida si la TRANSICIÓN de estado se narró; cl2_pnj_inactivo_actua "
              "y Kev validan si una mención POSTERIOR trata al PNJ como activo. Son constructos "
              "relacionados pero no idénticos — por eso Jericho solo tiene verdad de referencia "
              "en el estrato 'silencio' arriba, no en 'actuando'/'solo_referenciado'.")

    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.salida).write_text("\n".join(out), encoding="utf-8")
    print(f"-> {args.salida}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
