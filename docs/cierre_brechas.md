# Cierre de brechas de investigación con resultados deterministas (BORRADOR)

> **Borrador, no usar todavía.** Las 28 brechas (7 objetivos × 4) salen de un análisis previo hecho con otros resultados y con siete objetivos; la tesis tiene seis. Las brechas se rehacen después de plasmar los resultados y hacer la docimasia. Las tres listas y los anexos siguen siendo válidos como datos; la matriz de brechas y su porcentaje no.

Muestra: 27 parejas (Par01-27), 54 campañas, 75 600 turnos (1 400 por campaña); mismo modelo y mismo agente jugador en ambos brazos; medición 100 % determinista sobre texto normalizado, sin evaluadores humanos. Todas las cifras salen de `docs/reportes/consolidado_v2.csv` y `datos/datos_v2/cierre/` (`experimento/scripts/reporte_v2/`); son **descriptivas** y **posteriores (post hoc)** en lo que corrige instrumentos.

**Alcance.** Los instrumentos deterministas miden proxies de las dimensiones de la rúbrica (diversidad léxica, anclaje léxico, menciones, cumplimiento de la regla de oro del prompt). No miden interés, creatividad ni voz del personaje, y varios detectores tienen la precisión sin auditar (se indica en cada fila). Una diferencia entre brazos **no implica superioridad**. Los resultados del panel humano sobre 3 campañas G2 (orquestador anterior) no se mezclan con estos: escala y método distintos.

## 1. Estado de las brechas por objetivo

Regla: **cerrada** = la pregunta de la brecha se contesta directamente con datos; **parcial** = evidencia por proxy o detector sin auditar; **límite** = sin instrumento determinista (se declara); **pendiente** = redacción. **Cobertura de brechas** = (cerradas + 0,5 × parciales) / 4. No es comparable con el «cumplimiento» previo: aquel era una estimación del avance de cada objetivo con base en el panel humano sobre 3 campañas G2 y en los datos pendientes; esta mide cuántas brechas de la literatura tienen respuesta con datos deterministas.

| Objetivo | Cerradas | Parciales | Límite | Pendiente | Cobertura de brechas (regla) | Cumplimiento previo (otra base) |
|---|---|---|---|---|---|---|
| **OE-1** Revisión sistemática de la literatura sobre arquitecturas de IA para narrativa interactiva | 0 | 1 | 0 | 3 | — (es redacción; ver nota) | 40 % |
| **OE-2** Coherencia reactiva del sistema monolítico (G2) | 0 | 4 | 0 | 0 | 50 % | 60 % |
| **OE-3** Coherencia longitudinal del sistema monolítico (G2) | 0 | 2 | 2 | 0 | 25 % | 60 % |
| **OE-4** Calidad narrativa emergente del sistema monolítico (G2) | 0 | 3 | 1 | 0 | 38 % | 60 % |
| **OE-5** Comparación de la coherencia reactiva entre arquitecturas (G1 vs G2) | 3 | 1 | 0 | 0 | 88 % | 15 % |
| **OE-6** Comparación de la coherencia longitudinal entre arquitecturas | 0 | 2 | 2 | 0 | 25 % | 15 % |
| **OE-7** Comparación de la calidad narrativa emergente entre arquitecturas | 0 | 2 | 2 | 0 | 25 % | 15 % |

Nota OE-1: la SLR es un producto de redacción; los resultados deterministas no la sustituyen y su avance sigue siendo el de la estimación previa hasta que se redacte. OE-2 a OE-4 caracterizan a G2 (nivel absoluto en cada lista); OE-5 a OE-7 comparan G1 con G2 (diferencia por pareja).

## 2. Las tres listas de resultados deterministas

**Cómo leer.** Cada valor es la media de la campaña (turnos 2-1 400; `persona2` solo sobre turnos que no se usaron para construir el detector); la unidad de análisis es la pareja. HL = Hodges-Lehmann de G1 − G2 entre parejas; r = correlación rank-biserial pareada (+1 = G1 mayor en todas las parejas); p Holm = Wilcoxon exacto corregido sobre toda la tabla del consolidado. ↕: ↓ menos es mejor, ↑ más es mejor, · neutro. Detalle con IC, lotes y estado de cada instrumento en `docs/reportes/consolidado_v2.md`.

