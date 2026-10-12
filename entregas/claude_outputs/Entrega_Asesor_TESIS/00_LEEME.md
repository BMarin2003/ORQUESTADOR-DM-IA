# Entrega al asesor — Comparación de la Coherencia Narrativa en Campañas de D&D generadas por Sistemas Multiagente versus Sistemas Monolíticos

**Autores:** Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David
**Asesor:** Dr. Cueva Chavez, Walter Manuel
**Última actualización de esta carpeta:** 2026-09-28

## Actualizaciones desde la versión anterior de esta carpeta (2026-09-21)

Se cerró la brecha de validación humana del detector de personajes no jugadores inactivos
(`cl2_pnj_inactivo_actua`), identificada en la docimasia de H1e y ya incorporada al texto de la
tesis en el apartado 6.5.9 y la Tabla 11 (ver `01_Tesis/`).

- **Muestra:** 60 turnos extraídos por estrato según la salida del detector y de Jericho-QA;
  resultó en **59 casos únicos** — un ítem se presentó dos veces en la herramienta de etiquetado,
  detectado porque los tres evaluadores respondieron idéntico en ambas apariciones (no invalida
  ningún dato, ver nota en `03_Resultados_y_Analisis/Validacion_Humana_Brecha4_PNJ_Inactivo.md`).
- **Evaluadores:** tres voluntarios externos al equipo investigador (mismo principio de juez y
  parte que ya regía el resto del proyecto), etiquetado ciego e independiente.
- **Resultado:** acuerdo global bajo (κ de Fleiss = 0.138), sostenido casi enteramente por el par
  E1–E3 (79.7 %; κ = 0.595); el par E2 mostró señales claras de respuesta apresurada (mediana de
  12 s por caso frente a 60 y 38 s de E1/E3) y se excluyó del cálculo reportado. Frente al
  veredicto humano mayoritario (E1–E3), el detector refinado obtuvo precisión 62.5 % (IC95%
  38.6–81.5 %) y exhaustividad 40.0 % (IC95% 23.4–59.3 %), n=34.
- **Qué significa:** el detector es relativamente confiable cuando marca un error, pero se le
  escapa la mayoría de los errores reales — se mantiene como exploratorio y **H1e sigue sin
  instrumento confirmatorio**, misma conclusión que ya sostenían las tres brechas cerradas el
  21/09 (persona2, Jericho/relojes, Kaplan-Meier), ahora con una cuarta línea de evidencia
  independiente en la misma dirección.
- Documento nuevo: `03_Resultados_y_Analisis/Validacion_Humana_Brecha4_PNJ_Inactivo.md` (reporte
  completo, con las tres tablas de acuerdo entre evaluadores).
- `01_Tesis/Tesis_Coherencia_Narrativa_MAS_vs_Monolitico.docx` se regeneró a partir de la versión
  vigente del documento (incluye ya este cierre de brecha, la Tabla 11 y el Capítulo 6 completo
  con las tres docimasias H1d/H1e/H1f).

## Actualizaciones de la versión anterior (2026-09-21, misma fecha, mañana)

Se cerraron tres brechas metodológicas más, todas sobre coherencia longitudinal (H1e / OE-5, OE-6):

1. **Auditoría de precisión/recall del detector `persona2`** (primera pasada, asistida por IA — ver `03_Resultados_y_Analisis/Auditoria_Persona2_IA_Asistida.md`): precisión 25.6%, recall 67.9%. Es un borrador transparente pendiente de verificación humana, no un resultado definitivo — el documento explica por qué se hizo así.
2. **Prueba de sensibilidad A2 para Jericho recall y relojes reconocidos** (`03_Resultados_y_Analisis/Validacion_Sensibilidad_A2/Sensibilidad_Jericho_Relojes*.md`): el A2 mecánico da 100% en las cuatro perturbaciones, pero un diagnóstico adicional (comparación contra un baseline al azar) muestra que **relojes reconocidos no discrimina mejor que el azar** (88.3% real vs. 89.8% por azar) y que **Jericho recall solo discrimina en `npc.status`** (+21 a +25 puntos porcentuales sobre el azar), no en `npc.affinity` (que es el 55% de los eventos). Conclusión: Jericho queda "exploratorio", relojes queda "no usar" — con evidencia, no solo como nota de brecha pendiente.
3. **Curva de supervivencia (Kaplan-Meier) sobre la primera mención de un PNJ no vivo** (`03_Resultados_y_Analisis/Supervivencia_PNJ_No_Vivo/`): formaliza la incidencia cruda del Anexo B de `Cierre_de_Brechas_Metodologicas.md` en una curva con censura y una prueba de significancia (log-rank). G1 tarda más en promedio (mediana turno 1139 vs. 891 en G2), pero la diferencia no es estadísticamente significativa (p=0.77).

