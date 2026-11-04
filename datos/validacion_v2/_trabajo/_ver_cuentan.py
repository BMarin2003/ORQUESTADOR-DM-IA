import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.loads(Path(__file__).with_name("_dev_contexto_dnd.json").read_text(encoding="utf-8"))
for o in d:
    if o["id"] in ("V107089", "V865859", "V878945"):
        print("=" * 10, o["id"], o["brazo"], o["tiradas"][:1])
        print("ACCION:", o["accion"])
        for h in o["hallazgos"]:
            print("  >>", h["cat"], h["verbo"], "|", h["evid"])
