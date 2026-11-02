# Paquete de resultados para el capítulo 6

Generado por `experimento/scripts/reporte_v2/resultados_tesis.py` el 2026-10-31 00:44. Muestra: **27 parejas** (Par01-27; coincide con el N = 27 del diseño), 54 campañas de 1 400 turnos, mismo modelo y mismo agente jugador en ambos brazos, medición 100 % determinista sobre texto normalizado (se quita el formato de G1). Descriptivo: **no decide las hipótesis**; entrega las pruebas y su dirección. El uso propuesto de cada instrumento en la docimasia es una propuesta basada en la validación disponible.

**Cómo leer.** Cada valor es la media de la campaña (turnos 2-1 400; `persona2` solo sobre turnos que no se usaron para construir el detector); la unidad de análisis es la **pareja**, no el juicio de un evaluador. Cuartiles con interpolación lineal. Wilcoxon de rangos con signo **exacto** (condicional a empates, ceros descartados), con p bilateral y unilateral en cada dirección, como en el capítulo actual. **↕**: ↑ mayor es mejor, ↓ menor es mejor, · sin sentido de mejora (solo bilateral). «G1 mejor» = la dirección favorable a G1 según ↕. Holm: dentro de la familia de cada hipótesis, solo entre instrumentos confirmatorios. Shapiro-Wilk con SciPy.

**Punto abierto para la docimasia.** Las hipótesis H1a-H1c ('superior a la media') se contrastaban con Wilcoxon de una muestra contra μ₀ = 4, el punto medio de la escala Likert. Los instrumentos deterministas **no tienen punto medio**, así que para OE-1 a OE-3 este paquete entrega los valores de G2 (y de G1) pero no un contraste contra μ₀; hay que decidir cómo se operacionaliza esa hipótesis. Además, el texto de Limitaciones del capítulo 2 aún dice que la calidad narrativa emergente se mitiga con la rúbrica sobre un bloque piloto; hay que reconciliarlo con el giro totalmente determinista.

## 0. Ficha de instrumentos (para documentar la metodología)

