"""Vuelca el texto del deck por diapositiva (solo lectura). Uso: py volcar_deck.py [ruta.pptx]"""
import sys
from pathlib import Path
from pptx import Presentation

RUTA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "sustentacion" / "propuestas" / "Sustentacion_MAS_vs_Monolitico.pptx"
prs = Presentation(RUTA)
print(f"{RUTA.name}: {len(prs.slides)} diapositivas, {prs.slide_width}x{prs.slide_height}\n")
for i, s in enumerate(prs.slides, 1):
    print(f"=== {i} (layout: {s.slide_layout.name}) ===")
    for sh in s.shapes:
        tipo = sh.shape_type
        if sh.has_text_frame and sh.text_frame.text.strip():
            t = sh.text_frame.text.strip().replace("\n", " / ")
            print(f"  [{sh.shape_id}:{sh.name}] {t[:300]}")
        elif getattr(sh, "has_table", False) and sh.has_table:
            filas = [" | ".join(c.text for c in r.cells) for r in sh.table.rows]
            print(f"  [{sh.shape_id}:TABLA] " + " // ".join(filas)[:400])
        elif tipo == 13:
            print(f"  [{sh.shape_id}:IMAGEN {sh.name}]")
    if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
        print(f"  NOTAS: {s.notes_slide.notes_text_frame.text.strip()[:200]}")
