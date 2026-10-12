---
title: "Rúbrica de Calidad Narrativa D&D-IA"
subtitle: "Instrumento de Evaluación de la Coherencia Narrativa en Sistemas de IA para Dungeons & Dragons"
author: "Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David"
---

# UNIVERSIDAD PRIVADA ANTENOR ORREGO

**Facultad de Ingeniería · Escuela de Ingeniería de Sistemas e IA**

## Rúbrica de Calidad Narrativa D&D-IA

### Instrumento de Evaluación de la Coherencia Narrativa en Sistemas de IA para Dungeons & Dragons

**Autores:** Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David

**Asesor:** Dr. Cueva Chavez, Walter Manuel

**Trujillo, Perú · 2025 · Versión 2.0**

---

## 1. Definición Operacional del Instrumento

La Rúbrica de Calidad Narrativa D&D-IA es un instrumento de evaluación estandarizado diseñado para medir la coherencia narrativa en campañas de *Dungeons & Dragons* generadas por sistemas de Inteligencia Artificial actuando como Dungeon Masters (DMs). El instrumento operacionaliza la variable dependiente "Coherencia Narrativa" en tres dimensiones medibles, cada una compuesta por dos indicadores específicos, evaluados mediante una escala ordinal Likert de 7 puntos.

El instrumento es una síntesis y adaptación de marcos de evaluación validados en investigaciones del dominio de IA para D&D y narrativa generativa, complementada con evidencia de confiabilidad inter-evaluador (Inter-Annotator Agreement, IAA) documentada en literatura peer-reviewed adicional para los indicadores de coherencia longitudinal.

> **Nota de contexto para esta entrega (2026-09-21).** Este instrumento fue el diseño original del estudio (panel de 5 evaluadores humanos, escala Likert). El 2026-09-14 el asesor aprobó un pivote metodológico hacia una batería de instrumentos 100% deterministas (ver carpeta `03_Resultados_y_Analisis`), motivado por restricciones de tiempo/presupuesto de coordinar el panel sobre las 27 parejas del corpus y por un objetivo editorial de envío a una revista indexada. La rúbrica se conserva como evidencia histórica/piloto (Anexo 2 de la tesis) y como marco teórico de origen de los indicadores (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2), pero ya no es el instrumento vigente de medición.

### 1.1 Fuentes de Definición Operacional y Teórica

| Fuente | Publicación | Aporte al instrumento |
|---|---|---|
| Zhu, Osgood & Callison-Burch (2023) — FIREBALL | ACL 2023, *Proceedings of the 61st Annual Meeting* | Indicadores de Sensatez, Arraigo contextual e Interés; protocolo de evaluación humana con DMs expertos de Avrae. |
| Zhou, Zhu, et al. (2022) — G-DRAGON / I Cast Detect Thoughts | EMNLP 2022 | Criterios de Fluency (fluidez), Groundedness (arraigo) y Goal-Fulfillment (reactividad a la agencia); métricas de acción-intento. |
| Pan, Andronis, et al. (2025) — Guiding Generative Storytelling with Knowledge Graphs | *International Journal of Human-Computer Interaction* (2025) | Marco de evaluación multidimensional (Consistency, Characters, Plot, Holistic, Theme, Dialogue) para narrativas de múltiples escenas, con anclaje en narratología clásica (Chatman, Egri, Bova, Bakhtin, Todorov). |

### 1.2 Fuentes de Confiabilidad Inter-Evaluador (IAA)

Los siguientes cuatro estudios peer-reviewed proveen evidencia empírica de confiabilidad inter-evaluador para los criterios narrativos análogos a los indicadores del instrumento. Esta evidencia complementa la definición operacional descrita en 1.1 y se utiliza como referente de validez por convergencia para el protocolo de calibración descrito en la Sección 6.