| Indicador | Instrumento | ↕ | Uso propuesto | A2: confirmatorias que respondieron | Motivo y limitación |
|---|---|---|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool, 1 de cada 10 turnos) | ↑ | Descriptivo / no usar | 2/4 | techo ≈ 0.999: no discrimina; techo cercano a 1: discrimina poco |
| CR-1 | cr1: pifia narrada como éxito (% de turnos) | ↓ | Descriptivo / no usar | 2/2 | baja precisión (ignora la negación); tasas ≈ 0.1 %; baja precisión: ignora la negación («no logras») |
| CR-2 | CR-2a: respuesta a la acción específica (z) | ↑ | Confirmatorio | 25/26 | instrumento nuevo, matriz a4bc-2 (25 de 26 celdas direccionales); instrumento nuevo, matriz a4bc-2 |
| CR-2 | CR-2a: solapamiento con la acción (crudo) | ↑ | Exploratorio | 25/26 | complementa a z; misma evaluación a4bc-2; instrumento nuevo, matriz a4bc-2 |
| CR-2 | CR-2b: anclaje al escenario (coseno, ventana de 8) | ↑ | Exploratorio | 25/26 | no distingue deriva de evolución legítima del mundo; idf depende del conjunto de campañas; no distingue deriva de evolución legítima del mundo |
| CR-2 | CR-2b: anclaje sin nombres propios (ventana de 8) | ↑ | Exploratorio | 25/26 | casi plano: la señal la sostienen los nombres; casi plano: la señal la sostienen los nombres |
| CR-2 | Densidad del grafo de entidades | · | Descriptivo / no usar | 2/4 | A2: insensible a otro escenario; insensible a otro escenario (P8) |
| CR-2 | Turnos con algún nombre no reconocido | ↓ | Exploratorio | 2/4 | no separa nombres inventados de PNJ legítimos nuevos; v1 saturado en G1 por la línea mecánica |
| CR-2 | N.º de nombres no reconocidos por turno | ↓ | Exploratorio | 4/4 | ídem; no detecta nombres inventados por sí solo |
| CL-1 | Papalampidi C: coherencia de entidad | ↑ | Exploratorio | — | proxy de identidad; solo controles en A2; proxy de consistencia de personajes |
| CL-1 | Papalampidi V: consistencia de atributos | ↑ | Exploratorio | — | proxy; no mide voz ni motivaciones; proxy; no mide voz ni motivaciones |
| CL-1 | Entity Coreference Rate | ↑ | Descriptivo / no usar | — | saturado (≈ 1); saturado (≈ 1) |
| CL-2 | Jericho: recall de cambios de estado narrados | ↑ | Exploratorio | — | A2 mecánico 80/80 (léxico exacto insertado y quitado); frente al azar: 25.9 % real vs 12.9 %, con +21 a +25 pp en npc.status y solo +2 a +4.5 pp en npc.affinity (55 % de los eventos); A2 mecánico 80/80; frente al azar discrimina en npc.status (+21 a +25 pp) y casi nada en npc.affinity (+2 a +4.5 pp) |
| CL-2 | Relojes: fracción reconocida en la narración | ↑ | Descriptivo / no usar | — | A2 mecánico 23/23, pero 88.3 % real frente a 89.8 % por azar: el vocabulario (palabras funcionales y texto del evento) reconoce casi cualquier ventana; solo Par18-27 (10 parejas); A2 mecánico 23/23, pero reconoce lo mismo por azar (88 % real frente a 90 %): no discrimina |
| CL-2 | PNJ inactivo mencionado (% de turnos) | ↓ | Exploratorio | 8/8 | mide mención, no acción; precisión sin auditar; mide mención, no acción; precisión sin auditar |
| CL-2 | PNJ inactivo como sujeto (por 1 000 turnos) | ↓ | Exploratorio | 4/8 | solo ve nombres de una palabra; solo ve nombres de una palabra |
| CL-2 | Jaccard con la escena anterior | · | Exploratorio | 2/2 | continuidad léxica, no de eventos; continuidad léxica, no de eventos |
| CL-2 | Bucles: ciclos de ubicaciones | ↓ | Descriptivo / no usar | 0/2 | A2: no reacciona a permutar turnos; A2: no reacciona a permutar turnos |
| QN-1 | TTR (diversidad léxica) | ↑ | Exploratorio | 4/4 | respondió en A2, pero por turno depende de la longitud (G1 158 vs G2 116 palabras): la diferencia se invierte a igual longitud; ver ttr100, MTLD y MATTR; por turno: depende de la longitud (ver MTLD, MATTR y el control a 100 palabras) |
| QN-1 | Repetición de bigramas | ↓ | Exploratorio | 2/2 | respondió en A2, pero por turno crece con la longitud del turno: la diferencia se invierte a 100 palabras; ver ngram100; por turno: depende de la longitud (ver el control a 100 palabras) |
| QN-1 | Legibilidad Fernández-Huerta | · | Descriptivo / no usar | — | complejidad, sin sentido de mejora; complejidad, no calidad |
| QN-1 | Densidad del grafo por lema | · | Descriptivo / no usar | 0/2 | A2: insensible a otro escenario; insensible a otro escenario (P8) |
| QN-2 | Usurpación mental o verbal del PJ (% de turnos) | ↓ | Confirmatorio condicionado | DIR 7/10 · INV 4/4 | detector congelado v2b; precisión sin auditar (fase posterior); v2b congelado, léxico cerrado; precisión sin auditar (C2-C4) |
| QN-2 | · decisión | ↓ | Confirmatorio condicionado | DIR 7/10 · INV 4/4 | ídem; ídem |
| QN-2 | · pensamiento | ↓ | Confirmatorio condicionado | DIR 7/10 · INV 4/4 | ídem; ídem |
| QN-2 | · emoción | ↓ | Confirmatorio condicionado | DIR 7/10 · INV 4/4 | ídem; ídem |
| QN-2 | · habla | ↓ | Confirmatorio condicionado | DIR 7/10 · INV 4/4 | ídem; ídem |
| QN-2 | Acción física no declarada (experimental, % de turnos) | ↓ | Exploratorio | DIR 7/10 · INV 4/4 | experimental; experimental; equivalencia 70 % (A2) |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | ↓ | Exploratorio | — | medida simple; sin prueba de sensibilidad; medida simple, sin prueba A2; límite inferior de las fórmulas evasivas |
| QN-1 | MTLD de la campaña (complementa al TTR; no depende de la longitud) | ↑ | Exploratorio | — | complementa a TTR; no depende de la longitud; A2 (extensión): control P9 sin sesgo significativo (Holm 0.17 en G1, 1.0 en G2; G1 +2.0 de mediana, δ 0.43); sin celda que detecte un defecto real; medida nueva sobre texto concatenado; sin prueba A2 con datos reales |
| QN-1 | MATTR de la campaña, ventana de 50 (complementa al TTR) | ↑ | Exploratorio | — | complementa a TTR; no depende de la longitud; A2 (extensión): control P9 sin sesgo (Holm 0.73 en G1, 1.0 en G2); sin celda que detecte un defecto real; medida nueva sobre texto concatenado; sin prueba A2 con datos reales |
| QN-1 | TTR a 100 palabras (control de longitud del TTR por turno) | ↑ | Exploratorio | — | control de longitud del TTR por turno; sin prueba de sensibilidad; mismas 100 primeras palabras de cada turno con >= 100; sin prueba A2 |
| QN-1 | Repetición de bigramas a 100 palabras (control de longitud) | ↓ | Exploratorio | — | control de longitud de la repetición por turno; sin prueba de sensibilidad; mismas 100 primeras palabras de cada turno con >= 100; sin prueba A2 |
| QN-1 | Turnos con ≥ 100 palabras (fracción que entra al control) | · | Descriptivo / no usar | — | descriptivo: fracción de turnos que entra al control; descriptivo: el control excluye más turnos de G2 (más cortos) |
| QN-1 | Palabras por turno (mediana) | · | Descriptivo / no usar | — | descriptivo: longitud del turno (confusor del TTR y de los bigramas por turno); descriptivo: el TTR y la repetición de bigramas por turno dependen de la longitud del turno |
| QN-1 | Szigriszt-Pazos (legibilidad; complementa a Fernández-Huerta) | · | Descriptivo / no usar | — | complementa a Fernández-Huerta (no lo reemplaza); A2 (extensión): invariante exacto ante P6, incumple P11a en G2 igual que FH (artefacto de formato); sin celda confirmatoria posible para legibilidad; calculado del texto, no está en el motor; sin prueba A2; sin sentido de mejora |
| QN-1 | Estabilidad de estilo: variación del TTR entre bloques | ↓ | Exploratorio | — | medida simple; medida simple, sin prueba A2 |
| QN-1 | Estabilidad de estilo: variación de Fernández-Huerta entre bloques | ↓ | Exploratorio | — | medida simple; medida simple, sin prueba A2 |
| QN-1 | PNJ registrados hasta el turno 1 400 | · | Descriptivo / no usar | — | proxy descriptivo; G1 tiene un agente extra que crea entidades; proxy de emergencia; G1 tiene un agente extra que también crea entidades |
| QN-1 | Misiones registradas hasta el turno 1 400 | · | Descriptivo / no usar | — | casi constante (2 por campaña, sembradas); casi constante (2 por campaña, sembradas): el r no es informativo |
| CR-1 | Turnos con caracteres de otro alfabeto o U+FFFD (%) | ↓ | Exploratorio | — | medida simple; sin prueba de sensibilidad; medida simple; detecta fallos de codificación e idioma |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1 401 = nunca) | ↑ | Exploratorio | — | mide mención; censurado en 1 401; mide mención, no acción; censurado en 1 401 |
| OP | Segundos por turno (mediana; proxy de latencia) | ↓ | Descriptivo / no usar | — | operativo, fuera de la rúbrica; incluye al jugador LLM y la extracción; corridas concurrentes |

A2 = prueba de sensibilidad por perturbación (`docs/reportes/sensibilidad_baseline.md`; CR-2a/CR-2b en `sensibilidad_a4bc.md`; persona2 en `persona2_equivalencia.md`). «—» = sin prueba. CR-2a/CR-2b y persona2 son instrumentos nuevos de esta tesis; persona2 está congelado (hashes en `datos/validacion/persona2_congelado.sha256`).

## 1. OE-1. Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico (G2)

### Tabla 3. Estadísticos descriptivos del sistema monolítico (G2), n = 27 campañas y prueba de normalidad de Shapiro-Wilk

| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool, 1 de cada 10 turnos) | 27 | 0.9992 | 0.9991 | 0.9994 | 0.0003 | 0.9984 | 0.9998 | 0.9992 (0.0004) | 0.9587 | 0.3445 | sí |
| CR-1 | cr1: pifia narrada como éxito (% de turnos) | 27 | 0.07 % | 0.00 % | 0.14 % | 0.14 % | 0.00 % | 0.50 % | 0.09 % (0.11 %) | 0.7567 | <0.0001 | no |
| CR-2 | CR-2a: respuesta a la acción específica (z) | 27 | 2.81 | 2.61 | 3.01 | 0.40 | 2.45 | 3.51 | 2.82 (0.27) | 0.9545 | 0.2746 | sí |
| CR-2 | CR-2a: solapamiento con la acción (crudo) | 27 | 0.125 | 0.114 | 0.134 | 0.020 | 0.104 | 0.163 | 0.125 (0.014) | 0.9547 | 0.2788 | sí |
| CR-2 | CR-2b: anclaje al escenario (coseno, ventana de 8) | 27 | 0.072 | 0.061 | 0.082 | 0.021 | 0.047 | 0.145 | 0.076 (0.024) | 0.8994 | 0.0130 | no |
| CR-2 | CR-2b: anclaje sin nombres propios (ventana de 8) | 27 | 0.063 | 0.050 | 0.073 | 0.023 | 0.043 | 0.083 | 0.062 (0.013) | 0.9147 | 0.0295 | no |
| CR-2 | Densidad del grafo de entidades | 27 | 0.297 | 0.160 | 0.388 | 0.228 | 0.091 | 0.502 | 0.279 (0.127) | 0.9144 | 0.0291 | no |
| CR-2 | Turnos con algún nombre no reconocido | 27 | 5.08 % | 3.40 % | 7.72 % | 4.32 % | 2.43 % | 24.23 % | 6.75 % (5.08 %) | 0.7352 | <0.0001 | no |
| CR-2 | N.º de nombres no reconocidos por turno | 27 | 0.073 | 0.060 | 0.132 | 0.072 | 0.034 | 0.445 | 0.114 (0.096) | 0.7338 | <0.0001 | no |
| CR-1 | Turnos con caracteres de otro alfabeto o U+FFFD (%) | 27 | 0.07 % | 0.07 % | 0.14 % | 0.07 % | 0.00 % | 0.29 % | 0.10 % (0.08 %) | 0.8786 | 0.0045 | no |

Mismos estadísticos del sistema multiagente (G1), como referencia para la comparación:

| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool, 1 de cada 10 turnos) | 27 | 0.9994 | 0.9992 | 0.9994 | 0.0002 | 0.9979 | 0.9999 | 0.9993 (0.0004) | 0.7954 | 0.0001 | no |
| CR-1 | cr1: pifia narrada como éxito (% de turnos) | 27 | 0.07 % | 0.07 % | 0.14 % | 0.07 % | 0.00 % | 0.29 % | 0.10 % (0.08 %) | 0.8734 | 0.0035 | no |
| CR-2 | CR-2a: respuesta a la acción específica (z) | 27 | 2.70 | 2.51 | 2.77 | 0.27 | 2.22 | 3.38 | 2.69 (0.26) | 0.9616 | 0.4022 | sí |
| CR-2 | CR-2a: solapamiento con la acción (crudo) | 27 | 0.135 | 0.132 | 0.144 | 0.013 | 0.112 | 0.156 | 0.136 (0.011) | 0.9569 | 0.3139 | sí |
| CR-2 | CR-2b: anclaje al escenario (coseno, ventana de 8) | 27 | 0.143 | 0.098 | 0.174 | 0.077 | 0.027 | 0.234 | 0.134 (0.054) | 0.9816 | 0.8960 | sí |
| CR-2 | CR-2b: anclaje sin nombres propios (ventana de 8) | 27 | 0.073 | 0.068 | 0.077 | 0.009 | 0.029 | 0.116 | 0.075 (0.019) | 0.9421 | 0.1373 | sí |
| CR-2 | Densidad del grafo de entidades | 27 | 0.237 | 0.162 | 0.315 | 0.154 | 0.115 | 0.385 | 0.241 (0.086) | 0.9120 | 0.0255 | no |
| CR-2 | Turnos con algún nombre no reconocido | 27 | 3.00 % | 1.50 % | 10.19 % | 8.68 % | 0.29 % | 71.34 % | 8.52 % (14.38 %) | 0.5502 | <0.0001 | no |
| CR-2 | N.º de nombres no reconocidos por turno | 27 | 0.038 | 0.019 | 0.111 | 0.093 | 0.004 | 1.467 | 0.141 (0.297) | 0.4619 | <0.0001 | no |
| CR-1 | Turnos con caracteres de otro alfabeto o U+FFFD (%) | 27 | 0.07 % | 0.00 % | 0.14 % | 0.14 % | 0.00 % | 0.29 % | 0.09 % (0.09 %) | 0.8492 | 0.0011 | no |

## 2. OE-2. Evaluar la coherencia longitudinal a lo largo de las campañas generadas por el sistema monolítico (G2)

### Tabla 5. Estadísticos descriptivos del sistema monolítico (G2), n = 27 campañas y prueba de normalidad de Shapiro-Wilk

| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL-1 | Papalampidi C: coherencia de entidad | 27 | 1.67 | 0.92 | 2.29 | 1.38 | 0.00 | 3.33 | 1.60 (0.88) | 0.9714 | 0.6394 | sí |
| CL-1 | Papalampidi V: consistencia de atributos | 27 | 0.058 | 0.048 | 0.079 | 0.031 | 0.030 | 0.151 | 0.067 (0.032) | 0.8568 | 0.0016 | no |
| CL-1 | Entity Coreference Rate | 27 | 0.998 | 0.998 | 0.998 | 0.001 | 0.997 | 0.999 | 0.998 (0.000) | 0.9512 | 0.2287 | sí |
| CL-2 | Jericho: recall de cambios de estado narrados | 26 | 0.22 | 0.13 | 0.36 | 0.23 | 0.00 | 0.50 | 0.24 (0.16) | 0.9396 | 0.1312 | sí |
| CL-2 | Relojes: fracción reconocida en la narración | 10 | 0.83 | 0.67 | 1.00 | 0.33 | 0.33 | 1.00 | 0.80 (0.23) | 0.7809 | 0.0085 | no |
| CL-2 | PNJ inactivo mencionado (% de turnos) | 27 | 0.21 % | 0.00 % | 2.50 % | 2.50 % | 0.00 % | 15.94 % | 2.29 % (3.93 %) | 0.6490 | <0.0001 | no |
| CL-2 | PNJ inactivo como sujeto (por 1 000 turnos) | 27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 73.52 | 4.23 (14.55) | 0.3293 | <0.0001 | no |
| CL-2 | Jaccard con la escena anterior | 27 | 0.173 | 0.169 | 0.177 | 0.008 | 0.160 | 0.181 | 0.172 (0.006) | 0.9624 | 0.4186 | sí |
| CL-2 | Bucles: ciclos de ubicaciones | 27 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 (0.00) | — | — | — |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1 401 = nunca) | 27 | 891 | 380 | 1401 | 1021 | 83 | 1401 | 865 (520) | 0.8295 | 0.0005 | no |