### Lista 1. Coherencia reactiva (CR-1, CR-2)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) | r | p Holm | Parejas | Estado |
|---|---|---|---|---|---|---|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool, 1 de cada 10 turnos) | ↑ | 0.9993 | 0.9992 | +0.0001 | +0.28 | 1 | 27 | techo cercano a 1: discrimina poco |
| CR-1 | cr1: pifia narrada como éxito (% de turnos) | ↓ | 0.10 % | 0.09 % | +0.00 pp | +0.18 | 1 | 27 | baja precisión: ignora la negación («no logras») |
| CR-2 | CR-2a: respuesta a la acción específica (z) | ↑ | 2.69 | 2.82 | -0.13 | -0.47 | 0.5 | 27 | instrumento nuevo, matriz a4bc-2 |
| CR-2 | CR-2a: solapamiento con la acción (crudo) | ↑ | 0.136 | 0.125 | +0.011 | +0.84 | 0.00085 | 27 | instrumento nuevo, matriz a4bc-2 |
| CR-2 | CR-2b: anclaje al escenario (coseno, ventana de 8) | ↑ | 0.134 | 0.076 | +0.059 | +0.83 | 0.0011 | 27 | no distingue deriva de evolución legítima del mundo |
| CR-2 | CR-2b: anclaje sin nombres propios (ventana de 8) | ↑ | 0.075 | 0.062 | +0.013 | +0.62 | 0.071 | 27 | casi plano: la señal la sostienen los nombres |
| CR-2 | Densidad del grafo de entidades | · | 0.241 | 0.279 | -0.032 | -0.51 | 0.32 | 27 | insensible a otro escenario (P8) |
| CR-2 | Turnos con algún nombre no reconocido | ↓ | 8.52 % | 6.75 % | -0.79 pp | -0.07 | 1 | 27 | v1 saturado en G1 por la línea mecánica ⚠ signo distinto entre lotes |
| CR-2 | N.º de nombres no reconocidos por turno | ↓ | 0.141 | 0.114 | -0.027 | -0.18 | 1 | 27 | no detecta nombres inventados por sí solo ⚠ signo distinto entre lotes |
| CR-1 | Turnos con caracteres de otro alfabeto o U+FFFD (%) | ↓ | 0.09 % | 0.10 % | -0.04 pp | -0.15 | 1 | 27 | medida simple; detecta fallos de codificación e idioma |

### Lista 2. Coherencia longitudinal (CL-1, CL-2)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) | r | p Holm | Parejas | Estado |
|---|---|---|---|---|---|---|---|---|---|
| CL-1 | Papalampidi C: coherencia de entidad | ↑ | 2.13 | 1.60 | +0.58 | +0.54 | 0.31 | 27 | proxy de consistencia de personajes |
| CL-1 | Papalampidi V: consistencia de atributos | ↑ | 0.081 | 0.067 | +0.016 | +0.38 | 1 | 27 | proxy; no mide voz ni motivaciones |
| CL-1 | Entity Coreference Rate | ↑ | 0.997 | 0.998 | -0.001 | -0.74 | 0.0084 | 27 | saturado (≈ 1) |
| CL-2 | Jericho: recall de cambios de estado narrados | ↑ | 0.22 | 0.24 | -0.03 | -0.11 | 1 | 26 | heurística léxica; solo recall; sin prueba A2 ⚠ signo distinto entre lotes |
| CL-2 | Relojes: fracción reconocida en la narración | ↑ | 0.97 | 0.80 | +0.17 | +1.00 | 1 | 10 | proxy de solapamiento léxico; sin prueba A2 |
| CL-2 | PNJ inactivo mencionado (% de turnos) | ↓ | 7.80 % | 2.29 % | +4.66 pp | +0.50 | 0.5 | 27 | mide mención, no acción; precisión sin auditar |
| CL-2 | PNJ inactivo como sujeto (por 1 000 turnos) | ↓ | 7.35 | 4.23 | +0.00 | -0.43 | 1 | 27 | solo ve nombres de una palabra |
| CL-2 | Jaccard con la escena anterior | · | 0.192 | 0.172 | +0.019 | +1.00 | 5.4e-07 | 27 | continuidad léxica, no de eventos |
| CL-2 | Bucles: ciclos de ubicaciones | ↓ | 1.00 | 1.00 | +0.00 | +0.00 | 1 | 27 | A2: no reacciona a permutar turnos |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1 401 = nunca) | ↑ | 949 | 865 | +58 | +0.14 | 1 | 27 | mide mención, no acción; censurado en 1 401 |

