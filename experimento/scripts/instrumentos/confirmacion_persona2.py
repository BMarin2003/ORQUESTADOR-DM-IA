#!/usr/bin/env python3
"""
confirmacion_persona2.py -- muestra CIEGA de CONFIRMACIÓN del detector persona2 (SOLO SELECT).

El detector está CONGELADO (ver docstring de evaluar_persona2.py). Este script solo usa turnos que NO están en
datos/validacion/persona2_desarrollo_turnos.csv (falla si ese archivo no existe) y NO ajusta nada del detector.

Semilla 20260921. Pool = todos los turnos de las 42 campañas (21 pares x 2 brazos) menos los de desarrollo,
con los mismos criterios de validez que la evaluación (dm_output >= 20 caracteres y acción del jugador no vacía).
Se analiza el pool completo con nlp=None (misma salida que con spaCy: se comprueba sobre las filas elegidas).

Estratos (cada turno aparece una sola vez; se sortea en este orden):
  1. sonda_aleatoria      200 turnos al azar (100 por brazo), SIN filtro; categoria_detectada vacía y turno completo
  2. primaria:<CAT>       para VOLICION, EMOCION, HABLA, COGNICION (en ese orden) hasta 30 hallazgos por brazo
  3. muerte_pj            (extra) hasta 20 turnos donde narra_muerte_pj marca algo, si los hay
  4. secundaria           40 hallazgos ACCION_NO_DECLARADA en total (ambos brazos, al azar)
  5. sin_hallazgo         100 turnos sin hallazgo con un verbo mental de 2.ª persona descartado o no listado
Salidas: datos/validacion/confirmacion_persona2_muestra.csv (ciega: id_muestra, frase_evidencia_o_turno_completo,
accion_jugador, categoria_detectada, etiqueta_manual, nota) y datos/validacion/confirmacion_persona2_clave.csv
(id_muestra, campaign_id, turn_id, brazo, par, estrato, categoria_asignada, hallazgos_detector).
Etiquetas: USURPA | NO_USURPA | AMBIGUO.  Las filas de sonda y sin_hallazgo son turnos completos con la categoría en blanco
(no se distinguen a simple vista); en ellas etiqueta USURPA si el DM narra pensamiento/emoción/diálogo/decisión del PJ
(usurpación mental/verbal) y anota en «nota» si además narra una acción física no declarada.

Uso: PYTHONUTF8=1 py experimento/scripts/instrumentos/confirmacion_persona2.py
"""
import csv
import random
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import evaluar_persona2 as E  # noqa: E402
import persona2 as P  # noqa: E402
import psycopg  # noqa: E402
import spacy  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

SEMILLA = 20260921
DIR = E.RAIZ / "datos" / "validacion"
DEV = DIR / "persona2_desarrollo_turnos.csv"
MUESTRA = DIR / "confirmacion_persona2_muestra.csv"
CLAVE = DIR / "confirmacion_persona2_clave.csv"
ORDEN_PRIMARIAS = ["VOLICION", "EMOCION", "HABLA", "COGNICION"]


def cargar_dev():
    """Claves (campaign_id, turn_id) de los turnos de desarrollo, que la muestra de confirmación debe excluir; aborta si falta el CSV."""
    if not DEV.exists():
        sys.exit(f"ERROR: falta {DEV}; ejecuta procedencia_persona2.py primero.")
    with open(DEV, encoding="utf-8", newline="") as fh:
        return {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}


def cargar_pool(conn, dev, nombres):
    """Pool de turnos válidos de las 42 campañas (G1 y G2) que no son de desarrollo; consulta solo SELECT."""
    pool = []
    for e in E.cargar_pares():
        for brazo, cid in (("G1", e["campaign_g1"]), ("G2", e["campaign_g2"])):
            filas = conn.execute("SELECT turn_id, player_buffer, dm_output FROM turn_log "
                                 "WHERE campaign_id=%s AND turn_id >= 1 ORDER BY turn_id", (cid,)).fetchall()
            for f in filas:
                if (cid, f["turn_id"]) in dev or not E.turno_valido(f):
                    continue
                pool.append(E.registro(brazo, e, cid, f["turn_id"], f, nombres))
    return pool


