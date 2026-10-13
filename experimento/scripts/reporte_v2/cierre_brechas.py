"""
Documento de CIERRE DE BRECHAS (docs/cierre_brechas.md): las tres listas de resultados deterministas, la matriz 7 objetivos × 4 brechas con su evidencia y estado,
el porcentaje de cumplimiento por objetivo y los anexos. TODAS las cifras salen de docs/reportes/consolidado_v2.csv y datos/datos_v2/cierre/ (no se teclean).
Regla del estado: CERRADA = la pregunta de la brecha se contesta directamente con datos deterministas; PARCIAL = hay evidencia por proxy o un instrumento sin
auditar; LÍMITE = no hay instrumento determinista (se declara); PENDIENTE = es redacción. Cumplimiento del objetivo = (cerradas + 0.5 × parciales) / brechas.
    PYTHONUTF8=1 py experimento/scripts/reporte_v2/consolidar.py && PYTHONUTF8=1 py experimento/scripts/reporte_v2/cierre_brechas.py
"""
import csv
import statistics as st
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
CONS = RAIZ / "docs" / "reportes" / "consolidado_v2.csv"
D2 = RAIZ / "datos" / "datos_v2" / "cierre"
SALIDA = RAIZ / "docs" / "cierre_brechas.md"

PCT = {"cr1", "cl2_pnj_inactivo_actua", "cr2_nombres_no_reconocidos", "p2_primaria", "p2_volicion", "p2_cognicion", "p2_emocion", "p2_habla", "p2_secundaria",
       "rep_frases", "nolatin"}
DEC = {"grammaticality_lt": 4, "cr2a_z": 2, "cr2a_crudo": 3, "cr2b_cos_v8": 3, "cr2b_cos_v8_sn": 3, "papalampidi_C": 2, "papalampidi_V": 3, "ecr": 3, "jericho_recall": 2,
       "relojes_reconocidos": 2, "pnj_refinado": 2, "qn1_ttr": 3, "qn1_ngram_repeticion": 3, "qn1_legibilidad_fh": 1, "sd_ttr": 4, "sd_fh": 2, "n_npc": 1, "n_misiones": 1,
       "t_pnj": 0, "seg_turno": 1, "cl2_lugar_jaccard_similarity": 3, "cr2_entidad_grafo_densidad": 3, "cr2_n_nombres_no_reconocidos": 3, "grafo_lema": 3, "bucles_ciclos": 2}


def leer():
    """Carga `consolidado_v2.csv` indexado por la clave del instrumento."""
    with open(CONS, newline="", encoding="utf-8") as fh:
        return {r["clave"]: r for r in csv.DictReader(fh)}


C = leer()


def _f(v, clave):
    """Formatea un valor del consolidado: porcentaje si la clave está en `PCT`, si no con los decimales de `DEC`; «—» si falta."""
    if v in ("", None):
        return "—"
    x = float(v)
    return f"{100 * x:.2f} %" if clave in PCT else f"{x:.{DEC.get(clave, 3)}f}"


def g(clave, brazo):
    """Nivel medio del brazo ('G1' o 'G2')."""
    r = C[clave]
    return _f(r["media_" + brazo.lower()], clave) if r["media_g1"] != "" else "s/d"


def R(clave, hl=True):
    """«G1 x vs G2 y (HL h, r, p Holm, n parejas)»."""
    r = C[clave]
    if r["media_g1"] == "":
        return f"sin datos suficientes ({r['n']} parejas)"
    h = float(r["hl"])
    hl_txt = f"{100 * h:+.2f} pp" if clave in PCT else f"{h:+.{DEC.get(clave, 3)}f}"
    ph = float(r["p_holm"])
    return (f"G1 {g(clave, 'G1')} vs G2 {g(clave, 'G2')}" +
            (f" (HL G1−G2 {hl_txt}; r {float(r['rb']):+.2f}; p Holm {ph:.2g}; {r['n']} parejas)" if hl else ""))


def sg(clave):
    """¿Cambia de signo entre lotes?"""
    r = C[clave]
    a, b = r["hl_lote1"], r["hl_lote2"]
    return bool(a and b and float(a) * float(b) < 0)


