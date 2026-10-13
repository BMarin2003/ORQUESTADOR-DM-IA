#!/usr/bin/env python3
"""
Chequeo de las tiradas de combate (motor/jugador/dados.py) y de la red de seguridad contra
DM fuera de personaje. Sin base de datos ni LLM.   Uso: python experimento/scripts/test_dados_combate.py
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "motor" / "jugador"))
import dados  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
pjs = {p["id"]: p for p in json.loads((RAIZ / "motor" / "jugador" / "personajes_jugadores.json").read_text(encoding="utf-8"))["personajes"]}

# --- modificadores esperados (nivel 3, competencia +2) -----------------------
tarq = dados.tabla_pj(pjs["PJ23"])      # brujo: FUE 8 (-1), DES 13 (+1), CAR 15 (+2)
assert tarq["ataque"] == 1 + 2 and tarq["iniciativa"] == 1 and tarq["ataque magico"] == 2 + 2, tarq
osric = dados.tabla_pj(pjs["PJ27"])     # bárbaro: FUE 15 (+2), DES 13 (+1); no lanza conjuros
assert osric["ataque"] == 2 + 2 and osric["iniciativa"] == 1 and "ataque magico" not in osric, osric
assert dados.tabla_pj(pjs["PJ08"])["ataque magico"] == 2 + 2   # Reia, maga: INT 15
assert dados.tabla_pj(pjs["PJ02"])["ataque magico"] == 2 + 2   # Senna, clériga: SAB 15
print("OK modificadores de ficha")

# --- resolver_turno: todas las variantes se tiran con el modificador real ----
texto = "Ataco.\n{Ataque}\n{Ataque con la daga}\n{Ataque furtivo}\n{Iniciativa}\n{Ataque de conjuro}\n{Soborno}"
res, tiradas, rechazadas = dados.resolver_turno(texto, "camp-x", 5, tabla_modificadores=tarq)
mods = {t["etiqueta"]: t["modificador"] for t in tiradas}
assert mods == {"Ataque": 3, "Ataque con la daga": 3, "Ataque furtivo": 3, "Iniciativa": 1, "Ataque de conjuro": 4}, mods
assert rechazadas == ["Soborno"], rechazadas
assert "(resultado:" in res and "{Ataque}" not in res
print("OK resolver_turno: 5 tiradas de combate con su modificador; {Soborno} sigue rechazada")

# un bárbaro no lanza conjuros: {Ataque mágico} se rechaza (no se inventa un número)
_, t2, r2 = dados.resolver_turno("{Ataque mágico}", "camp-x", 6, tabla_modificadores=osric)
assert not t2 and r2 == ["Ataque mágico"], (t2, r2)
# sin tabla de PJ (campañas viejas) nada de combate: mismo criterio de siempre
_, t3, r3 = dados.resolver_turno("{Ataque}", "camp-x", 7, tabla_modificadores=None)
assert not t3 and r3 == ["Ataque"]
# reproducible: misma campaña/turno/etiqueta => misma tirada
a = dados.resolver_turno("{Ataque}", "camp-x", 9, tabla_modificadores=tarq)[1][0]["dado"]
b = dados.resolver_turno("{Ataque}", "camp-x", 9, tabla_modificadores=tarq)[1][0]["dado"]
assert a == b
print("OK no combate sin ficha / sin lanzador; tiradas reproducibles")

# --- red de seguridad ---------------------------------------------------------
meta = "[Para resolver este ataque necesito que realices una tirada de Ataque (1d20).]"
assert dados.es_meta_ooc(meta)
assert not dados.es_meta_ooc("El vigilante gruñe y retrocede un paso, con la mano en la empuñadura.")
assert not dados.es_meta_ooc("Dice: «[..]» corto")               # menos de 20 caracteres dentro
mixta = meta + "\n\n" + "La criatura reacciona con un espasmo violento, sus filamentos vibrando en el aire viciado. " * 2
assert not dados.es_meta_ooc(dados.quitar_meta_ooc(mixta))       # conserva la narración, quita el corchete
assert dados.quitar_meta_ooc(meta) == meta                       # solo meta: no hay nada que rescatar
print("OK red de seguridad: detecta, limpia lo mixto, no inventa texto")
print("TODO OK")
