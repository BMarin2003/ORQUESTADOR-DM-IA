#!/usr/bin/env python3
"""
Análisis del detector `persona2` (A3 / H1f): precisión y recall contra el etiquetado ciego de
evaluadores humanos, y acuerdo entre evaluadores (Cohen para pares, Fleiss para 2+) sobre el 20 %
de submuestra compartida. Kappa/PABAK/AC1 y Fleiss implementados a mano (sin scipy) -- mismas
fórmulas usadas y documentadas en scripts/analizar_brecha4.py (duplicadas a propósito ahí, no al
revés: este es el script original al que ese comentario se refiere). Verificadas en
scripts/test_analizar_persona2.py.

Diseño (fijado antes de ver resultados, ver docs/plan_A_detallado.md):
  - `--etiquetas` (1 archivo, obligatorio): etiquetado ciego de los 515 ítems de
    etiquetado_persona2_E1.html -- evaluador principal E1. Mientras el E1 humano no esté
    disponible puede usarse etiquetas_persona2_E1_IA-asistido.csv como proxy explícitamente
    marcado como tal (ver docs claude/persona2-auditoria-IA-analisis.md); en ese caso la sección 1
    de abajo es preliminar, no el resultado final de A3.
  - `--etiquetas2` (0 o más archivos): etiquetado ciego del subconjunto del 20 % (102 ítems,
    subconjunto EXACTO de los 515 -- verificado programáticamente) hecho con
    etiquetado_persona2_E2.html o una copia con el campo "evaluador" cambiado (E3, E4, ...). El
    diseño de "juez y parte" (nadie del equipo investigador puede evaluar) no limita CUÁNTOS
    evaluadores externos se usan, solo QUIÉN puede serlo -- con 2 o 3 se puede calcular Fleiss
    entre ellos y detectar a uno que rinde mal (mismo patrón que brecha 4, donde E2 resultó
    apresurado) en vez de quedar sin nada que reportar si el único evaluador falla.

Salida: docs/reportes/validacion_persona2.md (o --salida)

Uso:
  python scripts/analizar_persona2.py --etiquetas etiquetas_persona2_E1_IA-asistido.csv
  python scripts/analizar_persona2.py --etiquetas etiquetas_persona2_E1.csv \
      --etiquetas2 etiquetas_persona2_E2.csv etiquetas_persona2_E3.csv
"""
import argparse
import csv
import sys
from collections import Counter
from math import sqrt
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
Z = 1.959964
CATEGORIAS = ["no", "si", "dudoso"]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def wilson(x, n, z=Z):
    if not n:
        return (None, None)
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cohen_binario(a, b, c, d):
    """a=ambos sí · b=1 sí 2 no · c=1 no 2 sí · d=ambos no -- misma fórmula que
    scripts/analizar_brecha4.py:cohen_binario(), duplicada a propósito allá (documentado, mismo
    criterio en todo el proyecto) para no acoplar ese script a la ubicación exacta de este."""
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
    """tabla: {id_caso: {categoria: conteo}}. Fórmula estándar (Fleiss 1971) para N
    evaluadores/caso (N puede variar por caso si falta alguna respuesta -- se excluyen los casos
    con menos de 2 respuestas). Verificada en test_analizar_persona2.py contra un ejemplo de
    3 sujetos / 3 evaluadores con kappa=0.55 calculado a mano."""
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
    with Path(ruta).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def positivo(veredicto, modo):
    """modo='estricto': solo 'si' cuenta como violación. modo='amplio': 'si' o 'dudoso'."""
    if modo == "estricto":
        return veredicto == "si"
    return veredicto in ("si", "dudoso")


def matriz_confusion(clave, etiquetas, ids, modo):
    tp = fp = tn = fn = 0
    for i in ids:
        if i not in clave or i not in etiquetas:
            continue
        pred = bool(clave[i]["categoria_asignada"].strip())
        humano = positivo(etiquetas[i], modo)
        tp += pred and humano
        fp += pred and not humano
        fn += (not pred) and humano
        tn += (not pred) and (not humano)
    return tp, fp, tn, fn