### Lista 3. Calidad narrativa emergente (QN-1, QN-2)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) | r | p Holm | Parejas | Estado |
|---|---|---|---|---|---|---|---|---|---|
| QN-1 | TTR (diversidad léxica) | ↑ | 0.679 | 0.723 | -0.045 | -1.00 | 5.4e-07 | 27 | mide diversidad, no interés ni creatividad |
| QN-1 | Repetición de bigramas | ↓ | 0.029 | 0.018 | +0.011 | +1.00 | 5.4e-07 | 27 | mide repetición, no creatividad |
| QN-1 | Legibilidad Fernández-Huerta | · | 60.3 | 61.9 | -1.8 | -0.60 | 0.1 | 27 | complejidad, no calidad |
| QN-1 | Densidad del grafo por lema | · | 0.032 | 0.022 | +0.009 | +0.74 | 0.0087 | 27 | insensible a otro escenario (P8) |
| QN-2 | Usurpación mental o verbal del PJ (% de turnos) | ↓ | 0.24 % | 4.27 % | -3.66 pp | -1.00 | 5.4e-07 | 27 | v2b congelado, léxico cerrado; precisión sin auditar (C2-C4) |
| QN-2 |   · decisión | ↓ | 0.01 % | 0.17 % | -0.16 pp | -1.00 | 5e-05 | 27 | ídem |
| QN-2 |   · pensamiento | ↓ | 0.15 % | 3.24 % | -2.63 pp | -1.00 | 5.4e-07 | 27 | ídem |
| QN-2 |   · emoción | ↓ | 0.02 % | 0.28 % | -0.23 pp | -1.00 | 1.8e-06 | 27 | ídem |
| QN-2 |   · habla | ↓ | 0.05 % | 0.67 % | -0.42 pp | -0.98 | 6e-06 | 27 | ídem |
| QN-2 | Acción física no declarada (experimental, % de turnos) | ↓ | 3.05 % | 7.21 % | -6.27 pp | -0.86 | 0.00047 | 27 | experimental; equivalencia 70 % (A2) |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | ↓ | 3.29 % | 0.31 % | +1.96 pp | +0.95 | 1.3e-05 | 27 | medida simple, sin prueba A2; límite inferior de las fórmulas evasivas |
| QN-1 | Estabilidad de estilo: variación del TTR entre bloques | ↓ | 0.0038 | 0.0038 | -0.0001 | -0.06 | 1 | 27 | medida simple, sin prueba A2 ⚠ signo distinto entre lotes |
| QN-1 | Estabilidad de estilo: variación de Fernández-Huerta entre bloques | ↓ | 1.26 | 1.65 | -0.36 | -0.40 | 0.97 | 27 | medida simple, sin prueba A2 |
| QN-1 | PNJ registrados hasta el turno 1 400 | · | 4.0 | 8.9 | -4.0 | -0.97 | 2.3e-05 | 27 | proxy de emergencia; G1 tiene un agente extra que también crea entidades |
| QN-1 | Misiones registradas hasta el turno 1 400 | · | 2.0 | 2.0 | +0.0 | -1.00 | 1 | 27 | casi constante (2 por campaña, sembradas): el r no es informativo |

