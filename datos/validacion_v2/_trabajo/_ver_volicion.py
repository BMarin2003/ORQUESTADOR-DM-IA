import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for l in open(Path(__file__).with_name("_volcado_v4.jsonl"), encoding="utf-8"):
    x = json.loads(l)
    if x["motivo"] is None and x["lema"] in ("decidir", "elegir", "querer", "desear", "atrever", "rendir", "disponer", "aceptar"):
        print(f"[{x['par']} {x['brazo']} t{x['t']}] {x['lema']} d20={x['d20']} {x['hab']}\n   DM: …{x['ctx'][40:]}…\n   ACC: {x['accion'][:230]!r}")
