#!/usr/bin/env python3
"""
Crea y siembra las 22 campañas de Par 07-17 (11 pares x G2 + G1), mismo
patrón que Par03-06: crear_campana_real.py -> crear_campana_real_g1.py
(reusando tenant_id/user_id) -> sembrar_mundo_real.py x2 (mundos
independientes, mismo escenario/PJ).

Los ids (tenant_id/user_id/campaign_id) se PARSEAN de la salida real de cada
script -- nunca se copian a mano -- y cada paso se verifica contra Postgres
directamente antes de seguir con el siguiente (título, architecture,
current_turn=0 tras crear; conteo de locations/npcs/factions/quests/
characters tras sembrar, comparado contra el contenido real de los fixtures,
no contra un número supuesto).

Uso: python scripts/crear_sembrar_par07-17.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

PARES = [
    # (par, slug, lugar, tono, pj_key)
    ("07", "umbral_hondo", "Umbral Hondo", "grimdark", "pj_pj23"),
    ("08", "torre_alondra", "Torre Alondra", "heroic", "pj_pj04"),
    ("09", "bruma_honda", "Bruma Honda", "grimdark", "pj_pj17"),
    ("10", "puente_roto", "Puente Roto", "mixed", "pj_pj24"),
    ("11", "cima_clara", "Cima Clara", "heroic", "pj_pj26"),
    ("12", "muelle_gris", "Muelle Gris", "light", "pj_pj07"),
    ("13", "piedra_yerma", "Piedra Yerma", "mixed", "pj_pj21"),
    ("14", "roble_cantor", "Roble Cantor", "light", "pj_pj20"),
    ("15", "solar_viejo", "Solar Viejo", "heroic", "pj_pj01"),
    ("16", "cruce_salado", "Cruce Salado", "mixed", "pj_pj12"),
    ("17", "corral_alto", "Corral Alto", "light", "pj_pj22"),
]


def run(cmd):
    """Ejecuta un subproceso desde la raíz y devuelve su stdout; aborta con SystemExit si falla."""
    print(f"  $ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"FALLÓ (código {r.returncode}): {' '.join(cmd)}")
    return r.stdout


def extraer(salida, campo):
    """Extrae de la salida de un script el UUID que sigue a 'campo:'; aborta si no aparece."""
    m = re.search(rf"{campo}:\s*([0-9a-f-]{{36}})", salida)
    if not m:
        raise SystemExit(f"No se pudo extraer '{campo}' de la salida:\n{salida}")
    return m.group(1)


def verificar_campania(campaign_id, arquitectura_esperada, titulo_esperado, tono_esperado):
    """Comprueba en Postgres que la campaña recién creada tenga la arquitectura, el título y el tono esperados y turno 0; aborta con el detalle de lo que no coincide."""
    with psycopg.connect(db.DSN) as c:
        row = c.execute(
            "SELECT title, architecture, world_tone, current_turn "
            "FROM campaigns WHERE id=%s", (campaign_id,)).fetchone()
    if row is None:
        raise SystemExit(f"Campaña {campaign_id} no existe en Postgres tras crearla")
    title, arch, tone, turn = row
    problemas = []
    if arch != arquitectura_esperada:
        problemas.append(f"architecture={arch!r}, esperado {arquitectura_esperada!r}")
    if title != titulo_esperado:
        problemas.append(f"title={title!r}, esperado {titulo_esperado!r}")
    if tone != tono_esperado:
        problemas.append(f"world_tone={tone!r}, esperado {tono_esperado!r}")
    if turn != 0:
        problemas.append(f"current_turn={turn}, esperado 0")
    if problemas:
        raise SystemExit(f"Campaña {campaign_id} no coincide con lo esperado: "
                          + "; ".join(problemas))


def verificar_siembra(campaign_id, world, personas):
    """Comprueba que los conteos sembrados (lugares, PNJ, facciones, misiones, personajes) coincidan con los fixtures; aborta si no, y devuelve los conteos reales."""
    esperado = {
        "locations": len(world["locations"]),
        "npcs": len([k for k in personas if not k.startswith("_")]),
        "factions": len(world["factions"]),
        "quests": len(world["quests"]),
        "characters": len(world["characters"]),
    }
    with psycopg.connect(db.DSN) as c:
        real = {
            "locations": c.execute("SELECT count(*) FROM locations WHERE campaign_id=%s", (campaign_id,)).fetchone()[0],
            "npcs": c.execute("SELECT count(*) FROM npcs WHERE campaign_id=%s", (campaign_id,)).fetchone()[0],
            "factions": c.execute("SELECT count(*) FROM factions WHERE campaign_id=%s", (campaign_id,)).fetchone()[0],
            "quests": c.execute("SELECT count(*) FROM quests WHERE campaign_id=%s", (campaign_id,)).fetchone()[0],
            "characters": c.execute("SELECT count(*) FROM characters WHERE campaign_id=%s", (campaign_id,)).fetchone()[0],
        }
    if real != esperado:
        raise SystemExit(f"Siembra de {campaign_id} no coincide: real={real} esperado={esperado}")
    return real


def main():
    """Crea y siembra, para cada par pedido (o todos), la campaña G2 y la G1 con el mismo mundo, verificando cada paso, y guarda sus ids."""
    seleccion = set(sys.argv[1:])
    pares = [p for p in PARES if not seleccion or p[0] in seleccion]
    resultados = []
    for par, slug, lugar, tono, pj_key in pares:
        print(f"\n{'='*70}\nPar {par}: {lugar} ({tono})\n{'='*70}")
        titulo_g2 = f"Par {par} (real) · G2 (Monolítico) · {lugar}"
        titulo_g1 = f"Par {par} (real) · G1 (Multiagente) · {lugar}"
        lore = f"real/lore_{slug}.md"
        world_file = f"real/world_par{par}.json"
        personas_file = f"real/personas_par{par}.json"

        world = json.loads((RAIZ / "fixtures" / world_file).read_text(encoding="utf-8"))
        personas = json.loads((RAIZ / "fixtures" / personas_file).read_text(encoding="utf-8"))

        out = run([sys.executable, "scripts/crear_campana_real.py", titulo_g2, lore, tono])
        tenant_id = extraer(out, "tenant_id")
        user_id = extraer(out, "user_id")
        campaign_g2 = extraer(out, "campaign_id")
        verificar_campania(campaign_g2, "monolithic", titulo_g2, tono)
        print(f"  [ok] G2 creada y verificada: {campaign_g2}")

        out = run([sys.executable, "scripts/crear_campana_real_g1.py",
                   tenant_id, user_id, titulo_g1, lore, tono])
        campaign_g1 = extraer(out, "campaign_id")
        verificar_campania(campaign_g1, "mas", titulo_g1, tono)
        print(f"  [ok] G1 creada y verificada: {campaign_g1}")

        run([sys.executable, "scripts/sembrar_mundo_real.py",
             campaign_g2, tenant_id, user_id, pj_key, world_file, personas_file])
        siembra_g2 = verificar_siembra(campaign_g2, world, personas)
        print(f"  [ok] G2 sembrada y verificada: {siembra_g2}")

        run([sys.executable, "scripts/sembrar_mundo_real.py",
             campaign_g1, tenant_id, user_id, pj_key, world_file, personas_file])
        siembra_g1 = verificar_siembra(campaign_g1, world, personas)
        print(f"  [ok] G1 sembrada y verificada: {siembra_g1}")

        resultados.append({
            "par": par, "lugar": lugar, "tono": tono, "pj_key": pj_key,
            "tenant_id": tenant_id, "user_id": user_id,
            "campaign_g2": campaign_g2, "campaign_g1": campaign_g1,
        })

    out_path = RAIZ / "docs" / "ids_par07-17.json"
    out_path.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{'='*70}\nListo. 22 campañas creadas y sembradas, verificadas contra Postgres.")
    print(f"IDs guardados en {out_path}")


if __name__ == "__main__":
    main()
