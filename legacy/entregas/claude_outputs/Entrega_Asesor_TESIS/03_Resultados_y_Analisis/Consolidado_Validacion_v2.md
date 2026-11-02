# Informe consolidado G1 vs G2: 54 campañas (27 parejas), instrumentos sobre texto normalizado (v2)

Generado por `scripts/reporte_v2/consolidar.py` · commit `30b998f` · semilla 20260920 · B = 10000. **Descriptivo: no declara ganador.** Corrección posterior (post hoc) del instrumento, igual para los dos brazos; pendiente del visto bueno del asesor (ítem C1).

## Avance hacia resultados documentables en la tesis

**Resultados listos para plasmar (umbral): 14 de 15 ítems hechos (93 %)** `███████████████████░` · faltan 1 (0 míos, 1 tuyos, 0 del asesor)

Resultados plasmables y documentables = todos los ítems de la fase «resultados» hechos (bloques A, B y R).

- Metodología, docimasia y cierre de brechas (contigo y Claude Desktop): 0 de 9 hechos (0 %) · opcionales pendientes: 0
- Auditoría con humano y asesor (después de la redacción): 0 de 4 hechos (0 %) · opcionales pendientes: 1

| bloque | hechos | total | avance |
|---|---|---|---|
| A. Datos | 3 | 3 | 100 % |
| B. Cálculo de los instrumentos (27 parejas) | 10 | 10 | 100 % |
| R. Paquete de resultados para plasmar | 1 | 2 | 50 % |
| M. Metodología nueva (contigo y Claude Desktop) | 0 | 2 | 0 % |
| H. Docimasia (contigo y Claude Desktop) | 0 | 2 | 0 % |
| G. Análisis y cierre de brechas (después) | 0 | 5 | 0 % |
| P. Auditoría con humano y asesor (después) | 0 | 4 | 0 % |