## 3. Matriz de cierre de brechas

### OE-1. Revisión sistemática de la literatura sobre arquitecturas de IA para narrativa interactiva

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Sin taxonomías estandarizadas para arquitecturas de IA en narrativa de final abierto | No es medible con datos: es un producto de redacción (SLR con protocolo PRISMA). Insumo disponible: `docs/papers_revistas_q1-q3.md`. | **PENDIENTE** | Redactar la SLR: ecuaciones de búsqueda, criterios de inclusión y exclusión, flujo de selección. |
| 2 | Sin revisiones comparativas de mecanismos de memoria en narrativas largas | Ídem. Los datos propios aportan evidencia empírica sobre memoria (Lista 2) pero no sustituyen la revisión. | **PENDIENTE** | Ídem. |
| 3 | Sin protocolos de benchmarking estandarizados para narrativas co-creadas | Ídem. Aporte propio: matriz de cobertura rúbrica ↔ instrumentos y validación por sensibilidad (`docs/matriz_cobertura_rubrica_instrumentos.md`, `docs/reportes/sensibilidad_baseline.md`). | **PENDIENTE** | Redactar el vínculo entre el benchmark propuesto y la literatura. |
| 4 | Sin análisis de costos y latencias entre generación monolítica y orquestación multiagente | Tiempo por turno (mediana por campaña, proxy): G1 29.9 vs G2 14.0 (HL G1−G2 +16.1; r +1.00; p Holm 5.4e-07; 27 parejas). Costo total registrado del lote Par18-27: 37.05 USD (20 campañas); **el costo por brazo no se registró** (la base no guarda tokens). | **PARCIAL** | Costo por brazo desde el panel del proveedor si está disponible; si no, declararlo como límite. |

### OE-2. Coherencia reactiva del sistema monolítico (G2)

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Arraigo contextual frágil ante entradas caóticas o fuera de distribución | Respuesta a la acción (CR-2a, z): G2 2.82; cae 2.3-2.9 unidades al sustituir la respuesta por la de otro turno (matriz a4bc-2, 25 de 26 celdas direccionales aprobadas). Anclaje al escenario (CR-2b, coseno de ventana): G2 0.076, con deriva a lo largo de la campaña (Anexo A). | **PARCIAL** | No se clasificó la entrada del jugador por grado de caos; solo se mide el arraigo en general. |
| 2 | Recurrencia de placeholders y frases evasivas | Turnos con una frase idéntica repetida ≥ 3 veces: G2 0.31 % (medida simple, límite inferior; no ve paráfrasis). Frases más repetidas: Anexo C. | **PARCIAL** | Sin detector de paráfrasis evasivas. |
| 3 | Degradación semántica por sobrecarga de contexto (fragmentos en otros idiomas, fallos de codificación) | Turnos con caracteres de otro alfabeto o U+FFFD: G2 0.10 % de los turnos; tendencia por profundidad en el Anexo A. | **PARCIAL** | Se mide incidencia y tendencia; la causa (sobrecarga de contexto) no se aísla. |
| 4 | Faltan métricas que separen la corrección pragmática de la mecánica-reglamentaria | Tres instrumentos separados: gramaticalidad (lingüística) G2 0.9992 (techo, discrimina poco); pifia narrada como éxito, `cr1` (reglas) G2 0.09 % (baja precisión: ignora la negación); respuesta a la acción, CR-2a (pragmática). | **PARCIAL** | La plausibilidad lógica sigue sin instrumento. |

