import psycopg
from psycopg.rows import dict_row
c = psycopg.connect("host=127.0.0.1 port=5432 dbname=dmia_dev user=postgres password=dev_only_change_me", row_factory=dict_row)
for row in c.execute("SELECT id, title FROM campaigns WHERE title LIKE %s", ("Par 01%",)).fetchall():
    print(row["id"], row["title"])