| id | estado | quién | ítem |
|---|---|---|---|
| A1 | hecho | claude | 54 campañas de 27 parejas generadas (75 600 turnos): Par01-17 con el motor sin avance de reloj, Par18-27 con reloj determinista, dados de combate y guardia de metamensajes |
| A2 | hecho | claude | Integridad de las transcripciones verificada (Par07-27: 0 fallos duros) |
| A3 | hecho | claude | Formato de G1 normalizado y su efecto cuantificado |
| B1 | hecho | claude | Matriz de cobertura rúbrica ↔ instrumentos |
| B2 | hecho | claude | Sensibilidad por perturbación, línea base (24 instrumentos) |
| B3 | hecho | claude | Detector de 2.ª persona (persona2 v2b) construido, congelado y con equivalencia por persona gramatical |
| B4 | hecho | claude | Instrumentos nuevos CR-2a y CR-2b con matriz pre-especificada y evaluación (Par07-27) |
| B5 | hecho (54/54) | claude | Instrumentos por turno (numéricos) recalculados sobre texto normalizado en las 54 campañas |
| B6 | hecho (54/54) | claude | Booleanos (cr1, PNJ inactivo) recalculados en las 54 campañas |
| B7 | hecho (54/54) | claude | persona2 aplicado a las 54 campañas |
| B8 | hecho (54/54) | claude | Instrumentos de campaña (C/V, Jericho, ECR, relojes, bucles, grafo) en las 54 campañas |
| B9 | hecho (1/1) | claude | CR-2a y CR-2b (distribución por ventanas) recalculados para las 27 parejas |
| B10 | hecho (1/1) | claude | Medidas descriptivas adicionales (repetición de frases, alfabetos, deriva, estabilidad de estilo, entidades, tiempo por turno) |
| R1 | hecho | claude | Paquete de resultados con el formato del capítulo 6: descriptivos y normalidad de G2 (OE-1 a OE-3), comparaciones pareadas (OE-4 a OE-6), resumen por hipótesis y ficha de instrumentos (docs/resultados/) |
| R2 | **pendiente** | usuario | Revisión del paquete: que las tablas tengan las columnas y el orden que necesitan la metodología y la docimasia |
| M1 | **pendiente** | usuario | Documentar la metodología determinista (instrumentos, normalización, validación, limitaciones) usando la ficha de instrumentos |
| M2 | **pendiente** | usuario | Reconciliar el texto de Limitaciones (calidad narrativa mitigada con rúbrica en bloque piloto) con el giro totalmente determinista |
| H1 | **pendiente** | usuario | Decidir cómo se operacionaliza H1a-H1c (los instrumentos no tienen punto medio μ₀ = 4) |
| H2 | **pendiente** (falta R2, H1) | usuario | Docimasia de H1d, H1e y H1f y de la hipótesis general |
| G1 | **pendiente** (falta H2) | usuario | Rehacer el análisis de brechas con los resultados nuevos (el análisis previo salió de otros resultados; docs/cierre_brechas.md es un borrador) |
| G2 | **pendiente** | claude | Sección de límites declarados: interés y creatividad, voz del personaje, colisión de identidades, validez de constructo sin criterio humano |
| G3 | **pendiente** | claude | Referencias sin verificar comprobadas (DOI de Lowe 2017 y USR, coeficiente de Ochiai, umbral de Romano) |
| G4 | **pendiente** | claude | Defectos de contenido declarados (1 JSON crudo, ≈ 15 turnos con caracteres no latinos) |
| G5 | **pendiente** | usuario | Decisiones abiertas: relojes (limitación o arreglo), deriva del escenario, efecto de lote |
| P1 | **pendiente** | asesor | Conversación con el asesor: umbrales de A2, etiquetado solo como auditoría, declaración post hoc, QN-2 como cumplimiento de la regla de oro |
| P2 | **pendiente** | usuario | Etiquetado de la muestra de confirmación de persona2 (mínimo ≈ 300 de 515 turnos; ≈ 3.3 a 5.7 h) |
| P3 | **pendiente** | usuario | Segundo etiquetador sobre 102 turnos (acuerdo entre etiquetadores) |
| P4 | **pendiente** (falta P2, P3) | claude | Análisis de precisión y acuerdo de persona2 (scripts/analizar_persona2.py) |
| P5 | **pendiente** | usuario | Auditoría de precisión de cl2_pnj_inactivo_actua y cr1 (≈ 100 marcas cada uno, ≈ 2 h cada uno) *(opcional)* |

## Cómo leer las tablas

- Unidad de análisis: la **pareja** (27: Par01-27). Cada valor es la media de la campaña (turnos ≥ 2; `persona2` solo sobre turnos que no se usaron para construir el detector).
- **HL** = Hodges-Lehmann de la diferencia G1 − G2 entre parejas, con IC 95 % bootstrap sobre parejas; **r** = correlación rank-biserial pareada (−1 a +1; signo positivo = G1 mayor). **p Holm** = Wilcoxon exacto bilateral, corregido por Holm sobre TODA la tabla (referencia, no criterio de éxito).
- **Lotes**: HL por separado en Par01-17 (17 parejas, motor sin avance de reloj) y Par18-27 (10, con reloj determinista, dados de combate y guardia de metamensajes); si el signo cambia, la diferencia no es estable entre lotes (los lotes difieren, p. ej., en la frecuencia de combate).
- **Sentido**: ↓ menos es mejor, ↑ más es mejor, · neutro, según la definición del indicador en la rúbrica. No implica que el instrumento mida bien el constructo: mira la columna *Estado*.
- **A2**: celdas confirmatorias de la prueba de sensibilidad en que el instrumento respondió como se pre-especificó (k/n; «—» = sin prueba).
- Instrumentos de campaña (Papalampidi, Jericho, ECR, relojes, bucles, grafo): 54 de 54 campañas recalculadas; los que dependen de ellos usan solo las parejas completas (columna *Parejas*).

