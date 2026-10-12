#!/usr/bin/env python3
"""
Validador cruzado para fixtures/real/world_parXX.json + personas_parXX.json.

fixtures/validar_fixtures.py (el validador genérico del proyecto) exige
world.json/personas.json/turns.json/probes.json en fixtures/ -- los pares
reales no tienen turns.json/probes.json (esos son solo para el suite de
prueba del extractor, no para sembrar una campaña real). Este script reusa
el mismo subconjunto de invariantes de validar_fixtures.py que SÍ aplica a
world/personas (referencias cruzadas, rangos, secretos con reveal_condition,
al menos un PNJ de paso vacío), parametrizado por número de par.

Uso: python scripts/validar_fixtures_real.py 07 08 09 10 11 12 13 14 15 16 17
"""
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
from db import TURNOS_POR_DIA  # noqa: E402
FIX = RAIZ / "fixtures" / "real"
OBJETIVO_TURNOS = 1400


def validar_par(par):
    """Valida el mundo y las personas de un par (JSON válido, referencias cruzadas coherentes).

    Returns:
        Tupla (errores, avisos). Los errores impiden crear campañas; los avisos no.
    """
    errores, avisos = [], []

    def err(msg):
        """Registra un error de validación."""
        errores.append(msg)

    def warn(msg):
        """Registra un aviso de validación."""
        avisos.append(msg)

    wfile = FIX / f"world_par{par}.json"
    pfile = FIX / f"personas_par{par}.json"
    if not wfile.exists():
        return [f"falta {wfile.name}"], []
    if not pfile.exists():
        return [f"falta {pfile.name}"], []

    try:
        world = json.loads(wfile.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{wfile.name}: JSON inválido -- {e}"], []
    try:
        personas = json.loads(pfile.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{pfile.name}: JSON inválido -- {e}"], []

    loc_keys = {l["key"] for l in world["locations"]}
    fac_keys = {f["key"] for f in world["factions"]}
    quest_keys = {q["key"] for q in world["quests"]}
    pc_keys = {c["key"] for c in world["characters"]}
    npc_keys = {k for k in personas if not k.startswith("_")}
    known = {"npc": npc_keys, "location": loc_keys, "faction": fac_keys,
             "quest": quest_keys, "character": pc_keys, "world": {"world"}}

    if len(loc_keys) < 5:
        warn(f"solo {len(loc_keys)} locations (se esperaban ~7)")
    if len(world["factions"]) != 2:
        warn(f"{len(world['factions'])} facciones (se esperaban 2)")
    if len(world["quests"]) != 2:
        warn(f"{len(world['quests'])} misiones (se esperaban 2)")
    # Par 18+ (2026-09-19): el reloj del mundo ya es determinista (1 día cada
    # TURNOS_POR_DIA turnos, db.Campaña.sincronizar_dia). Un reloj dispara UNA
    # vez, así que para que la campaña de 1400 turnos tenga eventos de mundo
    # repartidos hacen falta 3, escalonados (temprano / medio / tardío).
    if len(world["clocks"]) != 3:
        warn(f"{len(world['clocks'])} relojes (se esperaban 3 escalonados; con 1 solo "
             f"el mundo se mueve una vez en toda la campaña)")
    if len(world["characters"]) != 1:
        err(f"{len(world['characters'])} characters (se esperaba exactamente 1, el PJ del par)")

    for l in world["locations"]:
        p = l.get("parent")
        if p is not None and p not in loc_keys:
            err(f"location '{l['key']}': parent inexistente '{p}'")
        if l.get("detail") == "observed" and not l.get("description_canonical"):
            err(f"location '{l['key']}': observed sin description_canonical")
        if l.get("detail", "sketch") == "sketch" and not l.get("sketch_text"):
            warn(f"location '{l['key']}': sketch sin sketch_text")

    for f in world["factions"]:
        if f.get("seat") and f["seat"] not in loc_keys:
            err(f"faction '{f['key']}': seat inexistente '{f['seat']}'")

    for c in world["clocks"]:
        if c["faction"] not in fac_keys:
            err(f"reloj: faction inexistente '{c['faction']}'")
        if c["progress"] >= c["threshold"]:
            warn(f"reloj '{c['agenda'][:40]}...': progress >= threshold ya al empezar")
        elif c["rate_per_game_day"] > 0:
            dias = math.ceil((c["threshold"] - c["progress"]) / c["rate_per_game_day"])
            turno = dias * TURNOS_POR_DIA
            c["_turno_disparo"] = turno
            if turno > OBJETIVO_TURNOS:
                err(f"reloj '{c['agenda'][:40]}...': dispararía en el turno {turno} "
                    f"(> {OBJETIVO_TURNOS}): nunca ocurriría en la campaña")
            elif turno < 100:
                warn(f"reloj '{c['agenda'][:40]}...': dispara en el turno {turno} "
                     f"(< 100, antes de que la escena esté establecida)")
        else:
            err(f"reloj '{c['agenda'][:40]}...': rate_per_game_day <= 0, no avanza nunca")
    disparos = sorted(c["_turno_disparo"] for c in world["clocks"] if "_turno_disparo" in c)
    if len(disparos) >= 2 and min(b - a for a, b in zip(disparos, disparos[1:])) < 200:
        warn(f"relojes muy juntos (disparan en los turnos {disparos}); separar ≥ 200 turnos")

    for q in world["quests"]:
        if q.get("visibility") == "dm_only" and q.get("status") not in ("unknown",):
            warn(f"quest '{q['key']}': dm_only pero status='{q.get('status')}' (se esperaba 'unknown')")

    ch = world["characters"][0] if world["characters"] else None
    if ch and ch["hp"] != ch["hp_max"]:
        err(f"character '{ch['key']}': hp ({ch['hp']}) != hp_max ({ch['hp_max']})")

    for key in npc_keys:
        p = personas[key]
        if p.get("location") and p["location"] not in loc_keys:
            err(f"persona '{key}': location inexistente '{p['location']}'")
        for t in (p.get("ibf", {}).get("bond_targets") or []):
            if t["key"] not in known.get(t["type"], set()):
                err(f"persona '{key}': bond_target inexistente {t['type']}:{t['key']}")
        d = p.get("disposition", {})
        for axis in ("affinity", "trust", "respect"):
            v = d.get(axis, 0)
            if not -100 <= v <= 100:
                err(f"persona '{key}': {axis}={v} fuera de rango")
        if d.get("trust", 0) > d.get("trust_ceiling", 100):
            err(f"persona '{key}': trust inicial supera su propio techo")
        for s in (p.get("secrets") or []):
            if not s.get("reveal_condition"):
                err(f"persona '{key}': secreto sin reveal_condition")
            if s.get("visibility") != "dm_only":
                warn(f"persona '{key}': secreto sin visibility='dm_only'")

    vacias = [k for k in npc_keys
              if not (personas[k].get("ibf") or {}).get("ideal_text")
              and not personas[k].get("traits")]
    if not vacias:
        warn("no hay ninguna persona 'de paso' con IBF vacío")
    if len(npc_keys) != 3:
        warn(f"{len(npc_keys)} PNJ (se esperaban 3: dos centrales + un PNJ de paso)")

    return errores, avisos


def main():
    """Valida los pares indicados (por defecto 07-17) y sale con código 1 si alguno tiene errores, para no crear campañas con fixtures inconsistentes."""
    pares = sys.argv[1:] or [f"{i:02d}" for i in range(7, 18)]
    total_err = 0
    for par in pares:
        errores, avisos = validar_par(par)
        estado = "OK" if not errores else "FALLA"
        print(f"\n=== Par {par}: {estado} ===")
        for w in avisos:
            print(f"  ! {w}")
        for e in errores:
            print(f"  x {e}")
        total_err += len(errores)
    print(f"\n{'='*60}")
    if total_err:
        print(f"TOTAL: {total_err} error(es) -- no crear campañas hasta corregir.")
        sys.exit(1)
    print("TOTAL: todos los pares pasaron la validación cruzada.")


if __name__ == "__main__":
    main()
