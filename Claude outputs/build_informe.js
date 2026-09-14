const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
  TableCell, WidthType, ShadingType, BorderStyle, AlignmentType,
  LevelFormat, convertInchesToTwip,
} = require("docx");

const PAGE = { width: 12240, height: 15840 }; // US Letter

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 160 },
    alignment: AlignmentType.JUSTIFIED,
  });
}
function pRich(runs) {
  return new Paragraph({ children: runs, spacing: { after: 160 }, alignment: AlignmentType.JUSTIFIED });
}
function bold(text) { return new TextRun({ text, bold: true }); }
function reg(text) { return new TextRun({ text }); }
function code(text) { return new TextRun({ text, font: "Consolas", size: 20 }); }
function bullet(text, level = 0) {
  return new Paragraph({
    children: [new TextRun({ text })],
    numbering: { reference: "bullets", level },
    spacing: { after: 80 },
  });
}
function bulletRich(runs, level = 0) {
  return new Paragraph({ children: runs, numbering: { reference: "bullets", level }, spacing: { after: 80 } });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "2F3B52" } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, bold: !!opts.header, color: opts.header ? "FFFFFF" : undefined, size: opts.size || 20 })],
    })],
    verticalAlign: "center",
  });
}

function table(colWidths, headerRow, rows) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({ children: headerRow.map((t, i) => cell(t, { header: true, width: colWidths[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) => cell(t, { width: colWidths[i] })) })),
    ],
  });
}