## Lista 1. Coherencia reactiva (CR-1 fluidez y sensatez; CR-2 arraigo contextual)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) [IC 95 %] | r [IC] | p Holm | Lotes (01-17 / 18-27) | Parejas | A2 | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool, 1 de cada 10 turnos) | ↑ | 0.999 | 0.999 | 9.64e-05 [-5.54e-05, 0.000282] | +0.28 [-0.15, +0.66] | 1 | 8.21e-05 / 0.000143 | 27 | 2/4 | techo cercano a 1: discrimina poco |
| CR-1 | cr1: pifia narrada como éxito (% de turnos) | ↓ | 0.00101 | 0.000927 | 0 [-0.000357, 0.000715] | +0.18 [-0.37, +0.68] | 1 | 0.000357 / 0 | 27 | 2/2 | baja precisión: ignora la negación («no logras») |
| CR-2 | CR-2a: respuesta a la acción específica (z) | ↑ | 2.69 | 2.82 | -0.133 [-0.254, -0.0266] | -0.47 [-0.80, -0.07] | 0.54 | -0.166 / -0.069 | 27 | 25/26 | instrumento nuevo, matriz a4bc-2 |
| CR-2 | CR-2a: solapamiento con la acción (crudo) | ↑ | 0.136 | 0.125 | 0.0107 [0.00639, 0.0148] | +0.84 [+0.58, +0.98] | 0.001 | 0.0109 / 0.0119 | 27 | 25/26 | instrumento nuevo, matriz a4bc-2 |
| CR-2 | CR-2b: anclaje al escenario (coseno, ventana de 8) | ↑ | 0.134 | 0.0763 | 0.0587 [0.0354, 0.0818] | +0.83 [+0.58, +0.97] | 0.0013 | 0.0727 / 0.0391 | 27 | 25/26 | no distingue deriva de evolución legítima del mundo |
| CR-2 | CR-2b: anclaje sin nombres propios (ventana de 8) | ↑ | 0.0745 | 0.0617 | 0.0126 [0.00524, 0.0204] | +0.62 [+0.26, +0.89] | 0.082 | 0.0121 / 0.0134 | 27 | 25/26 | casi plano: la señal la sostienen los nombres |
| CR-2 | Densidad del grafo de entidades | · | 0.241 | 0.279 | -0.0316 [-0.0661, -0.0065] | -0.51 [-0.83, -0.13] | 0.35 | -0.0453 / -0.0176 | 27 | 2/4 | insensible a otro escenario (P8) |
| CR-2 | Turnos con algún nombre no reconocido | ↓ | 0.0852 | 0.0675 | -0.00786 [-0.0304, 0.037] | -0.07 [-0.54, +0.37] | 1 | -0.0232 / 0.00679 ⚠ signo | 27 | 2/4 | v1 saturado en G1 por la línea mecánica |
| CR-2 | N.º de nombres no reconocidos por turno | ↓ | 0.141 | 0.114 | -0.0273 [-0.0643, 0.0411] | -0.18 [-0.63, +0.25] | 1 | -0.0465 / 3.47e-18 ⚠ signo | 27 | 4/4 | no detecta nombres inventados por sí solo |
| CR-1 | Turnos con caracteres de otro alfabeto o U+FFFD (%) | ↓ | 0.000873 | 0.00103 | -0.000357 [-0.000714, 0.000357] | -0.15 [-0.70, +0.37] | 1 | 0 / -0.000357 | 27 | — | medida simple; detecta fallos de codificación e idioma |

