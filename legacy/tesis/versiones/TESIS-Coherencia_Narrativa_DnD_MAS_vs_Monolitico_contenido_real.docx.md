6. # Presentación de resultados {#presentación-de-resultados}

   Para el capítulo de resultados, DM-IA opera bajo dos arquitecturas comparables: G1 (Sistema Multiagente, con agentes especializados —Árbitro, Actor, Mundo y Narrador— sobre una base de memoria externa estructurada con SQLite, ChromaDB y NetworkX) y G2 (Sistema Monolítico con LightRAG). Conforme al pivote metodológico documentado en el Capítulo 5 (decisión del asesor del 14 de setiembre de 2026), los seis indicadores de la Rúbrica D\&D-IA (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2) ya no se miden mediante un puntaje Likert asignado por un panel de jueces, sino mediante una batería de instrumentos deterministas aplicada sobre el texto normalizado del corpus completo.

   Los resultados de este capítulo corresponden al corpus final: N \= 27 pares de campañas (54 campañas, 75,600 turnos), generadas con el mismo modelo de lenguaje base y el mismo Agente Jugador Autónomo en ambos brazos, medidas mediante reporte\_validacion.py y medidas\_cierre.py (ficha completa de instrumentos en el Anexo 1). Como se documentó en el Capítulo 5.8, los objetivos OE-1 a OE-3 —que preguntan por el nivel que alcanza el sistema monolítico (G2) en cada dimensión, sin exigir una comparación— se resuelven mediante estadística descriptiva (mediana, cuartiles, rango intercuartílico, media, desviación estándar y prueba de normalidad de Shapiro-Wilk sobre las 27 campañas G2), reportando los mismos estadísticos de G1 únicamente como referencia de contexto, sin que ello constituya en esta etapa un contraste de hipótesis. El panel de cinco Dungeon Masters expertos que evaluó tres campañas G2 bajo escala Likert (n \= 15 observaciones) durante la fase piloto del proyecto se conserva como Anexo 2 (evidencia histórica), dado que varios de sus hallazgos cualitativos —en particular, la identificación temprana de colisiones de identidad de personajes no jugadores— anticiparon correctamente hallazgos que el corpus determinista de 27 pares confirma a continuación.

   Cada instrumento reportado se clasifica, según la ficha de instrumentos (Capítulo 5.6), en confirmatorio, confirmatorio condicionado, exploratorio o descriptivo/no usar, de acuerdo con su desempeño en una prueba de sensibilidad por perturbación pre-especificada; los instrumentos confirmatorios son los que sostienen la docimasia de las hipótesis comparativas H1d-H1f en los objetivos OE-4 a OE-6, que se presentan a continuación junto con OE-1 a OE-3.

   1. ## Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico. {#evaluar-la-coherencia-reactiva-de-las-respuestas-inmediatas-generadas-por-el-sistema-monolítico.}

      1. ### Definición del objetivo {#definición-del-objetivo}

      OE-1 busca establecer el nivel de coherencia reactiva que el sistema monolítico-RAG (G2) alcanza ante las interacciones del jugador, operacionalizado mediante los instrumentos deterministas de CR-1 (fluidez y corrección de la respuesta inmediata) y CR-2 (arraigo contextual a la acción del jugador), aplicados sobre las 27 campañas G2 del corpus final.

      2. ### Resultados {#resultados}

#### ***Tabla 3\. Estadísticos descriptivos — Coherencia reactiva, sistema monolítico (G2), n \= 27 campañas.*** {#tabla-3.-estadísticos-descriptivos-—-coherencia-reactiva,-sistema-monolítico-(g2),-n-=-27-campañas.}

| Indicador | Instrumento | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk p | ¿Normal? |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CR-1 | Gramaticalidad (LanguageTool) | 0.9992 | 0.9991 | 0.9994 | 0.0003 | 0.9984 | 0.9998 | 0.9992 (0.0004) | 0.3445 | sí |
| CR-1 | Pifia narrada como éxito (% de turnos) | 0.07 % | 0.00 % | 0.14 % | 0.14 % | 0.00 % | 0.50 % | 0.09 % (0.11 %) | \<0.0001 | no |
| CR-1 | Caracteres de otro alfabeto o U+FFFD (%) | 0.07 % | 0.07 % | 0.14 % | 0.07 % | 0.00 % | 0.29 % | 0.10 % (0.08 %) | 0.0045 | no |
| CR-2 | Respuesta a la acción específica (z), confirmatorio | 2.81 | 2.61 | 3.01 | 0.40 | 2.45 | 3.51 | 2.82 (0.27) | 0.2746 | sí |
| CR-2 | Solapamiento con la acción (crudo) | 0.125 | 0.114 | 0.134 | 0.020 | 0.104 | 0.163 | 0.125 (0.014) | 0.2788 | sí |
| CR-2 | Anclaje al escenario (coseno, ventana de 8\) | 0.072 | 0.061 | 0.082 | 0.021 | 0.047 | 0.145 | 0.076 (0.024) | 0.0130 | no |
| CR-2 | Turnos con algún nombre no reconocido | 5.08 % | 3.40 % | 7.72 % | 4.32 % | 2.43 % | 24.23 % | 6.75 % (5.08 %) | \<0.0001 | no |

*Nota. Elaboración propia a partir de reporte\_validacion.py/medidas\_cierre.py sobre las 27 campañas G2 del corpus final (2026-09-21). Tabla reducida a los instrumentos de mayor relevancia interpretativa; la ficha completa (Capítulo 5.6) reporta además los instrumentos descriptivos/no usar.*