def bloques():
    """Lee `bloques.csv` (7 bloques de 200 turnos) como {(indicador, brazo, par): {n_bloque: valor}}.

    Ignora los bloques sin valor.
    """
    with open(D2 / "bloques.csv", newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    out = {}
    for r in filas:
        if r["valor"] != "":
            out.setdefault((r["indicador"], r["brazo"], r["par"]), {})[int(r["bloque"])] = float(r["valor"])
    return out


def tabla_bloques(B, indicadores):
    """Tabla Markdown de la media por bloque (B1-B7) de cada indicador y brazo (Anexo A, deriva por profundidad).

    Solo usa series con los 7 bloques completos; la última columna cuenta las parejas con B7 > B1.
    """
    L = ["| Indicador | Brazo | B1 (1-200) | B2 | B3 | B4 | B5 | B6 | B7 (1201-1400) | último > primero |", "|---|---|---|---|---|---|---|---|---|---|"]
    for ind, etiq, pct in indicadores:
        for brazo in ("G1", "G2"):
            series = [v for (i, b, _), v in B.items() if i == ind and b == brazo and len(v) == 7]
            if not series:
                continue
            medias = [st.mean(s[k] for s in series) for k in range(1, 8)]
            sube = sum(1 for s in series if s[7] > s[1])
            fmt = (lambda x: f"{100 * x:.2f} %") if pct else (lambda x: f"{x:.3f}")
            L.append(f"| {etiq} | {brazo} | " + " | ".join(fmt(m) for m in medias) + f" | {sube}/{len(series)} |")
    return L


def incidencia():
    """Tabla Markdown de la incidencia acumulada del primer PNJ inactivo que actúa (`t_pnj`) por brazo.

    Cuenta campañas con `t_pnj` <= cada tope (200 a 1400), las que nunca ocurren y la mediana entre las que sí.
    """
    with open(D2 / "por_campana.csv", newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    L = ["| Brazo | ≤ 200 | ≤ 400 | ≤ 600 | ≤ 800 | ≤ 1000 | ≤ 1200 | ≤ 1400 | nunca | mediana (turno, entre las que ocurren) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for brazo in ("G1", "G2"):
        x = [r for r in filas if r["brazo"] == brazo]
        ts = [int(r["t_pnj"]) for r in x if r["t_pnj"] != ""]
        cel = [f"{sum(1 for t in ts if t <= T)}/{len(x)}" for T in range(200, 1401, 200)]
        L.append(f"| {brazo} | " + " | ".join(cel) + f" | {len(x) - len(ts)}/{len(x)} | {st.median(ts):.0f} |")
    return L


def top_frases():
    """Tabla Markdown con las 5 frases idénticas más repetidas por brazo, desde `top_frases.csv` (Anexo C)."""
    with open(D2 / "top_frases.csv", newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    L = ["| Brazo | Veces | Pareja | Frase (exactamente igual, normalizada a minúsculas) |", "|---|---|---|---|"]
    for brazo in ("G1", "G2"):
        for r in sorted([x for x in filas if x["brazo"] == brazo], key=lambda x: -int(x["veces"]))[:5]:
            L.append(f"| {brazo} | {r['veces']} | {r['par']} | {r['frase'][:140]} |")
    return L


# ------------------------------------------------------------------ la matriz
def brechas():
    """Matriz de brechas de la literatura por objetivo, con su evidencia y su estado.

    Returns:
        Lista de (id_objetivo, título, [(brecha, evidencia, estado, qué falta)]). Estados: CERRADA, PARCIAL,
        LÍMITE o PENDIENTE (ver regla en el docstring del módulo). Las cifras se interpolan desde el consolidado.
        Es borrador: las brechas se rehacen tras la docimasia (7 objetivos previos vs. 6 de la tesis).
    """
    ce, pa, li, pe = "CERRADA", "PARCIAL", "LÍMITE", "PENDIENTE"
    return [
        ("OE-1", "Revisión sistemática de la literatura sobre arquitecturas de IA para narrativa interactiva", [
            ("Sin taxonomías estandarizadas para arquitecturas de IA en narrativa de final abierto", "No es medible con datos: es un producto de redacción (SLR con protocolo PRISMA). Insumo disponible: `docs/papers_revistas_q1-q3.md`.", pe, "Redactar la SLR: ecuaciones de búsqueda, criterios de inclusión y exclusión, flujo de selección."),
            ("Sin revisiones comparativas de mecanismos de memoria en narrativas largas", "Ídem. Los datos propios aportan evidencia empírica sobre memoria (Lista 2) pero no sustituyen la revisión.", pe, "Ídem."),
            ("Sin protocolos de benchmarking estandarizados para narrativas co-creadas", "Ídem. Aporte propio: matriz de cobertura rúbrica ↔ instrumentos y validación por sensibilidad (`docs/matriz_cobertura_rubrica_instrumentos.md`, `docs/reportes/sensibilidad_baseline.md`).", pe, "Redactar el vínculo entre el benchmark propuesto y la literatura."),
            ("Sin análisis de costos y latencias entre generación monolítica y orquestación multiagente",
             f"Tiempo por turno (mediana por campaña, proxy): {R('seg_turno')}. Costo total registrado del lote Par18-27: 37.05 USD (20 campañas); **el costo por brazo no se registró** (la base no guarda tokens).", pa, "Costo por brazo desde el panel del proveedor si está disponible; si no, declararlo como límite."),
        ]),
        ("OE-2", "Coherencia reactiva del sistema monolítico (G2)", [
            ("Arraigo contextual frágil ante entradas caóticas o fuera de distribución",
             f"Respuesta a la acción (CR-2a, z): G2 {g('cr2a_z', 'G2')}; cae 2.3-2.9 unidades al sustituir la respuesta por la de otro turno (matriz a4bc-2, 25 de 26 celdas direccionales aprobadas). Anclaje al escenario (CR-2b, coseno de ventana): G2 {g('cr2b_cos_v8', 'G2')}, con deriva a lo largo de la campaña (Anexo A).", pa, "No se clasificó la entrada del jugador por grado de caos; solo se mide el arraigo en general."),
            ("Recurrencia de placeholders y frases evasivas",
             f"Turnos con una frase idéntica repetida ≥ 3 veces: G2 {g('rep_frases', 'G2')} (medida simple, límite inferior; no ve paráfrasis). Frases más repetidas: Anexo C.", pa, "Sin detector de paráfrasis evasivas."),
            ("Degradación semántica por sobrecarga de contexto (fragmentos en otros idiomas, fallos de codificación)",
             f"Turnos con caracteres de otro alfabeto o U+FFFD: G2 {g('nolatin', 'G2')} de los turnos; tendencia por profundidad en el Anexo A.", pa, "Se mide incidencia y tendencia; la causa (sobrecarga de contexto) no se aísla."),
            ("Faltan métricas que separen la corrección pragmática de la mecánica-reglamentaria",
             f"Tres instrumentos separados: gramaticalidad (lingüística) G2 {g('grammaticality_lt', 'G2')} (techo, discrimina poco); pifia narrada como éxito, `cr1` (reglas) G2 {g('cr1', 'G2')} (baja precisión: ignora la negación); respuesta a la acción, CR-2a (pragmática).", pa, "La plausibilidad lógica sigue sin instrumento."),
        ]),
        ("OE-3", "Coherencia longitudinal del sistema monolítico (G2)", [
            ("Colisión de identidades en entidades nombradas",
             f"**Sin instrumento determinista.** Proxies parciales: consistencia de atributos (Papalampidi V) G2 {g('papalampidi_V', 'G2')} y coherencia de entidad (C) G2 {g('papalampidi_C', 'G2')}. Evidencia cualitativa previa (panel humano, 3 campañas G2, orquestador anterior; no determinista): reasignación del nombre «Kaelen» a siete personajes.", li, "Declarar el límite (Sección de límites); una auditoría humana posterior puede cuantificarlo."),
            ("Degradación del linaje causal (olvido de eventos, restauración de estados ya modificados)",
             f"Cambios de estado registrados que la narración refleja (Jericho, recall): G2 {g('jericho_recall', 'G2')}. PNJ no vivo mencionado (% de turnos): G2 {g('cl2_pnj_inactivo_actua', 'G2')}; como sujeto: {g('pnj_refinado', 'G2')} por 1 000 turnos. Ambos detectores miden mención, no acción, y su precisión no está auditada.", pa, "Auditar la precisión de `cl2_pnj_inactivo_actua` (fase posterior)."),
            ("Inestabilidad de la alineación de facciones y relaciones morales",
             "Sin instrumento que mida cambios de bando. El recall de Jericho incluye las familias `npc.affinity` y `npc.status`, pero no se separó por familia ni mide alternancia.", li, "Declarar el límite o medir la alternancia de afinidad en `state_deltas`."),
            ("Las bases vectoriales planas no representan la mutación de grafos de estado",
             f"Evidencia indirecta: fracción de relojes de facción disparados que la narración reconoce (proxy léxico): G2 {g('relojes_reconocidos', 'G2')}; recall de Jericho G2 {g('jericho_recall', 'G2')}. Limitación conocida: Par01-17 sin avance de reloj.", pa, "Sin prueba de sensibilidad para Jericho ni relojes."),
        ]),
        ("OE-4", "Calidad narrativa emergente del sistema monolítico (G2)", [
            ("Monotonía estilística y aplanamiento expresivo",
             f"Diversidad léxica (TTR) G2 {g('qn1_ttr', 'G2')}; repetición de bigramas {g('qn1_ngram_repeticion', 'G2')}; frases idénticas repetidas {g('rep_frases', 'G2')}; tendencia por profundidad en el Anexo A. Miden diversidad y repetición, no expresividad.", pa, "Sin instrumento de interés ni creatividad."),
            ("Tensión entre reactividad local y arcos dramáticos globales",
             f"Reactividad local (CR-2a, z) estable a lo largo de la campaña, mientras el anclaje al escenario (CR-2b) cae (Anexo A): G2 {g('cr2b_cos_v8', 'G2')}. Fracción de relojes reconocidos (eventos de arco): G2 {g('relojes_reconocidos', 'G2')}.", pa, "El coseno no distingue deriva de evolución legítima del mundo."),
            ("Varianza y subjetividad de la evaluación estética entre jueces",
             "El enfoque determinista elimina la varianza entre jueces, pero **no mide interés**: es una limitación del método, no un dato.", li, "Auditoría humana posterior si el asesor la aprueba."),
            ("Degradación de la ilusión de agencia con el tiempo",
             f"Usurpación mental o verbal del PJ, G2 {g('p2_primaria', 'G2')} de los turnos; por profundidad, Anexo A. Las consecuencias visibles de las decisiones no tienen instrumento.", pa, "Precisión de `persona2` sin auditar (fase posterior)."),
        ]),
        ("OE-5", "Comparación de la coherencia reactiva entre arquitecturas (G1 vs G2)", [
            ("Faltan experimentos controlados que aíslen la arquitectura como única variable",
             "Diseño de 27 parejas con el mismo modelo (google/gemma-4-31B-it), el mismo lore, el mismo personaje y el mismo agente jugador en ambos brazos (`docs/especificaciones/descomposicion_prompts.md`, auditoría de paridad G1/G2). El formato de salida de G1 se normalizó y se cuantificó su efecto (`docs/reportes/reporte_v2_formato_normalizado.md`). Par01-17 y Par18-27 usan versiones distintas del motor y se analizan por lote.", ce, "—"),
            ("Se ignora el efecto de la latencia de la negociación entre agentes sobre la fluidez",
             f"Tiempo por turno: {R('seg_turno')}. Fluidez (gramaticalidad, techo): {R('grammaticality_lt')}. Caracteres de otro alfabeto: {R('nolatin')}. La latencia es un proxy de tiempo de pared con corridas concurrentes.", ce, "—"),
            ("Sin evidencia de que un agente supervisor elimine los placeholders",
             f"Frases idénticas repetidas: {R('rep_frases')}; G1 repite más, no menos (Anexo C: «La paciencia de … se ha agotado», hasta 95 veces en una campaña). Respuesta a la acción: {R('cr2a_z')}; anclaje: {R('cr2b_cos_v8')}. No hay ablación del supervisor: la comparación es entre sistemas completos.", pa, "Ablación del supervisor (fuera del alcance) o declarar."),
            ("Sin estudios inferenciales no paramétricos sobre pares de transcripciones",
             "Wilcoxon exacto sobre las diferencias por pareja, Hodges-Lehmann con IC bootstrap sobre parejas, correlación rank-biserial pareada y corrección de Holm (`experimento/scripts/reporte_v2/consolidar.py`). El doble ciego humano no aplica a la medición determinista.", ce, "—"),
        ]),
        ("OE-6", "Comparación de la coherencia longitudinal entre arquitecturas", [
            ("Sin evidencia de que grafos relacionales e identificadores inmutables mitiguen la colisión de identidades",
             f"Sin instrumento de colisión (ver OE-3). Proxies: C {R('papalampidi_C')}; V {R('papalampidi_V')}; PNJ no vivo mencionado {R('cl2_pnj_inactivo_actua')}.", li, "Declarar el límite; auditoría posterior."),
            ("No se mide la acumulación de entropía fáctica con la profundidad de la campaña",
             f"Deriva por bloques de 200 turnos en ambos brazos (Anexo A): PNJ no vivo mencionado, nombres no reconocidos, anclaje al escenario, repetición. Nombres no reconocidos por turno: {R('cr2_nombres_no_reconocidos')}.", pa, "Sin modelo de entropía propiamente dicho."),
            ("Faltan modelos cuantitativos de supervivencia de estados fácticos",
             f"Turno de la primera mención de un PNJ no vivo (1 401 = nunca): {R('t_pnj')}. Incidencia acumulada en el Anexo B. No es un modelo de supervivencia con censura formal.", pa, "Kaplan-Meier o similar si se decide; el detector no está auditado."),
            ("Faltan evaluaciones humanas a ciegas del rigor histórico con memoria persistente",
             "No aplica al enfoque determinista. Queda para la fase posterior (auditoría con humano y conversación con el asesor).", li, "Fase posterior."),
        ]),
        ("OE-7", "Comparación de la calidad narrativa emergente entre arquitecturas", [
            ("Inconsistencias estilísticas («esquizofrenia narrativa») en sistemas multiagente",
             f"Estabilidad de estilo dentro de la campaña (variación entre bloques): TTR {R('sd_ttr')}; Fernández-Huerta {R('sd_fh')}. Persona gramatical: G1 mezcla 2.ª y 3.ª persona (36.9 % en 2.ª) y G2 narra en 2.ª (84.5 %), medido en Par07-27 (`docs/matriz_cobertura_rubrica_instrumentos.md`).", pa, "Sin medida de tono."),
            ("Impacto de la competencia entre agentes sobre la agencia del jugador (QN-2)",
             f"Usurpación mental o verbal del PJ: {R('p2_primaria')}. Por categoría: decisión {g('p2_volicion', 'G1')} vs {g('p2_volicion', 'G2')}; pensamiento {g('p2_cognicion', 'G1')} vs {g('p2_cognicion', 'G2')}; emoción {g('p2_emocion', 'G1')} vs {g('p2_emocion', 'G2')}; habla {g('p2_habla', 'G1')} vs {g('p2_habla', 'G2')}. Detector congelado, léxico cerrado, precisión sin auditar.", pa, "Auditoría de precisión de `persona2` (fase posterior)."),
            ("Sin pruebas comparativas de innovación y emergencia de ganchos dramáticos",
             f"Sin instrumento de interés ni de ganchos. Proxies de emergencia (descriptivos): PNJ registrados {R('n_npc')}; misiones registradas {R('n_misiones')} (G1 tiene un agente extra que también crea entidades).", li, "Declarar el límite."),
            ("Faltan estudios con rúbricas validadas de calidad narrativa aplicadas por paneles a ciegas",
             "La rúbrica v2 con panel humano se sustituyó por medición determinista a petición del asesor; la rúbrica queda como definición de los constructos y los instrumentos como su operacionalización (`docs/matriz_cobertura_rubrica_instrumentos.md`). Un panel queda como fase posterior opcional (Ruta B).", li, "Fase posterior."),
        ]),
    ]


PESO = {"CERRADA": 1.0, "PARCIAL": 0.5, "LÍMITE": 0.0, "PENDIENTE": 0.0}
PREVIO = {"OE-1": 40, "OE-2": 60, "OE-3": 60, "OE-4": 60, "OE-5": 15, "OE-6": 15, "OE-7": 15}


def lista(titulo, dims, filas):
    """Tabla Markdown de una lista de resultados: filas del consolidado cuyas dimensiones están en `dims`.

    Muestra G1, G2, HL (G1−G2), r rank-biserial y p Holm; marca con ⚠ los instrumentos cuyo signo cambia entre
    lotes (`sg`) y indica «sin datos suficientes» si no hay medias.
    """
    L = [f"### {titulo}", "", "| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) | r | p Holm | Parejas | Estado |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in filas:
        if r["dimension"] not in dims:
            continue
        k = r["clave"]
        if r["media_g1"] == "":
            L.append(f"| {r['dimension']} | {r['etiqueta']} | {r.get('sentido', '')} | — | — | — | — | — | {r['n']} | sin datos suficientes (aún) |")
            continue
        h = float(r["hl"])
        hl = f"{100 * h:+.2f} pp" if k in PCT else f"{h:+.{DEC.get(k, 3)}f}"
        L.append(f"| {r['dimension']} | {r['etiqueta']} | {r['sentido']} | {g(k, 'G1')} | {g(k, 'G2')} | {hl} | {float(r['rb']):+.2f} | {float(r['p_holm']):.2g} | {r['n']} | {r.get('nota', '')}" +
                 (" ⚠ signo distinto entre lotes" if sg(k) else "") + " |")
    L.append("")
    return L


def main():
    """Genera `docs/cierre_brechas.md` (borrador): matriz de brechas por objetivo, tres listas de resultados y anexos.

    Todas las cifras salen del consolidado y de `datos/datos_v2/cierre/`. También imprime por consola el conteo de
    estados y la cobertura (cerradas + 0,5 × parciales) / brechas por objetivo.
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with open(CONS, newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    B = bloques()
    n_par = max(int(r["n"]) for r in filas)
    L = ["# Cierre de brechas de investigación con resultados deterministas (BORRADOR)", "",
         "> **Borrador, no usar todavía.** Las 28 brechas (7 objetivos × 4) salen de un análisis previo hecho con otros resultados y con siete objetivos; la tesis tiene seis. "
         "Las brechas se rehacen después de plasmar los resultados y hacer la docimasia. Las tres listas y los anexos siguen siendo válidos como datos; la matriz de brechas y su porcentaje no.", "",
         f"Muestra: {n_par} parejas (Par01-27), {2 * n_par} campañas, {format(2 * n_par * 1400, ',').replace(',', ' ')} turnos" +
         " (1 400 por campaña); mismo modelo y mismo agente jugador en ambos brazos; medición 100 % determinista sobre texto normalizado, sin evaluadores humanos. "
         "Todas las cifras salen de `docs/reportes/consolidado_v2.csv` y `datos/datos_v2/cierre/` (`experimento/scripts/reporte_v2/`); son **descriptivas** y **posteriores (post hoc)** en lo que corrige instrumentos.", "",
         "**Alcance.** Los instrumentos deterministas miden proxies de las dimensiones de la rúbrica (diversidad léxica, anclaje léxico, menciones, cumplimiento de la regla de oro del prompt). "
         "No miden interés, creatividad ni voz del personaje, y varios detectores tienen la precisión sin auditar (se indica en cada fila). Una diferencia entre brazos **no implica superioridad**. "
         "Los resultados del panel humano sobre 3 campañas G2 (orquestador anterior) no se mezclan con estos: escala y método distintos.", "",
         "## 1. Estado de las brechas por objetivo", "",
         "Regla: **cerrada** = la pregunta de la brecha se contesta directamente con datos; **parcial** = evidencia por proxy o detector sin auditar; **límite** = sin instrumento determinista (se declara); **pendiente** = redacción. "
         "**Cobertura de brechas** = (cerradas + 0,5 × parciales) / 4. No es comparable con el «cumplimiento» previo: aquel era una estimación del avance de cada objetivo con base en el panel humano sobre 3 campañas G2 y en los datos pendientes; esta mide cuántas brechas de la literatura tienen respuesta con datos deterministas.", "",
         "| Objetivo | Cerradas | Parciales | Límite | Pendiente | Cobertura de brechas (regla) | Cumplimiento previo (otra base) |", "|---|---|---|---|---|---|---|"]
    M = brechas()
    for oid, tit, bs in M:
        c = {k: sum(1 for b in bs if b[2] == k) for k in PESO}
        pct = 100 * sum(PESO[b[2]] for b in bs) / len(bs)
        regla = f"{pct:.0f} %" if oid != "OE-1" else "— (es redacción; ver nota)"
        L.append(f"| **{oid}** {tit} | {c['CERRADA']} | {c['PARCIAL']} | {c['LÍMITE']} | {c['PENDIENTE']} | {regla} | {PREVIO[oid]} % |")
    L += ["", "Nota OE-1: la SLR es un producto de redacción; los resultados deterministas no la sustituyen y su avance sigue siendo el de la estimación previa hasta que se redacte. "
          "OE-2 a OE-4 caracterizan a G2 (nivel absoluto en cada lista); OE-5 a OE-7 comparan G1 con G2 (diferencia por pareja).", "",
          "## 2. Las tres listas de resultados deterministas", "",
          "**Cómo leer.** Cada valor es la media de la campaña (turnos 2-1 400; `persona2` solo sobre turnos que no se usaron para construir el detector); la unidad de análisis es la pareja. "
          "HL = Hodges-Lehmann de G1 − G2 entre parejas; r = correlación rank-biserial pareada (+1 = G1 mayor en todas las parejas); p Holm = Wilcoxon exacto corregido sobre toda la tabla del consolidado. "
          "↕: ↓ menos es mejor, ↑ más es mejor, · neutro. Detalle con IC, lotes y estado de cada instrumento en `docs/reportes/consolidado_v2.md`.", ""]
    L += lista("Lista 1. Coherencia reactiva (CR-1, CR-2)", ("CR-1", "CR-2"), filas)
    L += lista("Lista 2. Coherencia longitudinal (CL-1, CL-2)", ("CL-1", "CL-2"), filas)
    L += lista("Lista 3. Calidad narrativa emergente (QN-1, QN-2)", ("QN-1", "QN-2"), filas)
    L += ["## 3. Matriz de cierre de brechas", ""]
    for oid, tit, bs in M:
        L += [f"### {oid}. {tit}", "", "| # | Brecha | Evidencia determinista | Estado | Qué falta |", "|---|---|---|---|---|"]
        for i, (brecha, ev, est, falta) in enumerate(bs, 1):
            L.append(f"| {i} | {brecha} | {ev} | **{est}** | {falta} |")
        L.append("")
    L += ["## 4. Anexos", "",
          "### Anexo A. Deriva por bloques de 200 turnos (media de las parejas)", "",
          "«Último > primero» = parejas en que el último bloque supera al primero (sobre 27).", ""]
    L += tabla_bloques(B, [("qn1_ttr", "TTR", False), ("qn1_ngram_repeticion", "Repetición de bigramas", False), ("rep_frases", "Frases idénticas repetidas", True),
                           ("cl2_pnj_inactivo_actua", "PNJ no vivo mencionado", True), ("cr2_nombres_no_reconocidos", "Nombres no reconocidos", True),
                           ("primaria", "Usurpación mental o verbal (persona2)", True), ("nolatin", "Otro alfabeto o U+FFFD", True),
                           ("cl2_lugar_jaccard_similarity", "Jaccard con la escena anterior", False)])
    L += ["", "Anclaje al escenario y respuesta a la acción por ventana de 200 turnos: `docs/reportes/sensibilidad_a4bc_distribucion_27.csv`.", "",
          "### Anexo B. Primera mención de un PNJ no vivo: campañas donde ya ocurrió", ""] + incidencia()
    L += ["", "### Anexo C. Frases idénticas más repetidas (por campaña, exactas)", ""] + top_frases()
    L += ["", "### Anexo D. Trazabilidad y advertencias", "",
          "- Detector `persona2` v2b congelado (hashes en `datos/validacion/persona2_congelado.sha256`); matriz de CR-2a/CR-2b a4bc-2, SHA-256 `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744`.",
          "- Par02 G2 tiene 1 668 turnos en la base; todos los cálculos se recortan a 1 400.",
          "- Sanidad del recálculo: en G2 (donde la normalización es la identidad) v1 = v2 en Par07-27 (0 discrepancias en 29 400 turnos por instrumento); en Par01-06, 42 de 8 400 turnos difieren en el recuento de nombres no reconocidos y 2 en la densidad del grafo (reconstrucción de entidades de un motor previo), sin efecto material.",
          "- Par01-17 se generaron con el motor sin avance de reloj ni guardia de metamensajes; Par18-27 con reloj determinista, dados de combate y guardia. Cada resultado del consolidado muestra el HL por lote y marca los cambios de signo.",
          "- Las medidas del Anexo A-C (`experimento/scripts/reporte_v2/medidas_cierre.py`) no tienen prueba de sensibilidad: son medidas simples y transparentes.", ""]
    SALIDA.write_text("\n".join(L), encoding="utf-8")
    print("escrito", SALIDA)
    for oid, tit, bs in M:
        print(oid, {k: sum(1 for b in bs if b[2] == k) for k in PESO}, f"{100 * sum(PESO[b[2]] for b in bs) / len(bs):.1f} %")


if __name__ == "__main__":
    main()
