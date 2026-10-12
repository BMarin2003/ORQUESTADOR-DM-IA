"""
Brecha OE-1: ¿qué son los «nombres no reconocidos»? Auditoría censal y determinista (solo lectura).

La tesis (recomendación de OE-1) pide separar nombres efectivamente inventados de PNJ legítimos
introducidos por el propio sistema antes de usar la cifra como evidencia. En vez de una muestra
manual, se clasifica CADA nombre marcado (v2, texto normalizado, mismas entidades vigentes por turno
que usa recalcular.py) contra la propia base:

  1. registrado_despues  la palabra forma parte de una entidad creada en ese turno o después
                         (el sistema la introdujo y el extractor la registró): NO es invención.
  2. lore                aparece con mayúscula en el lore (turno 0) o es nombre de un PJ:
                         vocabulario del mundo no registrado como entidad: NO es invención.
  3. palabra_comun       su forma en minúscula es frecuente en el corpus (>= MIN_MINUS y al menos
                         tantas veces como en mayúscula): título o sustantivo común capitalizado.
  4. recurrente          nunca registrada y marcada en >= MIN_TURNOS turnos distintos de la
                         campaña: entidad persistente que el estado no recoge (hueco de registro).
  5. efimero             el resto: candidato a nombre inventado y abandonado.

Salidas: docs/reportes/brechas/oe1_nombres.{csv,md} (+ ejemplos por categoría para revisión).

    $env:PYTHONUTF8="1"; py scripts/brechas/oe1_auditoria_nombres.py
"""
import csv
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                                   # noqa: E402
import instrumentos_texto as it                # noqa: E402
import pares as _pares                         # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