3. ### Análisis descriptivo {#análisis-descriptivo}

   El único instrumento de CR-2 validado como confirmatorio mediante la prueba de sensibilidad por perturbación —la respuesta a la acción específica normalizada en z— sitúa a G2 en 2.82 de media, con dispersión moderada (RIQ \= 0.40) y sin evidencia de asimetría marcada (Shapiro-Wilk no rechaza normalidad, p \= 0.27). La gramaticalidad se mantiene prácticamente en el techo de la escala (0.9992 de mediana), consistente con el hallazgo cualitativo del panel piloto de que la fluidez local no era, en general, un problema del sistema monolítico. El indicador exploratorio de turnos con algún nombre no reconocido —proxy imperfecto de arraigo, que no distingue nombres inventados de personajes no jugadores legítimos nuevos— muestra una mediana de 5.08 % con una cola larga hacia arriba (máximo 24.23 %), y se reporta como exploratorio, no como evidencia confirmatoria, precisamente por esa limitación de precisión.

   4. ### Discusión de resultados {#discusión-de-resultados}

      A diferencia de la evaluación piloto por panel (n \= 15, tres campañas), que había encontrado a CR-2 significativamente por debajo del punto medio de la escala Likert, el instrumento confirmatorio del corpus completo no tiene un punto de referencia externo contra el cual declarar a G2 “deficiente” o “aceptable” en términos absolutos: su valor solo adquiere sentido interpretativo pleno frente a G1, contraste que corresponde a OE-4 (H1d). Lo que sí permite establecer el análisis descriptivo de las 27 campañas es que el arraigo contextual de G2, medido por el único instrumento confirmatorio disponible, es una magnitud estable y de baja dispersión relativa (coeficiente de variación ≈ 10 %) a lo largo de escenarios, tonos narrativos y personajes jugadores distintos — es decir, el comportamiento de G2 en esta dimensión es consistente, no errático, con independencia de si resulta o no comparativamente superior a G1.

      5. ### Conclusiones {#conclusiones}

      Sobre las 27 campañas del corpus final, el sistema monolítico-RAG (G2) exhibe una coherencia reactiva estable: gramaticalidad cercana al techo de la escala, y un arraigo contextual (CR-2a en z) de magnitud consistente entre campañas (Mdn \= 2.81, RIQ \= 0.40). No se emite un juicio de suficiencia o deficiencia en términos absolutos para este objetivo, dado que los instrumentos deterministas carecen de un punto medio teórico no arbitrario contra el cual contrastarse (Capítulo 5.8); dicho juicio comparativo se resuelve en OE-4 mediante el contraste pareado G1-G2.

      6. ### Recomendaciones {#recomendaciones}

      Se recomienda auditar manualmente una muestra de los turnos marcados por el indicador exploratorio de “nombre no reconocido” para separar nombres efectivamente inventados de personajes no jugadores legítimos introducidos por el propio sistema, antes de usar esa cifra como evidencia sustantiva en la discusión general de la tesis.

   2. ## Evaluar la coherencia longitudinal a lo largo de las campañas generadas por el sistema monolítico. {#evaluar-la-coherencia-longitudinal-a-lo-largo-de-las-campañas-generadas-por-el-sistema-monolítico.}

      1. ### Definición del objetivo {#definición-del-objetivo-1}

      OE-2 evalúa la capacidad del sistema monolítico-RAG (G2) para mantener la integridad fáctica y la consistencia narrativa a lo largo de campañas de 1,400 turnos, mediante los instrumentos deterministas de CL-1 (consistencia de personajes: centralidad y consistencia de atributos según Papalampidi et al., y tasa de correferencia de entidades según Roemmele y Gordon) y CL-2 (consistencia de eventos y estado del mundo: recall de cambios de estado según Ammanabrolu et al., mención de personajes no jugadores inactivos, y ciclos de ubicación).

      2. ### Resultados {#resultados-1}

#### ***Tabla 5\. Estadísticos descriptivos — Coherencia longitudinal, sistema monolítico (G2), n \= 27 campañas.*** {#tabla-5.-estadísticos-descriptivos-—-coherencia-longitudinal,-sistema-monolítico-(g2),-n-=-27-campañas.}

| Indicador | Instrumento | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk p | ¿Normal? |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CL-1 | Papalampidi C: coherencia de entidad | 1.67 | 0.92 | 2.29 | 1.38 | 0.00 | 3.33 | 1.60 (0.88) | 0.6394 | sí |
| CL-1 | Papalampidi V: consistencia de atributos | 0.058 | 0.048 | 0.079 | 0.031 | 0.030 | 0.151 | 0.067 (0.032) | 0.0016 | no |
| CL-1 | Entity Coreference Rate | 0.998 | 0.998 | 0.998 | 0.001 | 0.997 | 0.999 | 0.998 (0.000) | 0.2287 | sí |
| CL-2 | Jericho: recall de cambios de estado narrados | 0.22 | 0.13 | 0.36 | 0.23 | 0.00 | 0.50 | 0.24 (0.16) | 0.1312 | sí |
| CL-2 | PNJ inactivo mencionado (% de turnos) | 0.21 % | 0.00 % | 2.50 % | 2.50 % | 0.00 % | 15.94 % | 2.29 % (3.93 %) | \<0.0001 | no |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1401 \= nunca) | 891 | 380 | 1401 | 1021 | 83 | 1401 | 865 (520) | 0.0005 | no |
| CL-2 | Bucles: ciclos de ubicaciones (fracción de campañas con ciclo) | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 (0.00) | — | — |

*Nota. Elaboración propia a partir de reporte\_validacion.py sobre las 27 campañas G2. Papalampidi C y V son proxies de identidad y de consistencia de atributos, sin prueba de sensibilidad A2 propia (solo controles); Entity Coreference Rate está saturado cerca de 1 en todo el corpus y se clasifica como descriptivo/no usar (Capítulo 5.6).*

3. ### Análisis descriptivo {#análisis-descriptivo-1}

   La centralidad de entidad de Papalampidi (Ci) sitúa a G2 en una mediana de 1.67 sobre un máximo posible de 4.5, con un mínimo de 0.00 — es decir, en al menos una campaña del corpus, ninguna de las entidades sembradas más mencionadas sobrevivió como referente rastreable entre su primera y su última mención. El recall de Jericho-QA (cambios de estado del mundo efectivamente narrados) es bajo en términos absolutos (Mdn \= 0.22), aunque este instrumento carece todavía de prueba de sensibilidad A2 y su n de deltas evaluables varía considerablemente entre campañas, por lo que se reporta como exploratorio. El indicador de PNJ inactivo mencionado tiene una mediana baja (0.21 %) pero una cola derecha marcada (máximo 15.94 %), y la variable censurada “turno de la primera mención de un PNJ no vivo” tiene una mediana de 891 sobre 1,400 posibles, con una proporción notable de campañas donde el valor censurado (1,401 \= nunca ocurre) domina el cuartil superior.

   4. ### Discusión de resultados {#discusión-de-resultados-1}

      La dimensión longitudinal es, de los tres objetivos de este avance, la que exhibe mayor heterogeneidad entre campañas (coeficientes de variación más altos y desviaciones marcadas de la normalidad en la mayoría de sus instrumentos), lo cual es consistente con la naturaleza acumulativa del fenómeno que mide: los defectos de consistencia de personajes y de estado del mundo se acumulan de forma no lineal a lo largo de 1,400 turnos, y su severidad depende en parte de decisiones narrativas específicas de cada campaña. Como en OE-1, ninguno de estos instrumentos tiene un punto de referencia externo no arbitrario que permita declarar a G2 “deficiente” o “aceptable” de forma absoluta; el contraste inferencial que decide si esta dimensión favorece a una arquitectura sobre la otra corresponde a OE-5 (H1e).

      5. ### Conclusiones {#conclusiones-1}

      Sobre las 27 campañas del corpus final, la coherencia longitudinal del sistema monolítico-RAG (G2) es la dimensión de mayor variabilidad entre campañas de este avance de resultados, con evidencia descriptiva de al menos un caso de pérdida total de centralidad de entidad (Papalampidi C \= 0.00) y una mediana de recall de cambios de estado narrados de 0.22. Como en OE-1, no se emite un juicio de suficiencia en términos absolutos; dicho juicio se resuelve en OE-5.

      6. ### Recomendaciones {#recomendaciones-1}

      Se recomienda investigar la causa exacta del caso de Papalampidi C \= 0.00 mediante lectura directa de la transcripción correspondiente, y completar la prueba de sensibilidad A2 para el recall de Jericho-QA antes de promoverlo de exploratorio a confirmatorio.

   3. ## Evaluar la calidad de la coherencia narrativa emergente en las campañas generadas por el sistema monolítico {#evaluar-la-calidad-de-la-coherencia-narrativa-emergente-en-las-campañas-generadas-por-el-sistema-monolítico}

      1. ### Definición del objetivo {#definición-del-objetivo-2}

      OE-3 evalúa la capacidad del sistema monolítico-RAG (G2) para generar narrativa de calidad creativa y para respetar la agencia del jugador, mediante los instrumentos deterministas de QN-1 (diversidad léxica vía TTR, MTLD y MATTR; legibilidad vía Fernández-Huerta y Szigriszt-Pazos; repetición de bigramas y de frases) y QN-2 (usurpación mental, verbal o de decisión del personaje jugador, instrumento persona2, confirmatorio condicionado a auditoría de precisión).

      2. ### Resultados {#resultados-2}

