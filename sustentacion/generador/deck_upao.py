"""Deck de sustentación en el formato oficial UPAO (plantilla REP_ICSI).

Abre la plantilla oficial, conserva su portada, su índice y su cierre (con el máster,
los layouts, el fondo y los logos) y genera las láminas de contenido sobre el layout
TWO_OBJECTS, con la barra lateral de navegación de la plantilla. Fuente de las cifras:
tesis/TESIS2.docx.md y sustentacion/CONTEXTO_SUSTENTACION.md.

Uso (desde la raíz del repo): python sustentacion/generador/deck_upao.py
"""
import copy
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA = RAIZ / "sustentacion" / "formato_oficial" / "REP_ICSI_CISNEROS.BARTRA_ADRIAN_GUZMÁN.MOSCOL_ALFREDO.pptx"
SALIDA = RAIZ / "sustentacion" / "Sustentacion_UPAO.pptx"

AZUL = RGBColor(0x00, 0x56, 0xA6)      # cabeceras de tabla y cajas (plantilla)
AZUL_OSC = RGBColor(0x0B, 0x2E, 0x6B)  # cajas de detalle
CLARO = RGBColor(0xDC, 0xE6, 0xF2)     # fondos suaves
NEGRO = RGBColor(0, 0, 0)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
GRIS = RGBColor(0x55, 0x5B, 0x6E)
ACENTO = RGBColor(0xC2, 0x41, 0x0C)    # solo para el hallazgo (H1f)

SECCIONES = ["Introducción", "Planteamiento del problema", "Marco teórico", "Hipótesis y variables",
             "Marco metodológico", "Resultados y discusión", "Conclusiones y Recomendaciones", "Anexos"]

prs = Presentation(PLANTILLA)
LAY = {l.name: l for l in prs.slide_layouts}


# ------------------------------------------------------------------ utilidades
def eliminar_slide(slide):
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        if prs.part.related_part(sid.rId) is slide.part:
            prs.part.drop_rel(sid.rId)
            lst.remove(sid)
            return


def quitar_enlaces(slide):
    """Quita los saltos internos heredados (apuntaban a láminas que ya no existen)."""
    for h in slide._element.iter(qn("a:hlinkClick")):
        h.getparent().remove(h)
    for rid, rel in list(slide.part.rels.items()):
        if rel.reltype == RT.SLIDE:
            slide.part.drop_rel(rid)


def enlazar(run, destino, slide):
    rid = slide.part.relate_to(destino.part, RT.SLIDE)
    rpr = run._r.get_or_add_rPr()
    h = etree.SubElement(rpr, qn("a:hlinkClick"))
    h.set(qn("r:id"), rid)
    h.set("action", "ppaction://hlinksldjump")