def clave_turno(r):
    """Clave única (campaña, turno) de un registro."""
    return (r["campaign_id"], r["turn_id"])


def resumen_hallazgos(r):
    """Texto categoria:verbo:pN de los hallazgos del detector (más MUERTE_PJ) para la hoja clave."""
    partes = [f"{h['categoria']}:{h['verbo_lema']}:p{h['persona']}" for h in r["hall"]]
    if r["muerte"]:
        partes.append("MUERTE_PJ")
    return ";".join(partes)


def fila_con_hallazgo(r, cat, estrato):
    """Fila de muestra con la evidencia marcada; para una categoría elige primero el hallazgo de confianza alta y luego el más temprano."""
    if cat == "MUERTE_PJ":
        m = r["muerte"]
        ev, ini, fin = m["evidencia"], m["inicio"], m["fin"]
    else:
        h = sorted((h for h in r["hall"] if h["categoria"] == cat), key=lambda h: (h["confianza"] != "alta", h["inicio"]))[0]
        ev, ini, fin = h["evidencia"], h["inicio"], h["fin"]
    return {"rec": r, "estrato": estrato, "cat": cat, "texto": E.marcar(ev, r["dm"], ini, fin)}


def seleccionar(pool, rnd):
    """Sortea los estratos de la muestra ciega en el orden fijo del diseño (sonda, primarias, muerte PJ, secundaria, sin hallazgo); cada turno aparece una sola vez."""
    filas, usados = [], set()
    ordenado = sorted(pool, key=clave_turno)

    # 1. sonda aleatoria (100 por brazo) sin filtro
    for brazo in ("G1", "G2"):
        cand = [r for r in ordenado if r["brazo"] == brazo]
        for r in rnd.sample(cand, 100):
            usados.add(clave_turno(r))
            filas.append({"rec": r, "estrato": "sonda_aleatoria", "cat": "", "texto": r["dm"]})

    # 2. primarias, hasta 30 por brazo y categoría
    for cat in ORDEN_PRIMARIAS:
        for brazo in ("G1", "G2"):
            cand = [r for r in ordenado if r["brazo"] == brazo and clave_turno(r) not in usados
                    and any(h["categoria"] == cat for h in r["hall"])]
            for r in rnd.sample(cand, min(30, len(cand))):
                usados.add(clave_turno(r))
                filas.append(fila_con_hallazgo(r, cat, f"primaria:{cat}"))

    # 3. (extra) muerte del PJ
    cand = [r for r in ordenado if clave_turno(r) not in usados and r["muerte"]]
    for r in rnd.sample(cand, min(20, len(cand))):
        usados.add(clave_turno(r))
        filas.append(fila_con_hallazgo(r, "MUERTE_PJ", "muerte_pj"))

    # 4. secundaria: 40 en total
    cand = [r for r in ordenado if clave_turno(r) not in usados and any(h["categoria"] == E.SECUNDARIA for h in r["hall"])]
    for r in rnd.sample(cand, min(40, len(cand))):
        usados.add(clave_turno(r))
        filas.append(fila_con_hallazgo(r, E.SECUNDARIA, "secundaria"))

    # 5. sin hallazgo con verbo mental descartado/no listado
    cand = [r for r in ordenado if clave_turno(r) not in usados and not r["hall"] and not r["muerte"]
            and any(e["categoria_potencial"] in E.MENTALES for e in r["excl"])]
    for r in rnd.sample(cand, min(100, len(cand))):
        usados.add(clave_turno(r))
        filas.append({"rec": r, "estrato": "sin_hallazgo", "cat": "", "texto": r["dm"]})
    return filas


