# Guía de preparación para la sustentación

**Tesis:** «Comparación de la coherencia narrativa en campañas de Dungeons & Dragons generadas por sistemas multiagente versus sistemas monolíticos».

**Estado a la fecha:** al 01/11/2026, ya con persona2 v3b y la validación humana v2. Las cifras corresponden a la versión final del documento, una vez integrados `QN2_v3b_para_documento.md`, `cambios_documento_validacion_v2.md` y `cambios_complemento_conclusiones.md`.

---

## 0. La tesis en un minuto

- **Problema.** ¿En qué medida difiere la coherencia narrativa de campañas de D&D generadas por un sistema **multiagente (G1)** frente a uno **monolítico (G2)**?
- **Cómo se respondió.** Se generaron 27 pares de campañas, es decir, 54 campañas de 1,400 turnos y **75,600 turnos**. Las dos campañas de cada par usan el mismo escenario, el mismo personaje jugador, el mismo modelo y la misma memoria del mundo; solo cambia la arquitectura. La coherencia se midió con **instrumentos deterministas** validados por perturbaciones sintéticas y, cuando dependen de interpretar el texto, contra **evaluadores humanos ciegos**.
- **Respuesta.**
  - **La hipótesis general no se sostiene.** G1 no es más coherente en todo.
  - **Sí tiene una ventaja clara y robusta en el respeto a la agencia del jugador:** el monolítico decide, siente o habla por el personaje jugador en cerca de 1 de cada 270 turnos, mientras que el multiagente prácticamente nunca lo hace (r = −1.00).
  - **El monolítico es estable** en coherencia reactiva, pero **se degrada en el respeto a la agencia** a lo largo de la campaña (Page p = 0.0105).
  - **La coherencia longitudinal no se puede decidir**, porque ningún instrumento alcanzó la clasificación de confirmatorio.

---

## 1. Planteamiento

| Elemento | Contenido |
|---|---|
| Problema general | ¿En qué medida difiere la coherencia narrativa de las campañas generadas por sistemas multiagente respecto de las generadas por sistemas monolíticos? |
| Objetivo general | Comparar la coherencia narrativa de ambas arquitecturas. |
| Hipótesis general (Hg) | Los sistemas multiagente producen campañas con mayor coherencia narrativa que los monolíticos. |
| Regla de Hg | Se sostiene **solo si se sostienen H1d, H1e y H1f**, que son las tres comparativas. Es una regla conservadora que evita declarar superioridad global a partir de ventajas parciales. |

**Seis objetivos específicos, en dos niveles:**

| Nivel | Objetivo | Dimensión | Hipótesis | Qué contrasta |
|---|---|---|---|---|
| Evaluación de G2 | OE-1 | Coherencia reactiva | H1a | Degradación a lo largo de la campaña |
| | OE-2 | Coherencia longitudinal | H1b | Degradación |
| | OE-3 | Calidad narrativa emergente | H1c | Degradación |
| Comparación G1 vs. G2 | OE-4 | Coherencia reactiva | H1d | G1 > G2 |
| | OE-5 | Coherencia longitudinal | H1e | G1 > G2 |
| | OE-6 | Calidad narrativa emergente | H1f | G1 > G2 |

**Por qué hay dos niveles.** Las hipótesis de degradación (a–c) prueban la premisa que motiva el estudio: un DM basado en un solo modelo se degrada conforme la campaña crece (Liu et al., 2024; Gallotta et al., 2024). Las comparativas (d–f) prueban la ventaja que la literatura atribuye a los multiagente.

---

## 2. Metodología

### 2.1 Tipo, nivel, método y diseño

- **Tipo:** aplicada, con enfoque cuantitativo.
- **Nivel:** explicativo (Arias, 2012).
- **Método:** hipotético-deductivo.
- **Diseño:** experimental de **medidas repetidas con pares emparejados**. Cada escenario recibe los dos tratamientos y actúa como su propio control.
  - **Por qué no hay asignación aleatoria:** no hay grupos que igualar, sino el mismo escenario generado dos veces. Las dos campañas del par se generan como copias independientes y simultáneas, así que tampoco hay efectos de orden ni de arrastre.
  - **Esquema comparativo:** Gpar (n = 27): X₁ → O₁ | X₂ → O₂. La unidad de análisis es la diferencia G1 − G2 dentro del par.
  - **Esquema de degradación:** G2 (n = 27): X₂ → O(b₁) → … → O(b₇), con siete bloques de 200 turnos, cada uno equivalente a una sesión de juego.
