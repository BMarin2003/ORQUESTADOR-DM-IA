"""Actualiza el deck de sustentación con los hallazgos del 2026-10-09 (no toca el original).

Cambios:
  - Lám. 17: modelo del jugador (Hermes también en los primeros turnos de los pares 4-6).
  - Lám. 28: "desde el par 4" -> "en 24 de 27 pares".
  - Lám. 31: respuesta de dados con la verificación empírica.
  - Dos láminas de respaldo nuevas (copias de la 31): capa semántica y controles finales.

    $env:PYTHONUTF8="1"; py scripts/verificacion/actualizar_deck.py
"""
import copy
from pathlib import Path

from pptx import Presentation

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "docs" / "Sustentacion_MAS_vs_Monolitico.pptx"
DESTINO = RAIZ / "docs" / "Sustentacion_MAS_vs_Monolitico_v2.pptx"


def forma(slide, sid):
    for sh in slide.shapes:
        if sh.shape_id == sid:
            return sh
    raise KeyError(f"shape {sid} no está en la lámina")


def poner(shape, texto):
    """Reemplaza el texto conservando el formato del primer run de cada párrafo."""
    lineas = texto.split("\n")
    pars = shape.text_frame.paragraphs
    assert len(pars) >= len(lineas), (shape.name, len(pars), len(lineas))
    for p, linea in zip(pars, lineas):
        runs = p.runs
        runs[0].text = linea
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
    for p in pars[len(lineas):]:
        p._p.getparent().remove(p._p)


def reemplazar(shape, viejo, nuevo):
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            if viejo in r.text:
                r.text = r.text.replace(viejo, nuevo)
                return True
    return False


def duplicar(prs, slide):
    nueva = prs.slides.add_slide(slide.slide_layout)
    for sh in list(nueva.shapes):
        sh._element.getparent().remove(sh._element)
    for el in slide.shapes._spTree.iterchildren():
        if el.tag.endswith("}nvGrpSpPr") or el.tag.endswith("}grpSpPr"):
            continue
        nueva.shapes._spTree.append(copy.deepcopy(el))
    bg = slide._element.cSld.bg
    if bg is not None:
        nueva._element.cSld.insert(0, copy.deepcopy(bg))
    return nueva


SEMANTICA = {
    2: "RESPALDO",
    3: "Capa semántica (pgvector): qué aporta y qué no",
    5: "¿Se usó pgvector para generar?",
    6: "No. Se añadió después, solo para medir: 457,613 oraciones con bge-m3 sobre los mismos turnos. Ninguna campaña se regeneró ni cambió el esquema.",
    8: "¿Por qué una versión 2?",
    9: "La v1 se encendía con solo nombrar al PNJ (SC2, p = .016). La v2 compara solo oraciones que lo mencionan y responde en las 4 pruebas A2 (SC2: p Holm = .25).",
    11: "¿Qué encontró?",
    12: "Con la mención controlada, el recall cae de 0.30 a 0.08 (azar 0.05): los embeddings casi no detectan cambios de estado. La brecha G1–G2 de la v1 era un artefacto.",
    14: "¿Qué implica para el diseño?",
    15: "El estado debe vivir en estructura con evidencia literal, como en ambos brazos; para medir CL-2 a futuro, NLI multilingüe. Es exploratorio: no decide hipótesis.",
}
NOTAS_SEMANTICA = (
    "Lámina de respaldo, solo si preguntan por la base vectorial. pgvector es una capa de medición añadida sobre el corpus ya "
    "generado; no participó en la generación ni cambió el esquema. La v1 del instrumento falló el control SC2: bastaba nombrar "
    "al PNJ para que se encendiera (7 encendidos, p = .016). La v2, sellada con SHA-256 antes de correr, compara solo oraciones "
    "que mencionan a la entidad, y responde en las cuatro perturbaciones (paráfrasis 38 a 0, ventana ajena 0 a 40, neutra 0, "
    "nombre 4 sin significancia). Sobre 631 eventos evaluables el recall baja de 0.30 a 0.08, cerca del azar de 0.05: lo que la v1 "
    "detectaba era el nombre, no el cambio de estado (sesgo de entidad, Nikolaev y Padó 2023). Conclusión de diseño: el estado "
    "tiene que guardarse estructurado con evidencia, y para medir CL-2 a futuro conviene NLI multilingüe. Es exploratorio; "
    "la clasificación de instrumentos fijada antes del contraste no se reabre."
)