Las tres son resultados negativos/nulos reales, no vacíos metodológicos: refuerzan, con evidencia adicional e independiente, la misma conclusión ya documentada en `Registro_Decisiones_Docimasia_H1d-H1f.md` — H1e sigue sin instrumento confirmatorio. Ese documento y `Cierre_de_Brechas_Metodologicas.md` todavía no citan estos tres resultados nuevos en su propio texto (se generaron después); el contenido no cambia, pero conviene tenerlo presente al leerlos.

## Cómo usar esta carpeta

Está organizada en cuatro bloques, en el orden en que conviene revisarlos. Cada archivo tiene un nombre descriptivo en español; no hace falta abrir el repositorio de desarrollo para entender el proyecto.

### 01_Tesis

El documento principal de tesis, en Word (`.docx`), listo para revisión o impresión. Incluye tabla de contenidos y numeración automática de secciones. Contiene el marco teórico, la metodología (incluyendo el pivote metodológico documentado más abajo) y la presentación completa de resultados (Capítulo 6, objetivos OE-1 a OE-6).

> **Nota de alcance de esta entrega (actualizada 2026-09-28).** El Capítulo 4 (hipótesis H1a-H1c) y las Tablas 1-2 ya usan el método determinista vigente (Page, Wilcoxon), no el diseño original de panel Likert — esa parte de la nota anterior ya no aplica. Lo que sí queda pendiente: el **Resumen** y el **Abstract** todavía describen el diseño original ("panel de cinco Dungeon Masters expertos... escala Likert de 1 a 7", en futuro — "se generarán veintisiete pares"), mientras que el cuerpo de la tesis documenta el pivote metodológico del 14 de setiembre de 2026 hacia instrumentos deterministas. Es una inconsistencia real que conviene resolver antes de la sustentación; no se editó en esta entrega por no ser parte del cierre de brecha 4.

### 02_Instrumentos_de_Evaluacion

- **Rúbrica de Calidad Narrativa D&D-IA (v2.0):** el instrumento original de la tesis (panel de 5 evaluadores expertos, escala Likert de 7 puntos). Se conserva como marco teórico de origen de los seis indicadores (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2) y como evidencia piloto/histórica (Anexo 2), no como método de medición vigente.
- **Especificaciones de los instrumentos deterministas nuevos** que reemplazan al panel humano como método vigente: validación de sensibilidad A2 (cómo se comprueba que un instrumento mide lo que dice medir), legibilidad Szigriszt-Pazos, y diversidad léxica MTLD/MATTR.
- **Matriz de cobertura:** qué instrumento determinista mide cada indicador original de la rúbrica.

### 03_Resultados_y_Analisis

El paquete de resultados completo sobre las 27 parejas del corpus (54 campañas, 75,600 turnos):

