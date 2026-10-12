"""
Crea la primera campaña REAL del experimento (par 1, G2 monolítico) y la
siembra con el corpus de lore como turno 0.

Por qué un tenant/usuario NUEVOS y no los de fixtures/seed.sql:
  campaigns.tenant_id tiene ON DELETE CASCADE hacia tenants(id), y
  fixtures/seed.sql borra y recrea su tenant fijo cada vez que se corre.
  Si esta campaña real colgara del tenant de fixtures, la próxima vez que
  alguien vuelva a cargar el fixture (p.ej. para un sondeo de desarrollo)
  el CASCADE borraría TODAS las campañas reales que cuelguen de ahí. Por
  eso el experimento vive en su propio tenant, nunca tocado por seed.sql.

Por qué G2 (monolítico) y no G1 (multiagente) para esta primera campaña:
  orquestador/vertical_slice.py -- el único script que genera una campaña
  turno a turno de punta a punta -- carga siempre dm/prompt_g2.md y no
  tiene ninguna rama que use router.py ni los cuatro prompts *_g1.md. G1
  no tiene todavía un bucle de generación ejecutable equivalente. Por lo
  tanto la primera campaña real solo puede ser G2; G1 queda pendiente de
  que se construya su propio orquestador antes de poder generar su
  contraparte del par 1.

Uso:
    python crear_campana_real.py
Imprime el UUID de la campaña nueva, para usarlo con:
    python orquestador/vertical_slice.py --campaign-id <UUID> --pj PJ01 --turnos N
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orquestador"))
import db as bd  # noqa: E402
import psycopg   # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent

CONTENT_BOUNDARIES = {
    "hard_lines": ["violencia sexual", "tortura descrita en detalle",
                    "genocidio o limpieza étnica", "daño a menores"],
    "veils": ["muerte de animales", "ejecuciones públicas"],
}

TITULO_DEFECTO = "Par 01 · G2 (Monolítico) · Vado de Ceniza"
CORPUS_DEFECTO = "lore_vado_de_ceniza.md"
WORLD_TONE_DEFECTO = "mixed"


def main():
    """Uso: python crear_campana_real.py [titulo] [corpus_filename] [world_tone] [party_register]
    corpus_filename es relativo a corpus/. world_tone por defecto 'mixed'
    (usar el tono real del escenario nuevo, p.ej. 'lugubrious')."""
    TITULO = sys.argv[1] if len(sys.argv) > 1 else TITULO_DEFECTO
    CORPUS = RAIZ / "corpus" / (sys.argv[2] if len(sys.argv) > 2 else CORPUS_DEFECTO)
    WORLD_TONE = sys.argv[3] if len(sys.argv) > 3 else WORLD_TONE_DEFECTO
    # Par 18+: registro configurable (serious|mixed|comedic); Par 01-17 fue siempre 'mixed'.
    REGISTRO = sys.argv[4] if len(sys.argv) > 4 else "mixed"
    if not CORPUS.exists():
        sys.exit(f"No encuentro el corpus en {CORPUS}")
    corpus_texto = CORPUS.read_text(encoding="utf-8")
    print(f"Corpus leído: {len(corpus_texto)} caracteres, "
          f"{len(corpus_texto.split())} palabras.")

    with psycopg.connect(bd.DSN, autocommit=False) as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (name) VALUES (%s) RETURNING id",
                ("Experimento 27 pares (real)",))
            tenant_id = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO users (tenant_id, email, display_name)
                   VALUES (%s, %s, %s) RETURNING id""",
                (tenant_id, "bryanmariny2003@gmail.com", "Investigador"))
            user_id = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO campaigns
                     (tenant_id, owner_id, title, architecture, profile,
                      world_tone, party_register, rules_visibility,
                      content_boundaries)
                   VALUES (%s, %s, %s, 'monolithic', 'adventure',
                           %s, %s, 50, %s)
                   RETURNING id""",
                (tenant_id, user_id, TITULO, WORLD_TONE, REGISTRO,
                 json.dumps(CONTENT_BOUNDARIES)))
            campaign_id = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO campaign_members (campaign_id, user_id, is_dm)
                   VALUES (%s, %s, true)""",
                (campaign_id, user_id))

            # SET LOCAL para que registrar_turno() más abajo (que abre su
            # propia conexión) no choque con RLS -- aquí insertamos el
            # turno 0 en la misma transacción, directo, sin pasar por
            # Campaña.registrar_turno() (que abriría una conexión nueva
            # sin la campaña aún commiteada).
            cur.execute("SELECT set_config('app.tenant_id', %s, true)",
                       (str(tenant_id),))
            cur.execute(
                """INSERT INTO turn_log
                     (tenant_id, campaign_id, turn_id, player_buffer,
                      dm_output, gate_passed)
                   VALUES (%s, %s, 0, %s, %s, NULL)""",
                (tenant_id, campaign_id, json.dumps([]), corpus_texto))

        c.commit()

    print("\nListo.")
    print(f"  tenant_id:   {tenant_id}")
    print(f"  user_id:     {user_id}")
    print(f"  campaign_id: {campaign_id}")
    print(f"\nAhora sembrar su mundo (world/personas del MISMO escenario que "
          f"este corpus -- para Par 01 son world.json/personas.json por "
          f"defecto; para un par con escenario propio, pasa los nombres "
          f"específicos, p.ej. world_par02.json personas_par02.json):")
    print(f"  python scripts\\sembrar_mundo_real.py {campaign_id} {tenant_id} "
          f"{user_id} <pj_key> [world_file] [personas_file]")
    print(f"\nY después generar turnos:")
    print(f"  python orquestador/vertical_slice.py --campaign-id {campaign_id} "
          f"--pj PJ01 --turnos 25")


if __name__ == "__main__":
    main()
