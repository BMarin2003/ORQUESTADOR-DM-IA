"""Genera la referencia de API del sitio Docusaurus a partir de los docstrings.

Recorre los módulos Python versionados del sistema y de la medición, extrae
con ``ast`` (sin importar los módulos, así no se abre ninguna conexión ni se
llama al modelo) el docstring de módulo, de clases y de funciones, y escribe
una página Markdown por módulo en ``website/docs/referencia/<carpeta>/``.

Uso (desde la raíz del repositorio):
    py scripts/documentacion/generar_referencia_api.py
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "website" / "docs" / "referencia"
EXCLUIR_PREFIJOS = ("website/", "sustentacion/", "entregas/", "scripts/utilidades/")
GITHUB = "https://github.com/BMarin2003/ORQUESTADOR-DM-IA/blob/main/"


def listar_modulos() -> list[Path]:
    """Devuelve los .py versionados que se documentan (sin pruebas ni scripts de una vez)."""
    salida = subprocess.check_output(["git", "ls-files", "*.py"], cwd=RAIZ, text=True)
    rutas = [Path(r) for r in salida.split()]
    return [
        r
        for r in rutas
        if not r.as_posix().startswith(EXCLUIR_PREFIJOS) and not r.name.startswith("test_")
    ]


def firma(nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Reconstruye la firma ``nombre(args) -> retorno`` de una función."""
    retorno = f" -> {ast.unparse(nodo.returns)}" if nodo.returns else ""
    prefijo = "async def " if isinstance(nodo, ast.AsyncFunctionDef) else "def "
    return f"{prefijo}{nodo.name}({ast.unparse(nodo.args)}){retorno}"


def bloque_docstring(texto: str | None) -> str:
    """Envuelve el docstring en un bloque de texto para que Markdown no lo reinterprete."""
    if not texto:
        return "_Sin documentar._\n"
    return f"```text\n{texto}\n```\n"


def seccion_funcion(nodo: ast.FunctionDef | ast.AsyncFunctionDef, nivel: str) -> str:
    """Sección de una función o método: encabezado, firma y docstring."""
    return (
        f"{nivel} `{nodo.name}`\n\n```python\n{firma(nodo)}\n```\n\n"
        f"{bloque_docstring(ast.get_docstring(nodo))}\n"
    )


def seccion_clase(nodo: ast.ClassDef) -> str:
    """Sección de una clase con sus métodos públicos."""
    partes = [f"## Clase `{nodo.name}`\n\n{bloque_docstring(ast.get_docstring(nodo))}\n"]
    for hijo in nodo.body:
        if isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            partes.append(seccion_funcion(hijo, "###"))
    return "".join(partes)


def pagina_modulo(ruta: Path) -> str:
    """Página Markdown completa de un módulo."""
    arbol = ast.parse((RAIZ / ruta).read_text(encoding="utf-8-sig"))
    partes = [
        f"---\ntitle: {ruta.name}\n---\n\n",
        f"Código fuente: [`{ruta.as_posix()}`]({GITHUB}{ruta.as_posix()})\n\n",
        bloque_docstring(ast.get_docstring(arbol)),
        "\n",
    ]
    for nodo in arbol.body:
        if isinstance(nodo, ast.ClassDef):
            partes.append(seccion_clase(nodo))
        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            partes.append(seccion_funcion(nodo, "##"))
    return "".join(partes)


def escribir_categoria(carpeta: Path, etiqueta: str) -> None:
    """Crea ``_category_.json``: nombre legible en el menú; la raíz lleva un índice generado."""
    carpeta.mkdir(parents=True, exist_ok=True)
    indice = ""
    if carpeta == SALIDA:
        indice = ', "link": {"type": "generated-index", "slug": "/referencia"}'
    (carpeta / "_category_.json").write_text(
        f'{{"label": "{etiqueta}", "collapsed": true{indice}}}\n', encoding="utf-8"
    )


def main() -> None:
    """Regenera toda la referencia desde cero."""
    modulos = listar_modulos()
    for ruta in modulos:
        carpeta = SALIDA.joinpath(*ruta.parent.parts) if ruta.parent.parts else SALIDA
        escribir_categoria(carpeta, ruta.parent.as_posix() or "raíz")
        (carpeta / f"{ruta.stem}.md").write_text(pagina_modulo(ruta), encoding="utf-8")
    escribir_categoria(SALIDA, "Referencia de código")
    print(f"{len(modulos)} módulos documentados en {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
