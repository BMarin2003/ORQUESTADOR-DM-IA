# R2. Pruebas de sensibilidad (A2) y auditoría de detectores (A3) sin jueces LLM

Alcance: literatura verificada y diseño concreto para (A2) pruebas de sensibilidad por perturbación y (A3) auditoría de precisión/recall de los detectores por etiquetado manual del investigador. La medición de los brazos G1/G2 sigue siendo 100 % determinista; las etiquetas humanas de A3 solo auditan la tasa de error de los instrumentos (presencia objetiva de un defecto según un codebook), no la calidad narrativa de los brazos.

## (a) Referencias verificadas

Cuartiles: salen de resúmenes de WebSearch restringido a scimagojr.com / resurchify.com / scijournal.org (SCImago da 403 al fetch directo). Es el mejor cuartil reciente de la revista (2024-25), no el del año de publicación. Verificación: **PDF** = metadatos y texto leído; **META** = metadatos coincidentes en varias fuentes, contenido no leído completo.

| # | Referencia | Venue y cuartil | Qué aporta | Verif. |
|---|---|---|---|---|
| 1 | Ribeiro, Wu, Guestrin, Singh (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList. aclanthology.org/2020.acl-main.442 | ACL 2020, congreso, sin cuartil | Tres tipos de prueba: MFT (casos con respuesta conocida), INV (perturbación que no debe cambiar la salida), DIR (perturbación con cambio esperado); se reporta tasa de fallo | PDF |
| 2 | Sai, Dixit, Sheth, Mohan, Khapra (2021). Perturbation CheckLists for Evaluating NLG Evaluation Metrics. EMNLP, pp. 7219-7234 | congreso, sin cuartil | 34 plantillas de perturbación, 18 criterios; algunas invariantes (sinónimos, contracciones) y otras que deben bajar el score (desordenar palabras, borrar frases, repetir, reordenar oraciones, pronominalizar). Su estadístico usa humanos; nosotros solo la dirección | PDF |
| 3 | Segura, Fraser, Sánchez, Ruiz-Cortés (2016). A Survey on Metamorphic Testing. IEEE Trans. Software Eng. 42(9):805-824 | Q1 | Relaciones metamórficas: propiedades necesarias entre salidas de entradas relacionadas, sin oráculo | META |
| 4 | Chen, Kuo, Liu, Poon, Towey, Tse, Zhou (2018). Metamorphic Testing: A Review of Challenges and Opportunities. ACM Comput. Surv. 51(1):4:1-27. doi:10.1145/3143561 | Q1 | Identificación de relaciones metamórficas, generación de casos | META |
| 5 | Barzilay & Lapata (2008). Modeling Local Coherence: An Entity-Based Approach. Comput. Linguistics 34(1):1-34 | Q1 | Discriminación: original vs. hasta 20 permutaciones aleatorias de oraciones; métrica = accuracy (azar 50 %), empates al azar; prueba del signo | PDF |
| 6 | Guinaudeau & Strube (2013). Graph-based Local Coherence Modeling. ACL, pp. 93-103 | congreso, sin cuartil | Discriminación (accuracy + F con empates, 20 permutaciones) e inserción de oración (Elsner & Charniak 2011); t pareada + Bonferroni; sin información de distancia el modelo no distingue original de permutación | PDF |
| 7 | Lapata (2006). Automatic Evaluation of Information Ordering: Kendall's Tau. Comput. Linguistics 32(4):471-484 | Q1 | τ de Kendall como medida de orden; correlaciona con juicios humanos y tiempos de lectura | META |
| 8 | Mohiuddin, Jwalapuram, Lin, Joty (2021). Rethinking Coherence Modeling: Synthetic vs. Downstream Tasks. EACL, pp. 3528-3539 | congreso, sin cuartil | El rendimiento en tareas sintéticas de orden correlaciona débilmente con tareas reales: límite de la prueba de permutación | META |
| 9 | Shen, Mistica, Salehi, Li, Baldwin, Qi (2021). Evaluating Document Coherence Modeling. TACL 9:621-640 | Q1 | Detección de oración intrusa (INSteD); caída fuera de dominio | META |
| 10 | Campbell & Fiske (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. Psychol. Bull. 56(2):81-105 | Q1 | Validez convergente y discriminante; varios métodos por rasgo | META |
| 11 | Cronbach & Meehl (1955). Construct validity in psychological tests. Psychol. Bull. 52:281-302 | Q1 | Red nomológica: validar un constructo sin criterio único | META |
| 12 | Messick (1995). Validity of psychological assessment... American Psychologist 50:741-749 | Q1 | Validez unitaria: aspectos de contenido, sustantivo, estructural, generalización, externo y consecuencial | META |
| 13 | Reiter (2018). A Structured Review of the Validity of BLEU. Comput. Linguistics 44(3):393-401. doi:10.1162/coli_a_00322 | Q1 | 284 correlaciones en 34 artículos: BLEU válida para MT diagnóstica, no para textos individuales ni contraste de hipótesis. La validez es por uso | META |
| 14 | Sai, Mohankumar, Khapra (2022). A Survey of Evaluation Metrics Used for NLG Systems. ACM Comput. Surv. 55(2), art. 26. doi:10.1145/3485766 | Q1 | Taxonomía de métricas y críticas de validez | META |
| 15 | Webber (2013). Approximate Recall Confidence Intervals. ACM Trans. Inf. Syst. 31(1):1-33. doi:10.1145/2414782.2414784 | Q1 | IC de recall por muestreo: la aproximación normal cubre mal; recomienda posteriores beta-binomiales + Monte Carlo | META |
| 16 | Grossman & Cormack (2014). Comments on "The Implications of Rule 26(g) on the Use of TAR". Federal Courts Law Review 7(1), desde p. 285 | revista jurídica, sin cuartil SJR | Define elusion y «eRecall» (Roitblat); los estimadores por razón (incl. eRecall) resultan sesgados con márgenes mucho mayores que los declarados; el método directo es sólido pero exige muestras grandes con baja prevalencia («no free lunch») | PDF |
| 17 | Lewis, Yang, Frieder (2021). Certifying One-Phase Technology-Assisted Reviews. CIKM. doi:10.1145/3459637.3482415 | congreso, sin cuartil | Reglas muestrales con cota de confianza sobre recall (QBCB) | META |
| 18 | Zobel (1998). How reliable are the results of large-scale IR experiments? SIGIR, pp. 307-314 | congreso, sin cuartil | Pooling: el recall se sobreestima porque quedan relevantes sin encontrar | META |
| 19 | Brown, Cai, DasGupta (2001). Interval Estimation for a Binomial Proportion. Statistical Science 16(2):101-133 | Q1 | Wald errático; recomiendan Wilson o Jeffreys (n pequeño) y Agresti-Coull (n grande) | META |
| 20 | Agresti & Coull (1998). Approximate is better than "exact"... Am. Statistician 52(2):119-126 | Q2-Q3 (fuentes discrepantes) | El intervalo «exacto» (Clopper-Pearson) es conservador; Wilson cubre cerca del nominal | META |
| 21 | Wilson (1927), J. Am. Stat. Assoc. 22(158):209-212; Clopper & Pearson (1934), Biometrika 26:404-413 | cuartil no verificado | Intervalos originales (Wilson, exacto) | META |
| 22 | Hanley & Lippman-Hand (1983). If nothing goes wrong, is everything all right? JAMA 249(13):1743-1745 | Q1 | Numerador cero: cota superior 95 % ≈ 3/n | META |
| 23 | Feinstein & Cicchetti (1990), J. Clin. Epidemiol. 43:543-549; Cicchetti & Feinstein (1990), ibid. 43(6):551-558 | Q1 | Paradojas de κ con marginales desbalanceados; proponen acuerdo positivo (p_pos) y negativo (p_neg) | META |
| 24 | Byrt, Bishop, Carlin (1993). Bias, prevalence and kappa. J. Clin. Epidemiol. 46(5):423-429 | Q1 | Índices de sesgo y prevalencia; PABAK | META |
| 25 | Gwet (2008). Computing inter-rater reliability and its variance in the presence of high agreement. Br. J. Math. Stat. Psychol. 61(1):29-48 | Q1 | AC1, estable ante las paradojas de κ; varianza sin supuesto de independencia | META |
| 26 | Wongpakaran, Wongpakaran, Wedding, Gwet (2013). A comparison of Cohen's Kappa and Gwet's AC1... BMC Med. Res. Methodol. 13:61 | Q1 | AC1 menos afectado que κ por prevalencia y marginales (datos clínicos) | META |
| 27 | Artstein & Poesio (2008). Inter-Coder Agreement for Computational Linguistics. Comput. Linguistics 34(4):555-596 | Q1 | κ, π, α; con datos sesgados un coeficiente bajo es «justificado»: la prueba real es el acuerdo en la categoría rara; α es casi π con corrección de muestra pequeña | PDF |
| 28 | Hayes & Krippendorff (2007). Answering the Call for a Standard Reliability Measure for Coding Data. Commun. Methods Meas. 1(1):77-89 | Q1 | α general (n.º de observadores, datos faltantes) | META |
| 29 | Holm (1979). A simple sequentially rejective multiple test procedure. Scand. J. Stat. 6(2):65-70 | Q2 | Control secuencial de FWER | META |
| 30 | Benjamini & Hochberg (1995). Controlling the false discovery rate. J. R. Stat. Soc. B 57:289-300 | Q1 | FDR; válido con independencia o dependencia positiva (PRDS) | META |
| 31 | Cliff (1993). Dominance statistics. Psychol. Bull. 114(3):494-509 | Q1 | δ ordinal = P(X>Y) − P(X<Y) | META |
| 32 | Kerby (2014). The Simple Difference Formula. Comprehensive Psychology 3, art. 1. doi:10.2466/11.IT.3.1 | cuartil no verificado | Correlación rank-biserial r = f − u | META |
| 33 | McNemar (1947). Note on the sampling error of the difference between correlated proportions. Psychometrika 12:153-157 | Q1 | Prueba para proporciones pareadas | META |
| 34 | Fagerland, Lydersen, Laake (2013). The McNemar test for binary matched-pairs data. BMC Med. Res. Methodol. 13:91 | Q1 | mid-p y asintótica mejores que la exacta condicional | META |
| 35 | Dror, Baumer, Shlomov, Reichart (2018). The Hitchhiker's Guide to Testing Statistical Significance in NLP. ACL, pp. 1383-1392 | congreso, sin cuartil | Protocolo de elección de pruebas; suelen omitirse o mal usarse | META |

Recuento (37 referencias individuales; #21 y #23 contienen dos cada una): revistas Q1-Q3 con cuartil verificado: **26**; revistas sin cuartil verificado: 3 (Wilson 1927, Clopper-Pearson 1934, Kerby 2014); revista jurídica sin SJR: 1; congresos: **7** (#1, 2, 6, 8, 17, 18, 35). No verifiqué Efron (bootstrap), Newcombe ni Vargha-Delaney: no se citan.

## (b) Diseño A2: pruebas de sensibilidad por perturbación

### b.1 Tres tipos de prueba (CheckList #1, relaciones metamórficas #3-4)
- **DIR**: se inyecta un defecto conocido en texto real; el instrumento debe reaccionar en una dirección pre-especificada.
- **INV**: perturbación que preserva el constructo (o placebo: espacios, orden de campos); el instrumento no debe cambiar. Es el control discriminante.
- **MFT**: minipares construidos con veredicto conocido. **Regla nueva: equivalencia por persona gramatical.** Todo defecto que un detector busque por nombre del PJ se inyecta en tres formas superficiales (nombre 3.ª persona, pronombre/elipsis, 2.ª persona «tú») y en textos de ambos brazos. Un detector que dispara solo en una forma es el fallo ya observado en G2 y esta prueba lo habría detectado.

### b.2 Catálogo de perturbaciones (ejecutar por brazo)

| Instrumento | Perturbación DIR | Esperado | Control INV |
|---|---|---|---|
| D1 PNJ inactivo actúa | PNJ con estado inactivo como sujeto de verbo de acción (nombre/alias/epíteto/pronombre) | marca = 1 | mismo verbo con PNJ activo: 0 |
| D2 veredicto de dado | invertir éxito↔fallo respecto al registro | 1 | reformular sin cambiar veredicto: 0 |
| D3 campo inmutable | alterar un campo inmutable en el delta | 1 | alterar campo mutable: 0 |
| D4 PJ muerto con HP>0 | HP>0 con estado muerto; PJ muerto actúa | 1 | HP>0 vivo: 0 |
| D5 PJ piensa narrado | insertar pensamiento/emoción del PJ (3 formas) | 1 en las tres | percepción del entorno sin estado mental: 0 |
| D6 nombres no reconocidos | nombre propio inventado | 1 | variante de mayúsculas/tilde/alias conocido: 0 |
| Gramaticalidad (LanguageTool) | errores de concordancia, tildes omitidas, palabras borradas (3 dosis) | errores/100 tokens ↑ monótono | sinónimos: Δ≈0 |
| Densidad de grafo / ECR | reemplazar 2.ª+ mención de entidades recurrentes por nombres nuevos; insertar turno intruso de otra campaña (#9) | ↓ | cambio de mayúsculas/flexión (lematizado): = |
| TTR / repetición de n-gramas | duplicar oraciones (3 dosis) | TTR ↓, repetición ↑ | permutar turnos: **exactamente =** |
| Fernández-Huerta | partir oraciones / unir con comas | ↑ / ↓ | permutar turnos: = |
| Recall de deltas (Jericho-QA) | borrar la oración que enuncia el cambio de estado | ↓ | añadir oración neutra: = |
| Reloj «reconocido» | quitar / añadir la mención | ↓ / ↑ | placebo |
| Papalampidi C/V | **sin dirección propuesta**: no puedo inferirla del contexto; fijarla desde su definición operativa antes de correr | — | — |

**Coherencia global (#5-9).** Para instrumentos sensibles al orden (grafo, ECR, recall de deltas): por ventana de turnos, comparar original vs. k = 20 permutaciones (#5, #6). Los instrumentos «de bolsa» (TTR, FH, repetición intra-turno) sirven de control negativo: deben dar ≈ 50 % con empates. Si no, la prueba está mal construida. Añadir inserción de turno (#6, #9).

### b.3 Pre-especificar la dirección antes de correr
1. Archivo `matriz_expectativas` (una fila por instrumento × perturbación × dosis) con: dirección ∈ {↑, ↓, =, sin predicción}, magnitud mínima, justificación mecánica en ≤ 2 líneas derivada de la **definición** del instrumento (no de su salida) y criterio de aprobación.
2. Commit con hash **antes** de escribir los generadores de perturbación; revisión del asesor sobre la matriz.
3. Las celdas sin dirección derivable se marcan «exploratorio» y no cuentan como aprobadas.
4. Cambios posteriores solo como adenda fechada «post hoc».

### b.4 Estadísticos
- **Booleanos DIR:** recall inyectado con IC de Wilson (#19), por forma superficial y por brazo; aprobar si el límite inferior ≥ 0,80 (umbral propuesto por mí; fijarlo antes). **INV:** tasa de disparo con Wilson o Clopper-Pearson; con 0/n reportar 3/n (#22). Como cada texto original y su perturbado forman un par, reportar los discordantes (0→1 vs. 1→0) y McNemar mid-p (#33, #34).
- **Numéricos:** Δ = m(perturbado) − m(original) por ítem. Reportar (i) mediana de Δ con IC bootstrap remuestreando **campañas** (los turnos están anidados), (ii) proporción de ítems que se mueven en la dirección esperada con Wilson, (iii) rank-biserial pareado (#32) o δ de Cliff (#31) sobre los valores por campaña, (iv) monotonía dosis-respuesta (Spearman entre dosis y media). Umbrales por defecto propuestos: ≥ 90 % en la dirección esperada y |r| ≥ 0,5. **INV:** el IC del Δ mediano debe caber dentro de ±tolerancia = percentil 95 de |Δ| bajo perturbación placebo.
- **Discriminación por permutación:** accuracy con empates explícitos (#5, #6) y τ de Kendall (#7) con IC bootstrap por campaña.
- **Multiplicidad:** el criterio de aprobación es de tamaño de efecto, no de p. Si se reportan p: Holm (#29) sobre la familia confirmatoria (celdas con dirección pre-especificada) y BH (#30) sobre el resto (supone independencia/PRDS). Ojo: la corrección castiga justo el objetivo de A2 (probar sensibilidad), por eso el peso recae en tamaños de efecto con IC (#35).

### b.5 Evitar el sesgo de confirmación
- Muestra de turnos por semilla fija; separar **desarrollo** (p. ej. pares 1-9, para depurar inyectores) y **evaluación congelada** (pares 10-27).
- Escribir las expectativas antes de implementar los inyectores y sin mirar las regex de los detectores. Un solo investigador lo hace todo: mitigarlo con la revisión del asesor.
- Ejecutar y reportar **todas** las celdas. Una celda fallida significa «bug o constructo inválido», nunca «cambiar la expectativa».
- Placebos en cada instrumento para estimar su piso de ruido.
- Estructura tipo MTMM (#10): la diagonal (instrumento × su defecto) es la evidencia convergente y las celdas fuera de la diagonal (instrumento × defecto ajeno) la discriminante. Es una adaptación: MTMM exige varios métodos por rasgo, que aquí no hay.

## (c) Diseño A3: auditoría de precisión y recall por etiquetado manual

### c.1 Tamaños de muestra (calculados con script propio, Python puro; ver fórmulas)

| Objetivo | Fórmula / método | Resultado |
|---|---|---|
| Precisión ±10 pts, IC 95 %, peor caso p = 0,5 | n = z²p(1−p)/d² = 96 | **n = 100 marcas** (Wilson da ±9,6) |
| Si p ≈ 0,8 / 0,9 | idem | n = 62 / 35-40 (Wilson n = 40, p̂ = 0,9: ±9,5) |
| Población finita (N marcas) | n = n₀/(1+(n₀−1)/N) | N = 100→50; 200→66; 300→73; 1000→88; si N ≤ 100 hacer censo |
| Cero eventos en n | regla de tres 3/n (#22) | n = 300→≤1,0 %; n = 1000→≤0,3 % |
| Recall por no-marcas, tasa de omisión m | FN esperados = m·n | m = 1 %, n = 400→4; m = 0,1 %, n = 1000→1 |
| P(≥1 evento) en 500 turnos aleatorios, prevalencia π | 1−(1−π)⁵⁰⁰ | π = 1 %: 99,3 %; 0,5 %: 91,8 %; 0,2 %: 63 % |
| Recall sintético (inyecciones) | Wilson | 90/100→±6,0; 180/200→±4,2 |

Para 95 % de confianza y ±10 puntos, Wilson (#19, #21) es el intervalo principal; Clopper-Pearson (#20, #21) se usa como comprobación conservadora.

### c.2 Precisión (muestrear marcas)
Por detector: 100 marcas (o censo), estratificadas por brazo (mínimo 30 por brazo) y repartidas entre las 27 parejas con semilla fija. Reportar por brazo y agregado. Con marcas agrupadas por campaña, el IC de Wilson es optimista: contrastar con bootstrap por campaña.

### c.3 Recall con eventos raros: tres capas
El muestreo de no-marcas (elusion) es inviable si la omisión es ≤ 0,5 %: hacen falta ≥ 10 FN, es decir n ≥ 2000. Los estimadores de razón (elusion + prevalencia, «eRecall») son sesgados (#16), y el método directo exige muestras grandes con baja prevalencia (#16, #15). Por eso:
1. **L1, recall sintético (A2):** 200 inyecciones por detector, brazo y forma superficial. IC estrecho, pero solo vale para los defectos que uno imagina.
2. **L2, pool enriquecido (Zobel #18):** un filtro liberal por detector, definido con independencia de su lógica (p. ej. D5 en G2: oraciones con verbo 2.ª persona de léxico mental; D1: turnos con PNJ inactivo mencionado). Etiquetar 200 turnos aleatorios de «filtrados no marcados» y 100 de «no filtrados» por brazo. FN = Σ N_h·f_h con f_h ~ Beta(x_h+½, n_h−x_h+½) (Jeffreys, #19) y 10 000 simulaciones Monte Carlo para el IC de recall = TP/(TP+FN). Es una adaptación mía de #15, no su método literal. Reportar el recall **relativo al filtro** y, aparte, la cota 3/n de fuga en no filtrados. Ese recall es un techo, no un valor puntual (#18).
3. **L3, sonda de prevalencia:** 500 turnos aleatorios por brazo etiquetados a la vez para los 6 defectos. Sirve para el caso G2: si π ≥ 0,5 %, una etiqueta positiva es casi segura (≥ 91,8 %) y cualquier positivo con 0 marcas confirma el punto ciego. Estos turnos forman parte del estrato «no filtrados».

Carga: 6 detectores × (100 + 300) + 1000 ≈ 3400 etiquetas (a ~40 s c/u, supuesto mío, ≈ 38 h). Prioridad 1: los 3 detectores rotos en G2 (L1-L3) y la precisión de todos en G1. Prioridad 2: el resto. Etiquetar cada turno para los 6 defectos a la vez reduce el costo.

### c.4 Etiquetado a ciegas
- El etiquetador ve el texto del turno y el mínimo estado necesario (estado del PNJ, veredicto registrado, HP/muerte), en formato neutro. No ve brazo, campaña, pareja ni salida de ningún detector.
- El orden es aleatorio y mezcla marcas, filtrados y no filtrados de ambos brazos, con ID hash.
- Codebook con ejemplos positivos y negativos en 2.ª y 3.ª persona, más semilla y script de muestreo, con commit **antes** de extraer la muestra.
- Ciego parcial, inevitable: la persona y el estilo delatan el brazo. Medirlo pidiendo adivinar el brazo en 50 ítems al final y reportar el acierto.
- No cambiar una etiqueta tras ver la marca del detector. Toda revisión se registra aparte y se conserva la etiqueta original para el acuerdo.
- **Desarrollo vs. confirmación:** las muestras usadas para arreglar los detectores (30 marcas y 100 no marcas, p. ej.) no se reutilizan para reportar su precisión. Tras corregir, auditar sobre una muestra fresca.

### c.5 Segundo etiquetador sobre el 20 %
Muestra aleatoria del 20 % estratificada por estrato (marcas / filtrados / no filtrados × brazo). Con baja prevalencia habrá pocos positivos: garantizar ≥ 15 ítems positivos por detector y reportarlos como «submuestra enriquecida» (no comparable en κ, que depende de la prevalencia de la muestra). Reportar, por detector:
1. n doble-etiquetado, n de positivos y acuerdo observado con IC de Wilson.
2. **Acuerdo positivo p_pos y negativo p_neg** (#23), que informan sobre la categoría rara (#27).
3. **AC1 de Gwet** como coeficiente ajustado por azar principal (#25, #26), con IC.
4. κ de Cohen y PABAK (#24) solo como comparación transparente, con índices de sesgo y prevalencia. PABAK = 2·p_o − 1 y hereda el acuerdo observado.
5. α de Krippendorff (#28) solo si se pide. Con dos etiquetadores y datos nominales es casi π (#27) y hereda la paradoja de κ.

Por qué no basta AC1: está diseñado para resistir el desbalance y puede ocultar un acuerdo pobre en la categoría rara. #27 sostiene justo lo contrario, que un coeficiente bajo con datos sesgados es informativo. De ahí p_pos + AC1 + κ juntos, no un único número. Las discrepancias las resuelve el segundo etiquetador y ambas versiones se reportan.

## (d) Amenazas a la validez que A2 y A3 NO cubren
1. **Validez de constructo y consecuencial (#11, #12, #13):** A2 y A3 muestran que los instrumentos detectan lo que definen, no que ese constructo mida la calidad de un DM. No hay criterio humano por diseño y la validez es por uso (#13).
2. **Representatividad de las inyecciones:** los defectos sintéticos pueden diferir de los naturales (#8); L1 no acota el recall natural.
3. **Recall natural solo acotado:** L2 es relativo al filtro (#18) y la fuga en no filtrados se acota, no se estima.
4. **Etiquetador único y autor de los instrumentos:** un codebook compartido correlaciona errores; acuerdo ≠ exactitud; el 20 % es una muestra pequeña con κ inestable.
5. **Ciego imperfecto** (persona y estilo delatan el brazo).
6. **Invarianza de medida entre brazos:** el instrumento puede ser más sensible en G1 que en G2 aunque supere ambas pruebas; A2 no demuestra escala comparable.
7. **Dependencia:** turnos anidados en campañas, detectores correlacionados; Wilson supone independencia y BH exige PRDS (#30).
8. **Errores aguas arriba** (LanguageTool, lematizador, NER): A2 valida dirección, no exactitud absoluta ni escala de intervalo.
9. **Deriva:** la auditoría vale para esta versión del código y este corpus. Cualquier cambio de detector exige nueva auditoría con muestra fresca.
10. **Potencia y validez de la comparación G1/G2** (27 pares): fuera de alcance, y las pruebas de #29-#34 no la garantizan.

## Notas de verificación
- 58 800 turnos = 42 campañas × 1400, no 27 pares × 1400 × 2 = 75 600: confirmar el denominador N por brazo antes de calcular FPC y estratos.
- «Lewis» se cubrió con Lewis, Yang y Frieder (CIKM 2021, #17). Cormack & Grossman (SIGIR 2014) no se incluyó porque trata de protocolos de aprendizaje, no de muestreo de validación; se usó #16.
- Umbrales (0,80, 90 %, |r| ≥ 0,5, tolerancia p95) y tiempos de etiquetado son propuestas mías, no de la literatura.
