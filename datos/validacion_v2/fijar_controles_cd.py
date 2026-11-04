"""
Fija los controles de C y D y arma el conjunto final A+B+C+D.
C: 5 Sí + 2 No (solo dos candidatos «No» resultaron inequívocos: en los cambios de disposición la actitud narrada suele ser
   ambigua incluso para los autores). D: 5 Sí (no existen respuestas inequívocamente ajenas a la acción en el corpus).
Salidas: controles_clave.csv (se le agregan los de C y D), items_final.json (todos los ítems, orden aleatorio).
    PYTHONUTF8=1 py validacion_v2/fijar_controles_cd.py
"""
import csv
import json
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ELEGIDOS = {"jericho_si": [2, 3, 4, 5, 6], "jericho_no": [4, 5], "accion_si": [1, 3, 4, 5, 7]}
SEMILLA = 20261102


def main():
    cand = json.loads((AQUI / "candidatos_control_cd.json").read_text(encoding="utf-8"))
    ab = json.loads((AQUI / "items_final.json").read_text(encoding="utf-8"))
    ab = [i for i in ab if i["tipo"] in ("persona2", "pnj")]            # idempotente: parte siempre de A+B
    cd = json.loads((AQUI / "items_cd.json").read_text(encoding="utf-8"))
    usados = {i["id"] for i in ab + cd}
    rng = random.Random(SEMILLA)
    with open(AQUI / "controles_clave.csv", newline="", encoding="utf-8") as fh:
        clave = [r for r in csv.DictReader(fh) if r["tipo"] in ("persona2", "pnj")]
    nuevos = []
    for celda, idx in ELEGIDOS.items():
        for k in idx:
            r = dict(cand[celda][k - 1])
            while True:
                iid = f"V{rng.randint(100000, 999999)}"
                if iid not in usados:
                    usados.add(iid)
                    break
            it = {c: r[c] for c in ("tipo", "hecho", "texto", "texto2", "turno", "pj", "accion") if c in r}
            it["id"] = iid
            nuevos.append(it)
            clave.append({"id": iid, "tipo": r["tipo"], "esperada": r["esperada"], "candidato": f"{celda}-{k:02d}", "par": r["par"],
                          "brazo": r["brazo"], "campaign_id": r["campaign_id"], "turn_id": r["turn_id"], "pnj": ""})
    final = ab + cd + nuevos
    rng.shuffle(final)
    (AQUI / "items_final.json").write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(AQUI / "controles_clave.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(clave[0]))
        w.writeheader()
        w.writerows(clave)
    from collections import Counter
    print(len(final), "ítems", Counter(i["tipo"] for i in final), "| controles", Counter((c["tipo"], c["esperada"]) for c in clave))


if __name__ == "__main__":
    main()