## Lista 2. Coherencia longitudinal (CL-1 personajes; CL-2 eventos y estado del mundo)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) [IC 95 %] | r [IC] | p Holm | Lotes (01-17 / 18-27) | Parejas | A2 | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CL-1 | Papalampidi C: coherencia de entidad | ↑ | 2.13 | 1.6 | 0.583 [0.166, 1] | +0.54 [+0.13, +0.86] | 0.34 | 0.584 / 0.5 | 27 | — | proxy de consistencia de personajes |
| CL-1 | Papalampidi V: consistencia de atributos | ↑ | 0.0814 | 0.0674 | 0.016 [-0.0015, 0.0315] | +0.38 [-0.05, +0.75] | 1 | 0.017 / 0.015 | 27 | — | proxy; no mide voz ni motivaciones |
| CL-1 | Entity Coreference Rate | ↑ | 0.997 | 0.998 | -0.000621 [-0.000898, -0.000305] | -0.74 [-0.95, -0.43] | 0.0099 | -0.000596 / -0.000642 | 27 | — | saturado (≈ 1) |
| CL-2 | Jericho: recall de cambios de estado narrados | ↑ | 0.216 | 0.237 | -0.0335 [-0.126, 0.0825] | -0.11 [-0.57, +0.34] | 1 | -0.0663 / 0.0085 ⚠ signo | 26 | — | A2 mecánico 80/80; frente al azar discrimina en npc.status (+21 a +25 pp) y casi nada en npc.affinity (+2 a +4.5 pp) |
| CL-2 | Relojes: fracción reconocida en la narración | ↑ | 0.967 | 0.8 | 0.167 [0, 0.333] | +1.00 [+1.00, +1.00] | 1 | — / 0.167 | 10 | — | A2 mecánico 23/23, pero reconoce lo mismo por azar (88 % real frente a 90 %): no discrimina |
| CL-2 | PNJ inactivo mencionado (% de turnos) | ↓ | 0.078 | 0.0229 | 0.0466 [0.00107, 0.0886] | +0.50 [+0.07, +0.83] | 0.54 | 0.0475 / 0.054 | 27 | 8/8 | mide mención, no acción; precisión sin auditar |
| CL-2 | PNJ inactivo como sujeto (por 1 000 turnos) | ↓ | 7.35 | 4.23 | 0 [-0.357, 0] | -0.43 [-1.00, +0.44] | 1 | 0 / 0 | 27 | 4/8 | solo ve nombres de una palabra |
| CL-2 | Jaccard con la escena anterior | · | 0.192 | 0.172 | 0.0195 [0.0172, 0.0226] | +1.00 [+1.00, +1.00] | 6.4e-07 | 0.0194 / 0.0195 | 27 | 2/2 | continuidad léxica, no de eventos |
| CL-2 | Bucles: ciclos de ubicaciones | ↓ | 1 | 1 | 0 [0, 0] | +0.00 [+0.00, +0.00] | 1 | 0 / 0 | 27 | 0/2 | A2: no reacciona a permutar turnos |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1 401 = nunca) | ↑ | 949 | 865 | 58 [-220, 384] | +0.14 [-0.34, +0.57] | 1 | 0 / 296 | 27 | — | mide mención, no acción; censurado en 1 401 |