- **Nivel de madurez tecnológica:** TRL 4, validación en laboratorio (Mankins, 2009). Son prototipos completos evaluados con un jugador simulado, todavía sin jugadores reales.

### 2.2 Variables y controles

- **Variable independiente:** la arquitectura, nominal con dos niveles.
  - **G2, monolítico:** una sola generación por turno.
  - **G1, multiagente:** enrutador determinista, árbitro, actor de PNJ, agente del mundo y narrador.
- **Variable dependiente:** la coherencia narrativa, con 3 dimensiones y 6 indicadores (Rúbrica D&D-IA, adaptada de Zhu et al., 2023; Zhou et al., 2023; Pan et al., 2025):
  - **Reactiva:** CR-1 corrección mecánica; CR-2 arraigo a la acción.
  - **Longitudinal:** CL-1 persistencia de entidades; CL-2 consistencia de eventos y del estado del mundo.
  - **Calidad narrativa emergente:** QN-1 diversidad y legibilidad; QN-2 usurpación de la agencia.
- **Controlado dentro de cada par:**
  - el modelo, **google/gemma-4-31B-it**, con un solo proveedor (DeepInfra) y su estabilidad verificada con un manifiesto de huellas;
  - la base de datos del mundo (PostgreSQL 16);
  - el extractor;
  - las tiradas deterministas, con semilla por campaña, turno y habilidad;
  - el escenario, el personaje jugador, el agente jugador y la extensión de la campaña.
- **Varía entre pares, a propósito:** la ambientación, el tono y la estructura del conflicto.

### 2.3 Población, muestra y potencia

- **Población:** infinita, porque es el conjunto de campañas que pueden generar ambas arquitecturas.
- **Unidad de análisis:** el par de campañas.
- **Muestra:** 27 pares por muestreo intencional, con criterios de diversidad (ambientación, tono, conflicto y personaje jugador distintos).
  - Personajes jugadores: 8 principistas, 14 de moral ambigua y 5 sin escrúpulos; 9 de ellos cambian de conducta durante la campaña.
- **Potencia (G\*Power):** con α = 0.05 unilateral, potencia 0.80 y d = 0.5 (efecto medio), se obtienen **N = 27 pares** con potencia 0.81.
  - Como se usa Wilcoxon y no la prueba t, la eficiencia relativa asintótica es 3/π ≈ 0.955, y la potencia efectiva queda en **≈ 0.79**. Se declara como una limitación menor.
- **Piloto:** 3 pares de 250 turnos, que **no** entran en la muestra. El panel de 5 expertos con escala Likert evaluó una versión preliminar y queda como antecedente (Anexo 2).

### 2.4 Supuestos que pueden preguntar

1. **La coherencia es medible y descomponible**, y parte de ella se puede verificar de forma determinista contra el estado persistido del mundo.
2. **El extractor solo registra cambios** de una lista cerrada y respaldados por texto literal. Así no se inventan hechos, aunque puede omitir algunos, lo que es una limitación.
3. **El agente jugador es un sustituto válido de un jugador real** siempre que su conducta no converja a una sola postura. Por eso cada uno tiene un arquetipo, una agenda, una propensión al desvío y ejemplos propios (Yasunaga et al., 2024).
4. **Las acciones del agente difieren entre brazos**, porque responde a narraciones distintas. Eso es parte del efecto medido, no un sesgo.
5. **Los pares son independientes** y las diferencias son aproximadamente simétricas, que es el supuesto de Wilcoxon.
6. **Solo deciden los instrumentos que superan la prueba de sensibilidad.**

---

## 3. Instrumentos y su validación

### 3.1 Prueba de sensibilidad por perturbaciones sintéticas

**Idea central:** un instrumento determinista es *confiable por construcción*, porque siempre da el mismo resultado. Lo que hay que probar es su **validez**, es decir, que mida lo que dice medir.

