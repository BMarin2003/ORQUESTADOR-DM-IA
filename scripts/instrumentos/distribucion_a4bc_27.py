"""
CR-2a/CR-2b, paso descriptivo de distribución (ventanas de 200 turnos) para las 27 parejas. NO repite la evaluación pre-especificada (matriz a4bc-2,
Par07-27, ya ejecutada una vez): solo reutiliza `correr_a4bc.distribucion`. El modelo idf de anclaje depende del conjunto de campañas, así que las cifras
de Par07-27 difieren un poco de sensibilidad_a4bc_distribucion.csv (21 parejas, se conserva como histórico). Recorta a 1 400 turnos (Par02 G2 tiene 1 668).
    PYTHONUTF8=1 py scripts/instrumentos/distribucion_a4bc_27.py
"""
import csv
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts" / "reporte_v2", RAIZ / "scripts" / "sensibilidad", RAIZ / "scripts", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import anclaje_escenario as ae      # noqa: E402
import correr_a4bc as C             # noqa: E402
import datos                        # noqa: E402
import pares as _pares              # noqa: E402

HASTA = 1400


class _Res:
    """Resultado mínimo con la interfaz fetchall() que espera `cargar_campanas`."""
    def __init__(self, filas):
        """Guarda las filas ya recortadas."""
        self._f = filas

    def fetchall(self):
        """Devuelve las filas guardadas."""
        return self._f


class ConnRecortada:
    """Solo lectura; devuelve los turnos ≤ HASTA de la consulta de turn_log que usa cargar_campanas."""
    def __init__(self, conn):
        """Envuelve la conexión de solo lectura."""
        self._c = conn

    def execute(self, sql, params=None):
        """Ejecuta la consulta y descarta los turnos posteriores a HASTA para igualar la longitud de todas las campañas."""
        return _Res([r for r in self._c.execute(sql, params).fetchall() if r["turn_id"] <= HASTA])


def main():
    """Calcula la distribución descriptiva por bloques para las 27 parejas (modelo idf sobre las 54 campañas) y la escribe en CSV; no repite la evaluación pre-especificada."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = lambda s: print(s, flush=True)   # noqa: E731
    t0 = time.perf_counter()
    pares = _pares.todos()
    conn = ConnRecortada(datos.abrir_conexion())
    log(f"cargando {2 * len(pares)} campañas (lemas con caché)...")
    camps, lores = C.cargar_campanas(conn, pares, log)
    esc = C.construir_escenarios(pares, lores, log)
    C.ESC_TODOS.update(esc)
    modelo = ae.ModeloAnclaje.desde_campanas([{"nombres": esc[c.par].nombres_lemas, "turnos": [c.tokR[t] for t in sorted(c.tokR)]} for c in camps.values()])
    log(f"modelo idf: {modelo.n_docs} campañas · t={time.perf_counter() - t0:.0f}s")
    assert all(len(c.tokR) == HASTA for c in camps.values()), {c.par: len(c.tokR) for c in camps.values() if len(c.tokR) != HASTA}
    dist, clases = C.distribucion(camps, esc, modelo, log)
    salida = RAIZ / "docs" / "reportes" / "sensibilidad_a4bc_distribucion_27.csv"
    with open(salida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dist[0]))
        w.writeheader()
        w.writerows(dist)
    log(f"escrito {salida} ({len(dist)} filas) · {time.perf_counter() - t0:.0f}s · clases de acción: {dict(clases)}")


if __name__ == "__main__":
    main()
