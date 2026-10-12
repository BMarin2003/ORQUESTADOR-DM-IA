"""
Relativiza `cl2_pnj_inactivo_actua` por bloque (pendiente #1 de docs/reportes/degradacion_bloques.md):
en vez de dividir entre los 200 turnos del bloque (tasa cruda), divide entre los turnos donde el
error era POSIBLE -- ya habia al menos un PNJ no-vivo entre las entidades visibles de la campana en
ese turno. Corrige el confusor que la propia propuesta de H1b senalaba: la tasa cruda puede subir
solo porque hacia el final de la campana hay mas PNJ muertos disponibles para el error, no porque el
sistema narre peor.

No recalcula el detector: lee el booleano YA calculado en datos_v2/booleanos/par{par}_{brazo}.csv
(columna cl2_pnj_inactivo_actua_v2, texto normalizado, generado por recalcular_booleanos.py) y solo
cuenta el denominador correcto reconstruyendo el estado de cada PNJ turno a turno con
datos.DatosCampana (la misma reconstruccion -- npcs + state_deltas -- que usa el motor y que ya usan
medidas_cierre.py / kaplan_meier_pnj.py). Deterministico, solo SELECT, sin LLM.

Un error solo puede ocurrir en un turno elegible (el detector exige que el PNJ mencionado ya este
inactivo), asi que n_errores no cambia -- solo cambia el denominador. Si n_elegibles=0 en un bloque
(ningun PNJ ha muerto todavia; tipico del bloque 1) la tasa relativizada queda vacia (indefinida, no
0/0) -- decision para el asesor/pagina_test.py, no se fuerza aqui.

Salida: datos_v2/cierre/pnj_inactivo_relativizado.csv
  columnas: brazo,par,bloque,n_turnos,n_elegibles,n_errores,tasa_cruda,tasa_relativizada
Uso: PYTHONUTF8=1 py scripts/reporte_v2/relativizar_pnj_inactivo.py
"""
import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                     # noqa: E402
import pares as _pares           # noqa: E402
import recalcular as rc          # noqa: E402

D2 = RAIZ / "datos_v2"
DESTINO = D2 / "cierre"
HASTA, BLOQUE = 1400, 200
COL_ERROR = "cl2_pnj_inactivo_actua_v2"


def cargar_errores(par, brazo):
    """turn_id -> bool ya calculado (texto normalizado), desde datos_v2/booleanos/."""
    ruta = D2 / "booleanos" / rc.nombre_csv(par, brazo)
    return {r["turn_id"]: bool(r[COL_ERROR]) for r in rc.leer_csv(ruta) if r.get(COL_ERROR) is not None}


def elegibles(dc, ts):
    """turn_id -> True si >=1 PNJ visible en ese turno ya esta inactivo (estado != 'alive')."""
    out = {}
    for t in ts:
        ents = dc._entidades_en(t)
        out[t] = any(dc.estado_en(e["nombre"], t) != "alive" for e in ents if e["tipo"] == "npc")
    return out


def main():
    """Recalcula `cl2_pnj_inactivo_actua` por bloque de 200 turnos relativizado a los turnos elegibles (ya hay un PNJ no vivo visible).

    Resuelve el confusor de H1b: la tasa cruda puede subir solo porque hacia el final hay más PNJ muertos. Escribe
    `datos_v2/cierre/pnj_inactivo_relativizado.csv`; con 0 elegibles la tasa relativizada queda vacía (indefinida).
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    DESTINO.mkdir(parents=True, exist_ok=True)
    filas = []
    with datos.abrir_conexion() as conn:
        for p in _pares.todos():
            for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
                cid = p[k]
                dc = datos.DatosCampana(conn, cid, brazo, p["par"])
                ts = [t for t in sorted(dc.turnos) if 1 <= t <= HASTA]
                err = cargar_errores(p["par"], brazo)
                elg = elegibles(dc, ts)
                for b in range(7):
                    rango = [t for t in ts if b * BLOQUE < t <= (b + 1) * BLOQUE]
                    n_turnos = len(rango)
                    n_elegibles = sum(1 for t in rango if elg.get(t))
                    n_errores = sum(1 for t in rango if err.get(t))
                    tasa_cruda = n_errores / n_turnos if n_turnos else ""
                    tasa_rel = n_errores / n_elegibles if n_elegibles else ""
                    filas.append({"brazo": brazo, "par": p["par"], "bloque": b + 1,
                                  "n_turnos": n_turnos, "n_elegibles": n_elegibles, "n_errores": n_errores,
                                  "tasa_cruda": tasa_cruda, "tasa_relativizada": tasa_rel})
                print(f"{brazo} par{p['par']}: ok", flush=True)
    ruta = DESTINO / "pnj_inactivo_relativizado.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["brazo", "par", "bloque", "n_turnos", "n_elegibles",
                                           "n_errores", "tasa_cruda", "tasa_relativizada"])
        w.writeheader()
        w.writerows(filas)
    n_g2_sin_elegibles = sum(1 for f in filas if f["brazo"] == "G2" and f["n_elegibles"] == 0)
    print(f"Escrito {ruta} ({len(filas)} filas). Bloques G2 sin ningun PNJ inactivo todavia (tasa "
          f"relativizada indefinida): {n_g2_sin_elegibles}.")


if __name__ == "__main__":
    main()