## Lista 3. Calidad narrativa emergente (QN-1 interés y creatividad, solo proxies léxicos; QN-2 no usurpar la agencia)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) [IC 95 %] | r [IC] | p Holm | Lotes (01-17 / 18-27) | Parejas | A2 | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QN-1 | TTR (diversidad léxica) | ↑ | 0.679 | 0.723 | -0.0455 [-0.0488, -0.0407] | -1.00 [-1.00, -1.00] | 6.4e-07 | -0.0451 / -0.0441 | 27 | 4/4 | por turno: depende de la longitud (ver MTLD, MATTR y el control a 100 palabras) |
| QN-1 | Repetición de bigramas | ↓ | 0.0293 | 0.0185 | 0.0107 [0.00952, 0.0119] | +1.00 [+1.00, +1.00] | 6.4e-07 | 0.011 / 0.0103 | 27 | 2/2 | por turno: depende de la longitud (ver el control a 100 palabras) |
| QN-1 | Legibilidad Fernández-Huerta | · | 60.3 | 61.9 | -1.78 [-2.76, -0.702] | -0.60 [-0.93, -0.21] | 0.12 | -1.53 / -2.25 | 27 | — | complejidad, no calidad |
| QN-1 | Densidad del grafo por lema | · | 0.0323 | 0.0221 | 0.009 [0.00475, 0.015] | +0.74 [+0.43, +0.94] | 0.01 | 0.0085 / 0.0115 | 27 | 0/2 | insensible a otro escenario (P8) |
| QN-2 | Usurpación mental o verbal del PJ (% de turnos) | ↓ | 0.0024 | 0.0427 | -0.0366 [-0.0487, -0.0274] | -1.00 [-1.00, -1.00] | 6.4e-07 | -0.0435 / -0.031 | 27 | DIR 7/10 · INV 4/4 | v2b congelado, léxico cerrado; precisión sin auditar (C2-C4) |
| QN-2 |   · decisión | ↓ | 8.02e-05 | 0.0017 | -0.00156 [-0.00214, -0.00107] | -1.00 [-1.00, -1.00] | 5.9e-05 | -0.0017 / -0.00148 | 27 | DIR 7/10 · INV 4/4 | ídem |
| QN-2 |   · pensamiento | ↓ | 0.00155 | 0.0324 | -0.0263 [-0.0369, -0.0189] | -1.00 [-1.00, -1.00] | 6.4e-07 | -0.0286 / -0.0251 | 27 | DIR 7/10 · INV 4/4 | ídem |
| QN-2 |   · emoción | ↓ | 0.000235 | 0.00278 | -0.00228 [-0.00293, -0.0017] | -1.00 [-1.00, -1.00] | 2.1e-06 | -0.0029 / -0.00148 | 27 | DIR 7/10 · INV 4/4 | ídem |
| QN-2 |   · habla | ↓ | 0.000537 | 0.00669 | -0.0042 [-0.00681, -0.00244] | -0.98 [-1.00, -0.90] | 7.1e-06 | -0.00553 / -0.00255 | 27 | DIR 7/10 · INV 4/4 | ídem |
| QN-2 | Acción física no declarada (experimental, % de turnos) | ↓ | 0.0305 | 0.0721 | -0.0627 [-0.0694, -0.0566] | -0.86 [-1.00, -0.59] | 0.00056 | -0.062 / -0.063 | 27 | DIR 7/10 · INV 4/4 | experimental; equivalencia 70 % (A2) |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | ↓ | 0.0329 | 0.00315 | 0.0196 [0.0129, 0.0343] | +0.95 [+0.83, +1.00] | 1.5e-05 | 0.0182 / 0.0196 | 27 | — | medida simple, sin prueba A2; límite inferior de las fórmulas evasivas |
| QN-1 | MTLD de la campaña (complementa al TTR; no depende de la longitud) | ↑ | 109 | 108 | 0.205 [-1.35, 1.86] | +0.05 [-0.38, +0.47] | 1 | 0.495 / -0.545 ⚠ signo | 27 | — | medida nueva sobre texto concatenado; sin prueba A2 con datos reales |
| QN-1 | MATTR de la campaña, ventana de 50 (complementa al TTR) | ↑ | 0.824 | 0.827 | -0.0035 [-0.005, -0.0015] | -0.68 [-0.97, -0.31] | 0.044 | -0.0025 / -0.0045 | 27 | — | medida nueva sobre texto concatenado; sin prueba A2 con datos reales |
| QN-1 | TTR a 100 palabras (control de longitud del TTR por turno) | ↑ | 0.741 | 0.739 | 0.0022 [0.00042, 0.00389] | +0.51 [+0.12, +0.84] | 0.36 | 0.00273 / 0.00143 | 27 | — | mismas 100 primeras palabras de cada turno con >= 100; sin prueba A2 |
| QN-1 | Repetición de bigramas a 100 palabras (control de longitud) | ↓ | 0.014 | 0.0154 | -0.00138 [-0.00186, -0.000918] | -0.83 [-0.99, -0.57] | 0.0011 | -0.00116 / -0.00178 | 27 | — | mismas 100 primeras palabras de cada turno con >= 100; sin prueba A2 |
| QN-1 | Turnos con ≥ 100 palabras (fracción que entra al control) | · | 0.997 | 0.817 | 0.182 [0.154, 0.212] | +1.00 [+1.00, +1.00] | 6.4e-07 | 0.174 / 0.182 | 27 | — | descriptivo: el control excluye más turnos de G2 (más cortos) |
| QN-1 | Palabras por turno (mediana) | · | 158 | 119 | 39.4 [34.2, 43.9] | +1.00 [+1.00, +1.00] | 6.4e-07 | 40 / 38.8 | 27 | — | descriptivo: el TTR y la repetición de bigramas por turno dependen de la longitud del turno |
| QN-1 | Szigriszt-Pazos (legibilidad; complementa a Fernández-Huerta) | · | 56.1 | 57.7 | -1.85 [-2.85, -0.763] | -0.60 [-0.93, -0.21] | 0.12 | -1.57 / -2.28 | 27 | — | calculado del texto, no está en el motor; sin prueba A2; sin sentido de mejora |
| QN-1 | Estabilidad de estilo: variación del TTR entre bloques | ↓ | 0.00379 | 0.00384 | -0.000148 [-0.00123, 0.000954] | -0.06 [-0.50, +0.37] | 1 | -0.000595 / 0.000911 ⚠ signo | 27 | — | medida simple, sin prueba A2 |
| QN-1 | Estabilidad de estilo: variación de Fernández-Huerta entre bloques | ↓ | 1.26 | 1.65 | -0.359 [-0.847, 0.0229] | -0.40 [-0.79, +0.02] | 1 | -0.353 / -0.347 | 27 | — | medida simple, sin prueba A2 |
| QN-1 | PNJ registrados hasta el turno 1 400 | · | 4.04 | 8.93 | -4 [-6.26, -3] | -0.97 [-1.00, -0.88] | 2.7e-05 | -5 / -3 | 27 | — | proxy de emergencia; G1 tiene un agente extra que también crea entidades |
| QN-1 | Misiones registradas hasta el turno 1 400 | · | 2 | 2.04 | 0 [0, 0] | -1.00 [-1.00, +0.00] | 1 | 0 / 0 | 27 | — | casi constante (2 por campaña, sembradas): el r no es informativo |