Mismos estadísticos del sistema multiagente (G1), como referencia para la comparación:

| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL-1 | Papalampidi C: coherencia de entidad | 27 | 2.17 | 1.50 | 2.67 | 1.17 | 1.00 | 3.00 | 2.13 (0.59) | 0.9163 | 0.0322 | no |
| CL-1 | Papalampidi V: consistencia de atributos | 27 | 0.074 | 0.062 | 0.097 | 0.035 | 0.039 | 0.138 | 0.081 (0.026) | 0.9533 | 0.2574 | sí |
| CL-1 | Entity Coreference Rate | 27 | 0.997 | 0.997 | 0.998 | 0.001 | 0.996 | 0.998 | 0.997 (0.001) | 0.9351 | 0.0923 | sí |
| CL-2 | Jericho: recall de cambios de estado narrados | 26 | 0.21 | 0.03 | 0.30 | 0.27 | 0.00 | 0.60 | 0.22 (0.18) | 0.9131 | 0.0311 | no |
| CL-2 | Relojes: fracción reconocida en la narración | 10 | 1.00 | 1.00 | 1.00 | 0.00 | 0.67 | 1.00 | 0.97 (0.11) | 0.3657 | <0.0001 | no |
| CL-2 | PNJ inactivo mencionado (% de turnos) | 27 | 3.86 % | 0.00 % | 12.47 % | 12.47 % | 0.00 % | 44.67 % | 7.80 % (10.56 %) | 0.7630 | <0.0001 | no |
| CL-2 | PNJ inactivo como sujeto (por 1 000 turnos) | 27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 198.43 | 7.35 (38.19) | 0.1930 | <0.0001 | no |
| CL-2 | Jaccard con la escena anterior | 27 | 0.193 | 0.187 | 0.197 | 0.010 | 0.175 | 0.213 | 0.192 (0.008) | 0.9740 | 0.7105 | sí |
| CL-2 | Bucles: ciclos de ubicaciones | 27 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 (0.00) | — | — | — |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1 401 = nunca) | 27 | 1139 | 480 | 1401 | 922 | 116 | 1401 | 949 (484) | 0.8212 | 0.0003 | no |

## 3. OE-3. Evaluar la calidad de la coherencia narrativa emergente en las campañas generadas por el sistema monolítico (G2)

### Tabla 7. Estadísticos descriptivos del sistema monolítico (G2), n = 27 campañas y prueba de normalidad de Shapiro-Wilk

| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QN-1 | TTR (diversidad léxica) | 27 | 0.725 | 0.719 | 0.732 | 0.013 | 0.701 | 0.737 | 0.723 (0.009) | 0.9216 | 0.0432 | no |
| QN-1 | Repetición de bigramas | 27 | 0.018 | 0.017 | 0.019 | 0.002 | 0.016 | 0.022 | 0.018 (0.002) | 0.9533 | 0.2580 | sí |
| QN-1 | Legibilidad Fernández-Huerta | 27 | 61.8 | 60.6 | 63.7 | 3.1 | 55.1 | 66.1 | 61.9 (2.5) | 0.9723 | 0.6640 | sí |
| QN-1 | Densidad del grafo por lema | 27 | 0.021 | 0.017 | 0.027 | 0.010 | 0.005 | 0.045 | 0.022 (0.009) | 0.9609 | 0.3877 | sí |
| QN-2 | Usurpación mental o verbal del PJ (% de turnos) | 27 | 0.37 % | 0.26 % | 0.58 % | 0.33 % | 0.09 % | 1.28 % | 0.43 % (0.26 %) | 0.8878 | 0.0071 | no |
| QN-2 | · decisión | 27 | 0.15 % | 0.07 % | 0.29 % | 0.21 % | 0.00 % | 0.43 % | 0.17 % (0.13 %) | 0.9243 | 0.0503 | sí |
| QN-2 | · pensamiento | 27 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % (0.00 %) | — | — | — |
| QN-2 | · emoción | 27 | 0.22 % | 0.15 % | 0.36 % | 0.21 % | 0.00 % | 1.02 % | 0.27 % (0.21 %) | 0.8200 | 0.0003 | no |
| QN-2 | · habla | 27 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.07 % | 0.00 % (0.01 %) | 0.1930 | <0.0001 | no |
| QN-2 | Acción física no declarada (experimental, % de turnos) | 27 | 7.23 % | 6.25 % | 8.43 % | 2.17 % | 3.91 % | 10.57 % | 7.21 % (1.58 %) | 0.9667 | 0.5179 | sí |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | 27 | 0.00 % | 0.00 % | 0.46 % | 0.46 % | 0.00 % | 1.79 % | 0.31 % (0.44 %) | 0.7540 | <0.0001 | no |
| QN-1 | MTLD de la campaña (complementa al TTR; no depende de la longitud) | 27 | 108.9 | 104.9 | 110.7 | 5.9 | 101.7 | 114.2 | 108.5 (3.8) | 0.9486 | 0.1985 | sí |
| QN-1 | MATTR de la campaña, ventana de 50 (complementa al TTR) | 27 | 0.828 | 0.825 | 0.829 | 0.005 | 0.820 | 0.833 | 0.827 (0.004) | 0.9498 | 0.2126 | sí |
| QN-1 | TTR a 100 palabras (control de longitud del TTR por turno) | 27 | 0.7393 | 0.7352 | 0.7419 | 0.0067 | 0.7292 | 0.7463 | 0.7387 (0.0046) | 0.9630 | 0.4304 | sí |
| QN-1 | Repetición de bigramas a 100 palabras (control de longitud) | 27 | 0.0154 | 0.0147 | 0.0161 | 0.0014 | 0.0135 | 0.0180 | 0.0154 (0.0011) | 0.9757 | 0.7557 | sí |
| QN-1 | Turnos con ≥ 100 palabras (fracción que entra al control) | 27 | 0.820 | 0.760 | 0.855 | 0.094 | 0.713 | 0.962 | 0.817 (0.072) | 0.9432 | 0.1464 | sí |
| QN-1 | Palabras por turno (mediana) | 27 | 116 | 111 | 120 | 10 | 110 | 146 | 119 (10) | 0.7732 | <0.0001 | no |
| QN-1 | Szigriszt-Pazos (legibilidad; complementa a Fernández-Huerta) | 27 | 57.6 (normal) | 56.3 | 59.6 | 3.2 | 50.8 | 62.0 | 57.7 (2.5) | 0.9722 | 0.6614 | sí |
| QN-1 | Estabilidad de estilo: variación del TTR entre bloques | 27 | 0.0034 | 0.0028 | 0.0043 | 0.0015 | 0.0013 | 0.0092 | 0.0038 (0.0018) | 0.8717 | 0.0032 | no |
| QN-1 | Estabilidad de estilo: variación de Fernández-Huerta entre bloques | 27 | 1.43 | 0.88 | 2.34 | 1.46 | 0.58 | 3.29 | 1.65 (0.88) | 0.9122 | 0.0257 | no |
| QN-1 | PNJ registrados hasta el turno 1 400 | 27 | 8.0 | 6.0 | 10.0 | 4.0 | 3.0 | 21.0 | 8.9 (4.4) | 0.8857 | 0.0064 | no |
| QN-1 | Misiones registradas hasta el turno 1 400 | 27 | 2.0 | 2.0 | 2.0 | 0.0 | 2.0 | 3.0 | 2.0 (0.2) | 0.1930 | <0.0001 | no |