#### ***Tabla 7\. Estadísticos descriptivos — Calidad narrativa emergente, sistema monolítico (G2), n \= 27 campañas.*** {#tabla-7.-estadísticos-descriptivos-—-calidad-narrativa-emergente,-sistema-monolítico-(g2),-n-=-27-campañas.}

| Indicador | Instrumento | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk p | ¿Normal? |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| QN-1 | TTR (diversidad léxica, por turno) | 0.725 | 0.719 | 0.732 | 0.013 | 0.701 | 0.737 | 0.723 (0.009) | 0.0432 | no |
| QN-1 | MTLD de la campaña (no depende de la longitud) | 108.9 | 104.9 | 110.7 | 5.9 | 101.7 | 114.2 | 108.5 (3.8) | 0.1985 | sí |
| QN-1 | MATTR de la campaña, ventana de 50 | 0.828 | 0.825 | 0.829 | 0.005 | 0.820 | 0.833 | 0.827 (0.004) | 0.2126 | sí |
| QN-1 | Legibilidad Fernández-Huerta | 61.8 | 60.6 | 63.7 | 3.1 | 55.1 | 66.1 | 61.9 (2.5) | 0.6640 | sí |
| QN-1 | Szigriszt-Pazos (banda INFLESZ: normal) | 57.6 | 56.3 | 59.6 | 3.2 | 50.8 | 62.0 | 57.7 (2.5) | 0.6614 | sí |
| QN-1 | Repetición de bigramas (por turno) | 0.018 | 0.017 | 0.019 | 0.002 | 0.016 | 0.022 | 0.018 (0.002) | 0.2580 | sí |
| QN-1 | Frases idénticas repetidas ≥ 3 veces (% de turnos) | 0.00 % | 0.00 % | 0.46 % | 0.46 % | 0.00 % | 1.79 % | 0.31 % (0.44 %) | \<0.0001 | no |
| QN-2 | Usurpación mental/verbal/de decisión del PJ (% de turnos), confirmatorio condicionado | 3.47 % | 2.10 % | 5.50 % | 3.40 % | 1.36 % | 11.40 % | 4.27 % (2.76 %) | 0.0017 | no |

*Nota. Elaboración propia a partir del paquete de resultados reporte\_v2 sobre las 27 campañas G2. MTLD, MATTR y Szigriszt-Pazos complementan a TTR y Fernández-Huerta sin reemplazarlos (Capítulo 5.6); persona2 (usurpación) es confirmatorio condicionado a la auditoría de precisión pendiente, no confirmatorio pleno.*

3. ### Análisis descriptivo {#análisis-descriptivo-2}

   La diversidad léxica de G2 medida sin controlar por longitud de turno (TTR \= 0.725 de mediana) no es comparable en sentido absoluto con la de otros sistemas sin ese control, dado que TTR decrece mecánicamente con la longitud del texto; MTLD (108.9) y MATTR (0.828), que no dependen de la longitud, ofrecen una lectura más estable de la misma propiedad. La legibilidad se ubica en la banda “normal” tanto por Fernández-Huerta (61.9 de media) como por Szigriszt-Pazos (57.7 de media, banda INFLESZ “normal”), dos fórmulas de la misma familia de regresión lineal sobre sílabas y longitud de frase, por lo que su coincidencia no debe leerse como confirmación independiente. La usurpación de agencia del jugador (persona2) tiene una mediana de 3.47 % de los turnos, instrumento condicionado a una auditoría de precisión aún pendiente antes de tratarse como evidencia confirmatoria plena.

   4. ### Discusión de resultados {#discusión-de-resultados-2}

      A diferencia de CR-1/CR-2 (OE-1) y CL-1/CL-2 (OE-2), varios instrumentos de QN-1 (legibilidad, densidad de grafo) no tienen siquiera un sentido de mejora definido — una legibilidad “más alta” no es necesariamente “mejor” narrativa—, por lo que se reportan explícitamente como descriptivos y no como evidencia de calidad en ninguna dirección. El instrumento de usurpación de agencia (persona2) es, de los reportados aquí, el más cercano a admitir una lectura de calidad directa (una tasa más baja de usurpación respeta mejor la agencia del jugador, principio central de QN-2 en la Rúbrica D\&D-IA), pero su condición de “confirmatorio condicionado” exige completar la auditoría de precisión antes de usarlo como evidencia decisiva.

      5. ### Conclusiones {#conclusiones-2}

      Sobre las 27 campañas del corpus final, el sistema monolítico-RAG (G2) mantiene una diversidad léxica estable una vez controlada la longitud del turno (MTLD Mdn \= 108.9, MATTR Mdn \= 0.828), una legibilidad en banda “normal” por dos fórmulas convergentes pero no independientes, y una tasa de usurpación de agencia del jugador de 3.47 % de mediana, aún pendiente de auditoría de precisión. Como en OE-1 y OE-2, el juicio comparativo sobre si estos valores favorecen a una arquitectura sobre la otra se resuelve en OE-6.

      6. ### Recomendaciones {#recomendaciones-2}

      Se recomienda priorizar la auditoría de precisión de persona2 antes de redactar la docimasia de H1f, dado que es el único instrumento de QN-2 con potencial confirmatorio pleno.


   4. ## Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura {#comparar-la-coherencia-reactiva-de-las-respuestas-inmediatas-generadas-por-ambos-tipos-de-arquitectura}

      1. ### Definición del objetivo {#definición-del-objetivo-3}

      OE-4 contrasta la coherencia reactiva de G1 frente a G2 mediante el diseño de medidas repetidas con pares emparejados (Gpar, Capítulo 5.4) sobre los 27 pares del corpus final, comparando la diferencia G1−G2 dentro de cada par con la prueba de Rangos con Signo de Wilcoxon exacta (Capítulo 5.8). Este objetivo, junto con OE-5 y OE-6, es el que efectivamente decide las hipótesis específicas comparativas (H1d, H1e, H1f) y, por extensión, informa la hipótesis general de la investigación.

      2. ### Resultados {#resultados-3}

#### ***Tabla 9\. Comparación pareada G1−G2, 27 parejas — Coherencia reactiva (H1d).*** {#tabla-9.-comparación-pareada-g1−g2,-27-parejas-—-coherencia-reactiva-(h1d).}

