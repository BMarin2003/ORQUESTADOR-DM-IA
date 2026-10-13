"""
Diagnostica (sin borrar nada) si una campaña fue sembrada dos veces por
sembrar_mundo_real.py -- cuenta filas por tabla y las agrupa en "rondas"
por ventana de tiempo de created_at, para ver si hay un set completo
duplicado (lugares, facciones, relojes, misiones, el PJ, los PNJ) o si
el duplicado fue puntual.

Uso:
    python scripts\\diagnosticar_siembra_doble.py <campaign_id>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db as bd  # noqa: E402


# (tabla, columna nombre, columna de tiempo real -- 'factions'/'quests'/
# 'faction_clocks' solo tienen created_at_turn (bigint), no timestamptz)
TABLAS = [
    ("locations", "name", "created_at"),
    ("factions", "name", None),
    ("faction_clocks", "agenda", None),
    ("quests", "title", None),
    ("characters", "name", "created_at"),
    ("npcs", "name", "created_at"),
]


def main():
    """Lista por tabla las filas de la campaña (id, tiempo, nombre) para detectar a ojo una siembra doble. Solo lectura."""
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    campaign_id = sys.argv[1]
    camp = bd.Campaña(campaign_id)
    with camp._conn() as c:
        camp._tx(c)
        for tabla, col_nombre, col_tiempo in TABLAS:
            orden = f"ORDER BY {col_tiempo}" if col_tiempo else "ORDER BY id"
            tiempo_sel = f"{col_tiempo} AS tiempo, " if col_tiempo else ""
            filas = c.execute(
                f"SELECT id, {tiempo_sel}{col_nombre} AS nombre "
                f"FROM {tabla} WHERE campaign_id=%s {orden}",
                (campaign_id,)).fetchall()
            print(f"\n{tabla}: {len(filas)} fila(s)")
            for f in filas:
                t = f" {col_tiempo}={f['tiempo']} " if col_tiempo else " "
                print(f"  id={f['id']} {t} · {f['nombre']}")


if __name__ == "__main__":
    main()