HASTA = 1400
MIN_MINUS = 10
MIN_TURNOS = 3
SALIDA = RAIZ / "docs" / "reportes" / "brechas"
RX_MAYUS = re.compile(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b")
RX_PAL = re.compile(r"\b[a-záéíóúñ]{3,}\b")
CATS = ["registrado_despues", "registrado_oculto", "lore", "palabra_comun", "recurrente", "efimero"]
PROBLEMA = {"recurrente", "efimero"}        # entidad que el estado nunca recoge


def marcar_campana(conn, par, brazo, cid):
    """Lista de marcas (turno, palabra, contexto) + vocabularios de la campaña."""
    dc = datos.DatosCampana(conn, cid, brazo, par)
    base = it.Contexto(pj_nombre=dc.pj_nombre, entidades=[], estados_pnj={}, brazo=brazo)
    creado = {}                                     # palabra -> primer turno en que existe una entidad que la contiene
    for e in dc._ents:
        t0 = e["creado"] if e["creado"] is not None else 0
        for w in [e["nombre"]] + [p for p in e["nombre"].split() if len(p) >= 3]:
            creado[w] = min(creado.get(w, 10 ** 9), t0)
    lore = set(RX_MAYUS.findall(dc.texto(0)))
    pjs = {p for n in dc.nombres_pj for p in n.split() if len(p) >= 3}
    marcas, textos = [], []
    for t in range(1, HASTA + 1):
        if t not in dc.turnos:
            continue
        texto = normalizar_turno(dc.texto(t), brazo)
        textos.append(texto)
        ctx = base.copia(entidades=dc._entidades_en(t))
        for w in it.nombres_no_reconocidos(texto, ctx):
            i = texto.find(w)
            marcas.append({"turno": t, "palabra": w, "ctx": texto[max(0, i - 90): i + 90].replace("\n", " ")})
    return marcas, creado, lore | pjs, textos


def clasificar(marcas, creado, lore, minus, mayus):
    """Clasifica cada marca de nombre no reconocido según la base: registrado después, registrado fuera de ventana, lore, palabra común, recurrente o efímero (candidato a invención).

    El orden de las reglas es parte del criterio y es determinista. Modifica y devuelve la lista de marcas.
    """
    turnos_por_palabra = defaultdict(set)
    for m in marcas:
        turnos_por_palabra[m["palabra"]].add(m["turno"])
    for m in marcas:
        w, t = m["palabra"], m["turno"]
        if w in creado and creado[w] >= t:
            m["cat"], m["retardo"] = "registrado_despues", creado[w] - t
        elif w in creado:
            m["cat"] = "registrado_oculto"          # objeto ya registrado, fuera de la ventana de 20 turnos
        elif w in lore:
            m["cat"] = "lore"
        elif minus[w.lower()] >= MIN_MINUS and minus[w.lower()] >= mayus[w]:
            m["cat"] = "palabra_comun"
        elif len(turnos_por_palabra[w]) >= MIN_TURNOS:
            m["cat"] = "recurrente"
        else:
            m["cat"] = "efimero"
    return marcas


def main():
    """Corre la auditoría censal de nombres en las 54 campañas, compara G1 y G2 por pares (Wilcoxon) y escribe el CSV y el informe."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from scipy.stats import wilcoxon
    conn = datos.abrir_conexion()
    por_camp, minus, mayus = {}, Counter(), Counter()
    for p in _pares.todos():
        par = f"{int(p['par']):02d}"
        for brazo, cid in (("G1", p["campaign_g1"]), ("G2", p["campaign_g2"])):
            marcas, creado, lore, textos = marcar_campana(conn, par, brazo, cid)
            for tx in textos:
                minus.update(RX_PAL.findall(tx))
                mayus.update(RX_MAYUS.findall(tx))
            por_camp[(brazo, par)] = (marcas, creado, lore, len(textos))
            print(f"  {brazo} par {par}: {len(marcas)} marcas", flush=True)
    filas, resumen = [], defaultdict(Counter)
    tasas = defaultdict(dict)       # métrica -> {(brazo, par): % de turnos}
    for (brazo, par), (marcas, creado, lore, n_turnos) in por_camp.items():
        clasificar(marcas, creado, lore, minus, mayus)
        por_turno = defaultdict(set)
        for m in marcas:
            resumen[brazo][m["cat"]] += 1
            por_turno[m["turno"]].add(m["cat"])
            filas.append({"brazo": brazo, "par": par, **{k: m.get(k, "") for k in ("turno", "palabra", "cat", "retardo", "ctx")}})
        tasas["marcado"][(brazo, par)] = 100 * len(por_turno) / n_turnos
        tasas["problema"][(brazo, par)] = 100 * sum(bool(c & PROBLEMA) for c in por_turno.values()) / n_turnos
        tasas["efimero"][(brazo, par)] = 100 * sum("efimero" in c for c in por_turno.values()) / n_turnos
        resumen[brazo]["_turnos_marcados"] += len(por_turno)
        resumen[brazo]["_turnos_problema"] += sum(bool(c & PROBLEMA) for c in por_turno.values())
        resumen[brazo]["_turnos_efimero"] += sum("efimero" in c for c in por_turno.values())
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / "oe1_nombres.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["brazo", "par", "turno", "palabra", "cat", "retardo", "ctx"])
        w.writeheader()
        w.writerows(filas)
    escribir_md(filas, resumen, tasas, wilcoxon)


def escribir_md(filas, resumen, tasas, wilcoxon):
    """Escribe el informe Markdown de la brecha OE-1: tabla por categoría, turnos marcados, comparación pareada y 5 ejemplos al azar por categoría (semilla fija) para revisión."""
    L = ["# Brecha OE-1: auditoría censal de «nombres no reconocidos»", "",
         f"Marcas totales: {len(filas)}. Clasificación determinista contra la base (ver docstring del script).", "",
         "| Categoría | G1 | G2 | ¿Invención? |", "|---|---|---|---|"]
    nota = {"registrado_despues": "no (el sistema la introdujo y la registró)", "registrado_oculto": "no (objeto registrado fuera de ventana)",
            "lore": "no (vocabulario del mundo)", "palabra_comun": "no (falso positivo léxico)",
            "recurrente": "entidad nunca registrada", "efimero": "candidato a invención"}
    for c in CATS:
        t1, t2 = sum(resumen["G1"][k] for k in CATS), sum(resumen["G2"][k] for k in CATS)
        L.append(f"| {c} | {resumen['G1'][c]} ({100 * resumen['G1'][c] / max(t1, 1):.1f} %) | "
                 f"{resumen['G2'][c]} ({100 * resumen['G2'][c] / max(t2, 1):.1f} %) | {nota[c]} |")
    L += ["", "| Turnos | G1 | G2 |", "|---|---|---|"]
    for k, et in (("_turnos_marcados", "marcados"), ("_turnos_problema", "con entidad nunca registrada"), ("_turnos_efimero", "con candidato a invención")):
        L.append(f"| {et} | {resumen['G1'][k]} | {resumen['G2'][k]} |")
    for k in ("_turnos_problema", "_turnos_efimero"):
        for b in ("G1", "G2"):
            L.append(f"\nPrecisión del indicador como detector ({k[8:]}) en {b}: "
                     f"{100 * resumen[b][k] / max(resumen[b]['_turnos_marcados'], 1):.1f} % de los turnos marcados.")
    L += ["", "## Comparación pareada (% de turnos por campaña, 27 pares)", "", "| Métrica | mediana G1 | mediana G2 | G1<G2 | p bilateral |", "|---|---|---|---|---|"]
    for met, dic in tasas.items():
        pares = sorted({p for _, p in dic})
        g1, g2 = [dic[("G1", p)] for p in pares], [dic[("G2", p)] for p in pares]
        d = [a - b for a, b in zip(g1, g2)]
        pv = wilcoxon(d).pvalue if any(d) else float("nan")
        L.append(f"| {met} | {sorted(g1)[13]:.2f} | {sorted(g2)[13]:.2f} | {sum(x < 0 for x in d)}/27 | {pv:.3g} |")
    random.seed(20261010)
    L += ["", "## Ejemplos por categoría (5 al azar, para revisión)"]
    for c in CATS:
        ej = [f for f in filas if f["cat"] == c]
        L.append(f"\n### {c}")
        for f in random.sample(ej, min(5, len(ej))):
            L.append(f"- {f['brazo']} par {f['par']} t{f['turno']} **{f['palabra']}**: …{f['ctx']}…")
    (SALIDA / "oe1_nombres.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
