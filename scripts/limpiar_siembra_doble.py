"""
Verifica y (con --confirmar) limpia una siembra doble accidental de
sembrar_mundo_real.py sobre una misma campaña -- ver bitácora QM punto 29.

Para cada tabla que sembrar_mundo_real.py escribe (npcs, characters,
quests, factions, locations), agrupa las filas por nombre (title en
quests) y exige que todo nombre repetido tenga EXACTAMENTE 2 filas -- si
alguno tiene 3+, se detiene sin borrar nada (no es una siembra doble
simple, revisar a mano). Un nombre con 1 sola fila (típico de locations
creadas orgánicamente durante los turnos) se ignora, no es un duplicado.

Para decidir CUÁL de las dos filas de un par es la fantasma: cuenta los
state_deltas que la referencian (entity_id). La fila CON deltas es la que
el juego usó de verdad -- esa se conserva SIEMPRE, sin importar el id o
la fecha de creación (el id es un UUID aleatorio, no indica orden). La
fila sin deltas es la candidata a borrar.
  - Si ninguna de las dos tiene deltas: se comparan campos de juego: si
    son idénticos (ambas siguen en su valor de siembra), se borra
    cualquiera de las dos (no importa cuál, son iguales). Si difieren
    sin que ninguna tenga deltas, ES RARO -- se detiene y reporta.
  - Si AMBAS tienen deltas: también rarísimo (implicaría que el juego
    escribió en las dos copias) -- se detiene y reporta, no se borra nada.

faction_clocks no se compara por campos propios: se borra el clock que
pertenezca a la faction marcada para borrar (mismo criterio, vía join).

Sin --confirmar el script solo IMPRIME qué borraría (dry-run). Con
--confirmar, borra en orden seguro para las FKs: npcs (cascada a sus
satélites) -> characters -> quests -> faction_clocks -> factions ->
locations (cascada a sub-lugares). Todo en una sola transacción.

Uso:
    python scripts\\limpiar_siembra_doble.py <campaign_id>              (dry-run)
    python scripts\\limpiar_siembra_doble.py <campaign_id> --confirmar  (borra)
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db as bd  # noqa: E402


# tabla -> (columna nombre, entity_type en state_deltas, campos de juego
# a comparar SOLO si ninguna de las dos filas tiene deltas)
TABLAS = {
    "npcs": ("name", "npc",
             ["status", "warmth", "candor", "principle", "boldness"]),
    "characters": ("name", "character",
                   ["hp_current", "hp_max", "conditions", "xp", "is_active"]),
    "quests": ("title", "quest", ["status", "next_step_known"]),
    "factions": ("name", "faction", ["stance_party", "knows_about_party"]),
    "locations": ("name", "location",
                  ["description_canonical", "sketch_text", "detail", "state"]),
}
ORDEN_BORRADO = ["npcs", "characters", "quests", "faction_clocks",
                  "factions", "locations"]


def resolver_par(c, campaign_id, tabla, tipo_delta, nombre, fila_a, fila_b,
                  campos, problemas):
    """Decide cuál de fila_a/fila_b es la fantasma. Devuelve el id a
    borrar, o None si hay que detenerse (deja el problema en `problemas`)."""
    def n_deltas(eid):
        return c.execute(
            "SELECT COUNT(*) AS n FROM state_deltas WHERE campaign_id=%s "
            "AND entity_type=%s AND entity_id=%s",
            (campaign_id, tipo_delta, eid)).fetchone()["n"]

    da, db_ = n_deltas(fila_a["id"]), n_deltas(fila_b["id"])
    if da and not db_:
        return fila_b["id"]
    if db_ and not da:
        return fila_a["id"]
    if da and db_:
        problemas.append(f"{tabla}: '{nombre}' -- AMBAS filas tienen "
                          f"state_deltas ({fila_a['id']}={da}, "
                          f"{fila_b['id']}={db_}); no se puede decidir sola")
        return None
    # ninguna tiene deltas -- deben ser idénticas en los campos de juego
    for campo in campos:
        if fila_a[campo] != fila_b[campo]:
            problemas.append(
                f"{tabla}: '{nombre}' difiere en {campo} sin que ninguna "
                f"fila tenga state_deltas: {fila_a['id']}={fila_a[campo]!r} "
                f"vs {fila_b['id']}={fila_b[campo]!r}")
            return None
    return fila_b["id"]  # idénticas, cualquiera sirve


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    campaign_id = sys.argv[1]
    confirmar = "--confirmar" in sys.argv[2:]
    camp = bd.Campaña(campaign_id)

    with camp._conn() as c:
        camp._tx(c)

        problemas = []
        ids_a_borrar = defaultdict(list)
        faction_ids_borradas = []

        for tabla, (col_nombre, tipo_delta, campos) in TABLAS.items():
            cols_extra = ", " + ", ".join(campos) if campos else ""
            filas = c.execute(
                f"SELECT id, {col_nombre} AS nombre{cols_extra} "
                f"FROM {tabla} WHERE campaign_id=%s",
                (campaign_id,)).fetchall()
            por_nombre = defaultdict(list)
            for f in filas:
                por_nombre[f["nombre"]].append(f)
            for nombre, grupo in por_nombre.items():
                if len(grupo) == 1:
                    continue  # sin duplicar (normal en locations orgánicas)
                if len(grupo) != 2:
                    problemas.append(
                        f"{tabla}: '{nombre}' tiene {len(grupo)} filas, "
                        f"se esperaban 1 o 2")
                    continue
                eid = resolver_par(c, campaign_id, tabla, tipo_delta, nombre,
                                    grupo[0], grupo[1], campos, problemas)
                if eid is not None:
                    ids_a_borrar[tabla].append(eid)
                    if tabla == "factions":
                        faction_ids_borradas.append(eid)

        # faction_clocks: no tiene entity_type propio en state_deltas --
        # se borra el clock que cuelgue de una faction ya marcada a borrar.
        if faction_ids_borradas:
            clocks = c.execute(
                "SELECT id FROM faction_clocks WHERE campaign_id=%s "
                "AND faction_id = ANY(%s)",
                (campaign_id, faction_ids_borradas)).fetchall()
            ids_a_borrar["faction_clocks"] = [r["id"] for r in clocks]

        if problemas:
            print("⚠ NO se borra nada -- encontré casos que necesitan "
                  "revisión manual:")
            for p in problemas:
                print(f"  - {p}")
            sys.exit(1)

        print("✓ Cada duplicado resuelto por state_deltas (o por campos "
              "idénticos si ninguna copia tiene deltas) -- seguro de "
              "borrar.\n")
        for tabla in ORDEN_BORRADO:
            print(f"  {tabla}: {len(ids_a_borrar[tabla])} fila(s) a "
                  f"borrar -> {ids_a_borrar[tabla]}")

        if not confirmar:
            print("\n(dry-run -- vuelve a correr con --confirmar para borrar)")
            return

        print("\nBorrando...")
        for tabla in ORDEN_BORRADO:
            ids = ids_a_borrar[tabla]
            if ids:
                c.execute(f"DELETE FROM {tabla} WHERE id = ANY(%s)", (ids,))
        c.commit()
        print("Listo -- filas duplicadas borradas.")


if __name__ == "__main__":
    main()