Mismos estadísticos del sistema multiagente (G1), como referencia para la comparación:

| Indicador | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk W | p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QN-1 | TTR (diversidad léxica) | 27 | 0.679 | 0.674 | 0.683 | 0.009 | 0.653 | 0.694 | 0.679 (0.008) | 0.9320 | 0.0774 | sí |
| QN-1 | Repetición de bigramas | 27 | 0.030 | 0.026 | 0.031 | 0.005 | 0.025 | 0.038 | 0.029 (0.003) | 0.9394 | 0.1180 | sí |
| QN-1 | Legibilidad Fernández-Huerta | 27 | 60.5 | 59.5 | 62.1 | 2.6 | 51.8 | 64.6 | 60.3 (2.6) | 0.9064 | 0.0188 | no |
| QN-1 | Densidad del grafo por lema | 27 | 0.032 | 0.024 | 0.038 | 0.015 | 0.018 | 0.055 | 0.032 (0.010) | 0.9352 | 0.0929 | sí |
| QN-2 | Usurpación mental o verbal del PJ (% de turnos) | 27 | 0.00 % | 0.00 % | 0.07 % | 0.07 % | 0.00 % | 0.17 % | 0.03 % (0.05 %) | 0.6712 | <0.0001 | no |
| QN-2 | · decisión | 27 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.07 % | 0.01 % (0.02 %) | 0.3705 | <0.0001 | no |
| QN-2 | · pensamiento | 27 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % (0.00 %) | — | — | — |
| QN-2 | · emoción | 27 | 0.00 % | 0.00 % | 0.04 % | 0.04 % | 0.00 % | 0.17 % | 0.02 % (0.04 %) | 0.5915 | <0.0001 | no |
| QN-2 | · habla | 27 | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % (0.00 %) | — | — | — |
| QN-2 | Acción física no declarada (experimental, % de turnos) | 27 | 0.68 % | 0.59 % | 0.94 % | 0.35 % | 0.17 % | 62.71 % | 3.05 % (11.93 %) | 0.2143 | <0.0001 | no |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | 27 | 1.79 % | 1.21 % | 3.14 % | 1.93 % | 0.43 % | 14.21 % | 3.29 % (3.78 %) | 0.6636 | <0.0001 | no |
| QN-1 | MTLD de la campaña (complementa al TTR; no depende de la longitud) | 27 | 109.0 | 107.5 | 111.3 | 3.8 | 99.3 | 118.5 | 108.9 (4.2) | 0.9741 | 0.7121 | sí |
| QN-1 | MATTR de la campaña, ventana de 50 (complementa al TTR) | 27 | 0.824 | 0.823 | 0.827 | 0.004 | 0.815 | 0.834 | 0.824 (0.004) | 0.9501 | 0.2159 | sí |
| QN-1 | TTR a 100 palabras (control de longitud del TTR por turno) | 27 | 0.7409 | 0.7393 | 0.7430 | 0.0037 | 0.7321 | 0.7485 | 0.7409 (0.0039) | 0.9740 | 0.7096 | sí |
| QN-1 | Repetición de bigramas a 100 palabras (control de longitud) | 27 | 0.0139 | 0.0134 | 0.0146 | 0.0012 | 0.0117 | 0.0168 | 0.0140 (0.0011) | 0.9801 | 0.8641 | sí |
| QN-1 | Turnos con ≥ 100 palabras (fracción que entra al control) | 27 | 0.999 | 0.998 | 0.999 | 0.001 | 0.977 | 1.000 | 0.997 (0.005) | 0.5289 | <0.0001 | no |
| QN-1 | Palabras por turno (mediana) | 27 | 158 | 152 | 162 | 11 | 142 | 176 | 158 (9) | 0.9814 | 0.8918 | sí |
| QN-1 | Szigriszt-Pazos (legibilidad; complementa a Fernández-Huerta) | 27 | 56.3 (normal) | 55.3 | 57.9 | 2.6 | 47.3 | 60.4 | 56.1 (2.7) | 0.9021 | 0.0150 | no |
| QN-1 | Estabilidad de estilo: variación del TTR entre bloques | 27 | 0.0034 | 0.0025 | 0.0045 | 0.0020 | 0.0012 | 0.0081 | 0.0038 (0.0019) | 0.8777 | 0.0043 | no |
| QN-1 | Estabilidad de estilo: variación de Fernández-Huerta entre bloques | 27 | 0.89 | 0.64 | 2.00 | 1.36 | 0.46 | 2.71 | 1.26 (0.80) | 0.8065 | 0.0002 | no |
| QN-1 | PNJ registrados hasta el turno 1 400 | 27 | 4.0 | 3.0 | 4.5 | 1.5 | 3.0 | 7.0 | 4.0 (1.0) | 0.8363 | 0.0006 | no |
| QN-1 | Misiones registradas hasta el turno 1 400 | 27 | 2.0 | 2.0 | 2.0 | 0.0 | 2.0 | 2.0 | 2.0 (0.0) | — | — | — |