### OE-3. Coherencia longitudinal del sistema monolítico (G2)

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Colisión de identidades en entidades nombradas | **Sin instrumento determinista.** Proxies parciales: consistencia de atributos (Papalampidi V) G2 0.067 y coherencia de entidad (C) G2 1.60. Evidencia cualitativa previa (panel humano, 3 campañas G2, orquestador anterior; no determinista): reasignación del nombre «Kaelen» a siete personajes. | **LÍMITE** | Declarar el límite (Sección de límites); una auditoría humana posterior puede cuantificarlo. |
| 2 | Degradación del linaje causal (olvido de eventos, restauración de estados ya modificados) | Cambios de estado registrados que la narración refleja (Jericho, recall): G2 0.24. PNJ no vivo mencionado (% de turnos): G2 2.29 %; como sujeto: 4.23 por 1 000 turnos. Ambos detectores miden mención, no acción, y su precisión no está auditada. | **PARCIAL** | Auditar la precisión de `cl2_pnj_inactivo_actua` (fase posterior). |
| 3 | Inestabilidad de la alineación de facciones y relaciones morales | Sin instrumento que mida cambios de bando. El recall de Jericho incluye las familias `npc.affinity` y `npc.status`, pero no se separó por familia ni mide alternancia. | **LÍMITE** | Declarar el límite o medir la alternancia de afinidad en `state_deltas`. |
| 4 | Las bases vectoriales planas no representan la mutación de grafos de estado | Evidencia indirecta: fracción de relojes de facción disparados que la narración reconoce (proxy léxico): G2 0.80; recall de Jericho G2 0.24. Limitación conocida: Par01-17 sin avance de reloj. | **PARCIAL** | Sin prueba de sensibilidad para Jericho ni relojes. |

### OE-4. Calidad narrativa emergente del sistema monolítico (G2)

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Monotonía estilística y aplanamiento expresivo | Diversidad léxica (TTR) G2 0.723; repetición de bigramas 0.018; frases idénticas repetidas 0.31 %; tendencia por profundidad en el Anexo A. Miden diversidad y repetición, no expresividad. | **PARCIAL** | Sin instrumento de interés ni creatividad. |
| 2 | Tensión entre reactividad local y arcos dramáticos globales | Reactividad local (CR-2a, z) estable a lo largo de la campaña, mientras el anclaje al escenario (CR-2b) cae (Anexo A): G2 0.076. Fracción de relojes reconocidos (eventos de arco): G2 0.80. | **PARCIAL** | El coseno no distingue deriva de evolución legítima del mundo. |
| 3 | Varianza y subjetividad de la evaluación estética entre jueces | El enfoque determinista elimina la varianza entre jueces, pero **no mide interés**: es una limitación del método, no un dato. | **LÍMITE** | Auditoría humana posterior si el asesor la aprueba. |
| 4 | Degradación de la ilusión de agencia con el tiempo | Usurpación mental o verbal del PJ, G2 4.27 % de los turnos; por profundidad, Anexo A. Las consecuencias visibles de las decisiones no tienen instrumento. | **PARCIAL** | Precisión de `persona2` sin auditar (fase posterior). |

### OE-5. Comparación de la coherencia reactiva entre arquitecturas (G1 vs G2)

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Faltan experimentos controlados que aíslen la arquitectura como única variable | Diseño de 27 parejas con el mismo modelo (google/gemma-4-31B-it), el mismo lore, el mismo personaje y el mismo agente jugador en ambos brazos (`docs/descomposicion_prompts.md`, auditoría de paridad G1/G2). El formato de salida de G1 se normalizó y se cuantificó su efecto (`docs/reportes/reporte_v2_formato_normalizado.md`). Par01-17 y Par18-27 usan versiones distintas del motor y se analizan por lote. | **CERRADA** | — |
| 2 | Se ignora el efecto de la latencia de la negociación entre agentes sobre la fluidez | Tiempo por turno: G1 29.9 vs G2 14.0 (HL G1−G2 +16.1; r +1.00; p Holm 5.4e-07; 27 parejas). Fluidez (gramaticalidad, techo): G1 0.9993 vs G2 0.9992 (HL G1−G2 +0.0001; r +0.28; p Holm 1; 27 parejas). Caracteres de otro alfabeto: G1 0.09 % vs G2 0.10 % (HL G1−G2 -0.04 pp; r -0.15; p Holm 1; 27 parejas). La latencia es un proxy de tiempo de pared con corridas concurrentes. | **CERRADA** | — |
| 3 | Sin evidencia de que un agente supervisor elimine los placeholders | Frases idénticas repetidas: G1 3.29 % vs G2 0.31 % (HL G1−G2 +1.96 pp; r +0.95; p Holm 1.3e-05; 27 parejas); G1 repite más, no menos (Anexo C: «La paciencia de … se ha agotado», hasta 95 veces en una campaña). Respuesta a la acción: G1 2.69 vs G2 2.82 (HL G1−G2 -0.13; r -0.47; p Holm 0.5; 27 parejas); anclaje: G1 0.134 vs G2 0.076 (HL G1−G2 +0.059; r +0.83; p Holm 0.0011; 27 parejas). No hay ablación del supervisor: la comparación es entre sistemas completos. | **PARCIAL** | Ablación del supervisor (fuera del alcance) o declarar. |
| 4 | Sin estudios inferenciales no paramétricos sobre pares de transcripciones | Wilcoxon exacto sobre las diferencias por pareja, Hodges-Lehmann con IC bootstrap sobre parejas, correlación rank-biserial pareada y corrección de Holm (`experimento/scripts/reporte_v2/consolidar.py`). El doble ciego humano no aplica a la medición determinista. | **CERRADA** | — |