| Fuente | Publicación | Indicador respaldado | Coeficiente reportado |
|---|---|---|---|
| Callison-Burch, Tomar, Martin, Ippolito, Bailis & Reitter (2022) | EMNLP 2022, *Dungeons and Dragons as a Dialog Challenge for Artificial Intelligence* | CR-1, CR-2 | Randolph Kappa = 0.60 (acuerdo por pares = 0.80) |
| Callison-Burch, Tomar, Martin, Ippolito, Bailis & Reitter (2022) | EMNLP 2022 (ídem) | QN-1 | Tau de Kendall = 0.46 |
| Chen, Wang, Yu & Zhang (2023) | AAAI 2023, *Learning to Memorize Entailment and Discourse Relations for Persona-Consistent Dialogues* | CL-1 | Fleiss' Kappa = 0.671 |
| Yang, Klein, Peng & Tian (2023) | ACL 2023, *DOC: Improving Long Story Coherence With Detailed Outline Control* | CL-2 | Fleiss' Kappa = 0.19–0.22 (dimensión Coherent) |
| Zhou, Zhu, et al. (2022) | EMNLP 2022, G-DRAGON | QN-2 | IAA = 0.78 (instrumento completo, incluye Goal-Fulfillment) |

> **Nota metodológica.** El valor de confiabilidad reportado para CL-2 (0.19–0.22, interpretado como acuerdo "razonable" según Landis & Koch, 1977) es notablemente inferior al de los demás indicadores. Este patrón se documenta también en el predecesor de dicho estudio (Re3, Yang et al., 2022), cuyo acuerdo se reportó por debajo de 0.10, lo que indica que medir consistencia narrativa de largo alcance es una tarea de alta variabilidad de juicio humano incluso en estudios especializados del propio campo de generación narrativa. Esta característica documentada del constructo justifica la necesidad del protocolo de calibración inter-evaluador (Sección 6) como mecanismo de verificación empírica en el contexto específico de esta investigación.

---

## 2. Estructura del Instrumento

El instrumento está organizado en tres dimensiones y seis indicadores:

| # | Dimensión | Cód. | Indicador |
|---|---|---|---|
| 1 | Coherencia Reactiva | CR-1 | Fluidez y sentido lógico de la respuesta inmediata (Sensatez) |
| | | CR-2 | Arraigo contextual a la acción del jugador y al estado del mundo |
| 2 | Coherencia Longitudinal | CL-1 | Consistencia de personajes a largo plazo |
| | | CL-2 | Consistencia de eventos y estado del mundo a largo plazo |
| 3 | Calidad de la Coherencia Narrativa Emergente | QN-1 | Nivel de interés, creatividad y atractivo de la narrativa |
| | | QN-2 | Reactividad significativa a la agencia del jugador |

---

## 3. Escala de Medición

Cada indicador se evalúa con una escala Likert ordinal de 7 puntos:

| Puntaje | Nivel | Descripción general |
|---|---|---|
| 7 | Excelente | El indicador se cumple de forma perfecta, sin fallos observables. Supera las expectativas del estándar narrativo. |
| 6 | Muy Bueno | El indicador se cumple muy bien con fallos mínimos e irrelevantes para la calidad global. |
| 5 | Bueno | El indicador se cumple satisfactoriamente; los fallos son menores y no interrumpen la experiencia narrativa. |
| 4 | Aceptable | El indicador se cumple de forma básica; los fallos son notables pero no impiden la comprensión general. |
| 3 | Deficiente | El indicador se cumple parcialmente; hay fallos importantes que afectan la calidad de la experiencia. |
| 2 | Muy Deficiente | El indicador apenas se cumple; los fallos son graves y frecuentes, comprometiendo seriamente la narrativa. |
| 1 | Completamente Deficiente | El indicador no se cumple. La respuesta es incoherente, contradictoria o no tiene relación con el contexto. |

---

## 4. Rúbrica Detallada por Indicador

### Dimensión 1 — Coherencia Reactiva (Indicadores CR-1 y CR-2)

#### CR-1 — Fluidez y Sentido Lógico de la Respuesta Inmediata (Sensatez)