| Indicador | Instrumento | Uso | Mdn G1 | Mdn G2 | Mdn dif. | HL \[IC 95 %\] | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CR-1 | Gramaticalidad | Descriptivo/no usar | 0.9994 | 0.9992 | \+0.0001 | \+0.0001 \[-0.0001, \+0.0003\] | 27 | 0.2176 | 0.1088 | 0.8935 | \+0.28 | — |
| CR-2 | Respuesta a la acción específica (z) | Confirmatorio | 2.70 | 2.81 | \-0.18 | \-0.13 \[-0.25, \-0.03\] | 27 | 0.0319 | 0.9850 | 0.0159 | \-0.47 | 0.0319 |
| CR-2 | Solapamiento con la acción (crudo) | Exploratorio | 0.135 | 0.125 | \+0.009 | \+0.011 \[+0.006, \+0.015\] | 27 | \<0.0001 | \<0.0001 | 1.0000 | \+0.84 | — |
| CR-2 | Anclaje al escenario (coseno) | Exploratorio | 0.143 | 0.072 | \+0.060 | \+0.059 \[+0.035, \+0.082\] | 27 | \<0.0001 | \<0.0001 | 1.0000 | \+0.83 | — |
| CR-2 | Anclaje sin nombres propios | Exploratorio | 0.073 | 0.063 | \+0.012 | \+0.013 \[+0.005, \+0.020\] | 27 | 0.0036 | 0.0018 | 0.9984 | \+0.62 | — |
| CR-2 | Turnos con nombre no reconocido | Exploratorio | 3.00 % | 5.08 % | \-2.00 pp | \-0.79 pp \[-3.04, \+3.70\] | 27 | 0.7676 | 0.3838 | 0.6252 | \-0.07 | — |

*Nota. Elaboración propia a partir de resultados\_tesis.md (Tabla 9, 2026-09-21). Tabla reducida a los instrumentos de mayor relevancia interpretativa.*

3. ### Análisis descriptivo {#análisis-descriptivo-3}

   El único instrumento validado como confirmatorio por la prueba de sensibilidad A2, la respuesta a la acción específica normalizada en z, muestra una diferencia mediana de \-0.18 a favor de G2 (HL \-0.13, IC 95 % \[-0.25, \-0.03\]), estadísticamente significativa (p bilateral \= 0.0319; p unilateral «G2 mejor» \= 0.0159) con un tamaño de efecto moderado (r \= \-0.47). Sin embargo, las tres versiones exploratorias del mismo constructo —arraigo contextual, medido sin normalizar— muestran la dirección opuesta con tamaños de efecto grandes: solapamiento crudo (r \= \+0.84), anclaje al escenario por coseno (r \= \+0.83) y anclaje sin nombres propios (r \= \+0.62), las tres a favor de G1 con p \< 0.01. Gramaticalidad no muestra diferencia significativa (p \= 0.2176).

   4. ### Discusión de resultados {#discusión-de-resultados-3}

      La coherencia reactiva es, de los tres objetivos comparativos, el único donde la evidencia confirmatoria y la exploratoria apuntan en direcciones opuestas dentro del mismo constructo, y no simplemente donde la evidencia confirmatoria es “delgada”: tres mediciones distintas de arraigo contextual arrojan tres conclusiones distintas según se normalice o no el puntaje. Esto sugiere un límite real de validez de constructo antes que una superioridad clara de cualquiera de las dos arquitecturas: la normalización en z que aplica el instrumento confirmatorio controla por variables (longitud de turno, vocabulario disponible) que las versiones crudas no controlan, y no está establecido cuál de las dos lecturas —normalizada o cruda— captura mejor el “arraigo contextual a la acción del jugador” tal como lo define la Rúbrica D\&D-IA original. Se documenta esta discordancia explícitamente, en lugar de reportar solamente el resultado confirmatorio como si fuera la historia completa de la dimensión.

      5. ### Docimasia {#docimasia}

      H1d: Los sistemas multiagente generan respuestas con mayor coherencia reactiva que los sistemas monolíticos.

      H0d: No existe diferencia significativa en el nivel de Coherencia Reactiva entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

      Con el único instrumento confirmatorio disponible (CR-2a en z), se rechaza H0d (p \= 0.0319 \< α \= 0.05), pero la dirección del efecto favorece a G2, no a G1: H1d, tal como está formulada, no se sostiene con la evidencia confirmatoria de este corpus. Dado que las versiones exploratorias del mismo indicador muestran la dirección contraria con tamaños de efecto grandes, la conclusión metodológicamente correcta no es “G2 es superior a G1 en coherencia reactiva”, sino que la dimensión de arraigo contextual, tal como se opera actualmente, no admite una lectura unívoca a favor de ninguna arquitectura, y que su resolución depende de una decisión de validez de constructo que excede lo que un único corpus puede zanjar.

      6. ### Conclusiones {#conclusiones-3}

      La coherencia reactiva es la única de las tres dimensiones comparativas donde la evidencia confirmatoria contradice a la exploratoria dentro del mismo constructo. El instrumento confirmatorio (CR-2a en z) favorece a G2 (p \= 0.0319, r \= \-0.47); las tres versiones exploratorias de arraigo contextual favorecen a G1 con efectos grandes (r entre \+0.62 y \+0.84). H1d no se sostiene con la evidencia confirmatoria disponible.

      7. ### Recomendaciones {#recomendaciones-3}

      Se recomienda una revisión de validez de constructo de CR-2a antes de la sustentación, decidiendo explícitamente si la normalización en z o la medición cruda captura mejor el arraigo contextual definido por la Rúbrica D\&D-IA original, y documentando el criterio en la ficha de instrumentos.

   5. ## Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas {#comparar-la-coherencia-longitudinal-a-lo-largo-de-las-campañas-generadas-por-ambos-sistemas}

      1. ### Definición del objetivo {#definición-del-objetivo-4}

      OE-5 contrasta la coherencia longitudinal de G1 frente a G2 mediante el mismo diseño Gpar y la misma prueba de Wilcoxon pareada que OE-4, sobre los indicadores de CL-1 (consistencia de personajes) y CL-2 (consistencia de eventos y estado del mundo).

      2. ### Resultados {#resultados-4}

#### ***Tabla 11\. Comparación pareada G1−G2, 27 parejas — Coherencia longitudinal (H1e).*** {#tabla-11.-comparación-pareada-g1−g2,-27-parejas-—-coherencia-longitudinal-(h1e).}

| Indicador | Instrumento | Uso | Mdn G1 | Mdn G2 | Mdn dif. | HL \[IC 95 %\] | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CL-1 | Papalampidi C: coherencia de entidad | Exploratorio | 2.17 | 1.67 | \+0.50 | \+0.58 \[+0.17, \+1.00\] | 25 | 0.0170 | 0.0085 | 0.9919 | \+0.54 |
| CL-1 | Papalampidi V: consistencia de atributos | Exploratorio | 0.074 | 0.058 | \+0.012 | \+0.016 \[-0.001, \+0.032\] | 27 | 0.0859 | 0.0430 | 0.9593 | \+0.38 |
| CL-2 | Jericho: recall de cambios de estado | Exploratorio | 0.21 | 0.22 | \-0.04 | \-0.03 \[-0.13, \+0.08\] | 25 | 0.6387 | 0.6855 | 0.3194 | \-0.11 |
| CL-2 | PNJ inactivo mencionado (% de turnos) | Exploratorio | 3.86 % | 0.21 % | \+3.86 pp | \+4.66 pp \[+0.11, \+8.86\] | 24 | 0.0315 | 0.9854 | 0.0157 | \+0.50 |
| CL-2 | PNJ inactivo como sujeto (refinado) | Exploratorio | 0.00 | 0.00 | \+0.00 | \+0.00 \[-0.36, \+0.00\] | 6 | 0.4375 | 0.2188 | 0.8438 | \-0.43 |