- `Resultados_Tesis_OE1-OE6.md` — el reporte fuente con todas las tablas estadísticas (descriptivas y comparativas) usadas en el Capítulo 6 de la tesis. Ya incluye la clasificación final de Jericho recall ("Exploratorio") y relojes ("Descriptivo / no usar").
- `Datos_Por_Pareja_Ancho.csv` / `Datos_Por_Campana_Largo.csv` — los datos crudos agregados, en formato tabular, por si el asesor quiere verificar o reprocesar algún cálculo.
- `Consolidado_Validacion_v2.md/csv` — estado de avance y consolidación de todo el bloque de validación.
- `Auditoria_Persona2_Equivalencia.md` — reporte de equivalencia del instrumento que sostiene H1f.
- `Auditoria_Persona2_IA_Asistida.md` + `Etiquetas_Persona2_E1_IA-Asistido.csv` — **nuevo.** Primera pasada de precisión/recall del detector `persona2` sobre los 515 ítems de la muestra E1, hecha por IA de forma transparente (ver el propio documento para el porqué), pendiente de verificación humana con la muestra E2.
- `Supervivencia_PNJ_No_Vivo/` — **nuevo.** Curva de Kaplan-Meier y prueba log-rank sobre la primera mención narrada de un PNJ no vivo (G1 vs. G2), con el script que la genera.
- `Validacion_Humana_Brecha4_PNJ_Inactivo.md` — **nuevo.** Auditoría de precisión/recall del detector `cl2_pnj_inactivo_actua` contra el veredicto de tres evaluadores externos ciegos: acuerdo entre evaluadores (Fleiss, Cohen, AC1) y precisión/recall del detector frente al consenso humano. Ya incorporada al texto de la tesis (apartado 6.5.9, Tabla 11).
- `Registro_Decisiones_Docimasia_H1d-H1f.md` — **documento clave para la sustentación**: explica el razonamiento detrás de cada una de las tres decisiones de contraste de hipótesis (por qué H1d no se sostiene pese a rechazar H0d, por qué H1e queda sin decisión confirmatoria, por qué H1f se acepta mas queda condicionada), con las cifras exactas de cada instrumento.
- `Cierre_de_Brechas_Metodologicas.md` y `Plan_de_Validacion_Instrumentos.md` — evidencia de que el cierre de brechas metodológicas identificadas durante el desarrollo fue planificado y ejecutado, no improvisado.
- `Informe_Brecha_Instrumentacion_Asesor.docx` — informe previo ya preparado sobre brechas de instrumentación, elaborado durante el desarrollo del proyecto.
- `Validacion_Sensibilidad_A2/` — los reportes completos de la prueba de sensibilidad por perturbación (línea base, extensión A4BC, extensión Szigriszt-Pazos/MTLD/MATTR, y **nuevo:** Jericho recall/relojes, con su diagnóstico adicional) que determinan qué instrumentos son confirmatorios.

### 04_Evidencia_y_Trazabilidad

Evidencia de que el proceso se ejecutó tal como se describe, no solo los resultados finales:

- `Bitacora_Ejecucion_Par07-17.md` — bitácora de trabajo del tramo de generación de campañas Par07 a Par17.
- `Integridad_Transcripciones_*.txt` — reportes de verificación de integridad de las transcripciones generadas.
- `Logs_Ejecucion_Pipeline/` — logs reales del supervisor del pipeline de generación (par01-17 y par18-27).
- `Reportes_Instrumentos_Por_Campana_Par07-27.zip` — el reporte de instrumentos deterministas ejecutado individualmente sobre cada una de las 21 parejas Par07-Par27 (42 archivos, ambos brazos G1/G2 de cada pareja), como evidencia granular campaña por campaña.
- `Transcripcion_Muestra_Par02/` — la transcripción completa de una pareja real (ambos brazos), como muestra representativa del tipo de contenido narrativo generado y evaluado. Ver la nota dentro de esa carpeta sobre por qué no se incluyen las 27 parejas completas (tamaño) y dónde consultar el resto.

## Resumen de una línea del hallazgo principal

La evidencia no respalda una superioridad general y uniforme del sistema multiagente (G1) sobre el monolítico (G2): hay una ventaja específica y bien fundamentada en agencia del jugador (H1f, condicionada a la auditoría de `persona2`, todavía pendiente de verificación humana externa), ninguna decisión confirmatoria en coherencia longitudinal (H1e, ahora con cuatro líneas de evidencia independientes que lo confirman: persona2 IA-asistido, Jericho/relojes, Kaplan-Meier y la validación humana de `cl2_pnj_inactivo_actua`), y evidencia confirmatoria que de hecho favorece a G2 en el único indicador normalizado de coherencia reactiva (H1d). El detalle completo está en `03_Resultados_y_Analisis/Registro_Decisiones_Docimasia_H1d-H1f.md`.
