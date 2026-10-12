"""
A4d sobre las 42 campañas: `persona2` v2b (CONGELADO; hashes en validacion/persona2_congelado.sha256) aplicado a todos los turnos válidos sobre
texto NORMALIZADO, con nlp=None (el detector da la misma salida con y sin spaCy; se comprobó en confirmacion_persona2.py). Un CSV por campaña en
datos_v2/persona2/parNN_G?.csv: turn_id, en_desarrollo (1 si el turno se usó para construir el detector), primaria, cada categoría, secundaria, muerte.
PRIMARIA = VOLICION|COGNICION|EMOCION|HABLA (regla de oro del prompt del DM); SECUNDARIA = ACCION_NO_DECLARADA (experimental).

    PYTHONUTF8=1 py scripts/reporte_v2/recalcular_persona2.py [--pares 07,08] [--forzar]
"""
import argparse
import csv
import hashlib
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "scripts" / "instrumentos", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                                   # noqa: E402
import pares as _pares                         # noqa: E402
import persona2 as P                           # noqa: E402
from evaluar_persona2 import cargar_nombres, jugador, turno_valido   # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

DESTINO = RAIZ / "datos_v2" / "persona2"
PRIM = ["VOLICION", "COGNICION", "EMOCION", "HABLA"]
COLUMNAS = ["turn_id", "en_desarrollo", "primaria"] + PRIM + ["secundaria", "muerte"]


def congelado_ok():
    """Verifica que persona2.py y el léxico siguen siendo los congelados."""
    ref = {}
    for linea in (RAIZ / "validacion" / "persona2_congelado.sha256").read_text(encoding="utf-8").splitlines():
        if linea and not linea.startswith("#"):
            h, ruta = linea.split(None, 1)
            ref[ruta.strip().lstrip("*")] = h
    for ruta in ("scripts/instrumentos/persona2.py", "scripts/instrumentos/lexicon_persona2.json"):
        if hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest() != ref[ruta]:
            sys.exit(f"ABORTA: {ruta} ya no coincide con el hash congelado")


def desarrollo():
    with open(RAIZ / "validacion" / "persona2_desarrollo_turnos.csv", newline="", encoding="utf-8") as fh:
        return {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}


def procesar(conn, par, brazo, cid, nombres, dev, hasta=1400):
    dc = datos.DatosCampana(conn, cid, brazo, par)
    filas = []
    for t in range(1, hasta + 1):
        f = dc.turnos.get(t)
        if not f or not turno_valido(f):
            continue
        buf = f["player_buffer"] or []
        pj = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
        texto, accion, nombre = normalizar_turno(f["dm_output"], brazo), jugador(buf), nombres.get(pj)
        cats = {h["categoria"] for h in P.detectar_usurpacion(texto, accion, None, nombre)}
        fila = {"turn_id": t, "en_desarrollo": int((cid, t) in dev), "primaria": int(any(c in cats for c in PRIM)),
                "secundaria": int(P.SECUNDARIA in cats) if hasattr(P, "SECUNDARIA") else int("ACCION_NO_DECLARADA" in cats),
                "muerte": int(P.narra_muerte_pj(texto, None, nombre) is not None)}
        for c in PRIM:
            fila[c] = int(c in cats)
        filas.append(fila)
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", default="")
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    congelado_ok()
    filtro = {p for p in a.pares.split(",") if p}
    pares = [p for p in _pares.todos() if not filtro or p["par"] in filtro]
    nombres, dev, t0 = cargar_nombres(), desarrollo(), time.time()
    DESTINO.mkdir(parents=True, exist_ok=True)
    with datos.abrir_conexion() as conn:
        for k, p in enumerate(pares, 1):
            for brazo in ("G1", "G2"):
                ruta = DESTINO / f"par{p['par']}_{brazo}.csv"
                if ruta.exists() and not a.forzar:
                    continue
                t1 = time.time()
                filas = procesar(conn, p["par"], brazo, p["campaign_g1" if brazo == "G1" else "campaign_g2"], nombres, dev)
                tmp = ruta.with_suffix(".tmp")
                with open(tmp, "w", newline="", encoding="utf-8") as fh:
                    w = csv.writer(fh); w.writerow(COLUMNAS)
                    for f in filas:
                        w.writerow([f[c] for c in COLUMNAS])
                tmp.replace(ruta)
                print(f"[{k:2}/{len(pares)}] par{p['par']} {brazo}: {len(filas)} turnos en {time.time() - t1:5.1f}s "
                      f"(primaria {sum(f['primaria'] for f in filas)}, secundaria {sum(f['secundaria'] for f in filas)})", flush=True)
    print(f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