*Nota. Elaboración propia a partir de resultados\_tesis.md (Tabla 11, 2026-09-21). Ningún instrumento de CL-1/CL-2 alcanzó la clasificación confirmatoria en la prueba de sensibilidad A2.*

3. ### Análisis descriptivo {#análisis-descriptivo-4}

   Papalampidi C (centralidad de entidad) favorece a G1 con significación nominal (p \= 0.0170, r \= \+0.54): las entidades sembradas se mantienen, en promedio, mejor rastreadas como referentes narrativos a lo largo de la campaña bajo la arquitectura multiagente. En la dirección opuesta, el indicador de PNJ inactivo mencionado —un personaje no jugador narrado como presente después de que su estado pasara a inactivo— es significativamente más frecuente en G1 que en G2 (p \= 0.0315, r \= \+0.50 en la escala donde menor es mejor, es decir, desfavorable para G1); sin embargo, la versión refinada del mismo indicador, que exige que el personaje inactivo sea sujeto gramatical de la oración y no solo mencionado o referido retrospectivamente, pierde por completo la significación (p \= 0.4375, n \= 6). Ningún instrumento de esta dimensión fue validado como confirmatorio por la prueba de sensibilidad A2.

   4. ### Discusión de resultados {#discusión-de-resultados-4}

      La coherencia longitudinal presenta el panorama más simétrico de los tres objetivos comparativos: un indicador exploratorio favorece a G1 (centralidad de entidad), otro favorece a G2 (mención de PNJ inactivo en su versión cruda), y ninguno de los dos alcanza el estatus confirmatorio necesario para decidir formalmente H1e. La caída de significación del indicador de PNJ inactivo al exigir que el personaje sea sujeto gramatical de la oración —y no solo mencionado o aludido— es, en sí misma, un hallazgo metodológico relevante: sugiere que buena parte del efecto crudo observado corresponde a referencias retrospectivas legítimas (el grupo recordando o discutiendo a un personaje ausente) más que a errores narrativos de continuidad donde el sistema efectivamente hace actuar a alguien que ya no debería estar presente. Se decidió, en consecuencia, no promover el indicador crudo a confirmatorio condicionado pese a su paralelismo con persona2: forzar esa promoción habría sido una decisión a conveniencia, no respaldada por el propio refinamiento del instrumento.

      5. ### Docimasia {#docimasia-1}

      H1e: Los sistemas multiagente mantienen una mayor coherencia longitudinal a lo largo de la campaña que los sistemas monolíticos.

      H0e: No existe diferencia significativa en el nivel de coherencia longitudinal entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

      Ningún instrumento de CL-1 o CL-2 alcanzó la clasificación confirmatoria en la validación por sensibilidad A2 (Capítulo 5.6): no existe, en consecuencia, evidencia confirmatoria disponible para rechazar o no rechazar H0e con el nivel de rigor exigido al resto de las hipótesis específicas de esta tesis. Esta ausencia de instrumento confirmatorio se documenta como una limitación explícita de la dimensión longitudinal, y no se sustituye con evidencia exploratoria ni se resuelve por defecto a favor de H0e ni de H1e.

      6. ### Conclusiones {#conclusiones-4}

      La coherencia longitudinal es la única de las tres dimensiones comparativas sin un instrumento confirmatorio disponible para decidir la hipótesis específica correspondiente. La evidencia exploratoria es mixta: centralidad de entidad favorece a G1 (p \= 0.0170); mención cruda de PNJ inactivo favorece a G2 (p \= 0.0315), efecto que desaparece en su versión sintácticamente refinada (p \= 0.4375). H1e queda sin decisión confirmatoria en este corpus.

      7. ### Recomendaciones {#recomendaciones-4}

      Se recomienda priorizar, para una futura extensión de la investigación, el desarrollo o la validación de un instrumento confirmatorio dedicado a CL-1/CL-2 —candidato más cercano: una versión ampliada del recall de Jericho-QA con prueba de sensibilidad A2 propia—, dado que es la única de las tres dimensiones de la Rúbrica D\&D-IA sin evidencia confirmatoria en el corpus actual.

   6. ## Comparar la calidad de la narrativa emergente producida por la arquitectura multiagente frente a la monolítica {#comparar-la-calidad-de-la-narrativa-emergente-producida-por-la-arquitectura-multiagente-frente-a-la-monolítica}

      1. ### Definición del objetivo {#definición-del-objetivo-5}

      OE-6 contrasta la calidad narrativa emergente de G1 frente a G2 mediante el mismo diseño Gpar, sobre los indicadores de QN-1 (diversidad léxica, legibilidad, repetición) y QN-2 (usurpación de agencia del jugador, instrumento persona2).

      2. ### Resultados {#resultados-5}

#### ***Tabla 13\. Comparación pareada G1−G2, 27 parejas — Calidad narrativa emergente (H1f).*** {#tabla-13.-comparación-pareada-g1−g2,-27-parejas-—-calidad-narrativa-emergente-(h1f).}

| Indicador | Instrumento | Uso | Mdn G1 | Mdn G2 | Mdn dif. | HL \[IC 95 %\] | n efect. | p bilateral | r | p Holm |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| QN-1 | TTR (por turno, sin controlar longitud) | Exploratorio | 0.679 | 0.725 | \-0.044 | \-0.045 \[-0.049, \-0.041\] | 27 | \<0.0001 | \-1.00 | — |
| QN-1 | Repetición de bigramas (por turno) | Exploratorio | 0.030 | 0.018 | \+0.010 | \+0.011 \[+0.010, \+0.012\] | 27 | \<0.0001 | \+1.00 | — |
| QN-1 | TTR a 100 palabras (control de longitud) | Exploratorio | 0.7409 | 0.7393 | \+0.0023 | \+0.0022 \[+0.0004, \+0.0039\] | 27 | 0.0200 | \+0.51 | — |
| QN-1 | Bigramas a 100 palabras (control de longitud) | Exploratorio | 0.0139 | 0.0154 | \-0.0017 | \-0.0014 \[-0.0019, \-0.0009\] | 27 | \<0.0001 | \-0.83 | — |
| QN-1 | MTLD de la campaña | Exploratorio | 109.0 | 108.9 | \+0.2 | \+0.2 \[-1.4, \+1.9\] | 27 | 0.8408 | \+0.05 | — |
| QN-1 | MATTR de la campaña | Exploratorio | 0.824 | 0.828 | \-0.004 | \-0.004 \[-0.005, \-0.002\] | 25 | 0.0018 | \-0.68 | — |
| QN-1 | Legibilidad Fernández-Huerta | Descriptivo/no usar | 60.5 | 61.8 | \-1.6 | \-1.8 \[-2.8, \-0.7\] | 27 | 0.0055 | \-0.60 | — |
| QN-1 | Szigriszt-Pazos | Descriptivo/no usar | 56.3 | 57.6 | \-1.6 | \-1.8 \[-2.8, \-0.8\] | 27 | 0.0055 | \-0.60 | — |
| QN-2 | Usurpación total del PJ | Confirmatorio condicionado | 0.17 % | 3.47 % | \-3.39 pp | \-3.66 pp \[-4.87, \-2.74\] | 27 | \<0.0001 | \-1.00 | \<0.0001 |
| QN-2 | · decisión | Confirmatorio condicionado | 0.00 % | 0.17 % | \-0.17 pp | \-0.16 pp \[-0.21, \-0.11\] | 20 | \<0.0001 | \-1.00 | \<0.0001 |
| QN-2 | · pensamiento | Confirmatorio condicionado | 0.09 % | 2.38 % | \-2.30 pp | \-2.63 pp \[-3.69, \-1.89\] | 27 | \<0.0001 | \-1.00 | \<0.0001 |
| QN-2 | · emoción | Confirmatorio condicionado | 0.00 % | 0.22 % | \-0.22 pp | \-0.23 pp \[-0.29, \-0.17\] | 25 | \<0.0001 | \-1.00 | \<0.0001 |
| QN-2 | · habla | Confirmatorio condicionado | 0.00 % | 0.43 % | \-0.34 pp | \-0.42 pp \[-0.68, \-0.24\] | 26 | \<0.0001 | \-0.98 | \<0.0001 |