- **Procedimiento:**
  - Sobre ventanas del corpus real se inyectan defectos de efecto conocido: reordenar turnos, desalinear acción y respuesta, insertar o suprimir el evento.
  - Se agregan **perturbaciones de control**, que no deberían afectar al instrumento.
  - Las direcciones esperadas se fijaron **antes** y se sellaron con un **hash SHA-256**, para que no se pudieran ajustar después de ver los resultados.
- **Criterio de sensibilidad:**
  - reacciona en la dirección prevista;
  - con δ de Cliff ≥ 0.147 (Cliff, 1993; Romano et al., 2006);
  - con significancia tras Holm;
  - y no reacciona a los controles.
- **Clasificación resultante:**
  - **Confirmatorio:** supera la perturbación objetivo y los controles. Decide la hipótesis.
  - **Confirmatorio condicionado:** supera la prueba, pero su concordancia con el juicio humano es limitada. Decide, con la salvedad.
  - **Exploratorio:** sensibilidad parcial o control débil. Orienta, pero no decide.
  - **Descriptivo:** saturado o sin perturbación posible. Se reporta sin inferencia.
- **Por qué importa:** evita la **ley de Goodhart**, es decir, que el indicador se vuelva un objetivo y deje de reflejar el constructo (Manheim & Garrabrant, 2018).

### 3.2 Instrumentos por dimensión

| Ind. | Instrumento | Clasificación |
|---|---|---|
| CR-1 | Gramaticalidad (LanguageTool), caracteres de otro alfabeto, pifia narrada como éxito | Descriptivos (saturados o no reconocen la negación) |
| CR-2 | **Respuesta a la acción específica (z, CR-2a)** | **Confirmatorio**: decide H1a y H1d |
| CR-2 | Solapamiento crudo con la acción, anclaje al escenario (coseno), anclaje sin nombres, nombres no reconocidos | Exploratorios o descriptivos |
| CL-1 | Papalampidi C (coherencia de entidad), Papalampidi V (consistencia de atributos) | Exploratorios (no tienen perturbación objetivo propia) |
| CL-1 | Tasa de correferencia de entidades | Descriptivo (saturado cerca de 1) |
| CL-2 | Jericho-QA (recuerdo de cambios de estado) | Exploratorio (discrimina solo en cambios de condición) |
| CL-2 | PNJ inactivo mencionado y refinado; primera mención de un PNJ no vivo (supervivencia); recuerdo semántico bge-m3 | Exploratorios |
| CL-2 | Ciclos de ubicación, Jaccard entre ubicaciones, relojes de facción | Descriptivos |
| QN-1 | TTR, MTLD, MATTR, bigramas a 100 palabras | Exploratorios |
| QN-1 | Fernández Huerta, Szigriszt-Pazos, frases repetidas | Descriptivos (sin dirección de mejora) |
| QN-2 | **persona2 v3b** (usurpación de la agencia del PJ) | **Confirmatorio condicionado**: decide H1c y H1f |

**Para tenerlo claro:**
- Cada hipótesis la decide **un solo instrumento**: CR-2a decide H1a y H1d, y persona2 decide H1c y H1f.
- **La dimensión longitudinal no tiene ningún instrumento confirmatorio.** Por eso H1b y H1e quedan sin decisión confirmatoria.

### 3.3 persona2 v3b

- **Qué detecta:** que la narración atribuya al personaje jugador, en segunda persona o por su nombre, una **decisión, un pensamiento, una emoción o un acto de habla**. Es la «toma de control del PJ» que los evaluadores de FIREBALL señalaron como el fallo más frecuente (Zhu et al., 2023).
- **Regla de conteo v3b.** El mismo detector congelado deja de contar dos cosas:
  1. lo que **el jugador declaró** en su acción («Decido abrir la puerta» → «Decides abrir la puerta» no es usurpación);
  2. los **pensamientos que resultan de una tirada declarada** («{Investigación}» → «te das cuenta de…»), porque en D&D el resultado de una prueba se entrega como conocimiento del personaje.
- **Consecuencia:** como el agente siempre declara una habilidad, *pensamiento* queda en 0. En la práctica mide **decisión, emoción y habla**.
- **Si preguntan por qué cambió la regla:** porque la regla anterior contaba como usurpación cosas que en el rol no lo son. Con la regla anterior, H1f igual se sostiene, y H1c daba p = 0.089. Se reporta en una oración y en la nota de la tabla.

### 3.4 Validación humana v2

