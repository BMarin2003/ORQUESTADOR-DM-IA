"""Busca en el .docx de la tesis los pasajes que la auditoría del 2026-10-09 marcó como errores de hecho
o como puntos a revisar. Solo lectura: imprime párrafo, número de párrafo y patrón encontrado.

    $env:PYTHONUTF8="1"; py scripts/verificacion/auditar_docx.py [ruta.docx]
"""
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

RAIZ = Path(__file__).resolve().parents[2]
POR_DEFECTO = RAIZ / "Claude outputs" / "Entrega_Asesor_TESIS" / "01_Tesis" / "Tesis_Coherencia_Narrativa_MAS_vs_Monolitico.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

PATRONES = {
    "RAG / recuperación por similitud": r"\bRAG\b|recuperaci[oó]n por similitud|retrieval",
    "Tiradas compartidas": r"misma secuencia de tiradas|mismas tiradas|misma semilla",
    "Panel / Likert (diseño original)": r"panel de cinco|cinco Dungeon|Likert|se generar[aá]n",
    "Potencia / G*Power": r"G\s*\*\s*Power|potencia estad|una cola|dos colas|unilateral|bilateral",
    "Evaluadores (conteo)": r"\b(un|uno|dos|tres|1|2|3) evaluador(es)?\b|evaluadores externos",
    "Jugador / autojuego": r"Hermes|autojuego|self-play|modelo distinto",
    "Tablas de la base": r"\b3[25] tablas\b",
    "pgvector / vectorial": r"pgvector|vectorial",
    "Jericho-QA (nombre)": r"Jericho-QA",
    "Sensatez (CR-1)": r"sensatez|sensibleness",
}


def parrafos(ruta):
    with zipfile.ZipFile(ruta) as z:
        raiz = ET.fromstring(z.read("word/document.xml"))
    for i, p in enumerate(raiz.iter(W + "p")):
        texto = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if texto:
            yield i, texto


def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else POR_DEFECTO
    if not ruta.exists():
        sys.exit(f"No existe: {ruta}")
    print(f"Documento: {ruta}\n")
    hallazgos = {k: [] for k in PATRONES}
    for i, texto in parrafos(ruta):
        for nombre, rx in PATRONES.items():
            if re.search(rx, texto, re.I):
                hallazgos[nombre].append((i, texto))
    for nombre, lista in hallazgos.items():
        print(f"## {nombre}: {len(lista)} párrafo(s)")
        for i, texto in lista[:12]:
            corto = texto if len(texto) <= 260 else texto[:257] + "..."
            print(f"  [p{i}] {corto}")
        if len(lista) > 12:
            print(f"  ... y {len(lista) - 12} más")
        print()


if __name__ == "__main__":
    main()