**Definición operacional:** Las respuestas generadas por el DM a lo largo de la campaña son: (a) cohesivas y comprensibles como enunciados independientes; (b) lógicamente consistentes con las reglas establecidas del juego y el contexto del mundo; (c) plausibles dado el estado inmediato anterior de la narrativa. No deben contener afirmaciones contradictorias entre sí ni con los hechos de cada turno.

**Fuentes:** Zhu, Osgood & Callison-Burch (2023). *FIREBALL: A Dataset of D&D Actual-Play with Structured Game State Information*. ACL 2023. [Criterio: "Does the response make sense?" — cohesive, consistent with rules, plausible given context]. Zhou, Zhu et al. (2022). *I Cast Detect Thoughts: Learning to Converse and Guide with Intents and Theory-of-Mind in D&D*. EMNLP 2022. [Criterio: Fluency]. Callison-Burch, Tomar, Martin, Ippolito, Bailis & Reitter (2022). *Dungeons and Dragons as a Dialog Challenge for Artificial Intelligence*. EMNLP 2022. [Randolph Kappa = 0.60, acuerdo por pares = 0.80, 6 evaluadores expertos con redundancia 3-way].

| N | Nivel | Descripción del desempeño observado |
|---|---|---|
| 7 | Excelente | Todas las respuestas son completamente cohesivas, lógicamente consistentes con las reglas del juego y perfectamente plausibles dado el contexto inmediato anterior. No se observa ninguna contradicción. |
| 6 | Muy Bueno | Las respuestas son muy cohesivas y lógicamente consistentes. Pueden presentarse fallos mínimos y aislados que no afectan la comprensión ni la plausibilidad general. |
| 5 | Bueno | Las respuestas son cohesivas y mayormente consistentes con las reglas y el contexto. Los fallos observados son menores y no interrumpen la experiencia narrativa. |
| 4 | Aceptable | Las respuestas son comprensibles en su mayoría, aunque se observan fallos notables de lógica o cohesión que no impiden el seguimiento general de la narrativa. |
| 3 | Deficiente | Se observan fallos importantes de cohesión o consistencia lógica que afectan apreciablemente la calidad de la experiencia narrativa en varios turnos. |
| 2 | Muy Deficiente | Los fallos de cohesión y consistencia lógica son graves y frecuentes, comprometiendo seriamente la comprensión de la narrativa. |
| 1 | Completamente Deficiente | Las respuestas son mayoritariamente incoherentes, contradictorias entre sí o respecto al contexto establecido. |

#### CR-2 — Arraigo Contextual a la Acción del Jugador y al Estado del Mundo

**Definición operacional:** Las respuestas están directamente ancladas en: (a) la acción o declaración específica del jugador en cada turno; (b) el estado actual del mundo de juego (HP, condiciones, posición, NPCs presentes). No ignoran ni reemplazan la entrada del jugador, no introducen entidades no establecidas previamente (alucinación), y no inician hilos narrativos irrelevantes o desconectados.

**Fuentes:** Zhu, Osgood & Callison-Burch (2023). FIREBALL: ACL 2023. [Criterio: "Is the response specific?" — flows logically from the specific action, logical next step in game progression; evaluators feedback: avoid hallucinating names/creatures not in game state]. Zhou, Zhu et al. (2022). I Cast Detect Thoughts. EMNLP 2022. [Criterio: Groundedness — entity overlap with context, "continuing the same story (grounded) vs. beginning a new story (NOT grounded)"]. Callison-Burch, Tomar, Martin, Ippolito, Bailis & Reitter (2022). EMNLP 2022. [Randolph Kappa = 0.60].

