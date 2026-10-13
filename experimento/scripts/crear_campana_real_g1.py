"""
Crea la contraparte G1 (multiagente) del par 01, sobre el MISMO tenant y
usuario que ya existen para G2 (crear_campana_real.py) -- un par comparte
investigador y corpus de lore, solo difiere en `architecture`. Sembrada
con el mismo turno 0 (corpus de lore) que la campaña G2, para que ambos
brazos arranquen de exactamente el mismo punto.

Por qué reutilizar tenant_id/user_id en vez de crear otro tenant nuevo:
  campaigns.tenant_id tiene ON DELETE CASCADE hacia tenants(id) -- crear un
  tenant por CAMPAÑA (en vez de por PAR) multiplicaría por dos el número de
  tenants sin ganar aislamiento real: las dos campañas de un mismo par ya
  están protegidas de experimento/fixtures/seed.sql en cuanto cuelgan del tenant del
  experimento, no del tenant del fixture. Ver crear_campana_real.py para
  el razonamiento original.

Uso:
    python crear_campana_real_g1.py <tenant_id> <user_id> [titulo] [corpus_filename] [world_tone] [party_register]
Imprime el UUID de la campaña nueva. Después hay que sembrar su mundo
(sembrar_mundo_real.py, world es independiente por campaña -- G1 y G2 no
comparten NPCs/lugares/facciones, cada brazo evoluciona su propia copia)
y recién ahí generar turnos con vertical_slice_g1.py. corpus_filename es
relativo a experimento/corpus/ (por defecto lore_vado_de_ceniza.md); debe ser EL MISMO
que se usó para la campaña G2 del mismo par. world_tone: enum de Postgres
(grimdark/heroic/light/mixed), por defecto 'mixed'; debe coincidir con el
tono real del escenario y con el usado en crear_campana_real.py (G2).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import db as bd  # noqa: E402
import psycopg   # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent

CONTENT_BOUNDARIES = {
    "hard_lines": ["violencia sexual", "tortura descrita en detalle",
                    "genocidio o limpieza étnica", "daño a menores"],
    "veils": ["muerte de animales", "ejecuciones públicas"],
}

TITULO_DEFECTO = "Par 01 · G1 (Multiagente) · Vado de Ceniza"
CORPUS_DEFECTO = "lore_vado_de_ceniza.md"
WORLD_TONE_DEFECTO = "mixed"


def main():
    """Crea la campaña G1 (arquitectura 'mas') con el mismo tenant, usuario, corpus y registro que su pareja G2, e imprime sus ids y los comandos siguientes.

    Los argumentos van por línea de comandos (ver docstring del módulo).
    """
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tenant_id, user_id = sys.argv[1], sys.argv[2]
    titulo = sys.argv[3] if len(sys.argv) > 3 else TITULO_DEFECTO
    CORPUS = RAIZ / "experimento" / "corpus" / (sys.argv[4] if len(sys.argv) > 4 else CORPUS_DEFECTO)
    world_tone = sys.argv[5] if len(sys.argv) > 5 else WORLD_TONE_DEFECTO
    # Par 18+: registro configurable (serious|mixed|comedic); debe coincidir con el de G2.
    registro = sys.argv[6] if len(sys.argv) > 6 else "mixed"

    if not CORPUS.exists():
        sys.exit(f"No encuentro el corpus en {CORPUS}")
    corpus_texto = CORPUS.read_text(encoding="utf-8")
    print(f"Corpus leído: {len(corpus_texto)} caracteres, "
          f"{len(corpus_texto.split())} palabras.")

    with psycopg.connect(bd.DSN, autocommit=False) as c:
        with c.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, true)",
                       (tenant_id,))

            cur.execute(
                """INSERT INTO campaigns
                     (tenant_id, owner_id, title, architecture, profile,
                      world_tone, party_register, rules_visibility,
                      content_boundaries)
                   VALUES (%s, %s, %s, 'mas', 'adventure',
                           %s, %s, 50, %s)
                   RETURNING id""",
                (tenant_id, user_id, titulo, world_tone, registro,
                 json.dumps(CONTENT_BOUNDARIES)))
            campaign_id = cur.fetchone()[0]

            cur.execute(
                """INSERT INTO campaign_members (campaign_id, user_id, is_dm)
                   VALUES (%s, %s, true)""",
                (campaign_id, user_id))

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
    print("\nAhora sembrar su mundo (independiente del de G2, pero MISMO "
          "escenario/world/personas que su contraparte G2 -- solo cambia "
          "el pj_key si quieres, aunque lo normal es usar el mismo PJ en "
          "ambos brazos del par):")
    print(f"  python experimento\scripts\\sembrar_mundo_real.py {campaign_id} {tenant_id} "
          f"{user_id} <pj_key> [world_file] [personas_file]")
    print("\nY después generar turnos:")
    print(f"  python motor\orquestador\\vertical_slice_g1.py --campaign-id "
          f"{campaign_id} --pj PJ01 --turnos 200")


if __name__ == "__main__":
    main()