## 4. OE-4. Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura

### Tabla 9. Comparación pareada G1 − G2, 27 parejas (H1d (coherencia reactiva))

| Indicador | Instrumento | ↕ | Uso | Mdn G1 (Q1–Q3) | Mdn G2 (Q1–Q3) | Mdn dif. | HL [IC 95 %] | W+ | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm | Shapiro dif. p | Lotes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool, 1 de cada 10 turnos) | ↑ | Descriptivo / no usar | 0.9994 (0.9992–0.9994) | 0.9992 (0.9991–0.9994) | +0.0001 | +0.0001 [-0.0001, +0.0003] | 241.0 | 27 | 0.2176 | 0.1088 | 0.8935 | +0.28 | — | 0.4088 | consistente |
| CR-1 | cr1: pifia narrada como éxito (% de turnos) | ↓ | Descriptivo / no usar | 0.07 % (0.07 %–0.14 %) | 0.07 % (0.00 %–0.14 %) | +0.00 pp | +0.00 pp [-0.04, +0.07] | 90.0 | 17 | 0.5338 | 0.7428 | 0.2669 | +0.18 | — | 0.0072 | consistente |
| CR-2 | CR-2a: respuesta a la acción específica (z) | ↑ | Confirmatorio | 2.70 (2.51–2.77) | 2.81 (2.61–3.01) | -0.18 | -0.13 [-0.25, -0.03] | 100.0 | 27 | 0.0319 | 0.9850 | 0.0159 | -0.47 | 0.0319 | 0.9225 | consistente |
| CR-2 | CR-2a: solapamiento con la acción (crudo) | ↑ | Exploratorio | 0.135 (0.132–0.144) | 0.125 (0.114–0.134) | +0.009 | +0.011 [+0.006, +0.015] | 347.0 | 27 | <0.0001 | <0.0001 | 1.0000 | +0.84 | — | 0.9472 | consistente |
| CR-2 | CR-2b: anclaje al escenario (coseno, ventana de 8) | ↑ | Exploratorio | 0.143 (0.098–0.174) | 0.072 (0.061–0.082) | +0.060 | +0.059 [+0.035, +0.082] | 345.0 | 27 | <0.0001 | <0.0001 | 1.0000 | +0.83 | — | 0.6026 | consistente |
| CR-2 | CR-2b: anclaje sin nombres propios (ventana de 8) | ↑ | Exploratorio | 0.073 (0.068–0.077) | 0.063 (0.050–0.073) | +0.012 | +0.013 [+0.005, +0.020] | 307.0 | 27 | 0.0036 | 0.0018 | 0.9984 | +0.62 | — | 0.9664 | consistente |
| CR-2 | Densidad del grafo de entidades | · | Descriptivo / no usar | 0.237 (0.162–0.315) | 0.297 (0.160–0.388) | -0.028 | -0.032 [-0.066, -0.006] | 92.0 | 27 | 0.0187 | — | — | -0.51 | — | 0.1495 | consistente |
| CR-2 | Turnos con algún nombre no reconocido | ↓ | Exploratorio | 3.00 % (1.50 %–10.19 %) | 5.08 % (3.40 %–7.72 %) | -2.00 pp | -0.79 pp [-3.04, +3.70] | 176.0 | 27 | 0.7676 | 0.3838 | 0.6252 | -0.07 | — | <0.0001 | ⚠ signo distinto |
| CR-2 | N.º de nombres no reconocidos por turno | ↓ | Exploratorio | 0.038 (0.019–0.111) | 0.073 (0.060–0.132) | -0.033 | -0.027 [-0.064, +0.041] | 155.0 | 27 | 0.4270 | 0.2135 | 0.7934 | -0.18 | — | <0.0001 | ⚠ signo distinto |
| CR-1 | Turnos con caracteres de otro alfabeto o U+FFFD (%) | ↓ | Exploratorio | 0.07 % (0.00 %–0.14 %) | 0.07 % (0.07 %–0.14 %) | +0.00 pp | -0.04 pp [-0.07, +0.04] | 73.0 | 18 | 0.5994 | 0.2997 | 0.7055 | -0.15 | — | 0.0592 | consistente |

## 5. OE-5. Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas

### Tabla 11. Comparación pareada G1 − G2, 27 parejas (H1e (coherencia longitudinal))

| Indicador | Instrumento | ↕ | Uso | Mdn G1 (Q1–Q3) | Mdn G2 (Q1–Q3) | Mdn dif. | HL [IC 95 %] | W+ | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm | Shapiro dif. p | Lotes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL-1 | Papalampidi C: coherencia de entidad | ↑ | Exploratorio | 2.17 (1.50–2.67) | 1.67 (0.92–2.29) | +0.50 | +0.58 [+0.17, +1.00] | 250.0 | 25 | 0.0170 | 0.0085 | 0.9919 | +0.54 | — | 0.6363 | consistente |
| CL-1 | Papalampidi V: consistencia de atributos | ↑ | Exploratorio | 0.074 (0.062–0.097) | 0.058 (0.048–0.079) | +0.012 | +0.016 [-0.001, +0.032] | 261.0 | 27 | 0.0859 | 0.0430 | 0.9593 | +0.38 | — | 0.5585 | consistente |
| CL-1 | Entity Coreference Rate | ↑ | Descriptivo / no usar | 0.997 (0.997–0.998) | 0.998 (0.998–0.998) | -0.001 | -0.001 [-0.001, -0.000] | 49.0 | 27 | 0.0004 | 0.9998 | 0.0002 | -0.74 | — | 0.9643 | consistente |
| CL-2 | Jericho: recall de cambios de estado narrados | ↑ | Exploratorio | 0.21 (0.03–0.30) | 0.22 (0.13–0.36) | -0.04 | -0.03 [-0.13, +0.08] | 144.5 | 25 | 0.6387 | 0.6855 | 0.3194 | -0.11 | — | 0.5110 | ⚠ signo distinto |
| CL-2 | Relojes: fracción reconocida en la narración | ↑ | Descriptivo / no usar | 1.00 (1.00–1.00) | 0.83 (0.67–1.00) | +0.00 | +0.17 [+0.00, +0.33] | 10.0 | 4 | 0.1250 | 0.0625 | 1.0000 | +1.00 | — | 0.0021 | consistente |
| CL-2 | PNJ inactivo mencionado (% de turnos) | ↓ | Exploratorio | 3.86 % (0.00 %–12.47 %) | 0.21 % (0.00 %–2.50 %) | +3.86 pp | +4.66 pp [+0.11, +8.86] | 225.0 | 24 | 0.0315 | 0.9854 | 0.0157 | +0.50 | — | 0.0781 | consistente |
| CL-2 | PNJ inactivo como sujeto (por 1 000 turnos) | ↓ | Exploratorio | 0.00 (0.00–0.00) | 0.00 (0.00–0.00) | +0.00 | +0.00 [-0.36, +0.00] | 6.0 | 6 | 0.4375 | 0.2188 | 0.8438 | -0.43 | — | <0.0001 | consistente |
| CL-2 | Jaccard con la escena anterior | · | Exploratorio | 0.193 (0.187–0.197) | 0.173 (0.169–0.177) | +0.019 | +0.019 [+0.017, +0.023] | 378.0 | 27 | <0.0001 | — | — | +1.00 | — | 0.2672 | consistente |
| CL-2 | Bucles: ciclos de ubicaciones | ↓ | Descriptivo / no usar | 1.00 (1.00–1.00) | 1.00 (1.00–1.00) | +0.00 | +0.00 [+0.00, +0.00] | 0.0 | 0 | 1.0000 | 1.0000 | 1.0000 | +0.00 | — | — | consistente |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1 401 = nunca) | ↑ | Exploratorio | 1139 (480–1401) | 891 (380–1401) | +0 | +58 [-220, +384] | 171.0 | 24 | 0.5646 | 0.2823 | 0.7272 | +0.14 | — | 0.4242 | consistente |