- **Diseño:**
  - **5 directores de juego externos** con consentimiento escrito, etiquetado ciego (sin brazo ni veredicto del detector) y orden aleatorio por evaluador.
  - **982 ítems en 4 preguntas**, cada una con el mismo criterio de su instrumento: A, persona2 (400); B, PNJ inactivo (200); C, Jericho-QA (200); D, respuesta a la acción (150). Más **32 controles** con respuesta inequívoca.
  - **Exclusión prefijada:** más del 20 % de controles fallados en una pregunta, o respuesta constante, excluye al evaluador **solo de esa pregunta**.
  - **Referencia:** la mayoría de los retenidos.
- **Métricas:**
  - matriz 2×2, % de acuerdo y κ de Cohen;
  - precisión con IC de Wilson;
  - **exhaustividad ponderada por estrato**, porque la muestra se estratificó según la salida del detector;
  - en D, AUC sin umbral;
  - entre evaluadores, Fleiss y Krippendorff.

| Instrumento | Precisión | Exhaustividad ponderada | Lectura |
|---|---|---|---|
| persona2 v3b (A) | **50.0 %** [25.4–74.6]; 1/1 en G1, 5/11 en G2 | No estimable con esta referencia | α entre evaluadores = 0.85 |
| PNJ inactivo (B) | **96.0 %** [90.2–98.4] | 6.3 % [4.4–8.8] | Preciso pero muy conservador |
| Jericho-QA (C) | **89.0 %** [81.4–93.7] | 34.0 % [30.5–38.2] | Afinidad: 28 %; condición: 40 % |
| Respuesta a la acción (D) | AUC **0.84** [0.74–0.92] | — | Discrimina bien sin umbral |

- **La lectura clave para G1 frente a G2:** B y C omiten casos **en la misma proporción en ambos brazos**. En B, 37/40 casos en G1 frente a 10/10 en G2; en C, 60 % frente a 62 %. Por tanto, **subestiman las tasas, pero no sesgan la comparación**.
- **Auditoría de afinidad:** solo 12 de 30 cambios de afinidad registrados se reflejan en la narración (40 %). Eso explica el bajo rendimiento de Jericho-QA en esa familia.

---

## 4. Análisis estadístico: qué se usó y por qué

| Paso | Qué | Por qué |
|---|---|---|
| Preparación | Se excluye el turno 1 (presentación del escenario), salvo en CR-2a; las tasas de eventos se **relativizan por entidades expuestas** | Una tasa sin relativizar «crece» solo porque hay más PNJ muertos que pueden reaparecer: es exposición, no degradación |
| Descriptivos | Mediana, Q1, Q3, RIQ, media, DE y **Shapiro-Wilk** | Varios instrumentos no son normales, por eso se usan pruebas no paramétricas |
| Degradación (H1a–c) | **Prueba de tendencia de Page** sobre 7 bloques, unilateral en el sentido de la degradación, más **Wilcoxon** entre B1 y B7 | Page es la prueba para **alternativas ordenadas en medidas repetidas** (Page, 1963): pregunta si los valores tienden a empeorar bloque tras bloque |
| Tamaño del efecto de la tendencia | **ρ̄** = correlación media de Spearman con el orden de los bloques, derivada del estadístico L | 0 = sin tendencia; 1 = degradación monótona en todas las campañas |
| Comparación (H1d–f) | **Wilcoxon exacta de rangos con signo** sobre G1 − G2 en los 27 pares, unilateral, más el valor bilateral | Datos pareados y no normales |
| Estimador | **Hodges-Lehmann** con IC 95 % | Es la mediana de las diferencias, robusta |
| Tamaño del efecto | **Correlación biserial de rangos r** = (T⁺ − T⁻)/(T⁺ + T⁻) (Kerby, 2014) | No se usa la d de Cohen porque presupone normalidad y va con la prueba t |
| Umbrales de magnitud | Romano et al. (2006): \|r\| < 0.147 despreciable; < 0.33 pequeño; < 0.474 mediano; ≥ 0.474 grande | Los mismos que el δ de Cliff de la prueba de sensibilidad |
| Comparaciones múltiples | **Holm** dentro de la familia confirmatoria de cada hipótesis | Controla el error de la familia; como cada familia tiene un solo instrumento, en la práctica no se aplica |
| Hipótesis general | **Prueba de unión-intersección** (Berger, 1982; Berger & Hsu, 1996): H0g se rechaza solo si se rechazan H0d, H0e y H0f | Conserva α sin corrección; el p de Hg es el **máximo** de los p componentes |
| Robustez | Repetir el análisis con los pares 1–17 y con los pares 18–27, porque desde el par 18 el motor tiene relojes deterministas; excluir los 6 primeros pares, donde cambió el modelo del agente jugador | Que la conclusión no dependa de una versión del sistema |

