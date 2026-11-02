"""
persona2 v3b: mismo detector congelado (persona2.py y léxico SIN cambios; se verifica el hash) con una regla de conteo
más estricta sobre sus hallazgos, ya calculados por el propio detector:
  * no cuenta lo que el jugador declaró en su acción (declarada = True);
  * no cuenta los pensamientos (COGNICION) que resultan de una tirada declarada (tirada_declarada = True): en D&D el
    resultado de una prueba de habilidad se entrega como conocimiento del personaje y no constituye usurpación.
Salida: datos/datos_v2/persona2_v3b/parNN_G?.csv con las mismas columnas que persona2/ (primaria = v3b).
    PYTHONUTF8=1 py experimento/scripts/reporte_v2/recalcular_persona2_v3b.py
"""
import csv
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import recalcular_persona2 as R                # noqa: E402

DESTINO = R.RAIZ / "datos" / "datos_v2" / "persona2_v3b"


def cuenta(h):
    return h["categoria"] in R.PRIM and not h["declarada"] and not (h["tirada_declarada"] and h["categoria"] == "COGNICION")


def procesar(conn, par, brazo, cid, nombres, dev, hasta=1400):
    dc = R.datos.DatosCampana(conn, cid, brazo, par)
    filas = []
    for t in range(1, hasta + 1):
        f = dc.turnos.get(t)
        if not f or not R.turno_valido(f):
            continue
        buf = f["player_buffer"] or []
        pj = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
        texto, accion, nombre = R.normalizar_turno(f["dm_output"], brazo), R.jugador(buf), nombres.get(pj)
        hs = [h for h in R.P.detectar_usurpacion(texto, accion, None, nombre) if cuenta(h)]
        cats = {h["categoria"] for h in hs}
        fila = {"turn_id": t, "en_desarrollo": int((cid, t) in dev), "primaria": int(bool(cats)), "secundaria": "", "muerte": ""}
        for c in R.PRIM:
            fila[c] = int(c in cats)
        filas.append(fila)
    return filas


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    R.congelado_ok()
    nombres, dev, t0 = R.cargar_nombres(), R.desarrollo(), time.time()
    DESTINO.mkdir(parents=True, exist_ok=True)
    with R.datos.abrir_conexion() as conn:
        for p in R._pares.todos():
            for brazo in ("G1", "G2"):
                filas = procesar(conn, p["par"], brazo, p["campaign_g1" if brazo == "G1" else "campaign_g2"], nombres, dev)
                with open(DESTINO / f"par{p['par']}_{brazo}.csv", "w", newline="", encoding="utf-8") as fh:
                    w = csv.DictWriter(fh, fieldnames=R.COLUMNAS)
                    w.writeheader()
                    w.writerows(filas)
                print(f"par{p['par']} {brazo}: {sum(f['primaria'] for f in filas)} turnos v3b", flush=True)
    print(f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