| N | Nivel | Descripción del desempeño observado |
|---|---|---|
| 7 | Excelente | Las respuestas están perfectamente ancladas. Abordan con precisión la acción específica del jugador, referencian el estado del mundo con exactitud (HP, condiciones, posición, entidades), e integran múltiples elementos establecidos sin introducir ningún elemento no fundamentado. |
| 6 | Muy Bueno | Las respuestas están muy bien ancladas. Reflejan fielmente la acción del jugador e integran coherentemente los elementos del estado del mundo. Pueden omitir un detalle menor sin introducir elementos ajenos al contexto. |
| 5 | Bueno | Las respuestas están claramente ancladas en la acción del jugador y en el estado del mundo. Hay conexiones explícitas reconocibles con el turno anterior. Puede haber omisiones de segundo nivel pero sin elementos inventados. |
| 4 | Aceptable | Las respuestas responden a la acción del jugador y se mantienen en el contexto general, aunque pueden omitir detalles relevantes del estado del mundo o hacer referencias genéricas en lugar de específicas. |
| 3 | Deficiente | Las respuestas responden parcialmente a la acción del jugador, pero introducen elementos no fundamentados, cambian el enfoque narrativo significativamente, o solo reconocen superficialmente la acción. |
| 2 | Muy Deficiente | Las respuestas apenas reconocen la acción del jugador. Los elementos narrativos son mayoritariamente genéricos o inventados (alucinaciones frecuentes). |
| 1 | Completamente Deficiente | Las respuestas ignoran completamente la acción del jugador, la contradicen directamente, o introducen personajes, objetos o situaciones que no existen en el estado del mundo establecido. |

---

### Dimensión 2 — Coherencia Longitudinal (Indicadores CL-1 y CL-2)

#### CL-1 — Consistencia de Personajes a Largo Plazo

**Definición operacional:** Los personajes jugadores (PJs) y no jugadores (PNJs) relevantes mantienen, a lo largo de múltiples sesiones, sus rasgos de personalidad, motivaciones, historia, capacidades, limitaciones y voz narrativa, tal como fueron establecidos anteriormente en la campaña. El evaluador detecta si el sistema contradice, ignora o altera sin justificación narrativa los atributos previamente definidos de cualquier personaje.