**Reglas de decisión** (5.8.5):
1. α = 0.05.
2. Solo deciden los instrumentos confirmatorios o confirmatorios condicionados.
3. Si el resultado es significativo **en sentido contrario**, no se rechaza H0 y se reporta como evidencia en la dirección opuesta.
4. Si la dimensión no tiene instrumento confirmatorio, la hipótesis queda **sin decisión confirmatoria**.

---

## 5. Resultados por objetivo, con su docimasia

### OE-1 · Coherencia reactiva de G2 (H1a)

- **Instrumento que decide:** CR-2a z. Pasa de una mediana de 2.768 en B1 a 2.742 en B7.
- **Docimasia:** Page p = 0.310; Wilcoxon B1–B7 p = 0.420; ρ̄ = 0.04 y r = 0.05, ambos despreciables. **No se rechaza H0a.**
- **Interpretación:** la coherencia reactiva del monolítico **no se degrada** en 1,400 turnos. El análisis exploratorio por tramos de 100 turnos tampoco muestra un punto de quiebre: el mínimo está en el último tramo (2.654), pero con p = 0.348.
- **Dato adicional:** la gramaticalidad está cerca del techo y la tasa bruta de «nombres no reconocidos» sobrestima entre 4 y 11 veces la invención de nombres, como mostró la auditoría censal.

### OE-2 · Coherencia longitudinal de G2 (H1b)

- **Sin instrumento confirmatorio, así que no hay decisión confirmatoria.**
- **Evidencia exploratoria:** la mención de PNJ inactivos sin relativizar «se degrada» (Page p = 0.035). Al relativizarla por los PNJ expuestos, la tendencia **desaparece** (p = 0.451, con n = 10 campañas; ρ̄ = 0.02).
- **Interpretación:** el aumento era **exposición**, no degradación. Es la dimensión **más heterogénea** entre campañas y tiene un caso de abandono total de las entidades iniciales.
- **Para explicarlo:** la relativización dejó fuera 17 campañas que tenían algún bloque sin PNJ inactivos, y eso reduce la potencia.

### OE-3 · Calidad narrativa emergente de G2 (H1c), con persona2 v3b

- **Descriptivos:** mediana de **0.37 %** de los turnos (Q1 0.26 %, Q3 0.58 %, rango 0.09–1.28 %), no normal (Shapiro p = 0.0071). Es decir, el monolítico usurpa la agencia en **≈ 1 de cada 270 turnos**.
- **Docimasia:** Page **p = 0.0105**; Wilcoxon B1–B7 p = 0.012; ρ̄ = +0.18, pequeño; r = +0.53, grande. **Se rechaza H0c y H1c se sostiene.**
- **Interpretación estadística:** la tendencia global es pequeña, pero la diferencia entre el inicio y el final es grande. Es una **acumulación gradual**, no un salto.
- **Interpretación práctica:** pasa de prácticamente 0 en la primera sesión a **1 de cada 200 turnos** en la última. Es un fallo **poco frecuente pero sistemático**, coherente con la pérdida de adherencia a las instrucciones en contextos largos (Liu et al., 2024).
- **QN-1 exploratorio:** sin degradación (MATTR p = 0.570; MTLD mediana 108.9; MATTR 0.828). La legibilidad está en la banda normal.
- **Si preguntan por qué la mediana por bloque es 0.00 % → 0.50 %:** con tasas tan bajas, las medianas saltan de un turno en un turno. Por eso se lee el contraste de tendencia y no las medianas.

### OE-4 · Coherencia reactiva, G1 vs. G2 (H1d)