*Nota. Elaboración propia a partir de resultados\_tesis.md (Tabla 13, 2026-09-21). Palabras por turno: mediana G1 158, G2 116 (diferencia \+41, p\<0.0001) — confusor de longitud que motiva reportar TTR y repetición de bigramas por turno como exploratorios, y sus versiones a 100 palabras como control.*

3. ### Análisis descriptivo {#análisis-descriptivo-5}

   Las cinco filas de persona2 —el único grupo de instrumentos confirmatorios (condicionados) de todo el capítulo— favorecen a G1 de forma unánime y con el tamaño de efecto máximo posible en una prueba pareada (r entre \-0.98 y \-1.00, es decir, G1 obtiene una tasa de usurpación de agencia del jugador menor que G2 en prácticamente los 27 pares sin excepción), con p \< 0.0001 en las cinco filas incluso tras la corrección de Holm dentro de la familia confirmatoria. La diversidad léxica sin controlar por longitud (TTR, bigramas) favorece a G2 con efectos también extremos (r \= ±1.00), pero esta diferencia se explica en gran medida por la diferencia de longitud de turno entre arquitecturas (G1: 158 palabras de mediana; G2: 116): al recalcular ambos instrumentos sobre las primeras 100 palabras de cada turno, la dirección del efecto se invierte para ambos (TTR a 100 palabras favorece a G1, r \= \+0.51; bigramas a 100 palabras favorece a G1, r \= \-0.83), y MTLD —que no depende de la longitud— no muestra diferencia significativa entre arquitecturas (p \= 0.8408). La legibilidad (Fernández-Huerta y Szigriszt-Pazos, misma familia de fórmulas) favorece levemente a G2, pero se reporta como descriptiva por no tener un sentido de mejora definido para la calidad narrativa.

   4. ### Discusión de resultados {#discusión-de-resultados-5}

      La calidad narrativa emergente es la única de las tres dimensiones comparativas con un bloque de instrumentos confirmatorios robusto y consistente: persona2 mide directamente el principio central de QN-2 en la Rúbrica D\&D-IA —que las decisiones del jugador no sean usurpadas por el sistema—, y lo hace con un efecto de magnitud casi perfecta en las cinco categorías medidas. La diversidad léxica, en cambio, ejemplifica el valor de haber corregido el confusor de longitud de turno antes de escribir esta docimasia (Capítulo 2.5, limitación documentada): el hallazgo inicial de TTR/bigramas favoreciendo a G2 se invierte al controlar por longitud, por lo que reportarlo como confirmatorio habría sido un error metodológico que una revisión posterior habría expuesto. Con el control de longitud aplicado, la diferencia léxica remanente entre arquitecturas es pequeña en magnitud absoluta (0.002 en TTR, 0.0014 en bigramas) aunque estadísticamente detectable, y favorece consistentemente a G1, no a G2.

      5. ### Docimasia {#docimasia-2}

      H1f: Los sistemas multiagente producen una Calidad de Narrativa Emergente superior en comparación con los sistemas monolíticos.

      H0f: No existe diferencia significativa en la Calidad de la Narrativa Emergente entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

      Se rechaza H0f con las cinco filas confirmatorias condicionadas de persona2 (p \< 0.0001, r entre \-0.98 y \-1.00 en las cinco, Holm \< 0.0001), aceptando H1f: G1 respeta significativamente mejor la agencia del jugador que G2. Esta aceptación queda condicionada a la auditoría de precisión de persona2, todavía pendiente, por lo que se trata de un resultado confirmatorio provisional, no definitivo, hasta que dicha auditoría se complete. La evidencia exploratoria de diversidad léxica, una vez controlada la longitud de turno, es consistente con esta misma dirección (favorece levemente a G1), reforzando sin decidir por sí sola la aceptación de H1f.

      6. ### Conclusiones {#conclusiones-5}

      De las tres hipótesis específicas comparativas, H1f es la única sostenida por un bloque de instrumentos confirmatorios robusto: persona2 favorece a G1 en las cinco categorías medidas, con el tamaño de efecto máximo observable en un diseño pareado. La evidencia exploratoria de diversidad léxica, corregida por el confusor de longitud de turno, es consistente con esta dirección, aunque de magnitud pequeña. H1f se acepta, condicionada a la auditoría de precisión pendiente de persona2.

      7. ### Recomendaciones {#recomendaciones-5}

      Se recomienda completar la auditoría de precisión de persona2 (fase P2-P4 del plan de cierre de la investigación) como prioridad inmediata antes de la sustentación, dado que es el instrumento que sostiene por sí solo la única hipótesis específica comparativa con evidencia confirmatoria robusta de este corpus.

      8. ### Cierre de la brecha metodológica identificada {#cierre-de-la-brecha-metodológica-identificada-3}

      La recomendación de completar la auditoría de precisión de persona2 como prioridad inmediata (apartado anterior) —dado que es el instrumento que sostiene por sí solo la única hipótesis específica comparativa con evidencia confirmatoria robusta de este corpus— se abordó mediante la misma primera pasada de etiquetado ciego descrita en el cierre de brecha de OE-3 (Capítulo 6.3.7): precisión de 25.6 % (IC 95 % 20.2–31.8 %) y recall de 67.9 % (IC 95 % 57.1–77.1 %) sobre los 515 ítems de la muestra E1. La lectura del detector muestra un patrón asimétrico entre sus categorías de violación: COGNICION es razonablemente fiable (56.7 % de acierto), mientras que VOLICION, EMOCION, ACCION\_NO\_DECLARADA y, sobre todo, HABLA (4.3 % de acierto) concentran la mayoría de los falsos positivos, originados principalmente en diálogo o reacciones de un personaje no jugador que el detector confunde con habla o emoción no declarada del personaje jugador. Esta primera pasada, ejecutada por un asistente de inteligencia artificial y documentada de forma transparente como tal, no sustituye la verificación humana prevista en el plan de validación —evaluador E2, submuestra del 20 % de los 515 ítems—, la cual permitirá además contrastar el acuerdo entre esta pasada asistida por IA y el juicio humano mediante el coeficiente kappa de Cohen [(Romero et al., 2021\)](https://www.zotero.org/google-docs/?UKrh5b) antes de tratar estos números como evidencia confirmatoria plena. Persona2 se mantiene, por tanto, como confirmatorio condicionado: la aceptación de H1f documentada en la docimasia de este objetivo permanece como resultado confirmatorio provisional, ahora con una primera estimación cuantitativa de su tasa de error que no estaba disponible al momento de redactar la docimasia original, pero sin que la verificación humana pendiente haya concluido todavía.

   7. ## Conclusiones {#conclusiones-6}

      El corpus final de 27 pares (54 campañas, 75,600 turnos), medido mediante la batería de instrumentos deterministas descrita en el Capítulo 5, arroja un patrón claro y no uniforme entre las tres dimensiones de la coherencia narrativa. En coherencia reactiva (H1d), el único instrumento confirmatorio disponible favorece a G2, en contradicción directa con las versiones exploratorias del mismo constructo, que favorecen a G1 con efectos grandes; H1d no se sostiene con la evidencia confirmatoria de este corpus, y la discordancia se documenta como un límite de validez de constructo, no como una conclusión zanjada. En coherencia longitudinal (H1e), ningún instrumento alcanzó la clasificación confirmatoria en la validación por sensibilidad A2, por lo que la hipótesis específica queda sin evidencia confirmatoria que la decida, con evidencia exploratoria mixta (centralidad de entidad favorece a G1; mención cruda de PNJ inactivo favorece a G2, efecto que no sobrevive el refinamiento sintáctico del instrumento). En calidad narrativa emergente (H1f), el bloque de instrumentos persona2 —confirmatorio condicionado a una auditoría de precisión todavía pendiente— favorece a G1 de forma unánime y con el tamaño de efecto máximo observable en las cinco categorías medidas, resultado reforzado por la diversidad léxica exploratoria una vez controlado el confusor de longitud de turno identificado en el Capítulo 2.5.

      En conjunto, la evidencia de este corpus no respalda una superioridad general y uniforme del sistema multiagente sobre el monolítico en las tres dimensiones de la coherencia narrativa por igual, sino una ventaja específica y bien fundamentada en el respeto a la agencia del jugador (H1f), sin evidencia confirmatoria decisiva todavía en coherencia longitudinal (H1e), y con evidencia confirmatoria que favorece al sistema monolítico en el único indicador normalizado de arraigo contextual disponible (H1d) — un hallazgo que matiza sustancialmente la hipótesis general de la investigación y que se retoma con mayor profundidad en una revisión pendiente de las hipótesis específicas H1a-H1c del Capítulo 4, cuya formulación original todavía depende del punto medio de la escala Likert del panel de expertos.

   8. ## Recomendaciones {#recomendaciones-6}

      Se recomienda: (a) completar la auditoría de precisión de persona2 —ya avanzada mediante una primera pasada de etiquetado ciego asistida por IA (precisión 25.6 %, recall 67.9 %; Capítulos 6.3.7 y 6.6.7), pendiente todavía de la verificación humana por el segundo evaluador (E2)—, dado que es el único bloque de instrumentos confirmatorios que sostiene una hipótesis específica de este corpus, y su condición de “condicionado” afecta directamente la solidez de H1f; (b) resolver la discordancia de validez de constructo entre CR-2a normalizado y sus versiones crudas antes de presentar H1d ante el jurado, dado que la dirección del hallazgo depende de esa decisión metodológica; (c) profundizar, en una futura extensión de la investigación, en un instrumento confirmatorio para CL-1/CL-2 —la prueba de sensibilidad A2 de Jericho-QA/relojes (Capítulo 6.2.7) y el análisis de supervivencia Kaplan-Meier sobre la primera mención de un personaje no jugador inactivo (Capítulo 6.5.8) ya se ejecutaron y no produjeron un instrumento confirmatorio, por lo que la ausencia de evidencia confirmatoria en esta dimensión queda reforzada, no resuelta—, dado que sigue siendo la única de las tres dimensiones de la Rúbrica D\&D-IA sin evidencia confirmatoria disponible; y (d) actualizar en una sesión futura el Capítulo 4 (hipótesis específicas H1a-H1c) y las Tablas 1 y 2 del Capítulo 4, que todavía describen el instrumento de medición como la Rúbrica de Calidad Narrativa D\&D-IA aplicada por panel bajo escala Likert, para que reflejen el pivote metodológico documentado en el Capítulo 5\.

7. # Referencias bibliográficas {#referencias-bibliográficas}

   [Amato, F., Moscato, F., & Xhafa, F. (2019). Generation of game contents by social media analysis and MAS planning. *Computers in Human Behavior*, *100*, 286–294. https://doi.org/10.1016/j.chb.2019.02.030](https://www.zotero.org/google-docs/?2kzKgM) 

   [Ammanabrolu, P., & Riedl, M. O. (2021). Situated language learning via interactive narratives. *Patterns*, *2*(9), 100316\. https://doi.org/10.1016/j.patter.2021.100316](https://www.zotero.org/google-docs/?2kzKgM) 

   [Balla, M., Long, G. E. M., Goodman, J., Gaina, R. D., & Perez-Liebana, D. (2024). PyTAG: Tabletop Games for Multiagent Reinforcement Learning. *IEEE Transactions on Games*, *16*(4), 993–1002. https://doi.org/10.1109/TG.2024.3404133](https://www.zotero.org/google-docs/?2kzKgM) 

   [Barambones, J., Cano-Benito, J., Sánchez-Rivero, I., Imbert, R., & Richoux, F. (2023). Multiagent Systems on Virtual Games: A Systematic Mapping Study. *IEEE Transactions on Games*, *15*(2), 134–147. https://doi.org/10.1109/TG.2022.3214154](https://www.zotero.org/google-docs/?2kzKgM) 

   [Bidarra, R., & Kybartas, B. (2017). A Survey on Story Generation Techniques for Authoring Computational Narratives. *IEEE Transactions on Computational Intelligence and AI in Games*, *9*(3), 239–253. https://doi.org/10.1109/TCIAIG.2016.2546063](https://www.zotero.org/google-docs/?2kzKgM) 

   [Binggang, Z., & Masaki, M. (2024). Utilizing GPT-4 to Solve TextWorld Commonsense Games Efficiently. *Games and Natural Language Processing 2024 at LREC-COLING 2024, Workshop Proceedings*, 76–84. https://www.scopus.com/pages/publications/85195203979?origin=resultslist](https://www.zotero.org/google-docs/?2kzKgM) 

   [Callison-Burch, C., Tomar, G. S., Martin, L., Ippolito, D., Bailis, S., & Reitter, D. (2022). Dungeons and Dragons as a Dialog Challenge for Artificial Intelligence. *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing*, 9379–9393. https://doi.org/10.18653/v1/2022.emnlp-main.637](https://www.zotero.org/google-docs/?2kzKgM) 

   [Casas-Roma, J., Nelson, M., Arnedo-Moreno, J., Gaudl, S., & Saunders, R. (2019). Towards Simulated Morality Systems: Role-Playing Games as Artificial Societies: *Proceedings of the 11th International Conference on Agents and Artificial Intelligence*, 244–251. https://doi.org/10.5220/0007496702440251](https://www.zotero.org/google-docs/?2kzKgM) 

   [De Lima, E. S., Feijó, B., & Furtado, A. L. (2023). Managing the plot structure of character-based interactive narratives in games. *Entertainment Computing*, *47*, 100590\. https://doi.org/10.1016/j.entcom.2023.100590](https://www.zotero.org/google-docs/?2kzKgM) 

   [George, R. A. (2015). Narrative Generation in Entertainment: Using Artificial Intelligence Planning. *Fields: journal of Huddersfield student research*, *1*(1). https://doi.org/10.5920/fields.2015.118](https://www.zotero.org/google-docs/?2kzKgM) 

   [Islam, M. S., Laskar, M. T. R., Parvez, M. R., Hoque, E., & Joty, S. (2024). DataNarrative: Automated Data-Driven Storytelling with Visualizations and Texts. *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing*, 19253–19286. https://doi.org/10.18653/v1/2024.emnlp-main.1073](https://www.zotero.org/google-docs/?2kzKgM) 

   [Jara Gonzalez, J., Cooper, S., & Guzdial, M. (2023). Mechanic Maker 2.0: Reinforcement Learning for Evaluating Generated Rules. *Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment*, *19*(1), 266–275. https://doi.org/10.1609/aiide.v19i1.27522](https://www.zotero.org/google-docs/?2kzKgM) 

   [Laclaustra, Iván M., Ledesma, José L., Méndez, Gonzalo, & Gervás, Pablo. (2014). *Kill the dragon and rescue the princess: Designing a plan-based multi-agent story generator*. https://www.scopus.com/pages/publications/85086287240?origin=resultslist](https://www.zotero.org/google-docs/?2kzKgM) 

   [Lara J, M., Srijan, S., & Mark O., R. (2018). *Dungeons and DQNs: Toward reinforcement learning agents that play tabletop roleplaying games*. *2321*. https://www.scopus.com/pages/publications/85062227150?inward\#](https://www.zotero.org/google-docs/?2kzKgM) 

   [Pan, Z., Andronis, A., Hayek, E., Wilkinson, O. A., Lasy, I., Parry, A., Gadney, G., Smith, T. J., & Grierson, M. (2025). *Guiding Generative Storytelling with Knowledge Graphs* (Versión 2). arXiv. https://doi.org/10.48550/ARXIV.2505.24803](https://www.zotero.org/google-docs/?2kzKgM) 

   [Peng, X., Cui, C., Zhou, W., Jia, R., & Riedl, M. (2023). *Story Shaping: Teaching Agents Human-like Behavior with Stories* (Versión 1). arXiv. https://doi.org/10.48550/ARXIV.2301.10107](https://www.zotero.org/google-docs/?2kzKgM) 

   [Qu, X., Damoah, A., Sherwood, J., Liu, P., Shun Jin, C., Chen, L., Shen, M., Aleisa, N., Hou, Z., Zhang, C., Gao, L., Li, Y., Yang, Q., Wang, Q., & De Souza, C. (2025). *A Comprehensive Review of AI Agents: Transforming Possibilities in Technology and Beyond* (Versión 1). arXiv. https://doi.org/10.48550/ARXIV.2508.11957](https://www.zotero.org/google-docs/?2kzKgM) 

   [Romero, N. G., Gutiérrez-Romero, M. F., Ríos, J. A. M., Mesa-Hoyos, T., & Blanco, O. A. C. (2021). Diseño y validación del instrumento para la evaluación de la calidad narrativa de relatos orales ficticios creados con el attachment script assessment. *Íkala*, *26*(2), 395–412. https://doi.org/10.17533/udea.ikala.v26n2a07](https://www.zotero.org/google-docs/?2kzKgM) 

   [Santiago, J. Ma., Parayno, R. L., Deja, J. A., & Samson, B. P. V. (2023). *Rolling the Dice: Imagining Generative AI as a Dungeons \&amp; Dragons Storytelling Companion* (Versión 1). arXiv. https://doi.org/10.48550/ARXIV.2304.01860](https://www.zotero.org/google-docs/?2kzKgM) 

   [Valdivia, A., & Burelli, P. (2025). Evaluating Quality of Gaming Narratives Co-Created with AI. *2025 IEEE Conference on Games (CoG)*, 1–4. https://doi.org/10.1109/CoG64752.2025.11114354](https://www.zotero.org/google-docs/?2kzKgM) 

   [Van Der Linden, R., Lopes, R., & Bidarra, R. (2014). Procedural Generation of Dungeons. *IEEE Transactions on Computational Intelligence and AI in Games*, *6*(1), 78–89. https://doi.org/10.1109/TCIAIG.2013.2290371](https://www.zotero.org/google-docs/?2kzKgM) 

   [Van Velsen, M., Williams, J., & Verhulsdonck, G. (2009). Concepts for Interactive Digital Storytelling: From Table-top to Game-AI. *Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment*, *5*(1), 173–178. https://doi.org/10.1609/aiide.v5i1.12374](https://www.zotero.org/google-docs/?2kzKgM) 

   [Viana, B. M. F., & Dos Santos, S. R. (2019). A Survey of Procedural Dungeon Generation. *2019 18th Brazilian Symposium on Computer Games and Digital Entertainment (SBGames)*, 29–38. https://doi.org/10.1109/SBGames.2019.00015](https://www.zotero.org/google-docs/?2kzKgM) 

   [Ware, S., Garcia, E. T., Fisher, M., Shirvani, A., & Farrell, R. (2023). Multiagent Narrative Experience Management as Story Graph Pruning. *IEEE Transactions on Games*, *15*(3), 378–387. https://doi.org/10.1109/TG.2022.3177125](https://www.zotero.org/google-docs/?2kzKgM) 

   [Xia, H., Peng, H., Qi, Y., Wang, X., Xu, B., Hou, L., & Li, J. (2025). *StoryWriter: A Multi-Agent Framework for Long Story Generation* (Versión 1). arXiv. https://doi.org/10.48550/ARXIV.2506.16445](https://www.zotero.org/google-docs/?2kzKgM) 

   [Zhu, A., Osgood, E., & Callison-Burch, C. (2025). *First Steps Towards Overhearing LLM Agents: A Case Study With Dungeons \&amp; Dragons Gameplay* (Versión 2). arXiv. https://doi.org/10.48550/ARXIV.2505.22809](https://www.zotero.org/google-docs/?2kzKgM) 

8. **Anexos**

**Anexo 1\.** Instrumentos de recolección de datos.

**Anexo 2\.** Evidencias de la ejecución de la investigación.

**Anexo 3\.** Resolución de aprobación del proyecto de investigación.

**Anexo 4\.** Constancia de autorización y asentimiento de la organización.

**Anexo 5\.** Constancia del asesor.

**Anexo 6\.** Metodología de desarrollo de software.