def escribir(filas, rnd):
    """Mezcla las filas, asigna ids opacos y escribe la muestra ciega (sin categoría real) y la clave con estrato y hallazgos."""
    rnd.shuffle(filas)
    for f, i in zip(filas, rnd.sample(range(100000, 1000000), len(filas))):
        f["id"] = f"C{i}"
    with open(MUESTRA, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["id_muestra", "frase_evidencia_o_turno_completo", "accion_jugador",
                    "categoria_detectada", "etiqueta_manual", "nota"])
        for f in filas:
            w.writerow([f["id"], f["texto"], f["rec"]["accion"], f["cat"], "", ""])
    with open(CLAVE, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["id_muestra", "campaign_id", "turn_id", "brazo", "par", "estrato", "categoria_asignada",
                    "hallazgos_detector"])
        for f in sorted(filas, key=lambda f: f["id"]):
            r = f["rec"]
            w.writerow([f["id"], r["campaign_id"], r["turn_id"], r["brazo"], r["par"], f["estrato"], f["cat"],
                        resumen_hallazgos(r)])


def tasas_poblacion(pool):
    """Imprime las tasas del detector congelado sobre todo el pool de no-desarrollo, con IC 95 % de Wilson por brazo."""
    print("\nTasas del detector CONGELADO sobre TODO el pool de no-desarrollo (% de turnos con >=1 hallazgo; IC 95 % Wilson):")
    por = {b: [r for r in pool if r["brazo"] == b] for b in ("G1", "G2")}
    print(f"  turnos: G1={len(por['G1'])}  G2={len(por['G2'])}")
    for nombre, cats in [(c, {c}) for c in E.PRIMARIAS] + [("PRIMARIA (4 categorías)", set(E.PRIMARIAS)),
                                                          ("SECUNDARIA (ACCION_NO_DECLARADA)", {E.SECUNDARIA})]:
        celdas = [E.celda(E.turnos_con(por[b], cats), len(por[b])) for b in ("G1", "G2")]
        print(f"  {nombre:34s} G1 {celdas[0]}   G2 {celdas[1]}")
    for b in ("G1", "G2"):
        n3 = sum(1 for r in por[b] for h in r["hall"] if h["persona"] == "3")
        nt = sum(1 for r in por[b] for h in r["hall"])
        nm = sum(1 for r in por[b] if r["muerte"])
        print(f"  {b}: hallazgos persona 3 = {n3} de {nt}; turnos con muerte del PJ = {nm}")


def main():
    """Orquesta la confirmación: carga pool, analiza con nlp=None, comprueba que spaCy da lo mismo en las filas elegidas y escribe la muestra."""
    dev = cargar_dev()
    nombres = E.cargar_nombres()
    with psycopg.connect(E.db.DSN, row_factory=dict_row) as conn:          # SOLO SELECT
        pool = cargar_pool(conn, dev, nombres)
    assert not any(clave_turno(r) in dev for r in pool)
    print(f"desarrollo: {len(dev)} turnos excluidos; pool de confirmación: {len(pool)} registros turno-brazo")
    E.analizar(pool, None)
    tasas_poblacion(pool)

    rnd = random.Random(SEMILLA)
    filas = seleccionar(pool, rnd)
    # comprobación: con spaCy la salida de las filas elegidas es idéntica a la de nlp=None
    nlp = spacy.load("es_core_news_sm", exclude=["ner", "parser"])
    dif = 0
    for f in filas:
        r = f["rec"]
        if P.detectar_usurpacion(r["dm"], r["accion"], nlp, r["nombre"]) != r["hall"]:
            dif += 1
    print(f"comprobación spaCy vs nlp=None en {len(filas)} filas elegidas: {dif} diferencias")
    escribir(filas, rnd)
    c = Counter((f["estrato"], f["rec"]["brazo"]) for f in filas)
    print(f"\nfilas escritas: {len(filas)}  -> {MUESTRA.name}, {CLAVE.name}")
    for k in sorted(c):
        print(f"  {k[0]:28s} {k[1]}: {c[k]}")


if __name__ == "__main__":
    main()