### OE-6. Comparación de la coherencia longitudinal entre arquitecturas

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Sin evidencia de que grafos relacionales e identificadores inmutables mitiguen la colisión de identidades | Sin instrumento de colisión (ver OE-3). Proxies: C G1 2.13 vs G2 1.60 (HL G1−G2 +0.58; r +0.54; p Holm 0.31; 27 parejas); V G1 0.081 vs G2 0.067 (HL G1−G2 +0.016; r +0.38; p Holm 1; 27 parejas); PNJ no vivo mencionado G1 7.80 % vs G2 2.29 % (HL G1−G2 +4.66 pp; r +0.50; p Holm 0.5; 27 parejas). | **LÍMITE** | Declarar el límite; auditoría posterior. |
| 2 | No se mide la acumulación de entropía fáctica con la profundidad de la campaña | Deriva por bloques de 200 turnos en ambos brazos (Anexo A): PNJ no vivo mencionado, nombres no reconocidos, anclaje al escenario, repetición. Nombres no reconocidos por turno: G1 8.52 % vs G2 6.75 % (HL G1−G2 -0.79 pp; r -0.07; p Holm 1; 27 parejas). | **PARCIAL** | Sin modelo de entropía propiamente dicho. |
| 3 | Faltan modelos cuantitativos de supervivencia de estados fácticos | Turno de la primera mención de un PNJ no vivo (1 401 = nunca): G1 949 vs G2 865 (HL G1−G2 +58; r +0.14; p Holm 1; 27 parejas). Incidencia acumulada en el Anexo B. No es un modelo de supervivencia con censura formal. | **PARCIAL** | Kaplan-Meier o similar si se decide; el detector no está auditado. |
| 4 | Faltan evaluaciones humanas a ciegas del rigor histórico con memoria persistente | No aplica al enfoque determinista. Queda para la fase posterior (auditoría con humano y conversación con el asesor). | **LÍMITE** | Fase posterior. |

### OE-7. Comparación de la calidad narrativa emergente entre arquitecturas

