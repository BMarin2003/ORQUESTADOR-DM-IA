"""Tamaños de población por estrato (para ponderar la exhaustividad). Reusa los pools de generar_muestra / ampliar_cd.
    PYTHONUTF8=1 py validacion_v2/poblaciones.py  -> validacion_v2/poblaciones.json
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import generar_muestra as G  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    campanas = [{"par": p["par"], "brazo": b, "campaign_id": str(p[k])}
                for p in G._pares.todos() for b, k in (("G1", "campaign_g1"), ("G2", "campaign_g2"))]
    vistos = G.ya_etiquetados()
    p2_si, p2_no, pnj_si, pnj_menc, pnj_nomenc = G.pools(campanas, vistos)
    out = {"persona2": {"si": len(p2_si), "no": len(p2_no)},
           "pnj": {"si": len(pnj_si), "no_mencionado": len(pnj_menc), "no_sin_mencion": len(pnj_nomenc)}}
    print(out, flush=True)
    if "--c" in sys.argv:
        import csv
        import ampliar_cd as A
        v = set(vistos)
        for nombre in ("clave.csv", "controles_clave.csv"):
            with open(AQUI / nombre, newline="", encoding="utf-8") as fh:
                v |= {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}
        c_si, c_no = A.pool_c(campanas, v, lambda s: None)
        out["jericho"] = {"si": len(c_si), "no": len(c_no)}
        from collections import Counter
        out["jericho_campo"] = {k: dict(Counter(f"{r['delta']['entity_type']}.{r['delta']['field_name']}" for r in pool))
                                for k, pool in (("si", c_si), ("no", c_no))}
        print(out, flush=True)
    (AQUI / "poblaciones.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