const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: convertInchesToTwip(0.3), hanging: convertInchesToTwip(0.15) } } } },
        { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: convertInchesToTwip(0.6), hanging: convertInchesToTwip(0.15) } } } },
      ],
    }],
  },
  sections: [{
    properties: { page: { size: PAGE, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children: [

      new Paragraph({ text: "Informe técnico para el asesor", heading: HeadingLevel.TITLE, spacing: { after: 80 } }),
      new Paragraph({
        children: [new TextRun({
          text: "Por qué persiste la brecha entre lo planificado y lo generado: la nueva orquestación del motor y la viabilidad de las métricas computacionales determinísticas",
          bold: true, size: 26,
        })],
        spacing: { after: 240 },
      }),
      pRich([reg("Tesis: "), italicRun("Comparación de la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos"), reg(" — QuestMasters, UPAO.")]),
      p("Fecha: 14 de septiembre de 2026. Preparado por Bryan Marín, con Luis Mostacero como co-autor."),

      h1("1. Resumen ejecutivo"),
      p("La brecha entre el número de pares planificados (27) y el número de pares efectivamente generados y validados (2 cerrados, 1 en generación al momento de este informe) no se debe a que la generación de campañas sea lenta o costosa -- el costo real medido es de $0.0007-$0.0013 por turno, muy por debajo de cualquier límite de presupuesto -- sino a que la FASE 0 del plan de cierre (\"cerrar brecha de instrumentación\", ver plan-cierre-investigacion.md) resultó ser sustancialmente más profunda de lo estimado. Antes de poder confiar en un solo número que compare G1 contra G2, fue necesario encontrar y corregir una serie de fallos silenciosos en el propio instrumento de medición -- fallos que, de no corregirse, habrían producido una comparación que parecía válida pero no lo era."),
      p("Este documento explica, en orden: (2) la arquitectura de la nueva orquestación que genera y mide las campañas; (3) los fallos de instrumentación encontrados esta sesión y por qué cada uno habría invalidado la comparación si no se corregía; (4) el estado actual del corpus generado; (5) una evaluación crítica de la viabilidad real de cada métrica computacional determinística, con los datos concretos de los dos pares ya cerrados; y (6) dónde encontrar la evidencia completa de cada afirmación."),

      h1("2. La nueva orquestación: arquitectura técnica"),
      p("El motor de generación vive en el repositorio local (no en el monorepo questmasters-monorepo, que es la reescritura en curso para producción) y separa nítidamente tres capas: persistencia estructurada, generación narrativa, y validación post-hoc."),

      h2("2.1 Persistencia estructurada (Postgres, migrations/001_schema.sql)"),
      p("El estado del mundo NO vive en el texto narrativo, vive en tablas relacionales: campaigns, locations (jerárquicas, con parent_id), factions, faction_clocks, quests, characters (los PJ), npcs (con sus satélites npc_ibf, npc_disposition, npc_knowledge, npc_secrets, npc_bond_targets), turn_log (el texto generado turno a turno) y state_deltas (el ledger de cada cambio de estado, con evidencia textual literal obligatoria para los deltas extraídos por el LLM). Una función almacenada, apply_delta(), es la única puerta de escritura sobre el estado narrativo: valida el campo contra una lista blanca (mutable_fields), aplica topes de dominio (p. ej. afinidad acotada a [-100, 100] con techos por personalidad del PNJ) y registra el delta en el ledger de forma atómica."),
      p("Esta separación es lo que hace posible medir: si el estado \"real\" no estuviera en tablas estructuradas sino solo implícito en la prosa, no habría forma determinística de comparar lo que el modelo narró contra lo que efectivamente pasó."),

      h2("2.2 Las dos arquitecturas generadoras"),
      pRich([bold("G2 (monolítico) -- "), reg("orquestador/vertical_slice.py. Un único prompt (dm/prompt_g2.md) recibe todo el contexto de escena y genera turno a turno: narración, extracción de deltas y validación en una sola pasada por turno.")]),
      pRich([bold("G1 (multiagente) -- "), reg("orquestador/vertical_slice_g1.py, con cuatro roles separados (dm/*_g1.md): Router decide qué PNJ actúa, Actor genera la reacción del PNJ (con acceso a su ficha completa e IBF), Narrador integra la escena en prosa (sin ver los secretos no revelados de los PNJ -- asimetría de información deliberada), y Mundo/Árbitro extrae los deltas de estado y valida contra la lista blanca antes de escribir.")]),
      p("Ambos brazos de un mismo par comparten tenant, corpus de lore (turno 0), fixtures de mundo/personajes (world_*.json / personas_*.json) y personaje jugador -- la única variable que cambia dentro de un par es la arquitectura. Entre pares, en cambio, el tono/tema del escenario SÍ varía deliberadamente (ver punto 27 de la bitácora QM): usar un único tono para los 27 pares sesgaría la comparación hacia la arquitectura que maneje mejor ese tono específico."),

      h2("2.3 Pipeline de generación de un par"),
      bullet("crear_campana_real.py / crear_campana_real_g1.py -- crean la fila de campaña y siembran el turno 0 con el corpus de lore como texto narrativo puro."),
      bullet("sembrar_mundo_real.py -- puebla las tablas estructuradas (lugares, facciones, relojes, misiones, el PJ activo, los PNJ con IBF/disposición/conocimiento/secretos) a partir de los fixtures JSON del escenario."),
      bullet("vertical_slice.py / vertical_slice_g1.py -- generan turno a turno, escribiendo narración + deltas validados."),
      bullet("orquestador/reporte_validacion.py -- corre post-hoc sobre la campaña ya generada, sin costo de API adicional. Produce cinco secciones: (1) resumen de turn_validation (heurísticas CL-1/CL-2/QN-1/QN-2/CR-1/CR-2 por turno), (2) detector de bucles narrativos, (3) relojes disparados, (4) coherencia C y consistencia V de Papalampidi et al. (2022), (5) Jericho-QA State Graph Recall (Ammanabrolu et al., 2020)."),

      h1("3. Fallos de instrumentación encontrados y corregidos esta sesión"),
      p("Cada uno de estos fallos, de no corregirse, habría producido un reporte que PARECÍA válido -- corría sin errores, imprimía números con dos decimales de precisión -- pero que en realidad medía otra cosa distinta de lo que aparentaba medir. Se documentan en detalle en la bitácora QM (ver sección 6); aquí el resumen orientado a por qué cada uno importa para la validez de la comparación."),

      h2("3.1 Caché de bytecode enmascarando un fix real (punto 26)"),
      p("Un fix ya aplicado al código de detección de cruces de banda de afinidad (npc.affinity) no se reflejaba en las corridas del reporte -- Python seguía ejecutando el .pyc compilado ANTES del fix, silenciosamente. El síntoma engañaba: parecía que el fix no funcionaba, cuando en realidad nunca se estaba ejecutando. Confirmado y corregido al limpiar __pycache__; el recall de G1 pasó de contar 44 deltas evaluables (incorrecto, contaba cruces de banda inexistentes) a 2 (correcto)."),

      h2("3.2 Rutas rotas tras la reorganización del proyecto"),
      p("Al mover los scripts de la raíz a scripts/ para ordenar el repositorio, seis scripts quedaron con dos tipos de bug de ruta relativa (RAIZ = Path(__file__).resolve().parent, y por separado sys.path.insert(..., parent / \"orquestador\")) que apuntaban a rutas inexistentes. El primero se corrigió en la primera pasada; el segundo -- una línea aparte con el mismo patrón -- se pasó por alto hasta que crear_campana_real.py falló en vivo con ModuleNotFoundError. Los seis scripts (crear_campana_real.py, crear_campana_real_g1.py, sembrar_mundo_real.py, verificar_sesion1.py, limpiar_turnos_corruptos.py, exportar_transcripcion_md.py) ya están corregidos y verificados."),

      h2("3.3 Guard contra NPCs duplicados incompleto"),
      p("El código que evita que el extractor cree un NPC con el mismo nombre que un personaje jugador (documentado desde antes como \"bug de raíz\") solo comparaba contra los PJ, nunca contra los NPCs YA SEMBRADOS de la campaña. Si el extractor proponía \"crear NPC: <nombre de un NPC que ya existía>\", nada lo detenía. Esto produjo una entidad \"Hendrik Vall\" duplicada en el Par 02 (G1), que desplazó a \"Ysolda Marn\" del top-3 de protagonistas del reporte de coherencia (sección 4) -- un resultado que parecía válido (números con decimales, sin errores) pero que estaba midiendo una entidad fantasma en vez de la real. Corregido en ambos scripts generadores (vertical_slice.py y vertical_slice_g1.py)."),

      h2("3.4 Siembra doble accidental -- el hallazgo más serio"),
      p("sembrar_mundo_real.py se corrió dos veces por error humano sobre la misma campaña (Par 02 G1), sin ninguna protección de idempotencia. El caso más grave: el personaje jugador (Otto) recibió escritura real en AMBAS filas duplicadas durante los 250 turnos (23 y 12 state_deltas respectivamente) -- las búsquedas por nombre resolvían a una fila u otra de forma ambigua turno a turno, así que el estado real del personaje (HP, condiciones, inventario) quedó repartido entre dos filas sin que ninguna, por sí sola, tuviera el estado correcto."),
      p("Esto se diagnosticó con dos scripts de solo lectura antes de tocar nada, se reconstruyó el estado real fusionando ambas filas (aplicando la semántica correcta de cada campo: \"último valor gana\" para HP, unión para condiciones acumulativas, concatenación con deduplicación de pares exactos para inventario), se reapuntaron los 23 deltas de la fila sobrante a la fila conservada -- sin pérdida de historial -- y recién entonces se borró la fila duplicada. El resto de entidades duplicadas (3 NPCs, 2 misiones, 1 facción, 1 reloj, 6 lugares) no tenían uso real y se borraron directamente tras verificar que ningún state_delta les apuntaba. Se añadió además una guarda de idempotencia a sembrar_mundo_real.py: ahora aborta si la campaña ya tiene algún NPC sembrado."),

      h1("4. Estado actual del corpus"),
      table(
        [1600, 3200, 1800, 1800, 1600],
        ["Par", "Escenario / tono", "G2 (monolítico)", "G1 (multiagente)", "Estado"],
        [
          ["Par 01", "Vado de Ceniza -- mixto/aventura", "250 turnos", "250 turnos", "Cerrado y validado"],
          ["Par 02", "Vela Honda -- grimdark/gótico", "250 turnos", "250 turnos", "Cerrado y validado (tras corregir siembra doble)"],
          ["Par 03", "Rocabella -- ligero/cómico", "En generación", "En generación", "Corpus/fixtures listos, campañas sembradas"],
        ],
      ),
      p(""),
      p("Con ~$6.98 de crédito DeepInfra restante al momento de este informe y un costo medido de $0.35-0.65 por par completo (dos campañas de 250 turnos), el presupuesto alcanza para aproximadamente 10-20 pares adicionales -- el límite real no es el costo de generación sino el tiempo de validación manual entre pares, como demuestra el trabajo de esta sesión."),

      h1("5. Viabilidad de las métricas computacionales determinísticas"),
      p("Esta es la pregunta central que motiva este informe: ¿el instrumento, ya depurado, produce señal utilizable para responder los objetivos de la tesis? La respuesta es distinta métrica por métrica."),

      h2("5.1 Jericho-QA State Graph Recall (Ammanabrolu et al., 2020)"),
      pRich([bold("Nota de verificación bibliográfica: "), reg("esta cita se marcó de forma ERRÓNEA como fabricada en una primera pasada de verificación (2026-09-07), porque esa verificación solo revisó el abstract del paper y no lo encontró ahí. Al leer el texto COMPLETO se confirmó que sí es real y está correctamente atribuida -- el paper introduce textualmente el dataset \"Jericho-QA\" (\"We introduce the Jericho-QA dataset, for question-answering in text-game-like environments\") y define Exact Match/F1 exactamente como se usa aquí. Se corrige explícitamente porque la primera verificación quedó documentada en la bitácora QM y podía leerse como un veredicto final si no se revisa el hilo completo. Regla de método adoptada desde entonces: toda verificación de citas debe leer el cuerpo completo del paper, nunca solo el abstract, antes de descartar algo como fabricado -- el abstract puede omitir contenido que sí aparece en el cuerpo (detalle completo en la bitácora QM, entrada de la quinta pasada).")]),
      table(
        [2600, 1700, 1700, 3200],
        ["Par / brazo", "Deltas evaluables", "Recall", "Detalle"],
        [
          ["Par01 G1", "2", "0.000", "npc.affinity: Sargento Brea (2 cruces de banda, ninguno reflejado en texto)"],
          ["Par01 G2", "10", "0.000", "npc.affinity: 5 PNJ distintos, 10 cruces de banda, ninguno reflejado"],
          ["Par02 G1", "0", "-- (sin deltas evaluables)", "Ningún cruce de banda de afinidad/status con vocabulario distintivo detectable"],
          ["Par02 G2", "1", "0.000", "npc.affinity: Ysolda Marn, 1 cruce, no reflejado"],
        ],
      ),
      p(""),
      pRich([bold("Lectura crítica: "), reg("recall = 0.000 en absolutamente todos los casos evaluables, en ambos pares, en ambas arquitecturas. Esto NO diferencia a G1 de G2 -- es un resultado parejo y consistentemente nulo. Hay dos lecturas posibles, y el plan de cierre ya señala la segunda como pendiente sin resolver: (a) que ningún narrador (ni G1 ni G2) esté verbalizando los cruces de banda de disposición de forma textualmente detectable por el matcher léxico actual, lo cual sería un hallazgo real sobre AMBAS arquitecturas; o (b) que el propio detector (comparación léxica estricta contra la evidencia del turno donde ocurrió el cruce, dentro de una ventana de turnos) sea demasiado estricto y esté generando falsos negativos sistemáticos. El plan de cierre ya identificaba esto como brecha pendiente (\"spot-check manual de una muestra de los turnos marcados... antes de citar esa cifra\") y sigue sin resolverse -- con recall=0.000 en TODOS los deltas evaluados hasta ahora (13 en total entre los dos pares), un spot-check manual de una muestra representativa deja de ser opcional: es la única forma de saber si Jericho-QA, tal como está implementado, es un instrumento viable para esta tesis o si necesita una ventana de evidencia más amplia / un matcher menos literal antes de poder usarse como resultado citable.")]),

      h2("5.2 CR-2 -- densidad de grafo de entidades / nombres no reconocidos (Guinaudeau & Strube)"),
      table(
        [2600, 2700, 2900],
        ["Par / brazo", "Turnos con nombre no reconocido", "cr2_entidad_grafo_densidad (prom.)"],
        [
          ["Par01 G1", "228/250 (91.2%)", "0.224"],
          ["Par01 G2", "66/250 (26.4%)", "0.353"],
          ["Par02 G1", "245/250 (98.0%)", "0.256"],
          ["Par02 G2", "52/250 (20.8%)", "0.395"],
        ],
      ),
      p(""),
      pRich([bold("Lectura crítica: "), reg("la asimetría G1 >> G2 es consistente y estable en los dos pares (91-98% vs. 21-26%), lo que descarta que sea un accidente de un escenario en particular -- es una propiedad estructural del pipeline de G1 (validaciones de creación de entidades más estrictas: tope de una creación por turno, evidencia literal obligatoria) frente al de G2. Esto es exactamente el \"confound de vocabulario mecánico del Narrador\" que el plan de cierre ya documentaba como pendiente sin investigar. La implicación para la tesis es directa: CR-2, tal como está calculado hoy, mide en gran parte CUÁNTAS entidades registra cada pipeline, no necesariamente cuán bien cada arquitectura mantiene el grafo de entidades en la narración -- confundir ambas cosas produciría una conclusión metodológicamente débil (\"G2 es mejor en CR-2\" cuando en realidad \"G2 registra más entidades como conocidas\"). Se necesita, antes de citar esta métrica en la sección comparativa, decidir si se corrige el pipeline de registro de G1 para emparejar su generosidad con el de G2, o si se reporta la asimetría como un hallazgo de diseño de arquitectura en sí mismo (lo cual es defendible, pero debe decirse explícitamente, no dejarse implícito).")]),

      h2("5.3 Coherencia (C) y Consistencia de atributos (V) -- Papalampidi et al. (2022)"),
      table(
        [2600, 1700, 1700, 2200],
        ["Par / brazo", "C promedio", "V promedio", "Nota"],
        [
          ["Par01 G1", "1.5", "0.133", "Sargento Brea Ci=4.5 domina el promedio"],
          ["Par01 G2", "1.667", "0.145", "Ilvard Ci=4.0 domina el promedio"],
          ["Par02 G1", "0.0", "0.134", "Los 3 PNJ solo mencionados en la sección 0 (tras corregir el bug de duplicados)"],
          ["Par02 G2", "0.333", "0.088", "Otto Ci=1.0, el resto Ci=0.0"],
        ],
      ),
      p(""),
      pRich([bold("Lectura crítica: "), reg("esta métrica sí funciona de forma confiable -- SIEMPRE Y CUANDO la extracción de entidades esté libre de duplicados, que es justo lo que se rompió y se corrigió esta sesión (sección 3.3). El valor de C=0.0 en Par02 G1 es ahora un hallazgo genuino (los PNJ no vuelven a mencionarse tras la primera sección), no un artefacto. La limitación declarada que sigue vigente: solo se rastrean los top-3 protagonistas por conteo de menciones LITERALES del nombre completo, sin resolución de correferencia (pronombres, apodos) -- un PNJ mencionado consistentemente por apodo en vez de nombre completo aparecería como \"olvidado\" sin estarlo. Esta limitación aplica por igual a ambas arquitecturas, así que no sesga la comparación, pero sí acota la interpretación de cualquier C o V individual.")]),

      h2("5.4 Heurísticas CL-1/CL-2/QN-1/QN-2/CR-1 (turn_validation)"),
      p("Estable y de comportamiento similar entre los dos pares cerrados: cl1_campo_inmutable_alterado se mantiene en el rango 2.4%-7.2% en las cuatro campañas; qn2_pj_piensa_narrado, cl2_pnj_inactivo_actua y cl2_pc_hp_contradice_narracion en 0% consistentemente en ambos pares y ambas arquitecturas -- señal de que esas tres heurísticas específicas no están capturando ningún problema real detectable en el corpus actual, lo cual puede ser un resultado positivo genuino (el motor no comete esos errores) o una señal de que las heurísticas necesitan revisarse para saber si de verdad están evaluando lo que dicen evaluar. Ningún reloj de facción se ha disparado todavía en ninguna de las cuatro campañas generadas -- la validación de sección 3 (relojes disparados) sigue sin tener un solo caso real que evaluar."),

      h1("6. Por qué la brecha no se ha cerrado (síntesis directa)"),
      p("No es una brecha de generación -- el presupuesto y el tiempo de cómputo sobran. Es una brecha de VALIDEZ del instrumento: cuatro fallos de instrumentación distintos (caché de bytecode, rutas rotas, guard de duplicados incompleto, siembra doble sin idempotencia) habrían producido, cada uno por separado, un número que parecía correcto pero no lo era. Corregirlos uno por uno, verificando cada corrección contra datos reales antes de generar el siguiente par, es lo que ha consumido el tiempo entre Par 01 y Par 02. La alternativa -- generar los 27 pares primero y confiar en que el instrumento estaba bien -- habría sido más rápida pero habría arriesgado tener que invalidar y regenerar corpus completo si alguno de estos bugs se descubría después."),
      p("Adicionalmente, dos de las cinco métricas del reporte (Jericho-QA recall y CR-2) muestran patrones que, aunque ahora confiablemente medidos, todavía no tienen interpretación metodológica cerrada: recall=0.000 universal necesita un spot-check manual antes de poder citarse como hallazgo, y la asimetría G1/G2 en CR-2 necesita decidirse si es un confound de instrumentación o un hallazgo de arquitectura legítimo. Ambos puntos ya estaban señalados como pendientes en el plan de cierre antes de esta sesión; lo que esta sesión aporta es la primera evidencia con dos pares independientes de que el patrón es consistente y no un accidente de un solo escenario."),

      h1("7. Dónde encontrar la evidencia"),
      h2("7.1 Vault de Obsidian (bitácora técnica completa, en orden cronológico)"),
      bulletRich([bold("UPAO/TESIS/QUESTMASTERS/QM - Respaldo bibliografico instrumentos deterministicos.md"), reg(" -- puntos 26 a 29: bug de caché, cierre de Par 01, decisión de variar tono por par (con la aclaración de que Calradia es un proyecto personal sin relación con la tesis), y el detalle completo de los cuatro bugs de esta sección 3 (guard de duplicados, siembra doble, fusión de Otto, guarda de idempotencia).")]),
      bulletRich([bold("UPAO/TESIS/QUESTMASTERS/QM - Estructura del proyecto.md"), reg(" -- mapa completo de carpetas, scripts y funciones del repositorio (snapshot, puede haber quedado un poco atrás de los cambios más recientes).")]),

      h2("7.2 Proyecto TESIS en Claude (docs)"),
      bulletRich([bold("claude/plan-cierre-investigacion.md"), reg(" -- el plan de cierre vigente (Fases 0-3), con el checklist de brechas técnicas pendientes citado en la sección 6 de este informe.")]),

      h2("7.3 Código y datos (repositorio local, C:\\BMARIN2003\\DEV\\proyecto)"),
      bullet("orquestador/ -- db.py (capa de base de datos), vertical_slice.py / vertical_slice_g1.py (generadores G2/G1), reporte_validacion.py (las cinco secciones de métricas)."),
      bullet("scripts/ -- crear_campana_real*.py, sembrar_mundo_real.py, y los scripts de diagnóstico/limpieza usados esta sesión (diagnosticar_npc_duplicado.py, diagnosticar_siembra_doble.py, limpiar_siembra_doble.py, fusionar_personaje_duplicado.py) -- quedan en el repo por si un problema similar vuelve a aparecer."),
      bullet("migrations/001_schema.sql -- esquema completo, incluye mutable_fields (lista blanca de campos delta-ables) y la función apply_delta()."),
      bullet("corpus/ -- lore_vado_de_ceniza.md (Par01), lore_par02_vela_honda.md (Par02), lore_par03_cosecha_dorada.md (Par03)."),
      bullet("fixtures/ -- world.json/personas.json (Par01), world_par02.json/personas_par02.json (Par02), world_par03.json/personas_par03.json (Par03)."),
      bullet("Para reproducir cualquier número citado en este informe: python orquestador\\reporte_validacion.py --campaign <UUID> --hasta-turno 250, usando los UUID de campaña documentados en la bitácora (punto 24 para Par01, punto 29 para Par02)."),

      new Paragraph({ text: "", spacing: { before: 400 } }),
      p("Este informe se limita a lo que hay evidencia real en el corpus generado -- ninguna cifra aquí está proyectada ni extrapolada más allá de los datos citados en las tablas de la sección 5.", { italics: true }),
    ],
  }],
});

function italicRun(text) { return new TextRun({ text, italics: true }); }

Packer.toBuffer(doc).then(buf => {
  require("fs").writeFileSync("/mnt/user-data/outputs/Informe_brecha_instrumentacion_asesor.docx", buf);
  console.log("OK, escrito");
});