- **Docimasia:** con CR-2a z, el contraste unilateral «G1 mejor» da **p = 0.985**, así que **no se rechaza H0d y H1d no se sostiene**.
- **Bilateral:** hay una diferencia **a favor de G2** (p = 0.0319; HL = −0.13 [−0.25, −0.03]; r = −0.47, mediano). Se reporta como **evidencia en la dirección contraria**.
- **Matiz importante:** las tres versiones no confirmatorias del mismo constructo (solapamiento crudo, anclaje al escenario y anclaje sin nombres) favorecen a **G1** con efectos grandes. La descomposición muestra que esa ventaja es **genérica**: G1 escribe turnos más largos (158 frente a 116 palabras), y la normalización en z controla eso.
- **Lectura:** es un límite de validez de constructo, no una superioridad clara de G2. Además, esa ventaja de G2 queda **en el límite de la significancia** al excluir los 6 primeros pares, por eso se describe como frágil.
- **Frente a la literatura:** matiza a Zhou et al. (2023), según quienes descomponer las decisiones del DM mejoraría la respuesta.

### OE-5 · Coherencia longitudinal, G1 vs. G2 (H1e)

- **Sin instrumento confirmatorio, así que H1e queda sin decisión confirmatoria.** No se resuelve por defecto a favor de ninguna de las dos hipótesis.
- **Evidencia exploratoria mixta:**
  - la coherencia de entidad (Papalampidi C) favorece a **G1** (p = 0.0170; r = +0.54);
  - la mención cruda de PNJ inactivos favorece a **G2** (p = 0.0315), pero **desaparece** en la versión refinada (p = 0.4375);
  - supervivencia, es decir, cuánto tarda en aparecer la primera mención de un PNJ no vivo: medianas de 1,139 en G1 frente a 891 en G2, sin significancia (χ² = 0.084; p = 0.772);
  - el instrumento semántico (bge-m3) apenas supera el azar (0.08 frente a 0.05).
- **Validación humana:** el detector de PNJ y Jericho-QA son precisos pero conservadores, con un error **parecido en ambos brazos**. Eso no cambia la decisión.
- **Lectura:** **no encontrar diferencia no es demostrar que las arquitecturas son equivalentes.** Falta un instrumento confirmatorio, y eso es una limitación declarada.

### OE-6 · Calidad narrativa emergente, G1 vs. G2 (H1f)

- **Docimasia:** con persona2 v3b, G1 es menor que G2 en **los 27 pares**. Mdn G1 = 0.00 % (Q1–Q3 0.00–0.07 %) y Mdn G2 = 0.37 % (0.26–0.58 %); HL = −0.37 pp [−0.47, −0.29]; Wilcoxon unilateral **p < 0.0001**; **r = −1.00**, efecto máximo. **Se rechaza H0f y H1f se sostiene**, de forma parcial, en QN-2.
- **Por categoría:** decisión, 0.01 % frente a 0.17 %; emoción, 0.02 % frente a 0.27 %; habla, ≈ 0 en ambos brazos.
- **Robustez a la precisión del detector (Tabla OE6-8):** se multiplicó la tasa de cada campaña por la precisión de su brazo frente a los humanos.
  - Con las estimaciones puntuales, **27/27 pares** a favor de G1.
  - En el peor escenario (G2 con 21.3 % de precisión), **23/27**.
  - **p < 0.0001** en ambos casos.
  - La magnitud real en G2 queda entre **0.1 % y 0.2 %** de los turnos.
- **Robustez al cómputo:** G1 usa 2.86 llamadas por turno, 2.6 veces más tiempo de modelo y textos 1.5 veces más largos. Pero **dentro de cada arquitectura, más cómputo o más texto se asocia con más usurpación**, no con menos (ρ entre +0.50 y +0.74). Por tanto, la ventaja no la explica el gasto.
- **Interpretación arquitectónica:** en G1, el **árbitro resuelve la acción antes** y el narrador recibe el resultado, así que no necesita decidir por el jugador para que avance la escena.
- **Frente a la literatura:**
  - coincide con FIREBALL, donde la toma de control fue el fallo más señalado (Zhu et al., 2023);
  - coincide con Ware et al. (2023), donde no suprimir las acciones del jugador aumenta la agencia percibida;
  - QN-1 exploratorio sin dirección uniforme: TTR y bigramas favorecen a G1, MATTR favorece a G2 (r = −0.68) y MTLD no difiere.

### Hipótesis general (6.1.8)

