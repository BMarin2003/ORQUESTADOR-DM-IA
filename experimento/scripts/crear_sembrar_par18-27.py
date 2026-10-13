#!/usr/bin/env python3
"""
Crea y siembra las 20 campañas de Par 18-27 (10 pares x G2 + G1). Mismo patrón que
crear_sembrar_par07-17.py, con dos diferencias: el `party_register` es configurable por par
(serious | mixed | comedic; en Par 01-17 fue siempre 'mixed') y los ids se guardan en
docs/ids_par18-27.json después de CADA par, no al final (un fallo a mitad no pierde lo ya creado).

Los ids se PARSEAN de la salida real de cada script y cada paso se verifica contra Postgres.
Uso: python experimento/scripts/crear_sembrar_par18-27.py [18 19 ...]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "motor" / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SALIDA = RAIZ / "docs" / "ids_par18-27.json"

PARES = [
    # (par, slug, lugar, world_tone, party_register, pj_key)
    ("18", "nubarron", "Nubarrón", "light", "comedic", "pj_pj27"),
    ("19", "karhad", "Karhad", "heroic", "serious", "pj_pj19"),
    ("20", "brasas_lentas", "Brasas Lentas", "mixed", "comedic", "pj_pj06"),
    ("21", "ceniza_mansa", "La Ceniza Mansa", "mixed", "serious", "pj_pj08"),
    ("22", "aguasmuertas", "Casa Aguasmuertas", "grimdark", "serious", "pj_pj15"),
    ("23", "sal_negra", "Sal Negra", "grimdark", "serious", "pj_pj16"),
    ("24", "villa_pilfera", "Villa Pilfera", "light", "comedic", "pj_pj09"),
    ("25", "balanza_real", "Balanza Real", "mixed", "comedic", "pj_pj18"),
    ("26", "lindero", "Lindero", "mixed", "serious", "pj_pj03"),
    ("27", "via_ultimo_silencio", "La Vía del Último Silencio", "heroic", "serious", "pj_pj25"),
]
LORE = {p[0]: f"lore_{p[1]}.md" for p in PARES}


def run(cmd):
    """Ejecuta un subproceso desde la raíz y devuelve su stdout; aborta con SystemExit si falla."""
    print(f"  $ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stdout, r.stderr, file=sys.stderr)
        raise SystemExit(f"FALLÓ (código {r.returncode}): {' '.join(cmd)}")
    return r.stdout


def extraer(salida, campo):
    """Extrae de la salida de un script el UUID que sigue a 'campo:'; aborta si no aparece."""
    m = re.search(rf"{campo}:\s*([0-9a-f-]{{36}})", salida)
    if not m:
        raise SystemExit(f"No se pudo extraer '{campo}' de la salida:\n{salida}")
    return m.group(1)


def verificar_campania(cid, arch, titulo, tono, registro):
    """Comprueba en Postgres que la campaña tenga título, arquitectura, tono y registro esperados y turno 0; aborta si difiere."""
    with psycopg.connect(db.DSN) as c:
        row = c.execute("SELECT title, architecture, world_tone, party_register, current_turn "
                        "FROM campaigns WHERE id=%s", (cid,)).fetchone()
    esperado = (titulo, arch, tono, registro, 0)
    if row is None or tuple(row) != esperado:
        raise SystemExit(f"Campaña {cid}: real={row} esperado={esperado}")


def verificar_siembra(cid, world, personas):
    """Comprueba que los conteos sembrados (incluidos los relojes de facción) coincidan con los fixtures; aborta si no, y devuelve los conteos reales."""
    esperado = {"locations": len(world["locations"]),
                "npcs": len([k for k in personas if not k.startswith("_")]),
                "factions": len(world["factions"]), "quests": len(world["quests"]),
                "characters": len(world["characters"]), "faction_clocks": len(world["clocks"])}
    with psycopg.connect(db.DSN) as c:
        real = {t: c.execute(f"SELECT count(*) FROM {t} WHERE campaign_id=%s", (cid,)).fetchone()[0]
                for t in esperado}
    if real != esperado:
        raise SystemExit(f"Siembra de {cid}: real={real} esperado={esperado}")
    return real


def main():
    """Crea y siembra G2 y G1 para cada par pendiente del lote 18-27 con tono y registro configurables; es reanudable, porque omite los pares ya presentes en el archivo de ids."""
    seleccion = set(sys.argv[1:])
    previos = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else []
    hechos = {e["par"] for e in previos}
    for par, slug, lugar, tono, registro, pj_key in PARES:
        if (seleccion and par not in seleccion) or par in hechos:
            continue
        print(f"\n{'=' * 70}\nPar {par}: {lugar} ({tono}/{registro})\n{'=' * 70}")
        t2 = f"Par {par} (real) · G2 (Monolítico) · {lugar}"
        t1 = f"Par {par} (real) · G1 (Multiagente) · {lugar}"
        lore, wf, pf = f"real/{LORE[par]}", f"real/world_par{par}.json", f"real/personas_par{par}.json"
        world = json.loads((RAIZ / "experimento" / "fixtures" / wf).read_text(encoding="utf-8"))
        personas = json.loads((RAIZ / "experimento" / "fixtures" / pf).read_text(encoding="utf-8"))

        out = run([sys.executable, "experimento/scripts/crear_campana_real.py", t2, lore, tono, registro])
        tenant, user, g2 = extraer(out, "tenant_id"), extraer(out, "user_id"), extraer(out, "campaign_id")
        verificar_campania(g2, "monolithic", t2, tono, registro)
        out = run([sys.executable, "experimento/scripts/crear_campana_real_g1.py", tenant, user, t1, lore, tono, registro])
        g1 = extraer(out, "campaign_id")
        verificar_campania(g1, "mas", t1, tono, registro)
        for cid in (g2, g1):
            run([sys.executable, "experimento/scripts/sembrar_mundo_real.py", cid, tenant, user, pj_key, wf, pf])
            print(f"  [ok] sembrada y verificada: {cid} {verificar_siembra(cid, world, personas)}")

        previos.append({"par": par, "lugar": lugar, "tono": tono, "registro": registro,
                        "pj": pj_key.replace("pj_pj", "PJ").upper(), "pj_key": pj_key,
                        "tenant_id": tenant, "user_id": user, "campaign_g2": g2, "campaign_g1": g1})
        SALIDA.write_text(json.dumps(previos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nListo. {len(previos)} pares en {SALIDA}")


if __name__ == "__main__":
    main()
