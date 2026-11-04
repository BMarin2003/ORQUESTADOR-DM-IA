import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.loads(Path(__file__).with_name("_dev_contexto_dnd.json").read_text(encoding="utf-8"))
for o in d:
    for h in o["hallazgos"]:
        t = o["tiradas"][0] if o["tiradas"] else {}
        print(f"[{o['id']} {o['brazo']}] {h['cat']} decl={int(h['decl'])} | {t.get('hab')} d20={t.get('dado')} tot={t.get('total')} "
              f"| verbo={h['verbo']} | {h['evid'][:170]}")
        print(f"      ACCION: {o['accion'][:200]!r}")