## 6. OE-6. Comparar la calidad de la narrativa emergente producida por la arquitectura multiagente frente a la monolítica

### Tabla 13. Comparación pareada G1 − G2, 27 parejas (H1f (calidad narrativa emergente))

| Indicador | Instrumento | ↕ | Uso | Mdn G1 (Q1–Q3) | Mdn G2 (Q1–Q3) | Mdn dif. | HL [IC 95 %] | W+ | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm | Shapiro dif. p | Lotes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QN-1 | TTR (diversidad léxica) | ↑ | Exploratorio | 0.679 (0.674–0.683) | 0.725 (0.719–0.732) | -0.044 | -0.045 [-0.049, -0.041] | 0.0 | 27 | <0.0001 | 1.0000 | <0.0001 | -1.00 | — | 0.3267 | consistente |
| QN-1 | Repetición de bigramas | ↓ | Exploratorio | 0.030 (0.026–0.031) | 0.018 (0.017–0.019) | +0.010 | +0.011 [+0.010, +0.012] | 378.0 | 27 | <0.0001 | 1.0000 | <0.0001 | +1.00 | — | 0.9195 | consistente |
| QN-1 | Legibilidad Fernández-Huerta | · | Descriptivo / no usar | 60.5 (59.5–62.1) | 61.8 (60.6–63.7) | -1.6 | -1.8 [-2.8, -0.7] | 76.0 | 27 | 0.0055 | — | — | -0.60 | — | 0.0483 | consistente |
| QN-1 | Densidad del grafo por lema | · | Descriptivo / no usar | 0.032 (0.024–0.038) | 0.021 (0.017–0.027) | +0.011 | +0.009 [+0.005, +0.015] | 328.0 | 27 | 0.0004 | — | — | +0.74 | — | 0.3728 | consistente |
| QN-2 | Usurpación mental o verbal del PJ (% de turnos) | ↓ | Confirmatorio condicionado | 0.00 % (0.00 %–0.07 %) | 0.37 % (0.26 %–0.58 %) | -0.37 pp | -0.37 pp [-0.47, -0.29] | 0.0 | 27 | <0.0001 | <0.0001 | 1.0000 | -1.00 | <0.0001 | 0.0011 | consistente |
| QN-2 | · decisión | ↓ | Confirmatorio condicionado | 0.00 % (0.00 %–0.00 %) | 0.15 % (0.07 %–0.29 %) | -0.15 pp | -0.15 pp [-0.21, -0.11] | 0.0 | 20 | <0.0001 | <0.0001 | 1.0000 | -1.00 | <0.0001 | 0.0409 | consistente |
| QN-2 | · pensamiento | ↓ | Confirmatorio condicionado | 0.00 % (0.00 %–0.00 %) | 0.00 % (0.00 %–0.00 %) | +0.00 pp | +0.00 pp [+0.00, +0.00] | 0.0 | 0 | 1.0000 | 1.0000 | 1.0000 | +0.00 | 1.0000 | — | consistente |
| QN-2 | · emoción | ↓ | Confirmatorio condicionado | 0.00 % (0.00 %–0.04 %) | 0.22 % (0.15 %–0.36 %) | -0.21 pp | -0.22 pp [-0.28, -0.16] | 0.0 | 25 | <0.0001 | <0.0001 | 1.0000 | -1.00 | <0.0001 | 0.0002 | consistente |
| QN-2 | · habla | ↓ | Confirmatorio condicionado | 0.00 % (0.00 %–0.00 %) | 0.00 % (0.00 %–0.00 %) | +0.00 pp | +0.00 pp [+0.00, +0.00] | 0.0 | 1 | 1.0000 | 0.5000 | 1.0000 | -1.00 | 1.0000 | <0.0001 | consistente |
| QN-2 | Acción física no declarada (experimental, % de turnos) | ↓ | Exploratorio | 0.68 % (0.59 %–0.94 %) | 7.23 % (6.25 %–8.43 %) | -6.30 pp | -6.27 pp [-6.94, -5.66] | 27.0 | 27 | <0.0001 | <0.0001 | 1.0000 | -0.86 | — | <0.0001 | consistente |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | ↓ | Exploratorio | 1.79 % (1.21 %–3.14 %) | 0.00 % (0.00 %–0.46 %) | +1.79 pp | +1.96 pp [+1.29, +3.43] | 369.0 | 27 | <0.0001 | 1.0000 | <0.0001 | +0.95 | — | <0.0001 | consistente |
| QN-1 | MTLD de la campaña (complementa al TTR; no depende de la longitud) | ↑ | Exploratorio | 109.0 (107.5–111.3) | 108.9 (104.9–110.7) | +0.2 | +0.2 [-1.4, +1.9] | 198.0 | 27 | 0.8408 | 0.4204 | 0.5888 | +0.05 | — | 0.0415 | ⚠ signo distinto |
| QN-1 | MATTR de la campaña, ventana de 50 (complementa al TTR) | ↑ | Exploratorio | 0.824 (0.823–0.827) | 0.828 (0.825–0.829) | -0.004 | -0.004 [-0.005, -0.002] | 51.5 | 25 | 0.0018 | 0.9991 | 0.0009 | -0.68 | — | 0.0196 | consistente |
| QN-1 | TTR a 100 palabras (control de longitud del TTR por turno) | ↑ | Exploratorio | 0.7409 (0.7393–0.7430) | 0.7393 (0.7352–0.7419) | +0.0023 | +0.0022 [+0.0004, +0.0039] | 285.0 | 27 | 0.0200 | 0.0100 | 0.9907 | +0.51 | — | 0.1947 | consistente |
| QN-1 | Repetición de bigramas a 100 palabras (control de longitud) | ↓ | Exploratorio | 0.0139 (0.0134–0.0146) | 0.0154 (0.0147–0.0161) | -0.0017 | -0.0014 [-0.0019, -0.0009] | 32.0 | 27 | <0.0001 | <0.0001 | 1.0000 | -0.83 | — | 0.0163 | consistente |
| QN-1 | Turnos con ≥ 100 palabras (fracción que entra al control) | · | Descriptivo / no usar | 0.999 (0.998–0.999) | 0.820 (0.760–0.855) | +0.176 | +0.182 [+0.154, +0.212] | 378.0 | 27 | <0.0001 | — | — | +1.00 | — | 0.1292 | consistente |
| QN-1 | Palabras por turno (mediana) | · | Descriptivo / no usar | 158 (152–162) | 116 (111–120) | +41 | +39 [+34, +44] | 378.0 | 27 | <0.0001 | — | — | +1.00 | — | 0.4970 | consistente |
| QN-1 | Szigriszt-Pazos (legibilidad; complementa a Fernández-Huerta) | · | Descriptivo / no usar | 56.3 (55.3–57.9) | 57.6 (56.3–59.6) | -1.6 | -1.8 [-2.8, -0.8] | 76.0 | 27 | 0.0055 | — | — | -0.60 | — | 0.0442 | consistente |
| QN-1 | Estabilidad de estilo: variación del TTR entre bloques | ↓ | Exploratorio | 0.0034 (0.0025–0.0045) | 0.0034 (0.0028–0.0043) | +0.0000 | -0.0001 [-0.0012, +0.0010] | 177.0 | 27 | 0.7857 | 0.3929 | 0.6162 | -0.06 | — | 0.8814 | ⚠ signo distinto |
| QN-1 | Estabilidad de estilo: variación de Fernández-Huerta entre bloques | ↓ | Exploratorio | 0.89 (0.64–2.00) | 1.43 (0.88–2.34) | -0.32 | -0.36 [-0.85, +0.02] | 113.0 | 27 | 0.0692 | 0.0346 | 0.9673 | -0.40 | — | 0.4193 | consistente |
| QN-1 | PNJ registrados hasta el turno 1 400 | · | Descriptivo / no usar | 4.0 (3.0–4.5) | 8.0 (6.0–10.0) | -4.0 | -4.0 [-6.3, -3.0] | 4.0 | 24 | <0.0001 | — | — | -0.97 | — | 0.0152 | consistente |
| QN-1 | Misiones registradas hasta el turno 1 400 | · | Descriptivo / no usar | 2.0 (2.0–2.0) | 2.0 (2.0–2.0) | +0.0 | +0.0 [+0.0, +0.0] | 0.0 | 1 | 1.0000 | — | — | -1.00 | — | <0.0001 | consistente |