| # | Brecha | Evidencia determinista | Estado | Qué falta |
|---|---|---|---|---|
| 1 | Inconsistencias estilísticas («esquizofrenia narrativa») en sistemas multiagente | Estabilidad de estilo dentro de la campaña (variación entre bloques): TTR G1 0.0038 vs G2 0.0038 (HL G1−G2 -0.0001; r -0.06; p Holm 1; 27 parejas); Fernández-Huerta G1 1.26 vs G2 1.65 (HL G1−G2 -0.36; r -0.40; p Holm 0.97; 27 parejas). Persona gramatical: G1 mezcla 2.ª y 3.ª persona (36.9 % en 2.ª) y G2 narra en 2.ª (84.5 %), medido en Par07-27 (`docs/matriz_cobertura_rubrica_instrumentos.md`). | **PARCIAL** | Sin medida de tono. |
| 2 | Impacto de la competencia entre agentes sobre la agencia del jugador (QN-2) | Usurpación mental o verbal del PJ: G1 0.24 % vs G2 4.27 % (HL G1−G2 -3.66 pp; r -1.00; p Holm 5.4e-07; 27 parejas). Por categoría: decisión 0.01 % vs 0.17 %; pensamiento 0.15 % vs 3.24 %; emoción 0.02 % vs 0.28 %; habla 0.05 % vs 0.67 %. Detector congelado, léxico cerrado, precisión sin auditar. | **PARCIAL** | Auditoría de precisión de `persona2` (fase posterior). |
| 3 | Sin pruebas comparativas de innovación y emergencia de ganchos dramáticos | Sin instrumento de interés ni de ganchos. Proxies de emergencia (descriptivos): PNJ registrados G1 4.0 vs G2 8.9 (HL G1−G2 -4.0; r -0.97; p Holm 2.3e-05; 27 parejas); misiones registradas G1 2.0 vs G2 2.0 (HL G1−G2 +0.0; r -1.00; p Holm 1; 27 parejas) (G1 tiene un agente extra que también crea entidades). | **LÍMITE** | Declarar el límite. |
| 4 | Faltan estudios con rúbricas validadas de calidad narrativa aplicadas por paneles a ciegas | La rúbrica v2 con panel humano se sustituyó por medición determinista a petición del asesor; la rúbrica queda como definición de los constructos y los instrumentos como su operacionalización (`docs/matriz_cobertura_rubrica_instrumentos.md`). Un panel queda como fase posterior opcional (Ruta B). | **LÍMITE** | Fase posterior. |

## 4. Anexos

### Anexo A. Deriva por bloques de 200 turnos (media de las parejas)

«Último > primero» = parejas en que el último bloque supera al primero (sobre 27).

| Indicador | Brazo | B1 (1-200) | B2 | B3 | B4 | B5 | B6 | B7 (1201-1400) | último > primero |
|---|---|---|---|---|---|---|---|---|---|
| TTR | G1 | 0.679 | 0.679 | 0.678 | 0.679 | 0.680 | 0.679 | 0.679 | 12/27 |
| TTR | G2 | 0.723 | 0.725 | 0.724 | 0.723 | 0.721 | 0.724 | 0.724 | 16/27 |
| Repetición de bigramas | G1 | 0.029 | 0.029 | 0.029 | 0.029 | 0.029 | 0.030 | 0.030 | 15/27 |
| Repetición de bigramas | G2 | 0.018 | 0.018 | 0.019 | 0.019 | 0.019 | 0.018 | 0.018 | 15/27 |
| Frases idénticas repetidas | G1 | 2.28 % | 2.61 % | 3.61 % | 3.56 % | 3.89 % | 3.69 % | 3.39 % | 13/27 |
| Frases idénticas repetidas | G2 | 0.35 % | 0.35 % | 0.46 % | 0.17 % | 0.33 % | 0.26 % | 0.28 % | 3/27 |
| PNJ no vivo mencionado | G1 | 2.22 % | 7.63 % | 4.59 % | 4.15 % | 8.98 % | 11.39 % | 15.59 % | 7/27 |
| PNJ no vivo mencionado | G2 | 0.41 % | 1.26 % | 2.15 % | 1.52 % | 3.61 % | 4.31 % | 2.78 % | 9/27 |
| Nombres no reconocidos | G1 | 11.69 % | 10.24 % | 8.70 % | 7.46 % | 7.78 % | 7.89 % | 5.96 % | 12/27 |
| Nombres no reconocidos | G2 | 6.74 % | 7.30 % | 6.48 % | 6.78 % | 7.41 % | 6.24 % | 6.37 % | 10/27 |
| Usurpación mental o verbal (persona2) | G1 | 0.15 % | 0.31 % | 0.28 % | 0.28 % | 0.17 % | 0.19 % | 0.20 % | 5/27 |
| Usurpación mental o verbal (persona2) | G2 | 3.46 % | 4.19 % | 4.28 % | 4.11 % | 5.06 % | 4.15 % | 4.43 % | 17/27 |
| Otro alfabeto o U+FFFD | G1 | 0.04 % | 0.09 % | 0.02 % | 0.06 % | 0.13 % | 0.15 % | 0.13 % | 5/27 |
| Otro alfabeto o U+FFFD | G2 | 0.15 % | 0.15 % | 0.04 % | 0.09 % | 0.17 % | 0.04 % | 0.09 % | 4/27 |
| Jaccard con la escena anterior | G1 | 0.190 | 0.191 | 0.192 | 0.193 | 0.194 | 0.194 | 0.192 | 16/27 |
| Jaccard con la escena anterior | G2 | 0.170 | 0.170 | 0.174 | 0.173 | 0.173 | 0.173 | 0.172 | 16/27 |

