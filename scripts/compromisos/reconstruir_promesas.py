"""Reconstruye los eventos de compromiso (promise_made/kept/broken) del corpus.

SOLO LEE. No escribe en la base.

Por qué existe: durante la generación el extractor SÍ reconocía promise_made
(extractor/contrato.json), y resolver_evento() lo convertía en un delta de
npc.affinity con su evidencia literal. Pero el tipo de evento no se guardaba
en state_deltas (promise_made no está en mutable_fields), así que
contexto_escena() nunca encontró compromisos que mostrar al DM.

Este script recupera el vínculo evento -> delta desde los logs por turno:
  sección [7]  "✓ evento <PNJ> · <event_kind>"
  sección [8]  "→ delta <id>: <PNJ> affinity <antes> → <después>"
y luego trae turno, PNJ y evidencia desde state_deltas por id de delta.

Uso (desde la raíz del repo):
  $env:PYTHONUTF8="1"; py scripts\\compromisos\\reconstruir_promesas.py
Salida: docs/reportes/compromisos/{eventos_compromiso.csv, resumen.md}
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "orquestador"))
from db import DSN  # noqa: E402  mismo DSN que el orquestador
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

LOGS = RAIZ / "logs"
SALIDA = RAIZ / "docs" / "reportes" / "compromisos"
KINDS = {"promise_made", "promise_kept", "promise_broken"}
TURNO_MAX = 1400

RE_EVENTO = re.compile(r"^\s*✓ evento (.+?) · (\w+)\s*$")
RE_AFIN = re.compile(r"^\s*→ delta (\d+): (.+?) affinity ")
RE_SECCION = re.compile(r"^### \[(\d+)\]\s*(.*)$")


def nombre_seccion(titulo):
    """G2 numera [7] validación y [8] escritura; G1 tiene más secciones y
    las numera [11]/[12]. Se identifican por el título, no por el número."""
    t = titulo.upper()
    if t.startswith("VALIDACI"):
        return "val"
    if t.startswith("ESCRITURA"):
        return "esc"
    return "otra"


def bloques(texto):
    """Parte un log en turnos: en ambos brazos cada turno empieza en [1]."""
    actual, sec = None, "otra"
    for linea in texto.splitlines():
        m = RE_SECCION.match(linea)
        if m and m.group(1) == "1":
            if actual is not None:
                yield actual
            actual, sec = defaultdict(list), "otra"
            continue
        if actual is None:
            continue
        if m:
            sec = nombre_seccion(m.group(2))
        else:
            actual[sec].append(linea)
    if actual is not None:
        yield actual


def emparejar(eventos, afines):
    """Empareja cada evento validado con su delta de afinidad, en orden y
    exigiendo el mismo nombre de PNJ. Devuelve (pares, sin_pareja)."""
    usados, pares, sueltos = set(), [], []
    for nombre, kind in eventos:
        idx = next((i for i, (_, n) in enumerate(afines)
                    if i not in usados and n == nombre), None)
        if idx is None:
            sueltos.append((nombre, kind))
            continue
        usados.add(idx)
        pares.append((int(afines[idx][0]), nombre, kind))
    return pares, sueltos


def leer_logs():
    """Recorre todos los logs .md (incluye reanudaciones solapadas: el
    duplicado se elimina después por id de delta)."""
    por_delta, sueltos, n_eventos = {}, Counter(), Counter()
    for ruta in sorted(LOGS.rglob("*.md")):
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        for b in bloques(texto):
            eventos = [m.groups() for l in b.get("val", [])
                       if (m := RE_EVENTO.match(l))]
            afines = [m.groups() for l in b.get("esc", [])
                      if (m := RE_AFIN.match(l))]
            pares, perdidos = emparejar(eventos, afines)
            for did, nombre, kind in pares:
                if kind in KINDS:
                    por_delta.setdefault(did, (kind, nombre, ruta.name))
            for _, kind in eventos:
                if kind in KINDS:
                    n_eventos[kind] += 1
            for nombre, kind in perdidos:
                if kind in KINDS:
                    sueltos[kind] += 1
                    if "--diag" in sys.argv and sueltos[kind] <= 6:
                        esc = [l.strip() for l in b.get("esc", []) if l.strip()]
                        print(f"[diag] {ruta.name} · {nombre} · {kind}\n"
                              f"       escritura: {esc[:4]}")
    return por_delta, sueltos, n_eventos


def consultar(ids):
    sql = """
        SELECT d.id AS delta_id, d.campaign_id, d.turn_id, d.entity_id,
               n.name AS pnj, d.evidence, c.title, c.architecture
          FROM state_deltas d
          JOIN campaigns c ON c.id = d.campaign_id
          LEFT JOIN npcs n ON n.id = d.entity_id
         WHERE d.id = ANY(%s) AND d.field_name = 'affinity'
           AND c.current_turn >= %s AND d.turn_id BETWEEN 1 AND %s"""
    with psycopg.connect(DSN, row_factory=dict_row) as c:
        return c.execute(sql, (list(ids), TURNO_MAX, TURNO_MAX)).fetchall()


def main():
    por_delta, sueltos, n_eventos = leer_logs()
    filas = consultar(por_delta.keys()) if por_delta else []
    for f in filas:
        kind, nombre_log, archivo = por_delta[f["delta_id"]]
        f["event_kind"], f["pnj_log"], f["log"] = kind, nombre_log, archivo
        m = re.search(r"Par (\d+)", f["title"] or "")
        f["par"] = int(m.group(1)) if m else None
        f["brazo"] = "G1" if f["architecture"] == "mas" else "G2"
    filas.sort(key=lambda f: (f["par"] or 0, f["brazo"], f["turn_id"]))

    SALIDA.mkdir(parents=True, exist_ok=True)
    cols = ["par", "brazo", "campaign_id", "turn_id", "event_kind", "pnj",
            "pnj_log", "delta_id", "evidence", "log"]
    with open(SALIDA / "eventos_compromiso.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)

    # conteo por par y brazo (los pares sin eventos cuentan como 0)
    pares = sorted({f["par"] for f in filas if f["par"]} | set(range(1, 28)))
    cuenta = Counter((f["par"], f["brazo"], f["event_kind"]) for f in filas)
    nombres_distintos = sum(1 for f in filas if f["pnj"] != f["pnj_log"])
    return filas, pares, cuenta, sueltos, n_eventos, nombres_distintos


def informe(filas, pares, cuenta, sueltos, n_eventos, nombres_distintos):
    L = ["# Eventos de compromiso reconstruidos desde los logs", "",
         "Solo lectura. Exploratorio: no decide ninguna hipótesis.", "",
         "## Auditoría de la reconstrucción", "",
         f"- Eventos de compromiso vistos en los logs (con duplicados de "
         f"reanudaciones): {dict(n_eventos)}",
         f"- Eventos sin delta de afinidad emparejado: {dict(sueltos)}",
         f"- Eventos únicos recuperados en las 54 campañas (turnos 1-1400): "
         f"{len(filas)}",
         f"- Filas donde el PNJ del log no coincide con el de la base: "
         f"{nombres_distintos}", "",
         "## Totales por brazo", "",
         "| Evento | G1 | G2 |", "|---|---|---|"]
    for k in sorted(KINDS):
        g1 = sum(cuenta[(p, "G1", k)] for p in pares)
        g2 = sum(cuenta[(p, "G2", k)] for p in pares)
        L.append(f"| {k} | {g1} | {g2} |")
    L += ["", "## promise_made por par", "", "| Par | G1 | G2 |",
          "|---|---|---|"]
    x = [cuenta[(p, "G1", "promise_made")] for p in pares]
    y = [cuenta[(p, "G2", "promise_made")] for p in pares]
    L += [f"| {p:02d} | {a} | {b} |" for p, a, b in zip(pares, x, y)]
    try:
        from scipy.stats import wilcoxon
        dif = [a - b for a, b in zip(x, y)]
        if any(dif):
            r = wilcoxon(x, y)
            L += ["", f"Wilcoxon pareado (promise_made, G1 vs G2): "
                  f"W = {r.statistic:.1f}, p = {r.pvalue:.4f}. Descriptivo."]
    except ImportError:
        L += ["", "scipy no disponible: sin prueba pareada."]
    (SALIDA / "resumen.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    informe(*main())
