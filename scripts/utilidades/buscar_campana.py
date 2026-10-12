import sys
sys.path.insert(0, "orquestador")
import db as bd, psycopg
with psycopg.connect(bd.DSN) as c:
    rows = c.execute("SELECT id, title, architecture, current_turn, created_at FROM campaigns WHERE title LIKE %s ORDER BY created_at DESC LIMIT 5", ("%Caleta Lumbre%",)).fetchall()
    for r in rows:
        print(r)