**Fuentes:** Pan, Andronis, et al. (2025). *Guiding Generative Storytelling with Knowledge Graphs*. IJHCI 2025. [Criterios: Characters — "believability, development, emotional depth", guiado por Egri (1972) y Bova (1994); Consistency — "logical alignment, preventing contradictions", guiado por Chatman (1980) y Rimmon-Kenan (2003)]. Zhu, Osgood & Callison-Burch (2023). FIREBALL: ACL 2023. [Hit Point Reasoning failure: los modelos narran incorrectamente la muerte de un objetivo con HP > 0, ejemplo de inconsistencia de estado de personaje]. Chen, Wang, Yu & Zhang (2023). *Learning to Memorize Entailment and Discourse Relations for Persona-Consistent Dialogues*. AAAI 2023. [Fleiss' Kappa = 0.671 para consistencia de persona, 4 evaluadores humanos, escala 1–3].

| N | Nivel | Descripción del desempeño observado |
|---|---|---|
| 7 | Excelente | Todos los personajes son completamente consistentes con lo establecido desde el inicio de la campaña. Su desarrollo es orgánico, creíble y sin contradicciones. La voz, motivaciones y capacidades son perfectamente coherentes con las sesiones previas. |
| 6 | Muy Bueno | Los personajes son muy consistentes en sus rasgos principales, historia y capacidades. Mantienen su voz y motivaciones a lo largo de la campaña. Una variación muy menor puede ser imprecisa pero no afecta la credibilidad general. |
| 5 | Bueno | Los personajes son consistentes en sus rasgos principales. Pequeñas variaciones en aspectos secundarios son justificables dentro del arco narrativo. La credibilidad general se mantiene. |
| 4 | Aceptable | Los personajes son mayormente consistentes, aunque se observa al menos una inconsistencia en un atributo secundario (vocabulario, un detalle biográfico, una capacidad menor). No afecta gravemente la credibilidad narrativa general. |
| 3 | Deficiente | Los personajes presentan inconsistencias notables en al menos un aspecto importante: motivación, capacidad relevante, historia o voz narrativa. Son detectables y afectan la credibilidad del personaje. |
| 2 | Muy Deficiente | Los personajes presentan múltiples inconsistencias graves. Atributos del personaje (nombre, clase, historia, motivaciones) son contradictorios con sesiones previas. La continuidad del personaje está seriamente comprometida. |
| 1 | Completamente Deficiente | Los personajes son completamente inconsistentes con lo establecido. Hay contradicciones flagrantes en atributos fundamentales (nombre incorrecto, clase cambiada, hechos biográficos contradictorios, capacidades inexistentes). |

#### CL-2 — Consistencia de Eventos y Estado del Mundo a Largo Plazo

**Definición operacional:** Los eventos previos de la campaña tienen consecuencias duraderas y verificables en el estado actual del mundo de juego. Los hechos establecidos (locaciones descubiertas, objetos obtenidos o perdidos, alianzas o enemistades, muertes de PNJs, cambios en facciones, logros o fracasos de misiones) son recordados y utilizados de forma consistente por el sistema en turnos y sesiones posteriores, sin que el sistema los ignore, contradiga o "reinicie" sin justificación narrativa.

**Fuentes:** Pan, Andronis, et al. (2025). Knowledge Graphs. IJHCI 2025. [Criterios: Consistency — preventing contradictions that break immersion; Plot — coherence of sequence of events; Structure — logical transitions between scenes, basado en Todorov (1971) y Freytag (1894)]. Zhu, Osgood & Callison-Burch (2023). FIREBALL: ACL 2023. [Game state tracking: hit points, alive/dead status, effects]. Yang, Klein, Peng & Tian (2023). *DOC: Improving Long Story Coherence With Detailed Outline Control*. ACL 2023. [Fleiss' Kappa = 0.19–0.22 para la dimensión Coherent, evaluación humana de coherencia narrativa de largo alcance en historias de varios miles de palabras].

| N | Nivel | Descripción del desempeño observado |
|---|---|---|
| 7 | Excelente | El sistema recuerda con total precisión todos los eventos significativos de la campaña. Las consecuencias narrativas son perfectamente consistentes a lo largo de las sesiones y enriquecen activamente la experiencia del jugador. |
| 6 | Muy Bueno | El sistema recuerda con precisión los eventos previos y los utiliza activamente para enriquecer la narrativa. Puede haber un detalle menor omitido, pero los aspectos cruciales del estado del mundo están correctamente representados. |
| 5 | Bueno | El sistema recuerda los eventos previos y los integra en la narrativa actual. El estado del mundo es consistente en sus aspectos principales, sin contradicciones activas. |
| 4 | Aceptable | El sistema recuerda la mayoría de los eventos importantes. Se observan errores aislados en detalles secundarios que no contradicen hechos centrales establecidos. |
| 3 | Deficiente | El sistema recuerda algunos eventos previos pero los aplica de forma inconsistente. Algunas contradicciones con el estado del mundo son evidentes. |
| 2 | Muy Deficiente | El sistema recuerda muy pocos eventos previos. Las contradicciones con el estado del mundo son frecuentes y graves. La progresión causal de la campaña está seriamente comprometida. |
| 1 | Completamente Deficiente | El sistema no recuerda eventos previos significativos. Introduce contradicciones directas con hechos establecidos. La continuidad causal de la campaña está completamente rota. |

---

### Dimensión 3 — Calidad de la Coherencia Narrativa Emergente (Indicadores QN-1 y QN-2)

#### QN-1 — Nivel de Interés, Creatividad y Atractivo de la Narrativa

**Definición operacional:** La narrativa generada va más allá de la respuesta mínimamente correcta. El evaluador mide si la respuesta: (a) utiliza lenguaje evocador, descriptivo o literario; (b) introduce elementos creativos, giros narrativos o "narrative hooks" que enriquecen la experiencia; (c) evita la repetición y la monotonía; (d) tiene la capacidad de capturar y mantener la atención del jugador.

**Fuentes:** Zhu, Osgood & Callison-Burch (2023). FIREBALL: ACL 2023. [Criterio: "How interesting is the response?" — catches attention, arouses curiosity, insightful, creative, or witty]. Pan, Andronis, et al. (2025). IJHCI 2025. [Criterios: Holistic, Theme, Dialogue, guiado por Bakhtin (2010)]. Callison-Burch, Tomar, Martin, Ippolito, Bailis & Reitter (2022). EMNLP 2022. [Tau de Kendall = 0.46 para la escala de interestingness, 6 evaluadores expertos].

| N | Nivel | Descripción del desempeño observado |
|---|---|---|
| 7 | Excelente | La narrativa es extraordinariamente creativa e interesante. Captura completamente la atención, utiliza lenguaje literario rico y evocador, introduce elementos narrativos memorables. Comparable con el trabajo de un DM humano excepcional. |
| 6 | Muy Bueno | La narrativa es muy interesante y creativa. Utiliza recursos literarios reconocibles, introduce sorpresas o profundidad narrativa que enriquecen significativamente la experiencia. |
| 5 | Bueno | La narrativa es interesante. Utiliza lenguaje descriptivo, introduce al menos un elemento creativo o un hook narrativo que enriquece la experiencia más allá del mínimo requerido. |
| 4 | Aceptable | La narrativa cumple con los requisitos básicos de una respuesta de DM pero no destaca ni sorprende. El lenguaje es funcional pero plano. |
| 3 | Deficiente | La narrativa tiene algún elemento de interés, pero es mayormente predecible, repetitiva o genérica. El lenguaje es pobre o demasiado mecánico. |
| 2 | Muy Deficiente | La narrativa es muy básica y predecible. Carece de elementos creativos o de interés. El lenguaje es muy plano, formulaico o repetitivo. |
| 1 | Completamente Deficiente | La narrativa es completamente insulsa, genérica o incoherente. No genera ningún interés ni cumple ningún estándar básico de calidad literaria. |

#### QN-2 — Reactividad Significativa a la Agencia del Jugador

**Definición operacional:** El sistema reconoce y responde de forma significativa y coherente a las decisiones del jugador, incluyendo acciones inesperadas, caóticas o no anticipadas, de modo que: (a) las decisiones del jugador tienen consecuencias narrativas reales y visibles en la respuesta; (b) el sistema no usurpa la agencia del jugador haciéndole hablar, moverse o actuar sin su control explícito; (c) la respuesta no es genérica sino específicamente generada en función de la elección particular del jugador.

**Fuentes:** Zhou, Zhu et al. (2022). I Cast Detect Thoughts. EMNLP 2022. [Criterio: Goal-Fulfillment / Action Matching — "guidance leads player to perform the intended action"; IAA = 0.78]. Zhu, Osgood & Callison-Burch (2023). FIREBALL: ACL 2023. [Evaluators feedback: "Removing Player Agency" — "several narrations had player characters acting or speaking in response to the action. That's something I would never want a human DM doing unprompted"].

| N | Nivel | Descripción del desempeño observado |
|---|---|---|
| 7 | Excelente | El sistema responde de forma excepcional a cualquier acción del jugador. Las acciones más inesperadas o caóticas son integradas brillantemente en la narrativa, generando consecuencias específicas, creativas y coherentes. Nunca usurpa la agencia del jugador. |
| 6 | Muy Bueno | El sistema responde de forma muy significativa a la acción del jugador. Incluso ante acciones caóticas o inesperadas, genera respuestas coherentes y ricas que reflejan la especificidad de la elección. No usurpa la agencia del jugador. |
| 5 | Bueno | El sistema responde de forma significativa a la acción del jugador. Las decisiones tienen consecuencias claras y narrativamente relevantes visibles en la respuesta. |
| 4 | Aceptable | El sistema responde de forma adecuada a la acción del jugador. La acción tiene consecuencias básicas reconocibles. La respuesta podría mejorar en especificidad pero cumple el estándar mínimo de reactividad. |
| 3 | Deficiente | El sistema reconoce la acción del jugador pero responde de forma genérica o parcial, sin consecuencias narrativas reales o específicas. |
| 2 | Muy Deficiente | El sistema reconoce muy superficialmente la acción del jugador. La respuesta es esencialmente genérica y no refleja la especificidad de la elección. |
| 1 | Completamente Deficiente | El sistema ignora completamente la acción del jugador, la contradice, o usurpa su agencia (hace hablar, moverse o actuar al personaje del jugador sin su control explícito). |

---

## 5. Hoja de Puntuación — Formulario de Registro

**Campaña / Par N°:** _______________________

**Sistema evaluado:** ☐ G1 — Multiagente-RAG &nbsp;&nbsp;&nbsp; ☐ G2 — Monolítico-RAG

**Evaluador (cód.):** _______________________ &nbsp;&nbsp;&nbsp; **Fecha:** _______________________

| Código | Dimensión | Indicador | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|---|---|---|
| CR-1 | Coherencia Reactiva | Fluidez y sentido lógico (Sensatez) | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| CR-2 | Coherencia Reactiva | Arraigo contextual | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| CL-1 | Coherencia Longitudinal | Consistencia de personajes | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| CL-2 | Coherencia Longitudinal | Consistencia de eventos / estado del mundo | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| QN-1 | Calidad Narrativa Emergente | Interés y creatividad narrativa | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| QN-2 | Calidad Narrativa Emergente | Reactividad a la agencia del jugador | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**Puntuación total de la campaña** (Σ CR-1 + CR-2 + CL-1 + CL-2 + QN-1 + QN-2) **= _______ / 42**

**Observaciones cualitativas del evaluador:**

_______________________________________________________________________

_______________________________________________________________________

_______________________________________________________________________

---

## 6. Instrucciones para el Panel de Evaluadores

**1. Perfil del evaluador.** El panel de evaluación está compuesto por cinco Dungeon Masters (DMs) con un mínimo de cinco años de experiencia activa en D&D 5e. Se priorizará la experiencia en el dominio narrativo y mecánico del juego sobre el conocimiento técnico de IA, dado que el objeto de evaluación es la calidad del artefacto narrativo resultante, independientemente del método computacional que lo generó.

**2. Condiciones de evaluación.** Protocolo de doble ciego: los evaluadores no sabrán en ningún momento qué arquitectura (G1 Multiagente o G2 Monolítico) generó cada transcripción. Las muestras serán anonimizadas bajo un código neutral ("Código de historia") y presentadas en lotes aleatorizados para mitigar el sesgo de orden.

**3. Objeto de evaluación.** Cada evaluador recibirá la transcripción completa de una campaña generada por el sistema DM de IA y la evaluará como una unidad narrativa holística. Para los indicadores CR-1 y CR-2, dado que capturan el patrón de respuesta del sistema a lo largo de toda la campaña, el evaluador podrá apoyarse en la revisión de una muestra representativa de turnos para fundamentar su puntuación global del indicador.

**4. Protocolo de calibración.** Previo a la evaluación formal, el panel completo realizará una sesión de calibración evaluando de forma independiente dos transcripciones de práctica. Se calculará el Coeficiente de Correlación Intraclase (ICC) por indicador. Si el ICC global es igual o superior a 0.75, se procede a la evaluación formal del corpus completo. Si el ICC global es inferior a 0.75, se realizará una segunda sesión de calibración con discusión guiada de los casos divergentes, sin revelar los puntajes finales individuales hasta alcanzar consenso sobre la interpretación del descriptor. Si tras la segunda sesión algún indicador específico mantiene un ICC inferior a 0.65, dicho indicador será reportado con su valor de confiabilidad real y sus resultados serán interpretados con la limitación correspondiente declarada explícitamente en la discusión de resultados.

**5. Registro de la evaluación.** Cada evaluador completa una Hoja de Puntuación (Sección 5) por cada campaña asignada, marcando el nivel correspondiente para cada uno de los seis indicadores y registrando observaciones cualitativas que respalden su juicio, particularmente en los casos de puntuación extrema (1–2 o 6–7).

---

## 7. Tabla de Correspondencia con las Fuentes

| Cód. | Indicador | FIREBALL (Zhu et al., 2023) | G-DRAGON (Zhou et al., 2022) | Knowledge Graphs (Pan et al., 2025) | Fuente de confiabilidad (IAA) |
|---|---|---|---|---|---|
| CR-1 | Fluidez y sensatez | "Does the response make sense?" (Sense) | Fluency Evaluation | — | Callison-Burch et al. (2022): Randolph Kappa = 0.60 |
| CR-2 | Arraigo contextual | "Is the response specific?" (Specific) | Groundedness Evaluation | — | Callison-Burch et al. (2022): Randolph Kappa = 0.60 |
| CL-1 | Consistencia de personajes | Game state tracking (HP, efectos, status) | — | Characters / Consistency | Chen et al. (2023): Fleiss' Kappa = 0.671 |
| CL-2 | Consistencia de eventos/mundo | World-state grounding | Groundedness (continuidad narrativa) | Consistency / Plot | Yang et al. (2023): Fleiss' Kappa = 0.19–0.22 |
| QN-1 | Interés y creatividad | "How interesting is the response?" (1–10) | — | Holistic / Theme / Dialogue | Callison-Burch et al. (2022): Tau de Kendall = 0.46 |
| QN-2 | Reactividad a la agencia | Player agency feedback | Goal-Fulfillment / Action Matching | — | Zhou et al. (2022): IAA = 0.78 |

---

## Referencias

Callison-Burch, C., Tomar, G. S., Martin, L. J., Ippolito, D., Bailis, S., & Reitter, D. (2022). Dungeons and Dragons as a Dialog Challenge for Artificial Intelligence. *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing*, 9379–9393. https://aclanthology.org/2022.emnlp-main.637/

Chen, R., Wang, J., Yu, L.-C., & Zhang, X. (2023). Learning to Memorize Entailment and Discourse Relations for Persona-Consistent Dialogues. *Proceedings of the AAAI Conference on Artificial Intelligence*. https://arxiv.org/abs/2301.04871

Pan, Z., Andronis, A., Hayek, E., Wilkinson, O. A. P., Lasy, I., Parry, A., Gadney, G., Smith, T. J., & Grierson, M. (2025). Guiding Generative Storytelling with Knowledge Graphs. *International Journal of Human-Computer Interaction*. https://doi.org/10.1080/10447318.2025.2603634

Yang, K., Klein, D., Peng, N., & Tian, Y. (2023). DOC: Improving Long Story Coherence With Detailed Outline Control. *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 3378–3465. https://aclanthology.org/2023.acl-long.190/

Zhou, P., Zhu, A., Hu, J., Pujara, J., Ren, X., Callison-Burch, C., Choi, Y., & Ammanabrolu, P. (2022). I Cast Detect Thoughts: Learning to Converse and Guide with Intents and Theory-of-Mind in Dungeons and Dragons. *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing*, 4636–4655. https://aclanthology.org/2022.emnlp-main

Zhu, A., Aggarwal, K., Feng, A., Martin, L. J., & Callison-Burch, C. (2023). FIREBALL: A Dataset of Dungeons and Dragons Actual-Play with Structured Game State Information. *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 4171–4193. https://aclanthology.org/2023.acl-long.229/

---

*Rúbrica D&D-IA v2.0 · Proyecto de Tesis UPAO 2025 · Marin Yupanqui & Mostacero Cieza · Asesor: Dr. Cueva Chavez*
