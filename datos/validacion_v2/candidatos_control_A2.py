"""Ronda A2 -- candidatos a control «Sí» (atribución NO declarada, criterio persona2 v3b) y estado v3b de los controles A previos.
Candidatos: turnos con persona2 v3b = 1, fuera de desarrollo, de la muestra, de los controles y de la validación anterior.
    PYTHONUTF8=1 py validacion_v2/candidatos_control_A2.py  -> candidatos_control_A2.md
"""
import csv
import random
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "experimento" / "scripts" / "reporte_v2"))
import generar_muestra as G            # noqa: E402
import recalcular_persona2 as R        # noqa: E402
import recalcular_persona2_v3b as V    # noqa: E402

SEMILLA = 20261106
N = 15


def hallazgos(dc, t, nombres, brazo):
    f = dc.turnos[t]
    buf = f["player_buffer"] or []
    pj = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
    texto, accion = R.normalizar_turno(f["dm_output"], brazo), R.jugador(buf)
    hs = R.P.detectar_usurpacion(texto, accion, None, nombres.get(pj))
    return texto, accion, nombres.get(pj) or dc.pj_nombre, hs


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    R.congelado_ok()
    nombres = R.cargar_nombres()
    vistos = G.ya_etiquetados()
    for nombre in ("clave.csv", "controles_clave.csv"):
        with open(AQUI / nombre, newline="", encoding="utf-8") as fh:
            vistos |= {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}
    campanas = [{"par": p["par"], "brazo": b, "campaign_id": str(p[k])}
                for p in G._pares.todos() for b, k in (("G1", "campaign_g1"), ("G2", "campaign_g2"))]
    pool = []
    for c in campanas:
        with open(RAIZ / "datos" / "datos_v2" / "persona2_v3b" / f"par{c['par']}_{c['brazo']}.csv", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                t = int(r["turn_id"])
                if r["primaria"] == "1" and r["en_desarrollo"] == "0" and t >= 2 and (c["campaign_id"], t) not in vistos:
                    pool.append(dict(c, turn_id=t))
    rng = random.Random(SEMILLA)
    pool.sort(key=lambda r: (r["campaign_id"], r["turn_id"]))
    rng.shuffle(pool)
    usados, sel = Counter(), []
    for r in pool:
        if usados[r["campaign_id"]] < 2 and len(sel) < N:
            usados[r["campaign_id"]] += 1
            sel.append(r)
    with open(AQUI / "controles_clave.csv", newline="", encoding="utf-8") as fh:
        previos = [r for r in csv.DictReader(fh) if r["tipo"] == "persona2"]
    L = ["# Ronda A2 — candidatos a control", "",
         f"Pool v3b = 1 elegible: {len(pool)} turnos. Semilla {SEMILLA}. Elegir 5 «Sí» inequívocos: el DM atribuye al PJ una decisión, "
         "emoción, acto de habla o pensamiento que el jugador **no declaró** (y que no es resultado de su tirada).", ""]
    with R.datos.abrir_conexion() as conn:
        cache = {}

        def dc_de(r):
            if r["campaign_id"] not in cache:
                cache[r["campaign_id"]] = R.datos.DatosCampana(conn, r["campaign_id"], r["brazo"], r["par"])
            return cache[r["campaign_id"]]

        L += ["## A. Controles A previos bajo la regla nueva", ""]
        for r in previos:
            texto, accion, pj, hs = hallazgos(dc_de(r), int(r["turn_id"]), nombres, r["brazo"])
            cuenta = [h for h in hs if V.cuenta(h)]
            L += [f"### {r['id']} · esperada antes: {r['esperada']} · v3b ahora: {'Sí' if cuenta else 'No'} · par{r['par']} {r['brazo']} t{r['turn_id']}", "",
                  f"**Hallazgos del detector:** " + ("; ".join(f"{h['categoria']} «{h['evidencia']}» decl={h['declarada']} tirada={h['tirada_declarada']}" for h in hs) or "ninguno"), "",
                  f"**PJ:** {pj}", "", f"**Acción:** {accion}", "", "**DM:**", "", "> " + texto.replace("\n", "\n> "), ""]
        L += ["## B. Candidatos a control «Sí» nuevo", ""]
        for k, r in enumerate(sel, 1):
            texto, accion, pj, hs = hallazgos(dc_de(r), r["turn_id"], nombres, r["brazo"])
            cuenta = [h for h in hs if V.cuenta(h)]
            L += [f"### [ ] A2si-{k:02d} · par{r['par']} {r['brazo']} t{r['turn_id']}", "",
                  "**Lo que cuenta v3b:** " + "; ".join(f"{h['categoria']} «{h['evidencia']}»" for h in cuenta), "",
                  f"**PJ:** {pj}", "", f"**Acción:** {accion}", "", "**DM:**", "", "> " + texto.replace("\n", "\n> "), ""]
            r["k"] = k
    (AQUI / "candidatos_control_A2.md").write_text("\n".join(L), encoding="utf-8")
    with open(AQUI / "candidatos_control_A2.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["k", "par", "brazo", "campaign_id", "turn_id"])
        w.writeheader()
        w.writerows({x: r[x] for x in w.fieldnames} for r in sel)
    print("pool", len(pool), "| candidatos", len(sel), "| brazos", Counter(r["brazo"] for r in sel))
    print("claves de hallazgo:", sorted(hs[0].keys()) if hs else "-")


if __name__ == "__main__":
    main()