Anclaje al escenario y respuesta a la acción por ventana de 200 turnos: `docs/reportes/sensibilidad_a4bc_distribucion_27.csv`.

### Anexo B. Primera mención de un PNJ no vivo: campañas donde ya ocurrió

| Brazo | ≤ 200 | ≤ 400 | ≤ 600 | ≤ 800 | ≤ 1000 | ≤ 1200 | ≤ 1400 | nunca | mediana (turno, entre las que ocurren) |
|---|---|---|---|---|---|---|---|---|---|
| G1 | 2/27 | 6/27 | 8/27 | 10/27 | 12/27 | 15/27 | 16/27 | 11/27 | 574 |
| G2 | 4/27 | 7/27 | 10/27 | 12/27 | 15/27 | 16/27 | 16/27 | 11/27 | 430 |

### Anexo C. Frases idénticas más repetidas (por campaña, exactas)

| Brazo | Veces | Pareja | Frase (exactamente igual, normalizada a minúsculas) |
|---|---|---|---|
| G1 | 95 | 17 | la paciencia de bibiana se ha agotado. |
| G1 | 67 | 13 | la paciencia de baldemar se ha agotado. |
| G1 | 64 | 12 | la paciencia de prín se ha agotado. |
| G1 | 45 | 13 | la paciencia de baldemar se ha agotado por completo. |
| G1 | 27 | 12 | la paciencia de osvaldo se ha agotado. |
| G2 | 8 | 02 | [para resolver esta acción es necesaria una tirada de destreza (herramientas de ladrón). |
| G2 | 8 | 02 | por favor, lanza el dado y añade el modificador correspondiente para determinar si la secuencia técnica tiene éxito.] |
| G2 | 8 | 14 | madame valeriane sostiene la mirada, imperturbable. |
| G2 | 7 | 16 | el impacto es seco y contundente. |
| G2 | 6 | 10 | hasta que no tenga el resultado, no puedo narrar si el tajo impacta o si el vigilante logra evitarlo.] |

### Anexo D. Trazabilidad y advertencias

- Detector `persona2` v2b congelado (hashes en `datos/validacion/persona2_congelado.sha256`); matriz de CR-2a/CR-2b a4bc-2, SHA-256 `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744`.
- Par02 G2 tiene 1 668 turnos en la base; todos los cálculos se recortan a 1 400.
- Sanidad del recálculo: en G2 (donde la normalización es la identidad) v1 = v2 en Par07-27 (0 discrepancias en 29 400 turnos por instrumento); en Par01-06, 42 de 8 400 turnos difieren en el recuento de nombres no reconocidos y 2 en la densidad del grafo (reconstrucción de entidades de un motor previo), sin efecto material.
- Par01-17 se generaron con el motor sin avance de reloj ni guardia de metamensajes; Par18-27 con reloj determinista, dados de combate y guardia. Cada resultado del consolidado muestra el HL por lote y marca los cambios de signo.
- Las medidas del Anexo A-C (`experimento/scripts/reporte_v2/medidas_cierre.py`) no tienen prueba de sensibilidad: son medidas simples y transparentes.
