"""Inserta items_final.json en plantilla_formulario.html -> formulario_v2.html (autocontenido, un solo archivo para los 5 evaluadores)."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
items = json.loads((AQUI / "items_final.json").read_text(encoding="utf-8"))
datos = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
html = (AQUI / "plantilla_formulario.html").read_text(encoding="utf-8")
assert html.count("__ITEMS__") == 1
(AQUI / "formulario_v2.html").write_text(html.replace("__ITEMS__", datos), encoding="utf-8")
print("formulario_v2.html:", len(items), "ítems")