## Medidas operativas (fuera de la rúbrica)

| Indic. | Instrumento | ↕ | G1 | G2 | HL (G1−G2) [IC 95 %] | r [IC] | p Holm | Lotes (01-17 / 18-27) | Parejas | A2 | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OP | Segundos por turno (mediana; proxy de latencia) | ↓ | 29.9 | 14 | 16.1 [15, 17] | +1.00 [+1.00, +1.00] | 6.4e-07 | 15.8 / 16.6 | 27 | — | incluye al jugador LLM y la extracción; corridas concurrentes |

## Trazabilidad

- Detector `persona2` v2b congelado: hashes en `validacion/persona2_congelado.sha256` (verificados antes de correr `recalcular_persona2.py`). Equivalencia por persona gramatical: `docs/reportes/persona2_equivalencia.md`.
- Instrumentos nuevos CR-2a/CR-2b: matriz a4bc-2, SHA-256 `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744`; `docs/reportes/sensibilidad_a4bc.md`.
- Línea base de sensibilidad: `docs/reportes/sensibilidad_baseline.md`. Numéricos: `docs/reportes/reporte_v2_formato_normalizado.md`. Booleanos: `docs/reportes/reporte_v2_booleanos.md`.
- Datos por campaña: `datos_v2/` (numéricos), `datos_v2/booleanos/`, `datos_v2/persona2/`, `datos_v2/campana/`. Solo SELECT; sin LLM.