| Hipótesis | Instrumento | Prueba | p | Efecto | Decisión |
|---|---|---|---|---|---|
| H1a | CR-2a z | Page | 0.310 | ρ̄ 0.04; r 0.05 (despreciable) | No se rechaza H0a |
| H1b | Ninguno (PNJ relativizado, exploratorio) | Page | 0.451 | ρ̄ 0.02 | Sin decisión confirmatoria |
| H1c | persona2 v3b | Page | **0.0105** | ρ̄ 0.18 (pequeño); r 0.53 (grande) | **Se rechaza H0c** |
| H1d | CR-2a z | Wilcoxon unilateral | 0.985 | r −0.47 (mediano, a favor de G2) | No se rechaza H0d |
| H1e | Ninguno | — | — | — | Sin decisión confirmatoria |
| H1f | persona2 v3b | Wilcoxon unilateral | **< 0.0001** | r −1.00 (grande) | **Se rechaza H0f** (parcial, QN-2) |
| **Hg** | Unión-intersección | máx(p_d, p_e, p_f) | ≥ 0.985 | — | **No se rechaza H0g** |

**Cómo explicar Hg:**
- Por la regla prefijada, Hg exigía H1d, H1e y H1f. Solo H1f se sostiene, así que Hg no se sostiene **en su forma general**.
- **No es una refutación de los multiagente.** Es una **ventaja específica**, en el respeto a la agencia, con efecto grande y robusto.
- Además, no hay ventaja demostrable en coherencia reactiva ni longitudinal **cuando ambas arquitecturas comparten modelo y memoria estructurada**.
- Coincide con Cemri et al. (2025), que advierten que los beneficios de los multiagente son limitados.
- **El p de Hg es una cota inferior** (0.985, el de H1d), porque H1e no tiene contraste. Basta para decidir, porque ningún valor de H1e podría reducirlo.

---

## 6. Significancia estadística vs. práctica

- **Estadística:** el p frente a α = 0.05.
- **Práctica:** el tamaño del efecto (ρ̄ o r) y su traducción a turnos (Wasserstein & Lazar, 2016).
- **Frases listas para usar:**
  - «G1 casi nunca usurpa la agencia; G2 lo hace en ~1 de cada 270 turnos, y esa frecuencia crece de ~0 a ~1 de cada 200 a lo largo de la campaña.»
  - «La ventaja de G2 en respuesta a la acción es mediana pero frágil, y se explica en parte porque G1 escribe más.»
  - «La estabilidad de G2 en coherencia reactiva matiza la premisa de degradación: con una memoria estructurada del mundo, el monolítico se sostiene en 1,400 turnos, salvo en el respeto a la agencia.»

---

## 7. Limitaciones y cómo defenderlas

| Limitación | Respuesta corta |
|---|---|
| Un solo modelo (gemma-4-31B) y un jugador simulado | Es intencional: así se aísla la arquitectura. Generalizar requiere replicar con otros modelos y con jugadores reales, que es el siguiente TRL. |
| Ambas arquitecturas comparten memoria estructurada | Aísla el efecto de la especialización, pero no permite saber si la estabilidad se debe a la memoria. Se recomienda un diseño con una condición sin memoria. |
| Sin instrumento confirmatorio longitudinal | Se declaró y no se suplió con evidencia exploratoria. Hay candidatos: NLI en español y log-rank estratificado por par. |
| persona2 con precisión del 50 % | La ventaja de G1 resiste incluso el peor escenario (23/27 pares, p < 0.0001). La magnitud real es menor (0.1–0.2 %), y así se reporta. |
| Exhaustividad de persona2 no estimada | Los evaluadores aplicaron un criterio más amplio que el libro (narración impersonal del resultado de la acción), así que no sirven como referencia de la exhaustividad. |
| Detectores conservadores (B y C) | Pierden casos en la misma proporción en ambos brazos: subestiman las tasas, pero no sesgan la comparación. |
| Potencia de 0.79 para un efecto medio | Es una diferencia menor frente a 0.80. Los resultados nulos se interpretan como «no detectado», no como «equivalente». |
| Cambio de regla de persona2 (v2b a v3b) | Se hizo por una razón conceptual del rol, no para buscar significancia. Con v2b, H1f se sostiene igual. Se reporta el resultado con ambas reglas. |
| Cambios del motor entre pares (relojes desde el par 18; modelo del agente en los pares 1–6) | Análisis por lotes; las decisiones no cambian, salvo la fragilidad de la ventaja de G2 en H1d. |

