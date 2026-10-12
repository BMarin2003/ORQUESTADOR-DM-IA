import sys
sys.path.insert(0, "orquestador")
import db as bd, psycopg
ids = {
    "Par04 G2": "fc6c19b0-49a6-4abb-ad44-b12de9438828",
    "Par04 G1": "ee613cb4-c84c-4c69-b276-bbf97e0cbbc6",
    "Par05 G2": "0bc0b20b-0dba-454d-a32e-94fbeb24dddf",
    "Par05 G1": "b7a090cf-032e-4a87-be01-e03fa88a9917",
    "Par06 G2": "d8bf034a-bcc9-4a12-999e-490be27c8a2e",
    "Par06 G1": "fbe6d980-964f-455c-89d9-96d34d9653fe",
}
with psycopg.connect(bd.DSN) as c:
    for nombre, cid in ids.items():
        r = c.execute("SELECT current_turn FROM campaigns WHERE id = %s", (cid,)).fetchone()
        print(nombre, "-> current_turn =", r[0] if r else "NO ENCONTRADA")
