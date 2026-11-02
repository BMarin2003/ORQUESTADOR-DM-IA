"""
Fija los 20 ítems de control elegidos por los autores (2026-10-28) y arma el conjunto final de 620 ítems.
Salidas: controles_clave.csv (PRIVADO: id, tipo, esperada, par, brazo, campaign_id, turn_id, pnj) e items_final.json.
    PYTHONUTF8=1 py validacion_v2/fijar_controles.py
"""
import csv
import json
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ELEGIDOS = {"persona2_si": [1, 4, 5, 6, 8], "persona2_no": [2, 3, 4, 5, 10],
            "pnj_si": [1, 3, 5, 9, 10], "pnj_no": [1, 2, 6, 7, 10]}
SEMILLA = 20261028 + 2


def main():
    cand = json.loads((AQUI / "candidatos_control.json").read_text(encoding="utf-8"))
    items = json.loads((AQUI / "items.json").read_text(encoding="utf-8"))
    usados = {i["id"] for i in items}
    rng = random.Random(SEMILLA)
    clave, nuevos = [], []
    for celda, idx in ELEGIDOS.items():
        tipo = "persona2" if celda.startswith("persona2") else "pnj"
        for k in idx:
            r = cand[celda][k - 1]
            while True:
                iid = f"V{rng.randint(100000, 999999)}"
                if iid not in usados:
                    usados.add(iid)
                    break
            it = {"id": iid, "tipo": tipo, "pj": r["pj"], "accion": r["accion"], "texto": r["texto"]}
            if tipo == "pnj":
                it["hecho"] = r["hecho"]
            nuevos.append(it)
            clave.append({"id": iid, "tipo": tipo, "esperada": r["esperada"], "candidato": f"{celda}-{k:02d}", "par": r["par"],
                          "brazo": r["brazo"], "campaign_id": r["campaign_id"], "turn_id": r["turn_id"], "pnj": r.get("pnj", "")})
    final = items + nuevos
    rng.shuffle(final)
    (AQUI / "items_final.json").write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(AQUI / "controles_clave.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(clave[0]))
        w.writeheader()
        w.writerows(clave)
    print(len(final), "ítems;", len(clave), "controles")


if __name__ == "__main__":
    main()