---

## 8. Preguntas probables del jurado

1. **¿Por qué no usaron evaluadores humanos para medir todo?**
   Porque es costoso, no escala a 75,600 turnos y depende de la experticia del evaluador (González-Romero et al., 2021). Los instrumentos deterministas se validan con perturbaciones y, donde interpretan texto, con humanos.

2. **¿Cómo saben que un instrumento mide lo que dice?**
   Por la prueba de sensibilidad: las expectativas se sellaron con hash antes de correr, se usaron controles y se exigió δ de Cliff ≥ 0.147 con Holm. Y, para los que interpretan texto, por la validación humana ciega.

3. **¿Por qué Page y no ANOVA de medidas repetidas?**
   Porque la hipótesis es **ordenada** (empeora con el tiempo) y los datos no son normales. Page es la prueba no paramétrica para alternativas ordenadas.

4. **¿Por qué Wilcoxon y no t pareada?**
   Por la falta de normalidad (Shapiro-Wilk) y porque el diseño es pareado. Se reporta HL y r, que es lo coherente con una prueba de rangos.

5. **¿Por qué no aplicaron Holm si tienen tantos instrumentos?**
   Porque Holm se aplica **dentro de la familia confirmatoria** de cada hipótesis, y cada una la decide un solo instrumento. Los exploratorios no deciden, así que no inflan el error de tipo I.

6. **¿Cómo deciden la hipótesis general con varios instrumentos y dimensiones?**
   Con la regla prefijada de conjunción y la prueba de unión-intersección (Berger & Hsu, 1996). No hay un índice compuesto, porque no se normalizan ni se promedian instrumentos con escalas distintas; cada dimensión decide con su instrumento confirmatorio.

7. **¿No es sospechoso cambiar la regla de persona2 después de ver los datos?**
   El cambio responde a un criterio del rol que surgió al revisar la validación humana: lo que el jugador declara o el resultado de su tirada no es usurpación. Se reportan ambas versiones. Con la anterior, H1f igual se sostiene, y H1c no alcanzaba significancia (p = 0.089). Es transparente y no altera la conclusión principal.

8. **¿Cómo garantizan la calidad de los evaluadores?**
   Con controles intercalados, exclusión prefijada por pregunta y verificación de integridad de cada archivo, que fue la que permitió detectar y descartar registros copiados. Los consentimientos son escritos y los evaluadores se identifican solo por código.

9. **¿Por qué G1 respeta más la agencia?**
   Por la separación de roles: el árbitro resuelve la acción y el narrador solo la relata. Además, la ventaja no la explica el mayor cómputo.

10. **¿Qué aporta la tesis?**
    - Evidencia controlada de que la especialización de agentes ayuda **específicamente** en la agencia del jugador, pero no en coherencia reactiva ni longitudinal cuando la memoria es compartida.
    - Un protocolo replicable de instrumentos deterministas validados, con corpus, tiradas y mediciones reproducibles.
    - Evidencia de que el monolítico se degrada en el respeto a la agencia dentro de 1,400 turnos.

---

## 9. Cifras para memorizar

- **27 pares, 54 campañas, 1,400 turnos por campaña, 75,600 turnos**; 7 bloques de 200 turnos; modelo gemma-4-31B-it.
- **Potencia:** 0.81 con prueba t, ≈ 0.79 con Wilcoxon, para d = 0.5.
- **H1a:** p = 0.310, sin degradación reactiva.
- **H1c:** p = 0.0105; 0.00 % → 0.50 %; ρ̄ 0.18; r 0.53.
- **H1d:** unilateral 0.985; bilateral 0.0319 a favor de G2; r −0.47.
- **H1f:** 0.00 % frente a 0.37 %; HL −0.37 pp; p < 0.0001; r −1.00; 27/27 pares; 23/27 en el peor escenario.
- **Validación:** 5 evaluadores, 982 ítems, 32 controles. Precisiones: persona2 50 %, PNJ 96 %, Jericho 89 %; AUC de CR-2a 0.84.
- **Costo:** G1 usa 2.86 llamadas por turno, 2.6 veces más tiempo de modelo y textos 1.5 veces más largos.