def fmt_pct(v):
    return "—" if v is None else f"{v:.1%}"


def fmt_ci(lo, hi):
    return "—" if lo is None else f"{lo:.1%}–{hi:.1%}"


def fmt_num(v, nd=3):
    return "—" if v is None else f"{v:.{nd}f}"


def cohen_amplio(a_veredictos, b_veredictos, ids):
    """Cohen binario (amplio: si+dudoso = positivo) entre dos diccionarios id->veredicto,
    restringido a los ids que ambos cubren."""
    comunes = [i for i in ids if i in a_veredictos and i in b_veredictos]
    aa = sum(positivo(a_veredictos[i], "amplio") and positivo(b_veredictos[i], "amplio") for i in comunes)
    bb = sum(positivo(a_veredictos[i], "amplio") and not positivo(b_veredictos[i], "amplio") for i in comunes)
    cc = sum((not positivo(a_veredictos[i], "amplio")) and positivo(b_veredictos[i], "amplio") for i in comunes)
    dd = sum((not positivo(a_veredictos[i], "amplio")) and (not positivo(b_veredictos[i], "amplio")) for i in comunes)
    return cohen_binario(aa, bb, cc, dd)


def mayoria_binaria(veredictos_por_evaluador, i):
    """Veredicto binario (amplio) mayoritario entre evaluadores que respondieron el ítem i.
    Empate -> 'sin_mayoria'."""
    votos = [positivo(d[i], "amplio") for d in veredictos_por_evaluador.values() if i in d]
    if not votos:
        return None
    conteo = Counter(votos)
    top, n_top = conteo.most_common(1)[0]
    empatados = [v for v, n in conteo.items() if n == n_top]
    if len(empatados) > 1:
        return "sin_mayoria"
    return "si" if top else "no"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiquetas", required=True,
                     help="CSV del evaluador principal (515 ítems, etiquetado_persona2_E1.html)")
    ap.add_argument("--etiquetas2", nargs="*", default=[],
                     help="0+ CSV del subconjunto del 20%% (102 ítems, etiquetado_persona2_E2.html "
                          "o copias con --evaluador distinto)")
    ap.add_argument("--clave", default=str(RAIZ / "validacion" / "confirmacion_persona2_clave.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "reportes" / "validacion_persona2.md"))
    args = ap.parse_args()

    clave = {r["id_muestra"]: r for r in leer(args.clave)}
    ids_515 = sorted(clave)

    filas_p = leer(args.etiquetas)
    principal_nombre = filas_p[0]["evaluador"] if filas_p else Path(args.etiquetas).stem
    principal = {r["id_muestra"]: r["veredicto"] for r in filas_p}
    faltan_p = [i for i in ids_515 if i not in principal]

    secundarios = {}
    for ruta in args.etiquetas2:
        filas = leer(ruta)
        nombre = filas[0]["evaluador"] if filas else Path(ruta).stem
        if nombre in secundarios:
            nombre = f"{nombre}_{Path(ruta).stem}"
        secundarios[nombre] = {r["id_muestra"]: r["veredicto"] for r in filas}

    conjuntos = {n: frozenset(d) for n, d in secundarios.items()}
    ids_20 = sorted(set().union(*conjuntos.values())) if secundarios else []
    mismos_conjuntos = len(set(conjuntos.values())) <= 1

    out = ["# Validación persona2 (A3 / H1f) — resultado\n"]
    out.append(f"Evaluador principal: **{principal_nombre}** ({len(principal)}/{len(ids_515)} ítems "
                f"de la clave, oculta durante el etiquetado).\n")
    if faltan_p:
        out.append(f"- ⚠ {principal_nombre} no respondió {len(faltan_p)} de {len(ids_515)} ítems "
                    f"todavía (export parcial).\n")
    if secundarios:
        cobertura = f"{len(ids_20)} ítems" + ("" if mismos_conjuntos else
                     " — ⚠ los conjuntos NO coinciden exactamente entre evaluadores, revisar exports")
        out.append(f"Evaluadores del subconjunto del 20 %: **{', '.join(sorted(secundarios))}** "
                    f"({cobertura}).\n")
    else:
        out.append("Sin evaluadores del subconjunto del 20 % todavía: solo se reporta la sección 1 "
                    "(detector vs. evaluador principal).\n")

    # === 1. Detector vs. evaluador principal (515 ítems) ===
    out.append("## 1. Detector vs. evaluador principal (515 ítems)\n")
    out.append("| Modo | N | TP | FP | TN | FN | Precisión | IC95% | Recall | IC95% | F1 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for modo, etiqueta in (("estricto", "Estricto (solo `si`)"), ("amplio", "Amplio (`si`+`dudoso`)")):
        tp, fp, tn, fn = matriz_confusion(clave, principal, ids_515, modo)
        n = tp + fp + tn + fn
        precision = tp / (tp + fp) if (tp + fp) else None
        recall = tp / (tp + fn) if (tp + fn) else None
        f1 = (2 * precision * recall / (precision + recall)
              if precision and recall and (precision + recall) else None)
        p_lo, p_hi = wilson(tp, tp + fp) if (tp + fp) else (None, None)
        r_lo, r_hi = wilson(tp, tp + fn) if (tp + fn) else (None, None)
        out.append(f"| {etiqueta} | {n} | {tp} | {fp} | {tn} | {fn} | {fmt_pct(precision)} | "
                    f"{fmt_ci(p_lo, p_hi)} | {fmt_pct(recall)} | {fmt_ci(r_lo, r_hi)} | "
                    f"{fmt_num(f1)} |")
    out.append("")

    if secundarios:
        # === 2. Principal vs. cada evaluador del 20 % ===
        out.append("## 2. Acuerdo: evaluador principal vs. cada evaluador del 20 % (ítems compartidos)\n")
        out.append("Sirve para validar si el evaluador principal (IA-asistido mientras no haya un "
                    "E1 humano) es un proxy razonable de juicio humano — ver "
                    "docs claude/persona2-auditoria-IA-analisis.md.\n")
        out.append("| Evaluador | n común | % acuerdo | kappa Cohen | PABAK | AC1 de Gwet |")
        out.append("|---|---|---|---|---|---|")
        for nombre, etq in sorted(secundarios.items()):
            r = cohen_amplio(principal, etq, ids_20)
            out.append(f"| {nombre} | {r['n']} | {fmt_pct(r['po'])} | {fmt_num(r['kappa'])} | "
                        f"{fmt_num(r['pabak'])} | {fmt_num(r['ac1'])} |")
        out.append("")

    if len(secundarios) >= 2:
        # === 3. Acuerdo entre evaluadores del 20 % (pares + Fleiss) ===
        out.append("## 3. Acuerdo entre evaluadores del 20 % (mide si el criterio humano es fiable)\n")
        nombres = sorted(secundarios)
        tabla = {}
        for i in ids_20:
            conteo = Counter()
            for nombre in nombres:
                v = secundarios[nombre].get(i)
                if v in CATEGORIAS:
                    conteo[v] += 1
            if conteo:
                tabla[i] = dict(conteo)
        kf = fleiss_kappa(tabla, CATEGORIAS)
        out.append(f"- Kappa de Fleiss ({len(nombres)} evaluadores, 3 categorías no/si/dudoso): "
                    f"**{fmt_num(kf)}**")
        out.append("")
        out.append("| Par | n común | % acuerdo | kappa Cohen | PABAK | AC1 de Gwet |")
        out.append("|---|---|---|---|---|---|")
        for a in range(len(nombres)):
            for b in range(a + 1, len(nombres)):
                e1, e2 = nombres[a], nombres[b]
                r = cohen_amplio(secundarios[e1], secundarios[e2], ids_20)
                out.append(f"| {e1}–{e2} | {r['n']} | {fmt_pct(r['po'])} | {fmt_num(r['kappa'])} | "
                            f"{fmt_num(r['pabak'])} | {fmt_num(r['ac1'])} |")
        out.append("")

        # === 4. Consenso mayoritario humano vs. detector, y vs. principal ===
        out.append("## 4. Consenso mayoritario del 20 % (mayoría entre evaluadores del subconjunto)\n")
        consenso = {i: mayoria_binaria(secundarios, i) for i in ids_20}
        n_sin_mayoria = sum(1 for v in consenso.values() if v == "sin_mayoria")
        out.append(f"Empates (sin mayoría, excluidos de precisión/recall): {n_sin_mayoria} de {len(ids_20)}.\n")

        tp = fp = tn = fn = 0
        for i in ids_20:
            v = consenso.get(i)
            if v is None or v == "sin_mayoria":
                continue
            pred = bool(clave[i]["categoria_asignada"].strip())
            humano = v == "si"
            tp += pred and humano
            fp += pred and not humano
            fn += (not pred) and humano
            tn += (not pred) and (not humano)
        n = tp + fp + tn + fn
        precision = tp / (tp + fp) if (tp + fp) else None
        recall = tp / (tp + fn) if (tp + fn) else None
        p_lo, p_hi = wilson(tp, tp + fp) if (tp + fp) else (None, None)
        r_lo, r_hi = wilson(tp, tp + fn) if (tp + fn) else (None, None)
        out.append(f"**Detector vs. consenso mayoritario humano** (n={n}, solo humano real, sin IA): "
                    f"TP={tp} FP={fp} TN={tn} FN={fn}.")
        out.append(f"- Precisión: {fmt_pct(precision)} (IC95% Wilson {fmt_ci(p_lo, p_hi)})")
        out.append(f"- Recall: {fmt_pct(recall)} (IC95% Wilson {fmt_ci(r_lo, r_hi)})")
        out.append("")

        consenso_bin = {i: v for i, v in consenso.items() if v in ("si", "no")}
        aa = sum(positivo(principal.get(i, ""), "amplio") and v == "si" for i, v in consenso_bin.items() if i in principal)
        bb = sum(positivo(principal.get(i, ""), "amplio") and v == "no" for i, v in consenso_bin.items() if i in principal)
        cc = sum((not positivo(principal.get(i, ""), "amplio")) and v == "si" for i, v in consenso_bin.items() if i in principal)
        dd = sum((not positivo(principal.get(i, ""), "amplio")) and v == "no" for i, v in consenso_bin.items() if i in principal)
        r = cohen_binario(aa, bb, cc, dd)
        out.append(f"**{principal_nombre} vs. consenso mayoritario humano**: n={r['n']}, "
                    f"acuerdo={fmt_pct(r['po'])}, kappa={fmt_num(r['kappa'])}. "
                    f"{'Si el acuerdo es alto, el proxy queda razonablemente validado para los ' + str(len(ids_515) - len(ids_20)) + ' ítems restantes que ningún humano etiquetó; si es bajo, revisar los criterios antes de citar la sección 1 en la tesis.' if r['kappa'] is not None else ''}")
        out.append("")
    elif secundarios:
        out.append("## 3-4. Acuerdo entre evaluadores del 20 % y consenso mayoritario\n")
        out.append("Con un solo evaluador del subconjunto no hay forma de calcular Fleiss ni un "
                    "consenso mayoritario, ni de detectar si ese evaluador etiquetó apurado o con "
                    "criterio distinto (fue justamente lo que pasó con E2 en la validación de "
                    "brecha 4). Sección 2 arriba sigue siendo válida (principal vs. este evaluador); "
                    "si se suma un segundo o tercer evaluador del 20 % después, volver a correr "
                    "este script con todos los `--etiquetas2` juntos para tener esto también.\n")

    out.append("## Nota metodológica")
    out.append("«Violación» para precisión/recall = veredicto humano 'si' (modo estricto) o "
                "'si'/'dudoso' (modo amplio). El detector se considera positivo cuando "
                "`categoria_asignada` no está vacío en la clave. La clave nunca se muestra a los "
                "evaluadores durante el etiquetado (diseño ciego). Ningún evaluador (principal ni "
                "del 20 %) puede pertenecer al equipo investigador (mismo principio de "
                "juez-y-parte que en brecha 4) — no hay límite de cuántos evaluadores externos se "
                "usen, solo de quién puede serlo.")

    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.salida).write_text("\n".join(out), encoding="utf-8")
    print(f"-> {args.salida}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
