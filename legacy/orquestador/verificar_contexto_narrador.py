r"""
Verifica que contexto_escena_narrador() no filtra secretos.

No llama a ningún modelo: solo lee Postgres. Busca un PNJ con al menos un
secreto sin revelar (revealed_at_turn IS NULL) en la campaña más antigua y
compara las dos funciones de contexto:

  - contexto_escena()          debe seguir mostrando el secreto (G2, extractor)
  - contexto_escena_narrador() NO debe mostrarlo (G1, el Narrador)

Si ningún PNJ en la base tiene un secreto sin revelar, el script lo dice
explícitamente en vez de dar un falso OK.

Uso:
  py orquestador\verificar_contexto_narrador.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "motor" / "orquestador"))
import db as bd  # noqa: E402
import psycopg


def main():
    """Comprueba en Postgres que `contexto_escena_narrador()` omite un secreto sin revelar que `contexto_escena()` sí muestra (sale 1 si no hay secreto, 2 si falla)."""
    with psycopg.connect(bd.DSN) as c:
        camp_row = c.execute(
            "SELECT id, title FROM campaigns ORDER BY created_at LIMIT 1"
        ).fetchone()
        if not camp_row:
            sys.exit("No hay campañas en la base. Carga fixtures/seed.sql")
        campaign_id, title = camp_row

        secreto = c.execute("""
            SELECT n.name, s.content
              FROM npc_secrets s JOIN npcs n ON n.id = s.npc_id
             WHERE n.campaign_id = %s AND s.revealed_at_turn IS NULL
             LIMIT 1""", (campaign_id,)).fetchone()

    print(f"Campaña: {title}")
    if not secreto:
        print("⚠ Ningún PNJ tiene un secreto sin revelar ahora mismo.\n"
              "  No es un fallo del código, pero esta corrida no prueba nada:\n"
              "  necesitas un secreto sin revelar en la base para verificar\n"
              "  que contexto_escena_narrador() lo omite.")
        sys.exit(1)

    nombre_pnj, contenido_secreto = secreto
    print(f"PNJ de prueba: {nombre_pnj}")
    print(f"Secreto (primeros 40 car.): «{contenido_secreto[:40]}...»\n")

    camp = bd.Campaña(campaign_id)
    completo = camp.contexto_escena([nombre_pnj])
    filtrado = camp.contexto_escena_narrador([nombre_pnj])

    fragmento = contenido_secreto[:25]  # suficiente para detectar la fuga
    en_completo = fragmento in completo
    en_filtrado = fragmento in filtrado

    print(f"  contexto_escena()          {'contiene' if en_completo else 'NO contiene'} el secreto")
    print(f"  contexto_escena_narrador() {'contiene' if en_filtrado else 'NO contiene'} el secreto")

    if en_completo and not en_filtrado:
        print("\n✓ OK — el Narrador no puede ver el secreto; el resto sí.")
        sys.exit(0)
    elif not en_completo:
        print("\n✗ FALLO — ni siquiera contexto_escena() (la función original) "
              "muestra el secreto. Revisa la consulta o el fixture.")
        sys.exit(2)
    else:
        print("\n✗ FALLO — contexto_escena_narrador() SIGUE mostrando el "
              "secreto. Ahí está la fuga que se quería evitar.")
        sys.exit(2)


if __name__ == "__main__":
    main()