Medidas descriptivas adicionales (fuera de la rúbrica): tiempo por turno y proxies de emergencia.

| Indicador | Instrumento | ↕ | Uso | Mdn G1 (Q1–Q3) | Mdn G2 (Q1–Q3) | Mdn dif. | HL [IC 95 %] | W+ | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm | Shapiro dif. p | Lotes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OP | Segundos por turno (mediana; proxy de latencia) | ↓ | Descriptivo / no usar | 29.8 (28.3–31.3) | 14.2 (12.7–14.6) | +16.5 | +16.1 [+15.0, +17.0] | 378.0 | 27 | <0.0001 | 1.0000 | <0.0001 | +1.00 | — | 0.2054 | consistente |

## 7. Resumen por hipótesis (dirección observada; no es la decisión de la docimasia)

Cuenta de instrumentos por resultado, con p bilateral < 0.05 (sin corregir) y la dirección respecto de ↕. Solo instrumentos con sentido de mejora definido.

| Hipótesis | Grupo de instrumentos | G1 mejor (p < 0.05) | G2 mejor (p < 0.05) | Sin diferencia significativa | Total |
|---|---|---|---|---|---|
| H1d (coherencia reactiva) | Confirmatorios y condicionados | 0 | 1 | 0 | 1 |
| H1d (coherencia reactiva) | Exploratorios | 3 | 0 | 3 | 6 |
| H1e (coherencia longitudinal) | Confirmatorios y condicionados | 0 | 0 | 0 | 0 |
| H1e (coherencia longitudinal) | Exploratorios | 1 | 1 | 4 | 6 |
| H1f (calidad narrativa emergente) | Confirmatorios y condicionados | 3 | 0 | 2 | 5 |
| H1f (calidad narrativa emergente) | Exploratorios | 3 | 4 | 3 | 10 |

Nota: un mismo constructo aparece con varios instrumentos correlacionados (por ejemplo, las cuatro categorías de `persona2` y su total); el conteo no equivale a hipótesis independientes.

## 8. Advertencias

- Los instrumentos miden proxies: no miden interés, creatividad ni voz del personaje. Los detectores con «precisión sin auditar» (persona2, PNJ inactivo) quedan condicionados a la auditoría posterior.
- Par01-17 y Par18-27 se generaron con versiones distintas del motor (sin y con avance de reloj, dados de combate y guardia de metamensajes); la columna *Lotes* marca los cambios de signo.
- G1 tiene un agente extra que crea entidades y un formato de salida distinto (normalizado aquí). Las diferencias por instrumento son entre sistemas completos, no una ablación.
- Par02 G2 tiene 1 668 turnos en la base; se recorta a 1 400. En Par01-06 (G2), 42 de 8 400 turnos difieren en el recuento de nombres no reconocidos entre el valor guardado y el recalculado; sin efecto material.
- Las medidas de repetición de frases, alfabetos, estabilidad de estilo, entidades registradas y tiempo por turno (`experimento/scripts/reporte_v2/medidas_cierre.py`) no tienen prueba de sensibilidad.