CONTROLES = {
    2: "RESPALDO",
    3: "Controles finales: último bloque, dados, jugador y potencia",
    5: "¿La degradación empieza al final?",
    6: "Turnos 1,301–1,400: ningún indicador empeora tras Holm. El arraigo de G2 toca su mínimo (2.65) sin significancia (p = .35): base para probar más turnos.",
    8: "¿Los dados favorecieron a un brazo?",
    9: "Las secuencias no son idénticas (coinciden 4.9 %, azar 5 %), pero el d20 medio es igual: G1 tuvo mejor suerte en 10 de 21 pares (p = .95).",
    11: "¿Qué modelo jugó?",
    12: "Hermes-3-70B en los pares 1–3 y en los primeros turnos de los pares 4–6; luego Gemma-4-31B-it, el que narra. Siempre igual en ambos brazos del par.",
    14: "¿La potencia fue suficiente?",
    15: "G*Power a priori, unilateral, efecto medio: n = 27 da 0.81 con t pareada y ≈0.79 con Wilcoxon. Los valores bilaterales (≈0.70) son complementarios.",
}
NOTAS_CONTROLES = (
    "Lámina de respaldo. Último bloque: partimos las campañas en 14 bloques de 100 turnos y comparamos el bloque 14 con los "
    "bloques 12 y 13, con la tendencia de los bloques 1 a 13 y entre brazos; con Holm ningún indicador empeora al final. "
    "El arraigo de G2 marca en el bloque 14 su valor más bajo, 2.65, pero no es significativo; G1 incluso sube sobre su tendencia. "
    "Por eso recomendamos campañas más largas como trabajo futuro, sin afirmar un quiebre. Dados: la semilla incluye el id de "
    "campaña y cada brazo tiene el suyo, así que las secuencias no son idénticas; lo verificamos en 3,371 tiradas de la misma "
    "habilidad en el mismo turno, 21 pares: coinciden 4.9 %, lo esperado por azar. El d20 medio no favorece a ningún brazo "
    "(Wilcoxon p = .95). Jugador: Hermes en pares 1 a 3 y unos pocos turnos iniciales de 4 a 6; después Gemma, siempre "
    "el mismo en ambos brazos. Potencia: el cálculo a priori fue unilateral, coherente con H1d–H1f direccionales."
)


def main():
    prs = Presentation(ORIGEN)
    s = prs.slides

    # Lám. 17: jugador
    assert reemplazar(forma(s[16], 7), "Hermes-3-70B en pares 1–3; Gemma-4-31B-it desde el par 4",
                      "Hermes-3-70B en pares 1–3 y primeros turnos de 4–6; luego Gemma-4-31B-it"), "lám. 17"
    # Lám. 28: limitación del jugador
    assert reemplazar(forma(s[27], 13), "Desde el par 4 es el mismo modelo que narra",
                      "En 24 de 27 pares es el mismo modelo que narra"), "lám. 28"
    # Lám. 31: dados
    poner(forma(s[30], 9), "Mismo mecanismo SHA-256, pero cada brazo tiene su id de campaña: la secuencia no es idéntica "
                           "(coincide 4.9 %, azar 5 %) y el d20 medio no favorece a ninguno (p = .95).")
    n31 = s[30].notes_slide.notes_text_frame
    n31.text = n31.text + (" Verificado el 9 de octubre en 21 pares: de 3,371 tiradas de la misma habilidad en el mismo turno, "
                           "coinciden 4.9 %, lo que da el azar; el d20 medio por brazo no difiere (Wilcoxon p = .95). "
                           "En la tesis hay que corregir la frase «la misma secuencia de tiradas».")

    plantilla = s[30]
    for textos, notas in ((SEMANTICA, NOTAS_SEMANTICA), (CONTROLES, NOTAS_CONTROLES)):
        nueva = duplicar(prs, plantilla)
        for sid, t in textos.items():
            poner(forma(nueva, sid), t)
        nueva.notes_slide.notes_text_frame.text = notas

    prs.save(DESTINO)
    print(f"guardado {DESTINO} ({len(prs.slides)} láminas)")


if __name__ == "__main__":
    main()
