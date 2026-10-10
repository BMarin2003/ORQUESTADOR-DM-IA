"""Imprime completos los párrafos indicados del .docx de la tesis (índices de auditar_docx.py).

    py scripts/verificacion/ver_parrafos.py 197 491 458
"""
import sys
from auditar_docx import POR_DEFECTO, parrafos

pedidos = {int(x) for x in sys.argv[1:]}
for i, texto in parrafos(POR_DEFECTO):
    if i in pedidos:
        print(f"[p{i}] {texto}\n")
