#!/usr/bin/env python3
"""
Valida los fixtures contra los mismos invariantes que exigirá el pipeline.

El chequeo que más importa: cada 'evidence' debe ser subcadena LITERAL del
texto del turno. Es la misma verificación que hará apply_delta antes de
escribir. Si un fixture no la pasa, el ground truth es inválido.

Uso:  python3 validar_fixtures.py
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).parent

# Espejo de la tabla mutable_fields del esquema. Si divergen, el fixture
# pide algo que apply_delta va a rechazar.
WHITELIST = {
    ("npc", "status"): ("enum", ["alive", "dead", "missing", "captured"]),
    ("npc", "location_id"): ("uuid", None),
    ("npc", "affinity"): ("numeric", (-100, 100)),
    ("npc", "trust"): ("numeric", (-100, 100)),
    ("npc", "respect"): ("numeric", (-100, 100)),
    ("npc", "knowledge"): ("append", None),
    ("npc", "secret_revealed"): ("append", None),
    ("location", "state"): ("enum", ["intact", "damaged", "destroyed", "occupied", "abandoned"]),
    ("location", "detail"): ("enum", ["sketch", "observed", "full"]),
    ("location", "controlling_faction_id"): ("uuid", None),
    ("faction", "knows_about_party"): ("bool", None),
    ("faction", "clock_progress"): ("numeric", (0, 9999)),
    ("quest", "status"): ("enum", ["unknown", "active", "completed", "failed", "abandoned"]),
    ("quest", "next_step_known"): ("bool", None),
    ("character", "hp_current"): ("numeric", (-99, 999)),
    ("character", "conditions"): ("append", None),
    ("character", "inventory"): ("append", None),
    ("world", "game_day"): ("numeric", (0, 999999)),
}

EVENT_KINDS = {
    "bribe_offered", "promise_made", "promise_kept", "promise_broken",
    "bond_target_protected", "bond_target_harmed", "life_saved",
    "betrayal_proven", "threat_made", "competence_shown",
    "ideal_honored", "ideal_violated", "public_status_given", "secret_entrusted",
}

errors, warnings = [], []


def err(msg):
    """Registra un error: los errores hacen fallar la validación."""
    errors.append(msg)


def warn(msg):
    """Registra un aviso: no hace fallar la validación."""
    warnings.append(msg)


def load(name):
    """Lee un JSON de fixtures relativo a BASE; si no se puede leer registra el error y termina con `sys.exit(1)`."""
    try:
        return json.loads((BASE / name).read_text(encoding="utf-8"))
    except Exception as e:
        err(f"{name}: no se pudo leer — {e}")
        sys.exit(1)


world = load("world.json")
personas = load("personas.json")
turns = load("turns.json")
probes = load("probes.json")

# ---------------------------------------------------------------- referencias
loc_keys = {l["key"] for l in world["locations"]}
fac_keys = {f["key"] for f in world["factions"]}
quest_keys = {q["key"] for q in world["quests"]}
pc_keys = {c["key"] for c in world["characters"]}
npc_keys = {k for k in personas if not k.startswith("_")}

known = {"npc": npc_keys, "location": loc_keys, "faction": fac_keys,
         "quest": quest_keys, "character": pc_keys, "world": {"world"}}

# --------------------------------------------------------------------- mundo
for l in world["locations"]:
    p = l.get("parent")
    if p is not None and p not in loc_keys:
        err(f"world: location '{l['key']}' tiene parent inexistente '{p}'")
    if l.get("detail") == "observed" and not l.get("description_canonical"):
        err(f"world: '{l['key']}' es observed pero no tiene description_canonical "
            f"(al colapsar, la descripción debe quedar congelada)")
    if l.get("detail", "sketch") == "sketch" and not l.get("sketch_text"):
        warn(f"world: '{l['key']}' es sketch sin sketch_text")

for f in world["factions"]:
    if f.get("seat") and f["seat"] not in loc_keys:
        err(f"world: faction '{f['key']}' tiene seat inexistente '{f['seat']}'")

for c in world["clocks"]:
    if c["faction"] not in fac_keys:
        err(f"world: reloj apunta a facción inexistente '{c['faction']}'")
    if c["progress"] >= c["threshold"]:
        warn(f"world: reloj '{c['agenda'][:30]}...' ya está en umbral al empezar")

# ------------------------------------------------------------------ personas
for key in npc_keys:
    p = personas[key]
    if p.get("location") and p["location"] not in loc_keys:
        err(f"persona '{key}': location inexistente '{p['location']}'")

    for t in p.get("ibf", {}).get("bond_targets") or []:
        if t["key"] not in known.get(t["type"], set()):
            err(f"persona '{key}': bond_target inexistente {t['type']}:{t['key']}")

    d = p.get("disposition", {})
    for axis in ("affinity", "trust", "respect"):
        v = d.get(axis, 0)
        if not -100 <= v <= 100:
            err(f"persona '{key}': {axis}={v} fuera de rango")
    if d.get("trust", 0) > d.get("trust_ceiling", 100):
        err(f"persona '{key}': trust inicial supera su propio techo")

    for s in p.get("secrets") or []:
        if not s.get("reveal_condition"):
            err(f"persona '{key}': secreto sin reveal_condition "
                f"(el actor no sabría bajo qué presión soltarlo)")

# Comprobación de diseño: debe existir al menos una persona completamente vacía.
vacias = [k for k in npc_keys
          if not (personas[k].get("ibf") or {}).get("ideal_text")
          and not personas[k].get("traits")]
if not vacias:
    warn("no hay ninguna persona 'de paso' con IBF vacío — "
         "falta el caso que verifica que el sistema no exija datos inexistentes")

# --------------------------------------------------------------------- turnos
ids = set()
kinds = {"trivial": 0, "conversational": 0, "consequential": 0}
neg_cases = 0
delta_count = 0
fields_seen = set()

for t in turns:
    tid = t["id"]
    if tid in ids:
        err(f"turno {tid}: id duplicado")
    ids.add(tid)
    kinds[t["kind"]] = kinds.get(t["kind"], 0) + 1

    # El texto completo del turno: buffer del jugador + salida del DM.
    full = " ".join(m["text"] for m in t["player_buffer"]) + " " + t["dm_output"]

    for m in t["player_buffer"]:
        if m["pc"] not in pc_keys:
            err(f"turno {tid}: PJ desconocido '{m['pc']}'")
    for n in t.get("npcs_present", []):
        if n not in npc_keys:
            err(f"turno {tid}: PNJ desconocido '{n}'")

    if not t["expected_deltas"] and not t.get("expected_events"):
        neg_cases += 1

    # Eventos: enum cerrado + evidencia literal + entidad existente
    for e in t.get("expected_events", []):
        if e["event_kind"] not in EVENT_KINDS:
            err(f"turno {tid}: event_kind '{e['event_kind']}' fuera del enum")
        if e["entity"] not in npc_keys:
            err(f"turno {tid}: evento sobre PNJ inexistente '{e['entity']}'")
        if e.get("evidence", "") not in full:
            err(f"turno {tid}: evidencia de evento NO literal "
                f"→ «{e.get('evidence','')[:60]}»")

    for d in t["expected_deltas"]:
        delta_count += 1
        et, fld = d["entity_type"], d["field"]
        fields_seen.add((et, fld))

        spec = WHITELIST.get((et, fld))
        if spec is None:
            err(f"turno {tid}: campo '{et}.{fld}' NO está en la lista blanca — "
                f"apply_delta lo rechazaría")
            continue

        kind, dom = spec
        if kind == "enum" and d["value"] not in dom:
            err(f"turno {tid}: valor '{d['value']}' no permitido para {et}.{fld}")
        if kind == "numeric":
            if not isinstance(d["value"], (int, float)):
                err(f"turno {tid}: {et}.{fld} debe ser numérico, es {type(d['value']).__name__}")
            elif not dom[0] <= d["value"] <= dom[1]:
                err(f"turno {tid}: {et}.{fld}={d['value']} fuera de rango {dom}")
        if kind == "bool" and not isinstance(d["value"], bool):
            err(f"turno {tid}: {et}.{fld} debe ser booleano")

        if d["entity"] not in known.get(et, set()):
            err(f"turno {tid}: entidad inexistente {et}:{d['entity']}")

        # EL CHEQUEO CENTRAL.
        ev = d.get("evidence", "")
        if not ev:
            err(f"turno {tid}: delta sobre {et}.{fld} SIN evidencia")
        elif ev not in full:
            err(f"turno {tid}: evidencia NO literal en el texto del turno "
                f"→ «{ev[:60]}»")

        if not d.get("rationale"):
            warn(f"turno {tid}: delta sobre {et}.{fld} sin rationale "
                 f"(el validador humano no puede juzgarlo)")

# ------------------------------------------------------------------ cobertura
print("=" * 66)
print("VALIDACIÓN DE FIXTURES")
print("=" * 66)
print(f"\nMundo      {len(world['locations'])} lugares · {len(world['factions'])} facciones · "
      f"{len(world['clocks'])} relojes · {len(world['quests'])} misiones")
print(f"Personas   {len(npc_keys)} PNJ ({len(vacias)} de paso con IBF vacío)")
print(f"Turnos     {len(turns)} · trivial {kinds.get('trivial',0)} · "
      f"conversacional {kinds.get('conversational',0)} · "
      f"consecuente {kinds.get('consequential',0)}")
event_count = sum(len(t.get("expected_events", [])) for t in turns)
print(f"Eventos    {event_count} esperados (resueltos por resolve_event)")
print(f"Deltas     {delta_count} directos en {len(turns)-neg_cases} turnos")
print(f"Negativos  {neg_cases} turnos sin deltas (miden PRECISIÓN)")
print(f"Sondeos    {len(probes['ooc'])} consultas OOC · {len(probes['escenas'])} escenas")

gate_true = sum(1 for t in turns if t["expected_gate"])
print(f"Compuerta  {gate_true}/{len(turns)} deberían pasar "
      f"({100*gate_true//len(turns)}%)")

print(f"\nCampos ejercitados: {len(fields_seen)}/{len(WHITELIST)} de la lista blanca")
sin_cubrir = set(WHITELIST) - fields_seen
if sin_cubrir:
    print("  sin cubrir: " + ", ".join(f"{a}.{b}" for a, b in sorted(sin_cubrir)))

if neg_cases < 4:
    warn(f"solo {neg_cases} casos negativos. Sobre-extraer es irrecuperable "
         f"(entra al canon y nada lo señala); conviene tener más.")

# --------------------------------------------------------------------- salida
print()
if warnings:
    print(f"AVISOS ({len(warnings)})")
    for w in warnings:
        print(f"  ! {w}")
    print()

if errors:
    print(f"ERRORES ({len(errors)})")
    for e in errors:
        print(f"  ✗ {e}")
    print("\nFIXTURES INVÁLIDOS")
    sys.exit(1)

print("FIXTURES VÁLIDOS — todos los spans de evidencia son literales,")
print("todos los campos están en la lista blanca, todas las referencias resuelven.")