def texto(slide, x, y, w, h, contenido, size=12, bold=False, color=NEGRO, align=PP_ALIGN.LEFT,
          anchor=MSO_ANCHOR.TOP, italic=False):
    """contenido: str (\n = párrafo) o lista de párrafos; cada párrafo, str o lista de (texto, {opciones})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.04))
    parrafos = contenido.split("\n") if isinstance(contenido, str) else contenido
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for t, o in ([(par, {})] if isinstance(par, str) else par):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = "Arial"
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = o.get("color", color)
    return tb


def caja(slide, x, y, w, h, contenido="", fill=AZUL, color=BLANCO, size=12, bold=True, forma=MSO_SHAPE.ROUNDED_RECTANGLE,
         linea=None, align=PP_ALIGN.CENTER):
    s = slide.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.12
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if linea:
        s.line.color.rgb = linea
        s.line.width = Pt(1.25)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for m in ("margin_left", "margin_right"):
        setattr(tf, m, Inches(0.08))
    parrafos = contenido.split("\n") if isinstance(contenido, str) else contenido
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for t, o in ([(par, {})] if isinstance(par, str) else par):
            r = p.add_run()
            r.text = t
            r.font.name = "Arial"
            r.font.size = Pt(o.get("size", size))
            r.font.bold = o.get("bold", bold)
            r.font.color.rgb = o.get("color", color)
    return s


def flecha(slide, x, y, w, h, fill=CLARO):
    return caja(slide, x, y, w, h, fill=fill, forma=MSO_SHAPE.RIGHT_ARROW)


def tabla(slide, filas, x, y, w, anchos, alto_fila=0.34, size=11, cabeceras=(0,), centrar_cols=()):
    """filas: lista de listas; una celda puede ser str o (str, {'span': n, 'bold':..., 'fill':..., 'color':..., 'align':...})."""
    nf, nc = len(filas), len(anchos)
    gf = slide.shapes.add_table(nf, nc, Inches(x), Inches(y), Inches(w), Inches(alto_fila * nf))
    t = gf.table
    tblpr = t._tbl.tblPr
    for a in ("firstRow", "bandRow"):
        tblpr.set(a, "0")
    total = sum(anchos)
    for j, a in enumerate(anchos):
        t.columns[j].width = Inches(w * a / total)
    for i in range(nf):
        t.rows[i].height = Inches(alto_fila)
        j = 0
        for celda in filas[i]:
            txt, o = (celda, {}) if isinstance(celda, str) else celda
            c = t.cell(i, j)
            span = o.get("span", 1)
            if span > 1:
                c.merge(t.cell(i, j + span - 1))
            cab = i in cabeceras
            c.fill.solid()
            c.fill.fore_color.rgb = o.get("fill", AZUL if cab else BLANCO)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            bordes(c)
            tf = c.text_frame
            tf.word_wrap = True
            for k, linea in enumerate(txt.split("\n")):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.alignment = o.get("align", PP_ALIGN.CENTER if (cab or j in centrar_cols) else PP_ALIGN.LEFT)
                r = p.add_run()
                r.text = linea
                r.font.name = "Arial"
                r.font.size = Pt(o.get("size", size))
                r.font.bold = o.get("bold", cab)
                r.font.color.rgb = o.get("color", BLANCO if cab else NEGRO)
            j += span
    return t


def bordes(celda, color="0061AE"):
    """Bordes de 0.75 pt en el azul de las tablas de la plantilla."""
    tcpr = celda._tc.get_or_add_tcPr()
    for lado in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for viejo in tcpr.findall(qn(lado)):
            tcpr.remove(viejo)
        ln = etree.SubElement(tcpr, qn(lado), w="9525", cap="flat", cmpd="sng")
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=color)
    # el esquema exige los bordes antes del relleno
    for tag in ("a:solidFill", "a:noFill"):
        for f in tcpr.findall(qn(tag)):
            tcpr.remove(f)
            tcpr.append(f)


def burbuja(slide, x, y, autor, contenido, w=4.3):
    """Antecedente / fundamento al estilo de la plantilla: círculo con el autor + caja con el hallazgo."""
    caja(slide, x + 0.75, y + 0.08, w - 0.75, 0.9, contenido, fill=CLARO, color=NEGRO, size=12, bold=False,
         forma=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.LEFT).text_frame.margin_left = Inches(0.7)
    c = caja(slide, x, y, 1.3, 1.06, autor, fill=AZUL_OSC, size=10, forma=MSO_SHAPE.OVAL)
    c.text_frame.margin_left = c.text_frame.margin_right = Inches(0.02)


def subtitulo(slide, t, y=1.25, x=2.4):
    texto(slide, x, y, 10.3, 0.45, t, size=16, bold=True)





def contenido(seccion, titulo):
    s = prs.slides.add_slide(LAY["TWO_OBJECTS"])
    ti = s.shapes.title
    ti.left, ti.top, ti.width, ti.height = Inches(0.92), Inches(0.12), Inches(11.5), Inches(1.05)
    ti.text = titulo
    ti.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    for r in ti.text_frame.paragraphs[0].runs:
        r.font.name, r.font.bold = "Arial", True
    for ph in list(s.placeholders):
        idx = ph.placeholder_format.idx
        if idx == 1:
            ph.left, ph.top, ph.width, ph.height = Inches(0.1), Inches(1.84), Inches(2.25), Inches(4.86)
            s._barra = ph
        elif idx != 0:
            ph._element.getparent().remove(ph._element)
    s._seccion = seccion
    return s


def barra(s, destinos):
    """Barra lateral de la plantilla: secciones enlazadas, la actual en negrita."""
    tf = s._barra.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, nombre in enumerate(SECCIONES):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_before = Pt(0 if i == 0 else 14)
        # en la barra estrecha estos dos nombres se partían a media palabra: salto de línea explícito
        partes = {"Planteamiento del problema": ["Planteamiento del", "problema"],
                  "Conclusiones y Recomendaciones": ["Conclusiones y", "Recomendaciones"]}.get(nombre, [nombre])
        for k, parte in enumerate(partes):
            if k:
                p.add_line_break()
            r = p.add_run()
            r.text = parte
            f = r.font
            f.name = "Arial"
            f.size = Pt(10)
            f.underline = True
            f.bold = i == s._seccion
            f.color.rgb = AZUL
            enlazar(r, destinos[i], s)


# ------------------------------------------------------------------ plantilla
originales = list(prs.slides)
portada, indice, cierre = originales[0], originales[1], originales[-1]
for sl in originales[2:-1]:
    eliminar_slide(sl)
for sl in (portada, indice, cierre):
    quitar_enlaces(sl)
# python-pptx numera las láminas nuevas por cantidad: se aparta el cierre para que no choque su nombre de parte
cierre.part.partname = PackURI("/ppt/slides/slide900.xml")
if cierre.has_notes_slide:
    cierre.notes_slide.part.partname = PackURI("/ppt/notesSlides/notesSlide900.xml")

# Portada: mismas 13 líneas, mismo formato
lineas = ["UNIVERSIDAD PRIVADA ANTENOR ORREGO", "Facultad de Ingeniería",
          "Escuela Profesional de Ingeniería de Sistemas e Inteligencia Artificial", "Tesis para optar el título profesional de:",
          "Ingeniero de Sistemas e Inteligencia Artificial",
          "“Comparación de la coherencia narrativa en campañas de Dungeons & Dragons generadas por sistemas multiagente versus sistemas monolíticos”",
          "Autores:", "Marin Yupanqui, Bryan Arturo", "Mostacero Cieza, Luis David", "Asesor:",
          "Dr. Cueva Chávez, Walter Manuel", "Trujillo - Perú", "2026"]
for sh in portada.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("UNIVERSIDAD"):
        runs = sh.text_frame.paragraphs[0].runs
        for r, t in zip(runs, lineas):
            r.text = t
            r.font.size = Pt(22 if r.font.bold else 19)
        runs[2].font.size = Pt(21)
portada.notes_slide.notes_text_frame.text = (
    "[0:00–0:30] Buenos días, señores miembros del jurado. Somos Bryan Marin y Luis Mostacero y presentamos nuestra tesis, "
    "asesorada por el Dr. Walter Cueva: comparamos la coherencia narrativa de un director de juego con inteligencia artificial "
    "construido como sistema multiagente (G1) frente a uno monolítico (G2).")
for sh in cierre.shapes:
    if sh.has_text_frame and "Gracias" in sh.text_frame.text:
        sh.text_frame.paragraphs[0].runs[0].text = "¡Gracias por su atención!"

# ------------------------------------------------------------------ láminas
slides = []

# 1 · Introducción
s = contenido(0, "Introducción")
hechos = [("Los LLM pierden la información del medio en contextos largos", "Liu et al. (2024)"),
          ("El LLM como director de juego pierde el estado y decide por el jugador", "Callison-Burch et al. (2022); Zhu et al. (2023)"),
          ("Sin un registro explícito del mundo, incluso los LLM de vanguardia pierden coherencia", "Ma et al. (2026)")]
causas = [("Promesa multiagente", "Xia et al. (2025)", ["Roles especializados", "Sin contraste controlado"]),
          ("Fallas propias del MAS", "Cemri et al. (2025)", ["14 modos de fallo", "Mejoras mínimas"]),
          ("Medición sin verificar", "Valdivia y Burelli (2025)", ["Sin prueba de sensibilidad", "Casi todo en inglés"])]
for i, (h, a) in enumerate(hechos):
    x = 2.45 + i * 2.85
    caja(s, x, 1.55, 2.5, 1.0, h, size=11)
    texto(s, x, 2.6, 2.5, 0.5, a, size=10, color=GRIS, align=PP_ALIGN.CENTER)
    if i < 2:
        for k in range(3):
            caja(s, x + 2.55 + k * 0.1, 2.0, 0.07, 0.07, fill=AZUL, forma=MSO_SHAPE.OVAL)
for i, (h, a, subs) in enumerate(causas):
    x = 2.45 + i * 2.85
    caja(s, x, 3.35, 2.5, 0.75, [[(h, {"bold": True})], [(a, {"size": 9, "bold": False, "color": GRIS})]], fill=BLANCO, color=NEGRO,
         size=12, linea=AZUL)
    for k, sub in enumerate(subs):
        caja(s, x + 0.3, 4.2 + k * 0.55, 2.2, 0.45, sub, fill=AZUL_OSC, size=11, bold=False)
caja(s, 10.95, 2.6, 1.95, 1.55, [[("BRECHA", {"bold": True, "size": 14})], [("MAS vs. monolítico en D&D, en español y en 2.ª persona", {"bold": False, "size": 10})]],
     fill=CLARO, color=AZUL_OSC, forma=MSO_SHAPE.OVAL, linea=AZUL)
texto(s, 2.45, 5.45, 8.3, 0.75, [[("Problema central: ", {"bold": True}), ("no se sabe si repartir las decisiones narrativas entre agentes especializados mejora la coherencia "
      "de campañas extensas frente a un sistema monolítico con el mismo modelo y la misma información del mundo.", {})]], size=12)
s._nota = ("[0:30–1:45] Un modelo de lenguaje que dirige una partida pierde información en contextos largos, olvida el estado del juego y llega a decidir "
            "por el jugador. La literatura propone repartir el trabajo entre agentes especializados, pero sin un contraste controlado, y advierte que "
            "los sistemas multiagente tienen fallas propias. Además, los instrumentos para medir coherencia no tienen su sensibilidad verificada y casi "
            "todo está en inglés. De ahí la brecha: comparar de forma controlada multiagente contra monolítico en D&D, en español y en segunda persona.")
slides.append(s)

# 2 · Planteamiento del problema
s = contenido(1, "Planteamiento del problema")
filas = [["Formulación del problema", "Objetivo general", "Hipótesis general"],
         ["¿Es superior la coherencia narrativa de campañas de Dungeons & Dragons generadas por sistemas multiagente en comparación con sistemas monolíticos de inteligencia artificial?",
          "Comparar la coherencia narrativa de las campañas de Dungeons & Dragons generadas por una arquitectura de sistema multiagente frente a una arquitectura monolítica.",
          "Los sistemas multiagente producen campañas de Dungeons & Dragons con mayor coherencia narrativa que los sistemas monolíticos."],
         [("Objetivos específicos", {"span": 3})],
         [("OE1: Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico.", {"span": 3})],
         [("OE2: Evaluar la coherencia longitudinal a lo largo de las campañas generadas por el sistema monolítico.", {"span": 3})],
         [("OE3: Evaluar la calidad narrativa emergente en las campañas generadas por el sistema monolítico.", {"span": 3})],
         [("OE4: Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura.", {"span": 3})],
         [("OE5: Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas.", {"span": 3})],
         [("OE6: Comparar la calidad narrativa emergente producida por la arquitectura multiagente frente a la monolítica.", {"span": 3})]]
t = tabla(s, filas, 2.45, 1.5, 10.45, [1, 1, 1], alto_fila=0.4, size=11, cabeceras=(0, 2))
t.rows[1].height = Inches(1.35)
s._nota = ("[1:45–2:30] La pregunta general es si la coherencia narrativa de un sistema multiagente es superior a la de uno monolítico. "
            "Se responde con seis objetivos específicos: los tres primeros evalúan al sistema monolítico por sí solo, en las tres dimensiones de la "
            "coherencia, y los tres últimos comparan ambas arquitecturas en esas mismas dimensiones.")
slides.append(s)

# 3 · Marco teórico
s = contenido(2, "Marco teórico")
filas = [["Coherencia reactiva\n(OE1 · OE4)", "Coherencia longitudinal\n(OE2 · OE5)", "Calidad narrativa emergente\n(OE3 · OE6)", "Arquitectura multiagente\n(VI)"],
         [("Yu et al. (2025)", {"bold": True, "align": PP_ALIGN.CENTER}), ("Papalampidi et al. (2022)", {"bold": True, "align": PP_ALIGN.CENTER}),
          ("Zhu et al. (2023)", {"bold": True, "align": PP_ALIGN.CENTER}), ("Xia et al. (2025) · Cemri et al. (2025)", {"bold": True, "align": PP_ALIGN.CENTER})],
         [("RPGBench: verificación objetiva de la mecánica del juego, sin intervención humana", {"align": PP_ALIGN.CENTER}),
          ("Métricas automáticas de coherencia y consistencia de entidades en historias generadas", {"align": PP_ALIGN.CENTER}),
          ("FIREBALL: ~25,000 sesiones reales; el estado estructurado mejora la generación", {"align": PP_ALIGN.CENTER}),
          ("Roles especializados mejoran historias largas, pero los MAS suman 14 modos de fallo", {"align": PP_ALIGN.CENTER})],
         ["Arraigo a la acción", "Estado del mundo", "Agencia del jugador", "Sistema multiagente"],
         [("La respuesta corresponde a lo que el jugador acaba de hacer", {"align": PP_ALIGN.CENTER, "size": 11}),
          ("Personajes, eventos y estado del mundo se mantienen consistentes", {"align": PP_ALIGN.CENTER, "size": 11}),
          ("El sistema no decide, piensa, siente ni habla por el jugador", {"align": PP_ALIGN.CENTER, "size": 11}),
          ("El turno se reparte entre agentes con contexto propio; el monolítico lo resuelve en una sola generación", {"align": PP_ALIGN.CENTER, "size": 11})]]
t = tabla(s, filas, 2.45, 1.6, 10.45, [1, 1, 1, 1], alto_fila=0.62, size=12, cabeceras=(0, 3))
t.rows[2].height = Inches(1.15)
t.rows[4].height = Inches(1.05)
texto(s, 2.45, 6.05, 8.3, 0.4, "Coherencia narrativa: integridad lógica y estructural de la historia, sin contradicciones (Zhu et al., 2023; Zhou et al., 2023).",
      size=11, italic=True, color=GRIS)
s._nota = ("[2:30–3:15] La coherencia narrativa se entiende como la integridad lógica de la historia, sin contradicciones, y se descompone en tres "
            "dimensiones. Cada una se apoya en un antecedente: la verificación objetiva de mecánicas de RPGBench, las métricas de entidades de "
            "Papalampidi y el estado estructurado de FIREBALL. Para la variable independiente, StoryWriter muestra que repartir roles ayuda en "
            "historias largas, y Cemri advierte que los sistemas multiagente tienen catorce modos de fallo propios.")
slides.append(s)

# 4 · Hipótesis
s = contenido(3, "Hipótesis")
filas = [["Tipo de hipótesis", "Descripción sintetizada", "Representación"],
         ["Hipótesis general (H1)", "Los sistemas multiagente producen campañas con mayor coherencia narrativa que los monolíticos; se sostiene solo si se sostienen H1d, H1e y H1f.", "H1d ∧ H1e ∧ H1f"],
         ["H1a · OE1", "La coherencia reactiva del sistema monolítico disminuye conforme avanza la campaña.", "Tendencia ↓ en 7 bloques (Page)"],
         ["H1b · OE2", "La coherencia longitudinal del sistema monolítico disminuye conforme avanza la campaña.", "Tendencia ↓ en 7 bloques (Page)"],
         ["H1c · OE3", "La calidad narrativa emergente del sistema monolítico disminuye conforme avanza la campaña.", "Tendencia ↓ en 7 bloques (Page)"],
         ["H1d · OE4", "Los sistemas multiagente generan respuestas con mayor coherencia reactiva que los monolíticos.", "MeD (G1 − G2) > 0"],
         ["H1e · OE5", "Los sistemas multiagente mantienen mayor coherencia longitudinal que los monolíticos.", "MeD (G1 − G2) > 0"],
         ["H1f · OE6", "Los sistemas multiagente producen una calidad narrativa emergente superior a la de los monolíticos.", "MeD (G1 − G2) > 0"]]
tabla(s, filas, 2.45, 1.5, 10.45, [1.3, 4.6, 1.9], alto_fila=0.6, size=12, centrar_cols=(0, 2))
s._nota = ("[3:15–3:50] Hay dos grupos de hipótesis. H1a a H1c plantean que el sistema monolítico se degrada a lo largo de la campaña, y se "
            "contrastan con la prueba de tendencia de Page sobre siete bloques de 200 turnos. H1d a H1f plantean que el multiagente supera al "
            "monolítico, y se contrastan con Wilcoxon pareado. La hipótesis general solo se sostiene si se sostienen las tres comparativas.")
slides.append(s)

# 5 · Variables
s = contenido(3, "Variables")
filas = [[("Tipo de arquitectura del sistema de IA (variable independiente)", {"span": 3})],
         [("Paradigma bajo el cual se organizan las decisiones que el sistema toma para generar cada turno: número de instancias que intervienen y reparto de responsabilidades narrativas.", {"span": 3, "size": 11})],
         [("G1: turno repartido entre cinco roles especializados · G2: turno resuelto en una sola generación", {"span": 2}), ("Nominal dicotómica", {"fill": CLARO, "align": PP_ALIGN.CENTER})],
         [("Coherencia narrativa (variable dependiente)", {"span": 3})],
         [("Integridad lógica y estructural de la historia generada y ausencia de contradicciones, medida con instrumentos deterministas por campaña y por bloque de 200 turnos.", {"span": 3, "size": 11})],
         [("Coherencia reactiva", {"bold": True}), "CR-1 fluidez · CR-2 arraigo a la acción del jugador", ("Razón e intervalo", {"fill": CLARO, "align": PP_ALIGN.CENTER})],
         [("Coherencia longitudinal", {"bold": True}), "CL-1 consistencia de personajes · CL-2 consistencia de eventos y del mundo", ("Razón", {"fill": CLARO, "align": PP_ALIGN.CENTER})],
         [("Calidad narrativa emergente", {"bold": True}), "QN-1 interés y diversidad · QN-2 respeto a la agencia del jugador", ("Razón", {"fill": CLARO, "align": PP_ALIGN.CENTER})]]
tabla(s, filas, 2.45, 1.5, 10.45, [2.3, 5.6, 1.7], alto_fila=0.5, size=12, cabeceras=(0, 3))
texto(s, 2.45, 5.75, 8.3, 0.6, "Controladas dentro del par: modelo, base de datos del estado, extractor, mecanismo de tiradas, escenario, personaje jugador, agente jugador y extensión.",
      size=11, italic=True, color=GRIS)
s._nota = ("[3:50–4:20] La variable independiente es el tipo de arquitectura, nominal con dos niveles. La dependiente es la coherencia narrativa, "
            "con tres dimensiones y seis indicadores. Todo lo demás se mantiene constante dentro de cada par.")
slides.append(s)

# 6 · Marco metodológico (diseño)
s = contenido(4, "Marco metodológico")
for i, (h, v) in enumerate([("Tipo de investigación", "Aplicada"), ("Enfoque y nivel", "Cuantitativo – Explicativo"), ("Diseño", "Experimental de medidas repetidas con pares emparejados")]):
    x = 2.45 + i * 3.5
    caja(s, x, 1.45, 2.0, 0.6, h, size=12, align=PP_ALIGN.LEFT)
    caja(s, x + 0.35, 1.95, 2.55, 0.75, "• " + v, fill=BLANCO, color=NEGRO, size=11, bold=False, linea=AZUL, align=PP_ALIGN.LEFT)
    if i < 2:
        flecha(s, x + 2.15, 1.5, 0.75, 0.45)
texto(s, 2.45, 2.95, 10.4, 0.45, [[("Diseño: ", {"bold": True}), ("Gpar (n = 27):   X₁ → O₁   |   X₂ → O₂", {})]], size=16, align=PP_ALIGN.CENTER)
caja(s, 3.0, 3.55, 1.4, 1.3, "Gpar", fill=BLANCO, color=NEGRO, size=26, linea=AZUL)
for k, (xx, oo) in enumerate([("X₁", "O₁"), ("X₂", "O₂")]):
    y = 3.45 + k * 0.85
    caja(s, 4.6, y + 0.12, 0.5, 0.4, fill=NEGRO, forma=MSO_SHAPE.RIGHT_ARROW)
    caja(s, 5.25, y, 1.0, 0.65, xx, fill=NEGRO, size=16)
    caja(s, 6.4, y + 0.12, 0.5, 0.4, fill=NEGRO, forma=MSO_SHAPE.RIGHT_ARROW)
    caja(s, 7.05, y, 1.0, 0.65, oo, fill=BLANCO, color=NEGRO, size=18, linea=AZUL)
texto(s, 8.4, 3.45, 4.5, 1.6, [[("Gpar: ", {"bold": True}), ("27 escenarios; cada uno recibe ambos tratamientos y es su propio control.", {})],
                              [("X₁ / X₂: ", {"bold": True}), ("arquitectura multiagente (G1) / monolítica (G2).", {})],
                              [("O: ", {"bold": True}), ("batería de instrumentos deterministas, por campaña y por bloque de 200 turnos.", {})]], size=12)
texto(s, 2.45, 5.2, 8.3, 0.9, "Método hipotético-deductivo · TRL 4 (validación en laboratorio) · α = 0.05. Nota. Diseño adaptado de Arias (2012).",
      size=11, italic=True, color=GRIS)
s._nota = ("[4:20–5:15] Es una investigación aplicada, cuantitativa y explicativa, con un diseño experimental de medidas repetidas con pares "
            "emparejados: cada uno de los 27 escenarios se genera dos veces, una con cada arquitectura, y actúa como su propio control. "
            "Lo que se analiza es la diferencia dentro del par.")
slides.append(s)

# 7 · Marco metodológico (población → análisis)
s = contenido(4, "Marco metodológico")
pasos = [("Población", ["Campañas generables por ambas arquitecturas"]),
         ("Muestra", ["27 pares = 54 campañas × 1,400 turnos", "75,600 turnos · 1 − β = 0.81"]),
         ("Técnicas e\ninstrumentos", ["Generación controlada con agente jugador", "Batería determinista (Rúbrica D&D-IA)"]),
         ("Validez", ["Perturbación: δ de Cliff ≥ 0.147 + Holm", "Evaluadores externos (κ = 0.595)"]),
         ("Procesamiento y\nanálisis de datos", ["Page (H1a–H1c)", "Wilcoxon pareado + HL + r (H1d–H1f)"])]
for i, (h, chips) in enumerate(pasos):
    x, y = 2.45 + i * 2.05, 4.75 - i * 0.78
    caja(s, x, y, 0.9, 0.9, str(i + 1), fill=AZUL, size=18, forma=MSO_SHAPE.OVAL)
    texto(s, x - 0.1, y - 0.62, 2.2, 0.6, h, size=13, bold=True, color=AZUL, anchor=MSO_ANCHOR.BOTTOM)
    for k, c in enumerate(chips):
        caja(s, x + 0.2, y + 0.98 + k * 0.5, 1.95, 0.44, c, fill=AZUL_OSC if k == 0 else BLANCO, color=BLANCO if k == 0 else AZUL_OSC,
             size=9, bold=k == 0, linea=None if k == 0 else AZUL)
texto(s, 2.45, 6.55, 8.3, 0.35, "Muestreo no probabilístico intencional; 3 pares piloto de 250 turnos fuera de la muestra.", size=10, italic=True, color=GRIS)
s._nota = ("[5:15–6:15] La población son las campañas que ambas arquitecturas pueden generar; trabajamos con 27 pares, 75,600 turnos, tamaño "
            "calculado con G*Power para un efecto medio con potencia de 0.81. El jugador es un agente autónomo, igual en ambos brazos. Como un panel "
            "humano no era viable a esta escala, medimos con instrumentos deterministas: el mismo texto da siempre la misma lectura. Cada "
            "instrumento pasó una prueba de perturbación, con expectativas selladas antes, y donde el instrumento interpreta texto lo validamos con "
            "evaluadores externos. El análisis usa Page para la degradación y Wilcoxon pareado para la comparación, con Holm.")
slides.append(s)

# 8 · Resultados: la propuesta DM-IA
s = contenido(5, "Resultados y discusión")
subtitulo(s, "Propuesta: el sistema DM-IA y sus dos arquitecturas")
ciclo = ["Estado del mundo\n(PostgreSQL)", "Contexto de la escena\n(SQL exacto)", "Agente jugador\n(acción + habilidad)", "Dados\n(d20 + modificador)"]
for i, c in enumerate(ciclo):
    caja(s, 2.45 + i * 2.65, 1.85, 2.3, 0.7, c, fill=CLARO, color=NEGRO, size=11)
    if i < 3:
        flecha(s, 2.45 + i * 2.65 + 2.33, 2.05, 0.28, 0.3, fill=AZUL)
caja(s, 2.45, 2.75, 1.1, 1.15, "G1", fill=RGBColor(0x0F, 0x8B, 0x8D), size=18)
for i, r in enumerate(["Enrutador\n(código)", "Árbitro\n(código)", "Actor de PNJ\n(modelo)", "Mundo\n(código + modelo)", "Narrador\n(modelo)"]):
    caja(s, 3.7 + i * 1.84, 2.85, 1.7, 0.95, r, fill=BLANCO, color=NEGRO, size=10, bold=True, linea=RGBColor(0x0F, 0x8B, 0x8D))
caja(s, 2.45, 4.05, 1.1, 0.8, "G2", fill=RGBColor(0xD0, 0x8C, 0x2E), size=18)
caja(s, 3.7, 4.1, 9.0, 0.7, "Director de juego: en una sola llamada arbitra, interpreta a los PNJ, mueve el mundo y escribe la prosa",
     fill=BLANCO, color=NEGRO, size=11, bold=False, linea=RGBColor(0xD0, 0x8C, 0x2E))
for i, (h, d) in enumerate([("Lista blanca", "solo 19 campos modificables"), ("Cita literal", "todo cambio cita el turno"), ("Magnitudes por personalidad", "los números los pone una tabla")]):
    caja(s, 2.45 + i * 2.8, 5.05, 2.6, 0.8, [[(h, {"bold": True})], [(d, {"bold": False, "size": 10})]], fill=AZUL_OSC, size=12)
texto(s, 2.45, 5.95, 8.3, 0.45, "77,413 turnos registrados · 17,908 cambios de estado con evidencia · ningún LLM escribe directamente en la base.", size=11, color=GRIS)
s._nota = ("[6:15–7:15] Construimos el sistema DM-IA. El ciclo del turno es igual en ambos brazos: se lee el estado del mundo en PostgreSQL, se arma "
            "el contexto con consultas exactas, el agente jugador declara su acción y el código tira los dados. Solo cambia quién produce la "
            "narración: en G1, cinco roles; en G2, un solo director de juego. Ambos comparten una memoria estructurada con tres candados contra la "
            "alucinación: lista blanca de campos, cita literal obligatoria y magnitudes que pone una tabla según la personalidad del personaje.")
slides.append(s)

# 9 · OE1–OE3
s = contenido(5, "Resultados y discusión")
subtitulo(s, "OE1–OE3: ¿Se degrada el sistema monolítico? (G2, n = 27, 7 bloques de 200 turnos)")
filas = [["Hipótesis", "Instrumento (clase)", "Bloque 1 → 7", "Page p", "Decisión"],
         ["H1a · reactiva", "Respuesta a la acción, z (C)", "2.768 → 2.742", "0.310", "No se rechaza H0a"],
         ["H1b · longitudinal", "PNJ inactivo relativizado (E)", "—", "0.451", "Sin decisión confirmatoria"],
         ["H1c · calidad", "persona2 (CC)", "3.0 % → 3.5 %", "0.089 (Holm 0.178)", "No se rechaza H0c"],
         [("Análisis exploratorio del último tramo (turnos 1,301–1,400): ningún indicador empeora tras Holm", {"span": 5, "fill": CLARO, "size": 11})]]
tabla(s, filas, 2.45, 1.85, 6.2, [1.3, 1.9, 1.2, 1.2, 1.5], alto_fila=0.62, size=11, centrar_cols=(2, 3, 4))
texto(s, 8.95, 1.8, 3.9, 0.35, "Antecedente", size=13, bold=True, color=AZUL)
burbuja(s, 8.9, 2.2, "Liu et al.\n(2024)", "El LLM pierde la información del medio de contextos largos: se esperaba degradación", w=4.0)
texto(s, 8.95, 3.5, 3.9, 0.35, "Discusión", size=13, bold=True, color=AZUL)
burbuja(s, 8.9, 3.9, "Ma et al.\n(2026)", "Con un registro explícito del estado del mundo, la coherencia se sostiene", w=4.0)
texto(s, 2.45, 5.25, 6.2, 0.9, "G2 no se degradó en 1,400 turnos: la memoria estructurada común contrarresta la deriva que la literatura atribuye a los contextos largos.",
      size=12, bold=True)
s._nota = ("[7:15–8:15] Primera pregunta: ¿se degrada el monolítico? No. La respuesta a la acción pasa de 2.768 a 2.742, sin tendencia (Page p = 0.31). "
            "En la longitudinal no hay instrumento confirmatorio, y el aumento crudo de personajes inactivos desaparece al relativizar por exposición. "
            "La usurpación sube de 3.0 a 3.5 por ciento sin significancia tras Holm. La literatura esperaba degradación en contextos largos; "
            "nuestro resultado concuerda con que un registro explícito del estado del mundo la contrarresta.")
slides.append(s)

# 10 · OE4
s = contenido(5, "Resultados y discusión")
subtitulo(s, "OE4: Coherencia reactiva, G1 vs G2 (27 pares)")
filas = [[("Instrumento confirmatorio: respuesta a la acción específica (z)", {"span": 2})],
         ["Mediana G1 / G2", "2.70 / 2.81"],
         ["Hodges-Lehmann [IC 95 %]", "−0.13 [−0.25, −0.03]"],
         ["p bilateral · r", "0.032 · −0.47 (leve a favor de G2)"],
         [("Descomposición del solapamiento crudo", {"span": 2})],
         ["Componente genérico", "G1 > G2 en 27/27 pares (p < 0.001)"],
         ["Componente específico", "Sin diferencia (p = 0.59)"],
         ["Extensión de G1", "+16 lemas por turno"],
         [("Decisión: no se rechaza H0d · H1d no se sostiene", {"span": 2, "fill": CLARO, "bold": True})]]
tabla(s, filas, 2.45, 1.85, 6.2, [1.6, 2.2], alto_fila=0.44, size=11, cabeceras=(0, 4), centrar_cols=(1,))
texto(s, 8.95, 1.8, 3.9, 0.35, "Antecedente", size=13, bold=True, color=AZUL)
burbuja(s, 8.9, 2.2, "Xia et al.\n(2025)", "Repartir roles mejora la coherencia de historias largas: no se confirma", w=4.0)
texto(s, 8.95, 3.45, 3.9, 0.35, "Crudo = genérico + específico", size=13, bold=True, color=AZUL)
for i, (t, f) in enumerate([("Genérico\nG1 > G2", AZUL), ("Específico\nempate", AZUL_OSC)]):
    caja(s, 9.0 + i * 1.95, 3.85, 1.85, 0.75, t, fill=f, size=11, forma=MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON)
texto(s, 8.95, 4.75, 3.9, 0.35, "Fundamento", size=13, bold=True, color=AZUL)
burbuja(s, 8.9, 5.1, "Cemri et al.\n(2025)", "Coordinar agentes no garantiza mejoras sobre una línea base sólida", w=4.0)
s._nota = ("[8:15–9:30] En la coherencia reactiva, el confirmatorio favorece levemente a G2: 2.70 contra 2.81, p = 0.032. Las versiones crudas favorecían a G1, "
            "así que separamos el solapamiento en una parte genérica y una específica. La genérica es mayor en G1 en los 27 pares porque escribe más "
            "largo; la específica no difiere. Ninguna arquitectura responde mejor a la acción concreta del jugador: no se confirma lo que reporta "
            "StoryWriter, y sí la advertencia de Cemri. H1d no se sostiene.")
slides.append(s)

# 11 · OE5
s = contenido(5, "Resultados y discusión")
subtitulo(s, "OE5: Coherencia longitudinal, G1 vs G2 (27 pares)")
filas = [["Línea de evidencia (exploratoria)", "G1 vs G2", "p"],
         ["Coherencia de entidad", "2.17 vs 1.67", "0.017"],
         ["PNJ inactivo mencionado (crudo / refinado)", "desfavorece a G1 / sin diferencia", "0.032 / 0.44"],
         ["Supervivencia: 1.ª mención de un PNJ no vivo", "turno 1,139 vs 891", "0.77"],
         ["Semántico (bge-m3, 457,613 oraciones)", "recall 0.08 vs azar 0.05", "—"],
         ["Jericho-QA (cambios de estado)", "solo discrimina en condición de personajes", "—"],
         [("Decisión: H1e sin decisión confirmatoria (ningún instrumento llegó a confirmatorio)", {"span": 3, "fill": CLARO, "bold": True})]]
tabla(s, filas, 2.45, 1.85, 6.2, [2.6, 2.2, 1.0], alto_fila=0.55, size=11, centrar_cols=(1, 2))
texto(s, 8.95, 1.8, 3.9, 0.35, "Antecedente", size=13, bold=True, color=AZUL)
burbuja(s, 8.9, 2.2, "Papalampidi\net al.\n(2022)", "Coherencia y consistencia de entidades medidas de forma automática", w=4.0)
texto(s, 8.95, 3.45, 3.9, 0.35, "Validación humana externa", size=13, bold=True, color=AZUL)
caja(s, 9.0, 3.85, 3.85, 0.8, "Detector de PNJ inactivo: κ = 0.595 · precisión 62.5 % · exhaustividad 40 %", fill=AZUL_OSC, size=11, bold=False)
texto(s, 8.95, 4.8, 3.9, 0.35, "Siguiente paso", size=13, bold=True, color=AZUL)
caja(s, 9.0, 5.2, 3.85, 0.7, "Clasificador NLI en español con su propia prueba de sensibilidad", fill=CLARO, color=NEGRO, size=11, bold=False)
s._nota = ("[9:30–10:30] La coherencia longitudinal fue la más difícil de medir. Probamos varias líneas: coherencia de entidad, personajes inactivos, "
            "supervivencia, un instrumento semántico y Jericho. La evidencia es mixta y ningún instrumento llegó a confirmatorio, así que H1e queda "
            "sin decisión. El paso siguiente recomendado es un clasificador de inferencia textual en español.")
slides.append(s)

# 12 · OE6
s = contenido(5, "Resultados y discusión")
subtitulo(s, "OE6: Calidad narrativa emergente, G1 vs G2 (27 pares)")
filas = [[("Instrumento: persona2, usurpación explícita de la agencia (CC)", {"span": 2})],
         ["Turnos con usurpación (Mdn)", [("G1 0.17 %  vs  G2 3.47 %")][0]],
         ["p (Holm) · r", "< 0.0001 · ≈ −1.00"],
         ["Precisión por brazo (evaluador externo)", "G1 42.9 % · G2 28.6 %"],
         ["Corregido por precisión", "G1 < G2 en 27/27 pares (peor caso 26/27)"],
         ["Diversidad léxica a 100 palabras", "pequeña, a favor de G1"],
         [("Decisión: se acepta H1f (condicionada a la precisión de persona2)", {"span": 2, "fill": ACENTO, "color": BLANCO, "bold": True})]]
tabla(s, filas, 2.45, 1.85, 6.2, [2.0, 2.2], alto_fila=0.52, size=11, centrar_cols=(1,))
texto(s, 2.45, 5.65, 6.2, 0.7, [[("Turno real (par 10, G2, turno 426): ", {"bold": True}), ("el jugador observa a Elian; el narrador decide por él que «interpretas su silencio […] como un signo de nerviosismo y debilidad».", {"italic": True})]],
      size=10, color=GRIS)
texto(s, 8.95, 1.8, 3.9, 0.35, "Antecedente", size=13, bold=True, color=AZUL)
burbuja(s, 8.9, 2.2, "Zhu et al.\n(2023)", "El sistema toma decisiones en nombre del jugador", w=4.0)
texto(s, 8.95, 3.45, 3.9, 0.35, "¿Gana por gastar más?", size=13, bold=True, color=AZUL)
caja(s, 9.0, 3.85, 3.85, 0.85, "G1: 2.86 llamadas por turno vs 1. Pero en cada brazo, más cómputo va con MÁS usurpación (ρ +0.51 / +0.74)",
     fill=AZUL_OSC, size=11, bold=False)
texto(s, 8.95, 4.85, 3.9, 0.35, "Fundamento", size=13, bold=True, color=AZUL)
caja(s, 9.0, 5.25, 3.85, 0.75, "El narrador de G1 solo escribe la prosa: no arbitra ni interpreta a los PNJ", fill=CLARO, color=NEGRO, size=11, bold=False)
s._nota = ("[10:30–12:00] Este es el resultado principal. G2 usurpa la agencia del jugador en el 3.47 por ciento de los turnos; G1, en el 0.17. "
            "persona2 tiene una precisión de 33 por ciento frente al evaluador externo de referencia, así que corregimos cada brazo por su propia "
            "precisión: G1 sigue menor en los 27 pares, y en el peor caso en 26. Cambia la magnitud, no la dirección. Y no se explica por el mayor "
            "cómputo de G1: dentro de cada brazo, más cómputo va con más usurpación. H1f se acepta, condicionada.")
slides.append(s)

# 13 · Objetivo general, limitaciones y futuro
s = contenido(5, "Resultados y discusión")
filas = [[("Objetivo general", {"span": 2})],
         [("Comparar la coherencia narrativa de las campañas de D&D generadas por una arquitectura multiagente frente a una monolítica.", {"span": 2, "align": PP_ALIGN.CENTER})],
         ["La hipótesis general no se sostiene: de las tres comparativas solo se sostiene H1f (agencia); H1d no se sostiene y H1e queda sin decisión.",
          "Con una memoria estructurada común, especializar agentes no mejora la coherencia medible, pero sí reduce que el sistema decida por el jugador."]]
t = tabla(s, filas, 2.45, 1.45, 10.45, [1, 1], alto_fila=0.45, size=12)
t.rows[2].height = Inches(0.95)
for i, (h, items) in enumerate([("Limitaciones", ["Jugador simulado (mismo modelo en 24/27 pares)", "Un modelo, un idioma y un sistema de reglas", "persona2: precisión 33 %", "Sin confirmatorio longitudinal"]),
                                ("Aspectos futuros", ["Clasificador NLI en español", "Jugadores humanos", "Monolítico con igual presupuesto de llamadas", "Campañas de más de 1,400 turnos"])]):
    x0 = 2.45 + i * 5.3
    caja(s, x0 + 1.5, 3.6, 2.0, 0.5, h, size=13)
    for k, it in enumerate(items):
        caja(s, x0 + (k % 2) * 2.55, 4.3 + (k // 2) * 0.9, 2.4, 0.75, it, fill=CLARO, color=NEGRO, size=10, bold=False)
s._nota = ("[12:00–12:45] En síntesis, la hipótesis general no se sostiene: gana solo en una de tres. Las limitaciones son el jugador simulado, un solo "
            "modelo e idioma, la precisión de persona2 y la falta de un confirmatorio longitudinal; de ahí salen los trabajos futuros.")
slides.append(s)

# 14 · Conclusiones
s = contenido(6, "Conclusiones")
concl = [("OG", "Hipótesis general no sostenida: la ventaja del multiagente es específica, en la agencia del jugador."),
         ("OE1", "G2 sostiene una coherencia reactiva estable (Mdn z = 2.81) y no se degrada (Page p = 0.310)."),
         ("OE2", "La coherencia longitudinal de G2 es la más variable; sin confirmatorio y sin degradación exploratoria."),
         ("OE3", "G2 usurpa la agencia en el 3.47 % de los turnos, sin degradarse a lo largo de la campaña."),
         ("OE4", "Empate en lo específico; la ventaja cruda de G1 se debe a la extensión: H1d no se sostiene."),
         ("OE5", "Ningún instrumento longitudinal llegó a confirmatorio: H1e sin decisión."),
         ("OE6", "G1 0.17 % vs G2 3.47 %, robusto a la precisión y al cómputo: se acepta H1f (condicionada).")]
for i, (k, v) in enumerate(concl):
    y = 1.45 + i * 0.72
    caja(s, 3.25, y + 0.04, 9.4, 0.58, v, fill=ACENTO if k == "OE6" else AZUL, size=11, align=PP_ALIGN.LEFT).text_frame.margin_left = Inches(0.55)
    caja(s, 2.75, y - 0.02, 0.72, 0.7, k, fill=BLANCO, color=NEGRO, size=11, forma=MSO_SHAPE.OVAL, linea=AZUL)
s._nota = ("[12:45–13:45] Concluimos que, con una memoria estructurada común, especializar agentes no mejoró la coherencia medible: el monolítico no "
            "se degrada, la reactiva empata en lo específico y la longitudinal queda sin decisión. Pero separar los roles sí reduce que el sistema "
            "decida, piense, sienta o hable por el jugador, y eso resiste la corrección por precisión y el análisis de costo.")
slides.append(s)

# 15 · Recomendaciones
s = contenido(6, "Recomendaciones")
recs = [("Instrumento", "Refinar el libro de códigos de persona2 y calibrar con más evaluadores externos para promoverlo a confirmatorio pleno."),
        ("Longitudinal", "Desarrollar un confirmatorio para CL-1 y CL-2: un clasificador NLI en español con su propia prueba de sensibilidad."),
        ("Diseño", "Contrastar G1 con un monolítico de igual presupuesto de llamadas y registrar los tokens consumidos."),
        ("Jugadores", "Validar la ventaja en la agencia con jugadores humanos en lugar del agente jugador."),
        ("Horizonte", "Extender las campañas más allá de 1,400 turnos para verificar si la ausencia de degradación se mantiene.")]
for i, (k, v) in enumerate(recs):
    y = 1.5 + i * 0.98
    caja(s, 2.5, y, 1.95, 0.85, k, fill=AZUL, size=11, forma=MSO_SHAPE.PENTAGON)
    caja(s, 4.6, y + 0.05, 8.15, 0.75, v, fill=BLANCO, color=NEGRO, size=12, bold=False, linea=AZUL)
s._nota = ("[13:45–14:30] Recomendamos calibrar persona2 con más evaluadores, desarrollar un confirmatorio longitudinal en español, contrastar con un "
            "monolítico de igual presupuesto, validar con jugadores humanos y extender las campañas más allá de 1,400 turnos.")
slides.append(s)

# 16 · Anexo: batería de instrumentos
s = contenido(7, "Anexo: Batería de instrumentos")
C_, CC, E, D = "Confirmatorio", "Confirmatorio condicionado", "Exploratorio", "Descriptivo"
filas = [["Indicador", "Instrumento", "Clase"],
         ["CR-1 Fluidez", "Gramaticalidad (LanguageTool) · pifia narrada como éxito · otro alfabeto", D],
         ["CR-2 Arraigo a la acción", "Respuesta a la acción específica (z)", C_],
         ["", "Solapamiento con la acción · anclaje al escenario · nombres no reconocidos", E],
         ["CL-1 Personajes", "Coherencia de entidad C y consistencia de atributos V", E],
         ["CL-2 Eventos y mundo", "Jericho-QA · PNJ inactivo · supervivencia de PNJ no vivo", E],
         ["QN-1 Interés y diversidad", "MTLD · MATTR · TTR y bigramas a 100 palabras", E],
         ["QN-2 Agencia del jugador", "persona2: usurpación por decisión, pensamiento, emoción y habla", CC]]
tabla(s, filas, 2.45, 1.55, 10.45, [2.2, 5.6, 2.3], alto_fila=0.5, size=12, centrar_cols=(2,))
texto(s, 2.45, 5.75, 8.3, 0.6, "Cada instrumento pasó una prueba de sensibilidad por perturbaciones con expectativas selladas (SHA-256), δ de Cliff ≥ 0.147 y corrección de Holm.",
      size=11, italic=True, color=GRIS)
s._nota = "Respaldo: clasificación de cada instrumento según su prueba de sensibilidad (Anexo 1 de la tesis)."
slides.append(s)

# 17 · Anexo: evidencias y trazabilidad
s = contenido(7, "Anexo: Evidencias y trazabilidad")
cifras = [("77,413", "turnos registrados"), ("17,908", "cambios de estado con evidencia"), ("387", "PNJ"), ("947", "hechos conocidos por PNJ"), ("1,725", "lugares"), ("2,890", "objetos")]
for i, (n, l) in enumerate(cifras):
    x, y = 2.45 + (i % 3) * 2.8, 1.5 + (i // 3) * 1.25
    caja(s, x, y, 2.6, 1.05, [[(n, {"size": 22, "bold": True})], [(l, {"size": 11, "bold": False})]], fill=AZUL if i < 2 else CLARO, color=BLANCO if i < 2 else AZUL_OSC)
texto(s, 2.45, 4.15, 8.3, 0.35, "Ejemplo de cambio registrado con su cita literal (par 02, G2, turno 979)", size=13, bold=True, color=AZUL)
caja(s, 2.45, 4.55, 8.3, 0.75, [[("Jugador: «Prometo que haré todo lo posible para protegerte…»  →  ", {"bold": False}), ("promesa hecha", {"bold": True}),
                                 (" a «el hombre de los harapos», con esa cita literal", {"bold": False})]], fill=BLANCO, color=NEGRO, size=12, linea=AZUL, align=PP_ALIGN.LEFT)
texto(s, 2.45, 5.5, 8.3, 0.8, "Código, datos, transcripciones, validaciones humanas y análisis: repositorio del proyecto (ver README).", size=12, color=GRIS)
caja(s, 11.0, 1.5, 1.9, 2.45, [[("Acceso a repositorio y evidencias", {"bold": True})], [("github.com/BMarin2003/ORQUESTADOR-DM-IA", {"bold": False, "size": 9})]], fill=AZUL, size=11)
s._nota = "Respaldo: la base de datos del estado del mundo y un ejemplo real de cambio registrado con su cita literal."
slides.append(s)

# ------------------------------------------------------------------ orden, barra, índice y notas
lst = prs.slides._sldIdLst
ids = list(lst)
cierre_id = next(i for i in ids if prs.part.related_part(i.rId) is cierre.part)
lst.remove(cierre_id)
lst.append(cierre_id)

primera = {}
for sl in slides:
    primera.setdefault(sl._seccion, sl)
destinos = [primera[i] for i in range(len(SECCIONES))]
for sl in slides:
    barra(sl, destinos)
for sh in indice.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Introducción"):
        for p, d in zip(sh.text_frame.paragraphs, destinos):
            enlazar(p.runs[0], d, indice)
indice.notes_slide.notes_text_frame.text = "Recorrido de la exposición por las secciones del formato oficial."
for sl in slides:
    sl.notes_slide.notes_text_frame.text = sl._nota

prs.save(SALIDA)
print("OK", SALIDA, len(prs.slides), "láminas")
