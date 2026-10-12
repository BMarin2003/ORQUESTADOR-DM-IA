    # Entrega al asesor — Comparación de la Coherencia Narrativa en Campañas de D&D generadas por Sistemas Multiagente versus Sistemas Monolíticos

**Autores:** Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David
**Asesor:** Dr. Cueva Chavez, Walter Manuel
**Última actualización de esta carpeta:** 2026-09-21

## Cómo usar esta carpeta

Está organizada en cuatro bloques, en el orden en que conviene revisarlos. Cada archivo tiene un nombre descriptivo en español; no hace falta abrir el repositorio de desarrollo para entender el proyecto.

### 01_Tesis

El documento principal de tesis, en Word (`.docx`), listo para revisión o impresión. Incluye tabla de contenidos y numeración automática de secciones. Contiene el marco teórico, la metodología (incluyendo el pivote metodológico documentado más abajo) y la presentación completa de resultados (Capítulo 6, objetivos OE-1 a OE-6).

> **Nota de alcance de esta entrega.** El Capítulo 4 (hipótesis específicas H1a-H1c) y las Tablas 1-2 (operacionalización de variables) todavía usan el lenguaje del diseño original (panel de evaluadores, escala Likert). Su actualización al método determinista vigente está programada para la siguiente sesión de trabajo — se avisa aquí para que no se lea como una inconsistencia sin explicación.

### 02_Instrumentos_de_Evaluacion

- **Rúbrica de Calidad Narrativa D&D-IA (v2.0):** el instrumento original de la tesis (panel de 5 evaluadores expertos, escala Likert de 7 puntos). Se conserva como marco teórico de origen de los seis indicadores (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2) y como evidencia piloto/histórica (Anexo 2), no como método de medición vigente.
- **Especificaciones de los instrumentos deterministas nuevos** que reemplazan al panel humano como método vigente: validación de sensibilidad A2 (cómo se comprueba que un instrumento mide lo que dice medir), legibilidad Szigriszt-Pazos, y diversidad léxica MTLD/MATTR.
- **Matriz de cobertura:** qué instrumento determinista mide cada indicador original de la rúbrica.

### 03_Resultados_y_Analisis

El paquete de resultados completo sobre las 27 parejas del corpus (54 campañas, 75,600 turnos):

- `Resultados_Tesis_OE1-OE6.md` — el reporte fuente con todas las tablas estadísticas (descriptivas y comparativas) usadas en el Capítulo 6 de la tesis.
- `Datos_Por_Pareja_Ancho.csv` / `Datos_Por_Campana_Largo.csv` — los datos crudos agregados, en formato tabular, por si el asesor quiere verificar o reprocesar algún cálculo.
- `Consolidado_Validacion_v2.md/csv` — estado de avance y consolidación de todo el bloque de validación.
- `Auditoria_Persona2_Equivalencia.md` — reporte de equivalencia del instrumento que sostiene H1f.
- `Registro_Decisiones_Docimasia_H1d-H1f.md` — **documento clave para la sustentación**: explica el razonamiento detrás de cada una de las tres decisiones de contraste de hipótesis (por qué H1d no se sostiene pese a rechazar H0d, por qué H1e queda sin decisión confirmatoria, por qué H1f se acepta mas queda condicionada), con las cifras exactas de cada instrumento.
- `Cierre_de_Brechas_Metodologicas.md` y `Plan_de_Validacion_Instrumentos.md` — evidencia de que el cierre de brechas metodológicas identificadas durante el desarrollo fue planificado y ejecutado, no improvisado.
- `Informe_Brecha_Instrumentacion_Asesor.docx` — informe previo ya preparado sobre brechas de instrumentación, elaborado durante el desarrollo del proyecto.
- `Validacion_Sensibilidad_A2/` — los tres reportes completos de la prueba de sensibilidad por perturbación (línea base, extensión A4BC, extensión Szigriszt-Pazos/MTLD/MATTR) que determinan qué instrumentos son confirmatorios.

### 04_Evidencia_y_Trazabilidad

Evidencia de que el proceso se ejecutó tal como se describe, no solo los resultados finales:

- `Bitacora_Ejecucion_Par07-17.md` — bitácora de trabajo del tramo de generación de campañas Par07 a Par17.
- `Integridad_Transcripciones_*.txt` — reportes de verificación de integridad de las transcripciones generadas.
- `Logs_Ejecucion_Pipeline/` — logs reales del supervisor del pipeline de generación (par01-17 y par18-27).
- `Reportes_Instrumentos_Por_Campana_Par07-27.zip` — el reporte de instrumentos deterministas ejecutado individualmente sobre cada una de las 21 parejas Par07-Par27 (42 archivos, ambos brazos G1/G2 de cada pareja), como evidencia granular campaña por campaña.
- `Transcripcion_Muestra_Par02/` — la transcripción completa de una pareja real (ambos brazos), como muestra representativa del tipo de contenido narrativo generado y evaluado. Ver la nota dentro de esa carpeta sobre por qué no se incluyen las 27 parejas completas (tamaño) y dónde consultar el resto.

## Resumen de una línea del hallazgo principal

La evidencia no respalda una superioridad general y uniforme del sistema multiagente (G1) sobre el monolítico (G2): hay una ventaja específica y bien fundamentada en agencia del jugador (H1f, condicionada a una auditoría pendiente), ninguna decisión confirmatoria en coherencia longitudinal (H1e), y evidencia confirmatoria que de hecho favorece a G2 en el único indicador normalizado de coherencia reactiva (H1d). El detalle completo está en `03_Resultados_y_Analisis/Registro_Decisiones_Docimasia_H1d-H1f.md`.
