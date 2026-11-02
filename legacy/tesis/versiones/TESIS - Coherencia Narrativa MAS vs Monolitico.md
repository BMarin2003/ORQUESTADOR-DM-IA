**UNIVERSIDAD PRIVADA ANTENOR ORREGO**

**FACULTAD DE INGENIERÍA**  
**ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS E INTELIGENCIA ARTIFICIAL**

***PROYECTO DE TESIS PARA OPTAR EL TÍTULO PROFESIONAL DE***  
***INGENIERO DE SISTEMAS E INTELIGENCIA ARTIFICIAL***

| Comparación de la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos |
| :---: |

***Línea de investigación:***  
*Sistemas Inteligentes*  
***Autores:***  
*Marin Yupanqui, Bryan Arturo*  
*Mostacero Cieza, Luis David*  
				***Jurado Evaluador:***

***Asesor:***  
*Cueva Chavez, Walter Manuel*  
*Código Orcid: [https://orcid.org/0000-0001-9660-6354](https://orcid.org/0000-0001-9660-6354)*

* **TRUJILLO, PERÚ***  
***2026***

**Fecha de sustentación:**  
MARCAR MODALIDAD:  **P**  SP  D

**UNIVERSIDAD PRIVADA ANTENOR ORREGO**

**FACULTAD DE INGENIERÍA**  
**ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS E INTELIGENCIA ARTIFICIAL**

***PROYECTO DE TESIS PARA OPTAR EL TÍTULO PROFESIONAL DE***  
***INGENIERO DE SISTEMAS E INTELIGENCIA ARTIFICIAL***

| Comparación de la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos |
| :---: |

***Línea de investigación:***  
*Sistemas Inteligentes*  
***Autores:***  
*Marin Yupanqui, Bryan Arturo*  
*Mostacero Cieza, Luis David*  
				***Jurado Evaluador:***

***Asesor:***  
*Cueva Chavez, Walter Manuel*  
*Código Orcid: [https://orcid.org/0000-0001-9660-6354](https://orcid.org/0000-0001-9660-6354)*

* **TRUJILLO, PERÚ***  
***2026***

**Fecha de sustentación:**  
MARCAR MODALIDAD:  **P**  SP  D

# **Dedicatoria**

# **Agradecimiento** {#agradecimiento}

A la Universidad Privada Antenor Orrego, por facilitar el acceso a la infraestructura académica y los recursos bibliográficos necesarios para el desarrollo de esta investigación.

Al Mgtr. Walter Manuel Cueva Chávez, por su asesoría técnica y metodológica, cuya orientación fue determinante para la estructuración del diseño experimental y el análisis de la arquitectura MAS propuesta.

A los docentes del Programa de Estudio de Ingeniería de Sistemas e Inteligencia Artificial, por los conocimientos impartidos que sirvieron de base teórica para entrenar y orquestar los diferentes modelos.

A todas las personas e instituciones que, de manera directa o indirecta, proporcionaron la información y el entorno académico requeridos para la validación de este estudio.  
**Los autores.**

# **Resumen** {#resumen}

El objetivo de esta investigación es comparar la coherencia narrativa de las campañas de Dungeons & Dragons generadas por sistemas multiagente (MAS) frente a los sistemas de inteligencia artificial monolíticos. El problema identificado se centra en las limitaciones de los sistemas monolíticos a la hora de mantener la coherencia narrativa a largo plazo, lo que se pone de manifiesto en la pérdida de contexto, las contradicciones lógicas y la inconsistencia estilística en campañas interactivas prolongadas. El estudio aborda una laguna fundamental en la bibliografía: la ausencia de evidencia comparativa empírica entre ambas arquitecturas dentro del ámbito específico de los juegos de rol de mesa.

La metodología consiste en una investigación aplicada con un enfoque cuantitativo y un diseño experimental puro que utiliza medidas repetidas con pares emparejados. Se generarán veintisiete pares de campañas en condiciones controladas, estandarizando el modelo de lenguaje base (LLM) y la técnica RAG en ambas arquitecturas para aislar la gestión narrativa como única variable independiente. La evaluación la llevará a cabo un panel de cinco Dungeon Masters expertos en condiciones de doble ciego, aplicando la rúbrica de calidad narrativa D\&D-AI (adaptada de Zhu et al., 2023; Zhou et al., 2022; Pan et al., 2025), que mide la coherencia en tres dimensiones: coherencia reactiva, coherencia longitudinal y calidad narrativa emergente, utilizando una escala Likert de 1 a 7\. Se espera que los resultados proporcionen evidencia empírica sobre qué arquitectura produce campañas más coherentes, contribuyendo al diseño de Dungeon Masters virtuales de alta calidad y al campo de la narratología computacional.

**Palabras clave**: sistemas multiagente; sistemas monolíticos; coherencia narrativa; Dungeons & Dragons; inteligencia artificial generativa. 

# **Abstract** {#abstract}

De acuerdo con el cumplimiento de las disposiciones del reglamento de grados y títulos de la Universidad Privada Antenor Orrego, exponemos a vuestra consideración la tesis titulada: Comparación de la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos. Desarrollado con el fin de obtener el título de Ingeniero de Sistemas e Inteligencia Artificial. El objetivo principal es comparar la coherencia narrativa de las campañas de Dungeons & Dragons generadas por una arquitectura de sistema multiagente frente a una arquitectura monolítica, evaluando sus dimensiones de Coherencia Reactiva, Coherencia Longitudinal y Calidad de la Narrativa Emergente mediante un diseño experimental controlado con pares emparejados y un panel de expertos bajo condiciones de doble ciego. A ustedes miembros del jurado, mostramos nuestro especial y mayor reconocimiento por el dictamen que se haga merecedor y correspondiente del presente trabajo.

La generación automática de narrativas interactivas representa uno de los desafíos más ambiciosos en la intersección de la inteligencia artificial y el entretenimiento digital. Dungeons & Dragons (D\&D), el juego de rol de mesa más influyente de la historia, se ha convertido en un banco de pruebas paradigmático para estos sistemas por su exigencia de coherencia narrativa sostenida, agencia del jugador y creatividad emergente. La evolución tecnológica reciente, impulsada por los modelos de lenguaje a gran escala (LLMs) y las arquitecturas de sistemas multiagente (MAS), ha abierto posibilidades sin precedentes para digitalizar el rol del Dungeon Master, pero también ha evidenciado limitaciones críticas en la coherencia a largo plazo. El debate central que motiva esta investigación gira en torno a si la distribución de responsabilidades narrativas entre agentes especializados (MAS) ofrece ventajas empíricamente verificables sobre los enfoques monolíticos optimizados con RAG.

**Palabras clave**: sistemas multiagente; sistemas monolíticos; coherencia narrativa; Dungeons & Dragons; inteligencia artificial generativa. 

# **Presentación** {#presentación}

Señores miembros del jurado:

	De acuerdo con el cumplimiento de las disposiciones del reglamento de grados y títulos de la Universidad Privada Antenor Orrego, exponemos a vuestra consideración la tesis titulada: “Comparación de la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos”.

	Desarrollado con el fin de obtener el título de Ingeniero de Sistemas e Inteligencia Artificial. El objetivo principal es Comparar la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos, con el fin de saber que arquitectura puede soportar una carga tan extensa de conversación e historia sin alucinar.

	A ustedes miembros del jurado, mostramos nuestro especial y mayor reconocimiento por el dictamen que se haga merecedor y correspondiente del presente trabajo.

|  |  |  |
| ----- | ----- | ----- |
| Marin Yupanqui, Bryan Arturo |  | Mostacero Cieza, Luis David |
| DNI: ORCID: |  | DNI: ORCID: |

# **Índice de contenidos** {#índice-de-contenidos}

[**Dedicatoria**	ii](#heading=h.t6lblk5irim5)

[**Agradecimiento**	iii](#agradecimiento)

[**Resumen**	iv](#resumen)

[**Abstract**	v](#abstract)

[**Presentación**	vi](#presentación)

[**Índice de contenidos**	vii](#índice-de-contenidos)

[**Índice de tablas**	ix](#índice-de-tablas)

[**Índice de figuras**	x](#índice-de-figuras)

[**1\.**	**Introducción**	11](#introducción)

[1.1.	Contexto y antecedentes	11](#contexto-y-antecedentes)

[1.2.	Descripción y justificación del estudio	12](#descripción-y-justificación-del-estudio)

[1.3.	Organización del documento	12](#organización-del-documento)

[**2\.**	**Planteamiento del problema de investigación**	13](#planteamiento-del-problema-de-investigación)

[2.1.	Descripción y delimitación del problema	13](#descripción-y-delimitación-del-problema)

[2.1.1.	Formulación del problema	13](#formulación-del-problema)

[2.1.2.	Problema central del estudio	13](#problema-central-del-estudio)

[2.2.	Objetivos de la investigación	13](#objetivos-de-la-investigación)

[2.2.1.	Objetivo general	13](#objetivo-general)

[2.2.2.	Objetivos específicos	14](#objetivos-específicos)

[2.3.	Importancia del estudio	14](#importancia-del-estudio)

[2.4.	Justificación de la investigación	14](#justificación-de-la-investigación)

[2.5.	Limitaciones del estudio	15](#limitaciones-del-estudio)

[**3\.**	**Marco teórico**	16](#marco-teórico)

[3.1.	Marco histórico	16](#marco-histórico)

[3.2.	Investigaciones antecedentes relacionadas con el tema	16](#investigaciones-antecedentes-relacionadas-con-el-tema)

[3.3.	Base teórica – científica	17](#base-teórica)

[3.4.	Definición de términos básicos	17](#definición-de-términos-básicos)

[**4\.**	**Hipótesis y variables**	19](#hipótesis-y-variables)

[4.1.	Supuestos básicos	19](#supuestos-básicos)

[4.2.	Hipótesis general	19](#hipótesis-general)

[4.3.	Hipótesis específicas:	20](#hipótesis-específicas)

[4.4.	Variables	21](#variables)

[4.5.	Matriz de consistencia	22](#matriz-de-consistencia)

[**5\.**	**Marco metodológico**	23](#marco-metodológico)

[5.1.	Tipo de investigación	23](#tipo-de-investigación)

[5.2.	Nivel de madurez tecnológica	23](#nivel-de-madurez-tecnológica)

[5.3.	Método de investigación	24](#método-de-investigación)

[5.4.	Diseño del estudio	24](#diseño-del-estudio)

[5.5.	Población y muestra	25](#población-y-muestra)

[5.6.	Técnicas e instrumentos de recolección de datos	25](#técnicas-e-instrumentos-de-recolección-de-datos)

[5.7.	Procedimientos de ejecución del estudio	25](#procedimientos-de-ejecución-del-estudio)

[5.8.	Técnicas de procesamiento y análisis de datos	26](#técnicas-de-procesamiento-y-análisis-de-datos)

[**6\.**	**Presentación de resultados**	27](#presentación-de-resultados)

[6.1.	Resultados de la investigación	27](#heading=h.yyef8g1wfjga)

[6.2.	Conclusiones	29](#heading=h.ff00mguct51c)

[6.3.	Recomendaciones	31](#heading=h.kdf96gajboa4)

[**7\.**	**Referencias bibliográficas**	33](#referencias-bibliográficas)

[**8\.**	**Anexos**	34](#anexos)

# **Índice de tablas** {#índice-de-tablas}

[Tabla 1\. Operacionalización de variables.	17](#heading=h.1w4usnhlpiaf)  
[Tabla 2\. Matriz de consistencia de la investigación.	18](#heading=h.wzqpw3b50hb7)

# **Índice de figuras** {#índice-de-figuras}

[Figura 1\. Diseño con posprueba únicamente y grupo de control.	24](#heading=h.ro0bdg935mkj)

1. # Introducción {#introducción}

   1. ## Contexto y antecedentes {#contexto-y-antecedentes}

   Los antecedentes internacionales relevantes abarcan desde los primeros sistemas de planificación narrativa basados en IA clásica [(George, 2015; Laclaustra et al., 2014\)](https://www.zotero.org/google-docs/?z8X9H1) hasta las propuestas más recientes como StoryWriter [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?xR4tqi), que demuestran cómo equipos de agentes pueden producir historias largas y coherentes. Trabajos fundamentales como Callison-Burch et al. [(2022)](https://www.zotero.org/google-docs/?NvTheB) establecieron D\&D como desafío de diálogo para la IA, mientras que Valdivia & Burelli [(2025)](https://www.zotero.org/google-docs/?DT8ATG) identificaron la brecha de evaluación en narrativas co-creadas. En el ámbito local y nacional no existen antecedentes directos, lo que subraya la relevancia pionera de esta investigación en el contexto peruano.

   En este contexto, el presente estudio surge de la necesidad urgente de evidencia empírica que respalde o refute la superioridad teórica de los sistemas multiagente para la generación narrativa coherente. Mientras la literatura postula las ventajas de los MAS para gestionar la memoria a largo plazo en tareas creativas [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?49qL0K), estas afirmaciones carecen de validación experimental frente a los cada vez más potentes sistemas monolíticos basados en LLMs [(Binggang & Masaki, 2024\)](https://www.zotero.org/google-docs/?uBZzlP). La justificación teórica radica en llenar este vacío empírico mediante la comparación directa y controlada de ambas arquitecturas dentro del dominio de D\&D, aportando al conocimiento sobre cómo las decisiones de diseño arquitectónico impactan propiedades emergentes complejas como la coherencia narrativa. Desde el punto de vista práctico, esta investigación provee a desarrolladores de videojuegos y sistemas de IA para entretenimiento con datos objetivos para sus decisiones de diseño, acelerando la creación de Dungeon Masters virtuales de alta calidad capaces de democratizar el acceso al juego de rol.

2. ## Descripción y justificación del estudio {#descripción-y-justificación-del-estudio}

   A pesar del gran potencial de los LLMs para actuar como Dungeon Masters, la generación de narrativas extensas y de alta calidad sigue siendo un desafío formidable [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?ZPwpmv). Los sistemas monolíticos sufren de pérdida de contexto y generan contradicciones lógicas que afectan la credibilidad de la historia [(Callison-Burch et al., 2022\)](https://www.zotero.org/google-docs/?pnfg7h). Las arquitecturas MAS se proponen como solución prometedora al distribuir responsabilidades narrativas entre agentes especializados [(Barambones et al., 2023\)](https://www.zotero.org/google-docs/?VSb7XT), mejorando la consistencia y la memoria a largo plazo [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?Yr9CYc). Sin embargo, existe una marcada ausencia de estudios empíricos que comparen de forma controlada la coherencia narrativa de un MAS frente a un sistema monolítico con RAG optimizado en el dominio de D\&D, vacío que esta investigación busca cerrar mediante la siguiente formulación del problema: ¿es superior la coherencia narrativa de campañas de Dungeons & Dragons generadas por sistemas multiagente en comparación con sistemas monolíticos de inteligencia artificial?

   3. ## Organización del documento {#organización-del-documento}

   El presente documento se organiza en seis capítulos principales. El Capítulo 2 desarrolla el planteamiento del problema, incluyendo la formulación del problema central, los objetivos general y específicos, la importancia del estudio, su justificación en dimensiones teórica, práctica, metodológica y social, así como las limitaciones identificadas. A continuación, el Capítulo 3 presenta el marco teórico, con el marco histórico, los antecedentes internacionales, la base teórica-científica sobre coherencia narrativa y sistemas de IA, y la definición de términos básicos. Sobre esa base conceptual, el Capítulo 4 establece las hipótesis y variables, incluyendo los supuestos básicos, la hipótesis general y específicas, la operacionalización de variables y la matriz de consistencia. Una vez definido el aparato hipotético, el Capítulo 5 detalla el marco metodológico: tipo y método de investigación, diseño experimental, población y muestra, técnicas e instrumentos, procedimientos y análisis estadístico. Finalmente, el Capítulo 6 recoge la presentación de resultados, las conclusiones y las recomendaciones derivadas de la ejecución del estudio.

2. # Planteamiento del problema de investigación {#planteamiento-del-problema-de-investigación}

   1. ## Descripción y delimitación del problema {#descripción-y-delimitación-del-problema}

   A pesar del gran potencial de los LLMs para actuar como Dungeon Masters, la generación de narrativas extensas de alta calidad sigue siendo un desafío formidable [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?azQh1l) dado que uno de los obstáculos más significativos es mantener la coherencia narrativa a lo largo de campañas que pueden durar múltiples sesiones [(De Lima et al., 2023\)](https://www.zotero.org/google-docs/?raBq49).

   Actualmente, los sistemas monolíticos sufren de pérdida de contexto generando contradicciones lógicas que terminan afectando la credibilidad de la historia y la capacidad de seguir el estado del juego [(Callison-Burch et al., 2022\)](https://www.zotero.org/google-docs/?imsedJ), en consecuencia las arquitecturas de sistemas multiagente (MAS) se proponen como una solución prometedora a este problema [(Barambones et al., 2023\)](https://www.zotero.org/google-docs/?LcqMx8) dado que estos sistemas distribuyen las responsabilidades narrativas entre agentes especializados para mejorar la consistencia y la memoria a largo plazo [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?vOpse9).

      1. ### Formulación del problema {#formulación-del-problema}

   ¿Es superior la coherencia narrativa de campañas de Dungeons & Dragons generadas por sistemas multiagente en comparación con sistemas monolíticos de inteligencia artificial?

      2. ### Problema central del estudio {#problema-central-del-estudio}

   Los LLMs poseen un notable potencial para emular el rol de un Dungeon Master; sin embargo, generar campañas narrativamente coherentes a largo plazo constituye un desafío técnico significativo, dado que los sistemas monolíticos demuestran limitaciones críticas en campañas extensas incluso cuando incorporan RAG. Estas limitaciones incluyen la pérdida de coherencia causal ante acciones caóticas del jugador, así como la degradación de memoria y la inconsistencia estilística que se acumulan a lo largo de la partida [(De Lima et al., 2023\)](https://www.zotero.org/google-docs/?lsfwnh), lo cual termina por desfragmentar la experiencia del jugador y socavar la credibilidad del mundo narrativo. Frente a este panorama, se han propuesto arquitecturas de Sistemas Multiagente (MAS) que distribuyen las responsabilidades entre agentes especializados con el fin de mejorar la coherencia [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?VnkPaM); no obstante, existe una marcada ausencia de estudios empíricos controlados en el dominio de Dungeons & Dragons que comparen un sistema MAS frente a un sistema monolítico con RAG optimizado, por lo que no se ha documentado si dicha especialización mejora efectivamente la coherencia interactiva. Esta situación deja una brecha fundamental entre la propuesta teórica y su validación experimental, y evidencia además la ausencia de un marco estandarizado para evaluar narrativas emergentes [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?YITCNG). 

   2. ## Objetivos de la investigación {#objetivos-de-la-investigación}

      1. ### Objetivo general {#objetivo-general}

   Comparar la coherencia narrativa de las campañas de Dungeons & Dragons generadas por una arquitectura de sistema multiagente frente a una arquitectura monolítica.

      2. ### Objetivos específicos {#objetivos-específicos}

         1. Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico.  
         2. Evaluar la coherencia longitudinal a lo largo de las                campañas generadas por el sistema monolítico.  
         3. Evaluar la calidad de la coherencia narrativa emergente en las campañas generadas por el sistema monolítico.  
         4. Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura.  
         5. Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas.  
         6. Comparar la calidad de la narrativa emergente producida por la arquitectura multiagente frente a la monolítica.

   3. ## Importancia del estudio {#importancia-del-estudio}

   En el creciente campo de la inteligencia artificial aplicada a la narrativa interactiva, emerge un debate fundamental sobre la arquitectura más idónea para generar narrativas complejas y de larga duración [(Bidarra & Kybartas, 2017\)](https://www.zotero.org/google-docs/?ZlbfsA), la importancia capital de esta investigación radica en que proporciona una de las primeras evaluaciones empíricas y comparativas entre las arquitecturas multiagente y las monolíticas, centrada específicamente en la métrica de la coherencia narrativa dentro del exigente dominio de Dungeons & Dragons, para ello este estudio traslada el debate desde la postulación teórica, donde se asume que los sistemas multiagente son superiores para gestionar la complejidad [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?ucWEVb), hacia la evidencia empírica, abordando una brecha de conocimiento que hasta ahora ha limitado la toma de decisiones de diseño basadas en datos [(Barambones et al., 2023\)](https://www.zotero.org/google-docs/?AH6WNh), por lo que al medir sistemáticamente la coherencia en sus distintas dimensiones, esta tesis ofrece un conocimiento de gran valor práctico para desarrolladores e investigadores, proveyendo un criterio objetivo para determinar qué enfoque arquitectónico es más efectivo para evitar la degradación narrativa y las contradicciones lógicas en sistemas de IA conversacionales complejos [(De Lima et al., 2023; Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?jaiAQS).

   4. ## Justificación de la investigación {#justificación-de-la-investigación}

   Esta investigación aborda la relación entre la arquitectura de IA y la calidad narrativa emergente, dado que la literatura postula ventajas de los MAS para tareas creativas [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?9wyYQm), si bien estas afirmaciones carecen todavía de validación empírica frente a los potentes sistemas monolíticos actuales [(Binggang & Masaki, 2024\)](https://www.zotero.org/google-docs/?CGUFyW); por ello, este estudio busca proveer evidencia que permita validar o refutar dichas hipótesis. En consecuencia, la investigación aportará significativamente a la teoría de los sistemas de IA al demostrar cómo el diseño arquitectónico impacta en la coherencia narrativa emergente, lo cual resulta particularmente relevante dado que los desarrolladores enfrentan hoy una decisión crucial entre enfoques multiagente o monolíticos [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?kXejRT). Por ello, este estudio busca ofrecer datos comparativos que guíen dicha decisión en la industria, lo que permitirá producir DMs virtuales y compañeros narrativos de mayor calidad [(Santiago et al., 2023\)](https://www.zotero.org/google-docs/?VBDErP). Asimismo, ante la falta de metodologías estandarizadas, se establecerá un protocolo de benchmarking riguroso mediante la adaptación de un nuevo instrumento de evaluación basado en investigaciones punteras [(Pan et al., 2025; Zhu et al., 2025\)](https://www.zotero.org/google-docs/?CxMQEC), de modo que se ofrezca a la comunidad una metodología robusta y replicable que fomente un progreso acumulativo en la generación de narrativas interactivas. Finalmente, se proporcionará evidencia clara sobre la arquitectura más efectiva, acelerando así la creación de Dungeon Masters de IA de alta calidad que, al resultar suficientemente creíbles, puedan democratizar el acceso a los juegos de rol al eliminar la barrera de encontrar un director de juego humano, fomentando con ello la creatividad, la resolución de problemas y las habilidades sociales.

   5. ## Limitaciones del estudio {#limitaciones-del-estudio}

   Un desafío técnico fundamental es el sesgo potencial en la implementación de las arquitecturas, dado que un MAS conlleva mayor complejidad de ingeniería que un sistema monolítico; sin embargo, esta disparidad es la naturaleza misma de la variable independiente, por lo que el diseño experimental controlará rigurosamente las variables de confusión: ambos sistemas utilizarán el mismo LLM base y la misma base de conocimiento RAG, de modo que cualquier diferencia observada será atribuible a la arquitectura de gestión del entorno y no a asimetrías en los componentes subyacentes. Asimismo, se aborda el riesgo de obsolescencia tecnológica de los modelos generativos centrando la investigación en paradigmas de gestión del estado y razonamiento causal, problemas estructurales que persisten incluso en los modelos de vanguardia [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?t8hPy1) y que permiten asumir que el MAS actúa como un andamiaje escalable frente a dicha obsolescencia. No obstante, si bien se asumió inicialmente que la coherencia narrativa carecía de una verdad fundamental computacionalmente verificable y que, en consecuencia, su evaluación dependería íntegramente de un panel de expertos humanos, el desarrollo del estudio permitió identificar que varios de los indicadores de coherencia reactiva y longitudinal sí admiten una verificación determinística al contrastarse directamente contra el estado persistido del mundo de juego —identidad y estado de los personajes no jugadores, cumplimiento de misiones, activación de eventos—, de modo que dichos indicadores se miden mediante un conjunto de instrumentos computacionales aplicados de forma sistemática sobre la totalidad del corpus generado; la subjetividad que sí conserva la dimensión de calidad narrativa emergente, al depender del juicio experto sobre creatividad e interés, se mitiga en cambio mediante la rúbrica adaptada de la literatura [(Pan et al., 2025\)](https://www.zotero.org/google-docs/?bBNnyF), aplicada sobre un bloque piloto de campañas y complementada con la confiabilidad intercodificadores [(Romero et al., 2021\)](https://www.zotero.org/google-docs/?UKrh5b) como referencia histórica de contraste. Otra decisión metodológica relevante fue abstraer la interacción con jugadores humanos reales, priorizando la validez interna y el control de variables sobre la validez ecológica, dado que la variabilidad humana dificultaría la comparación técnica directa [(Binggang & Masaki, 2024\)](https://www.zotero.org/google-docs/?mHToTI); por ello se optó por un Agente Jugador Autónomo basado en LLM, configurado con arquetipos de personaje predefinidos y árboles de decisión que incluyen perfiles de comportamiento divergentes y caóticos propios del rol en Dungeons & Dragons, lo que asegura estímulos idénticos para ambas arquitecturas y garantiza la continuidad de la prueba ante escenarios de conflicto propios de D\&D sin introducir la variabilidad no controlada de sujetos externos. Asimismo, el diseño contempla el análisis de las campañas como unidades holísticas, dado que la degradación de coherencia es un fenómeno acumulativo a largo plazo; en consecuencia, el estudio analizará campañas de duración extendida y alta densidad de eventos, equivalentes a una campaña completa de siete sesiones de juego, en lugar de recurrir a fragmentos reducidos que subestimarían la degradación propia de interacciones prolongadas [(De Lima et al., 2023\)](https://www.zotero.org/google-docs/?3fOUAa). Conviene precisar, además, el límite metodológico que afecta específicamente al indicador CL-1 (Entity Coreference Rate) y a su complemento CR-2 basado en grafos de entidades, ambos dependientes de identificar cuándo una entidad ya introducida en la campaña vuelve a aparecer en un turno posterior, tarea que en la literatura de procesamiento de lenguaje natural se resuelve típicamente mediante sistemas de resolución de correferencia; sin embargo, el estado del arte reciente en esa tarea —ejemplificado por Maverick [(Martinelli et al., 2024)], que alcanza el mejor desempeño reportado sobre el benchmark CoNLL-2012— se entrena y valida exclusivamente sobre corpus en inglés (OntoNotes, LitBank, PreCo), sin que exista hasta la fecha un sistema equivalente de calidad de producción validado para el español, de modo que instalar dicha herramienta quedaba descartado de antemano por incompatibilidad lingüística y no por preferencia de diseño. Ante esta ausencia, el estudio no intenta resolver cadenas de correferencia pronominal completas, sino que opera mediante el reconocimiento de la reaparición literal del nombre completo o del lema de cada entidad —previamente registrada en el estado persistido de la campaña— dentro del turno evaluado, complementado en CR-2 con lematización real vía spaCy es\_core\_news\_sm en lugar de coincidencia por subcadena; esta operacionalización no constituye una simplificación arbitraria, sino que resulta consistente con la definición original de Roemmele y Gordon, cuya tasa de correferencia de entidades tampoco resuelve pronombres, sino que mide mediante segmentación sintáctica la proporción de frases nominales del texto generado que corefieren con una entidad ya presente en el contexto, sin recurrir a una resolución anafórica exhaustiva. Esta limitación se acentúa, por lo demás, por el hecho de que la narración del corpus se produce mayoritariamente en segunda persona hacia el personaje jugador, convención estructural propia de Dungeons & Dragons ausente tanto de los corpus de entrenamiento en tercera persona sobre los que se valida Maverick como de la práctica totalidad de la literatura de coherencia narrativa computacional consultada, de modo que incluso si existiese una herramienta de correferencia validada para el español, su aplicabilidad directa a este dominio narrativo seguiría siendo incierta; en lugar de forzar sobre el corpus una herramienta ajena tanto al idioma como a la convención narrativa del dominio, el estudio optó por instrumentos propios —persona2 y sus subcategorías, y los indicadores CR-2a y CR-2b de arraigo contextual— diseñados específicamente para operar sobre narración en segunda persona, lo que se documenta como aporte metodológico original del proyecto y no como una carencia sin resolver. Finalmente, aunque los LLMs actuales puedan quedar tecnológicamente superados en un futuro próximo, los hallazgos de este estudio ofrecerán principios duraderos sobre la superioridad de la memoria estructurada.

3. # Marco teórico {#marco-teórico}

   1. ## Marco histórico {#marco-histórico}

   La evolución de los juegos de rol ha estado intrínsecamente ligada a la búsqueda de experiencias narrativas cada vez más inmersivas y dinámicas [(Van Velsen et al., 2009\)](https://www.zotero.org/google-docs/?841uSU). Todo comienza con Gary Gygax y Dave Arneson, ambos aficionados a los conocidos “Wargames”, juegos de mesa originados en el ya extinto Reino de Prusia y empleados inicialmente para estudios de estrategia militar y, posteriormente, con fines recreativos; naturalmente, estos juegos desarrollaron variantes y modificaciones según el interés de los distintos jugadores, aunque su foco se mantuvo siempre en la estrategia y los combates a gran escala. Gary y Dave eran aficionados en particular a una de esas variantes, conocida como Chainmail, la cual se apartaba del estilo clásico de los Wargames al emplear un escenario medieval en lugar de las figuras y ejércitos victorianos o napoleónicos habituales. Con el tiempo, y bajo la influencia de obras como “El Señor de los Anillos” de J.R.R. Tolkien, los cuentos de H.P. Lovecraft y diversas mitologías, ambos crearon Dungeons & Dragons en la década de 1970, sistema que rápidamente revolucionó el ocio al proponer la narración colaborativa como mecánica central, con un director de juego humano (Dungeon Master) que asume el rol de narrador, árbitro y arquitecto del mundo, siendo el responsable de mantener la coherencia narrativa, la consistencia de los personajes y la causalidad de los eventos [(Balla et al., 2024; Binggang & Masaki, 2024\)](https://www.zotero.org/google-docs/?jHi8av). La posterior transición a plataformas digitales expuso tanto el enorme potencial de la tecnología como las limitaciones de los sistemas existentes para replicar la complejidad y adaptabilidad del rol humano. El primer intento por digitalizar la narrativa interactiva se materializó en las aventuras conversacionales de los años setenta y ochenta, como Colossal Cave Adventure y Zork [(Ammanabrolu & Riedl, 2021\)](https://www.zotero.org/google-docs/?49WWiC); basados en texto, estos juegos ofrecían mundos explorables y acertijos, aunque sus narrativas eran fundamentalmente estáticas y predefinidas, limitadas por árboles de diálogo y eventos programados. Posteriormente, la llegada de los videojuegos de rol (CRPGs) introdujo narrativas épicas, si bien estas seguían siendo en gran medida lineales o de ramificación limitada, incapaces de reaccionar ante acciones no anticipadas por los desarrolladores [(De Lima et al., 2023\)](https://www.zotero.org/google-docs/?6mlegZ). Con el objetivo de superar estas limitaciones, la industria recurrió posteriormente a la inteligencia artificial a través de la Generación Procedural de Contenido (PCG) [(Amato et al., 2019\)](https://www.zotero.org/google-docs/?TSADO6), la cual se empleó con éxito para crear elementos como mapas y mazmorras [(Van Der Linden et al., 2014; Viana & Dos Santos, 2019\)](https://www.zotero.org/google-docs/?cotyDt); no obstante, su aplicación a la narrativa (PCG-N) resultó ser un desafío considerablemente mayor, dado que los primeros sistemas carecían de la capacidad para mantener una coherencia a largo plazo o desarrollar personajes con profundidad [(Bidarra & Kybartas, 2017\)](https://www.zotero.org/google-docs/?XTcBO7). El panorama actual representa, sin embargo, un punto de inflexión histórico impulsado por los avances en los modelos de lenguaje de gran escala (LLMs) y las arquitecturas de sistemas multiagente [(Qu et al., 2025\)](https://www.zotero.org/google-docs/?xAicdv): a diferencia de los enfoques anteriores, los LLMs poseen una capacidad sin precedentes para generar texto coherente, adaptarse a las acciones del jugador en tiempo real y simular conversaciones complejas [(Binggang & Masaki, 2024\)](https://www.zotero.org/google-docs/?nt0Jzn). En particular, las arquitecturas multiagente surgen como una solución prometedora para superar las limitaciones de los modelos monolíticos, tales como la pérdida de memoria contextual y la inconsistencia en la caracterización de personajes [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?Ul7aFO), y es precisamente esta evolución tecnológica la que da origen al problema central de esta investigación: ante la emergencia de una tecnología capaz de generar narrativas dinámicas, se vuelve imperativo evaluar si la calidad de dichas narrativas, y en particular su coherencia, alcanza el nivel esperado [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?MfBOE6).

   2. ## Investigaciones antecedentes relacionadas con el tema {#investigaciones-antecedentes-relacionadas-con-el-tema}

   La investigación en la intersección de la inteligencia artificial (IA) y la narrativa interactiva es un campo de estudio internacional con una rica trayectoria. Los esfuerzos iniciales para la generación automática de historias se fundamentaron en paradigmas de la IA clásica, utilizando sistemas de planificación para construir secuencias de eventos que formaran una trama lógica [(George, 2015; Laclaustra, Iván M. et al., 2014\)](https://www.zotero.org/google-docs/?PUJIsN); varios de estos sistemas pioneros demostraron la viabilidad de modelar la narrativa como un problema de planificación, aunque a menudo estaban limitados a dominios de conocimiento restringidos. El punto de inflexión en el campo ha sido, sin embargo, la irrupción de los Modelos de Lenguaje a Gran Escala (LLMs), cuya capacidad para comprender y generar lenguaje natural con una fluidez sin precedentes ha abierto la posibilidad de abordar dominios narrativos de final abierto como Dungeons & Dragons. En esa línea, algunos trabajos recientes exploran activamente el potencial de los LLMs para actuar como Dungeon Masters o como asistentes narrativos, destacando su habilidad para crear diálogos dinámicos y adaptarse a la libertad de acción de los jugadores [(Binggang & Masaki, 2024; Santiago et al., 2023; Zhu et al., 2025\)](https://www.zotero.org/google-docs/?IbafQY).

   

   Para superar las limitaciones inherentes a los modelos monolíticos, una corriente significativa de la investigación internacional se ha centrado en el uso de Sistemas Multiagente (MAS), donde la narrativa no es generada por una única entidad, sino que emerge de la interacción de múltiples agentes autónomos, cada uno con roles y motivaciones especializadas [(Barambones et al., 2023\)](https://www.zotero.org/google-docs/?rjnv21). Este enfoque resulta particularmente idóneo para los juegos de rol, que pueden conceptualizarse como "sociedades artificiales" donde los personajes interactúan para crear una historia colaborativa [(Casas-Roma et al., 2019\)](https://www.zotero.org/google-docs/?K6osuL). En esta línea, se han identificado arquitecturas recientes como StoryWriter, que demuestran cómo un equipo de agentes de IA puede colaborar para producir historias largas y coherentes, asignando tareas como la planificación del argumento, la escritura de secciones y la revisión a diferentes agentes [(Xia et al., 2025\)](https://www.zotero.org/google-docs/?qrvzbd).

   

   Paralelamente al avance en las técnicas de generación, ha surgido una línea de investigación crucial enfocada en la evaluación de la calidad de estas narrativas generadas, dado que el desarrollo de la capacidad generativa de la IA ha superado nuestra habilidad para medir y garantizar la calidad de su producción [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?oq1SMx). Para abordar esta brecha, la comunidad científica internacional ha propuesto marcos de evaluación sistemáticos: algunos se centran en la creación de instrumentos validados que descomponen la calidad narrativa en dimensiones medibles y objetivas, como la coherencia pragmática, global y local [(Romero et al., 2021\)](https://www.zotero.org/google-docs/?VY70Gd), mientras que otros utilizan metodologías de consenso de expertos, como el estudio Delphi, para identificar y priorizar las "Dimensiones de Calidad de la Historia" más críticas para la satisfacción del jugador [(Valdivia & Burelli, 2025\)](https://www.zotero.org/google-docs/?MVFO92). La convergencia de estas corrientes define el contexto en el que se inscribe la presente tesis, la cual busca aportar evidencia empírica comparativa sobre la efectividad de distintas arquitecturas de IA en la producción de narrativas coherentes.

   3. ## Base teórica {#base-teórica}

      1. ## Coherencia Narrativa

   Constructo que mide la integridad lógica, estructural y la ausencia de contradicciones en la historia generada, permitiendo que sea percibida como una unidad con sentido [(Zhu et al., 2023; Zhou et al., 2022\)](https://www.zotero.org/google-docs/?uP31Dn).

      2. ## Coherencia Reactiva

   Evalúa la validez de la respuesta turno-a-turno. Una respuesta reactiva coherente debe ser "sensata" (lógica y plausible en el contexto) y estar "arraigada" (grounded), es decir, que continúe la conversación y el estado del mundo actual en lugar de ignorar la entrada del jugador o iniciar un hilo irrelevante [(Zhu et al., 2023; Zhou et al., 2022\)](https://www.zotero.org/google-docs/?ubXq8E) 

      3. Coherencia Longitudinal

   Mide la memoria y la integridad fáctica a largo plazo, es decir, la capacidad del sistema para mantener la "consistencia" de los detalles, eventos y estados de los personajes establecidos a lo largo de múltiples sesiones, previniendo contradicciones internas [(Zhu et al., 2023; Pan et al., 2025\)](https://www.zotero.org/google-docs/?9PuSN7) 

      4. Calidad de la Coherencia Narrativa Emergente

   Evalúa la calidad creativa de la narrativa emergente y además de ser lógicamente correcta, una respuesta coherente en un contexto lúdico debe ser "interesante", demostrando ingenio, creatividad y evitando la monotonía a través de la calidad del lenguaje, uso de hooks narrativos o ausencia de repetición [(Zhu et al., 2023; Pan et al., 2025\)](https://www.zotero.org/google-docs/?OHSGZP) 

      5. Continuidad Causal y Memoria Persistente

   Un pilar fundamental de la coherencia a largo plazo es la continuidad causal, el principio que establece que los eventos no ocurren de forma aislada, sino como resultado de eventos anteriores y como causa de eventos futuros, esto se materializa a través de la memoria persistente, que es la capacidad del sistema para registrar acciones y eventos significativos, haciendo que tengan consecuencias duraderas en el estado futuro de la simulación [(De Lima et al., 2023\)](https://www.zotero.org/google-docs/?j0Edy5). La falta de una memoria robusta es una crítica común a muchos sistemas generativos, ya que rompe la inmersión y la sensación de agencia del jugador, al hacer que sus decisiones parezcan irrelevantes a largo plazo [(Lara J et al., 2018\)](https://www.zotero.org/google-docs/?OTLdzr), pero técnicamente, la memoria persistente puede implementarse mediante grafos de conocimiento dinámicos que se actualizan en tiempo real [(Ammanabrolu & Riedl, 2021\)](https://www.zotero.org/google-docs/?YvgywH) o mediante arquitecturas de agentes donde algunos se especializan en mantener y consultar el estado del mundo.

      6. Coherencia en las IAs Generativas

         1. Sistemas Monolíticos 

      Operan de forma "top-down", donde un planificador central genera una secuencia de acciones para alcanzar un objetivo narrativo predefinido, este enfoque garantiza una fuerte coherencia estructural y causal, ya que el plan resultante es una cadena lógica de eventos [(George, 2015; Ware et al., 2023\)](https://www.zotero.org/google-docs/?KNejmP), su principal ventaja es el control y la predictibilidad de la trama.

         2. Sistemas Multiagente

      Funcionan de manera "bottom-up". La narrativa emerge de las interacciones descentralizadas de agentes autónomos, cada uno persiguiendo sus propias metas [(Laclaustra, Iván M. et al., 2014\)](https://www.zotero.org/google-docs/?IPH5w4), este modelo favorece la complejidad, la sorpresa y la adaptabilidad en tiempo real y tiene como principal ventaja la capacidad de generar una mayor variedad de historias y de reaccionar de forma orgánica a las acciones del jugador [(Barambones et al., 2023\)](https://www.zotero.org/google-docs/?4zqCd7).

      7. Evaluación de la Coherencia

      Los Grandes Modelos de Lenguaje (LLMs), a pesar de su fluidez, presentan desafíos específicos para mantener la coherencia en narrativas largas [(Valdivia & Burelli, 2025; Callison-Burch et al., 2022\)](https://www.zotero.org/google-docs/?dfgQpL) 

      8. Pérdida de Contexto

      El modelo puede "olvidar" detalles o eventos cruciales mencionados previamente, llevando a inconsistencias y contradicciones cuando la interacción se va extendiendo más y más [(De Lima et al., 2023\)](https://www.zotero.org/google-docs/?yYRBGm).

      9. Alucinación

      El modelo puede generar información que no está fundamentada ni en la entrada previa ni en el estado del mundo conocido, rompiendo la verosimilitud de la historia [(Islam et al., 2024\)](https://www.zotero.org/google-docs/?2FpFUw).

   4. ## Definición de términos básicos {#definición-de-términos-básicos}

      1. ## Sistemas Multiagente (MAS)

   Sistema compuesto por múltiples agentes autónomos que interactúan entre sí y con su entorno. En la generación narrativa, los MAS distribuyen responsabilidades (planificación, gestión de estado, diálogo) entre agentes especializados, de modo que la historia emerge de sus interacciones cooperativas [(Barambones et al., 2023; Laclaustra et al., 2014\)](https://www.zotero.org/google-docs/?DirRjL).

      2. ## Sistema Monolítico

   Arquitectura de IA donde un único modelo centralizado (LLM) gestiona todas las responsabilidades narrativas, opcionalmente aumentado con RAG (Retrieval-Augmented Generation) para consultar una base de conocimiento externa. Opera de forma top-down donde un planificador central genera la secuencia narrativa [(George, 2015; Ware et al., 2023\)](https://www.zotero.org/google-docs/?5EAOmU).

      3. ## RAG (Retrieval-Augmented Generation)

   Técnica que aumenta los LLMs con la capacidad de consultar una base de conocimiento externa durante la generación, permitiendo recuperar información relevante (contexto del mundo, historial de eventos) para producir respuestas más precisas y contextualmente fundamentadas [(Callison-Burch et al., 2022\)](https://www.zotero.org/google-docs/?gUMhqW).

      4. ## Dungeon Master (DM) / Game Master (GM)

   Jugador que asume el rol de narrador, árbitro de las reglas y director de la historia en D\&D. Describe el mundo, presenta desafíos e interpreta a todos los personajes no controlados por los demás jugadores, siendo el responsable de mantener la coherencia narrativa, la consistencia de personajes y la causalidad de los eventos [(Binggang & Masaki, 2024; Lara J et al., 2018\)](https://www.zotero.org/google-docs/?NGswfI).

4. # Hipótesis y variables {#hipótesis-y-variables}

   1. ## Supuestos básicos {#supuestos-básicos}

   Para emprender la presente investigación se parte del supuesto epistemológico fundamental de que la coherencia narrativa en un dominio interactivo, a pesar de su naturaleza cualitativa, es un constructo susceptible de ser descompuesto, operacionalizado y medido sistemáticamente. Por ello, este estudio asume que una medición válida para Dungeons & Dragons (D\&D) debe priorizar la coherencia reactiva e interactiva, apoyándose en instrumentos y métricas validadas por investigaciones específicas del dominio de la IA narrativa. Asimismo, se presupone que la compleja interacción que define una campaña de D\&D es un fenómeno emergente y co-creado, por lo que se rechaza la validez de analizar artefactos de texto estáticos y se asume que es metodológicamente necesario incorporar la interacción humana; en consecuencia, los investigadores, actuando bajo un protocolo de cegamiento y utilizando un Agente Jugador Autónomo basado en LLM configurado con arquetipos de personaje predefinidos y árboles de decisión que incluyen perfiles de comportamiento divergentes y caóticos propios del rol en Dungeons & Dragons, constituyen un proxy válido y consistente de la agencia del jugador real, lo que permite medir la capacidad de respuesta del sistema sin introducir la variabilidad no controlada de sujetos externos [(Zhu et al., 2023; Zhou et al., 2022; Pan et al., 2025\)](https://www.zotero.org/google-docs/?jUi238). Se asume, además, que las arquitecturas a comparar representan paradigmas de gestión de estado y razonamiento causal distintos y maduros para la generación compleja, y que la arquitectura de memoria estructurada del sistema multiagente actúa como una capa de andamiaje independiente de la potencia bruta del modelo base; ello implica que los hallazgos sobre su superioridad o inferioridad estructural mantendrán su vigencia teórica independientemente de la posible obsolescencia tecnológica del LLM específico utilizado. Finalmente, se asume que, al estandarizar el modelo de lenguaje base y la implementación técnica de RAG en ambos grupos, el diseño experimental aísla eficazmente la "arquitectura de gestión narrativa" como la única variable independiente responsable de las diferencias observadas, mientras que el protocolo de doble ciego mitiga adecuadamente el sesgo de implementación y evaluación, asegurando la objetividad de los datos recolectados [(Romero et al., 2021\)](https://www.zotero.org/google-docs/?bauoS0).

   2. ## Hipótesis general {#hipótesis-general}

   H1 (Hipótesis Alternativa): Los sistemas multiagente producen campañas de Dungeons & Dragons con mayor coherencia narrativa que los sistemas monolíticos.

   H0 (Hipótesis Nula): Los sistemas multiagente producen campañas de Dungeons & Dragons de igual coherencia narrativa que los sistemas monolíticos.

   3. ## Hipótesis específicas {#hipótesis-específicas}

   H1a: Los sistemas monolíticos generan respuestas con una coherencia reactiva superior a la media.

   H0a: Los sistemas monolíticos generan respuestas con una coherencia reactiva inferior o igual a la media.

   H1b: Los sistemas monolíticos generan respuestas con una coherencia longitudinal a lo largo de la campaña superior a la media.

   H0b: Los sistemas monolíticos generan respuestas con una coherencia longitudinal a lo largo de la campaña inferior o igual a la media.

   H1c: Los sistemas monolíticos generan respuestas con una calidad de la coherencia narrativa emergente superior  a la media.

   H0c: Los sistemas monolíticos generan respuestas con una calidad de la coherencia narrativa emergente inferior o igual a la media.

   H1d: Los sistemas multiagente generan respuestas con mayor coherencia reactiva que los sistemas monolíticos.

   H0d: No existe diferencia significativa en el nivel de Coherencia Reactiva entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

   H1e: Los sistemas multiagente mantienen una mayor coherencia longitudinal a lo largo de la campaña que los sistemas monolíticos.

   H0e: No existe diferencia significativa en el nivel de coherencia longitudinal entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

   H1f: Los sistemas multiagente producen una Calidad de Narrativa Emergente superior en comparación con los sistemas monolíticos.

   H0f: No existe diferencia significativa en la Calidad de la Narrativa Emergente entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

   4. ## Variables {#variables}

#### ***Tabla 1\. Operacionalización de variables.***

| Variable | Definición Conceptual | Definición Operacional | Dimensión | Indicadores | Escala | Instrumentos |
| ----- | ----- | ----- | ----- | ----- | :---: | ----- |
| VD: Coherencia Narrativa | Constructo que mide la integridad lógica, estructural y la ausencia de contradicciones en la historia generada, permitiendo que sea percibida como una unidad con sentido [(Zhu et al., 2023; Zhou et al., 2022\)](https://www.zotero.org/google-docs/?od0PmR). | Puntuación ordinal obtenida a través de la aplicación de la Rúbrica D\&D-IA por un panel de expertos sobre las transcripciones de las campañas generadas. | Coherencia Reactiva | Fluidez y sentido lógico de la respuesta inmediata. | Ordinal (Escala Likert 1-7)  | Rúbrica de Calidad Narrativa D\&D-IA [(Adaptada de Zhu et al., 2023; Zhou et al., 2022; Pan et al., 2025\)](https://www.zotero.org/google-docs/?PV0V13) |
|  |  |  |  | Arraigo contextual |  |  |
|  |  |  | Coherencia Longitudinal | Consistencia de personajes a largo plazo |  |  |
|  |  |  |  | Consistencia de eventos y estado del mundo a largo plazo |  |  |
| VI: Tipo de Arquitectura del Sistema IA | Es el paradigma fundamental bajo el cual se organiza el sistema de IA para generar la campaña narrativa, difiriendo en su método de gestión de estado, memoria y responsabilidades narrativas | Implementación y uso de dos sistemas (G1 y G2) que utilizan el mismo LLM base y la misma técnica RAG base, pero difieren en su arquitectura de gestión: (G1) Multiagente con memoria especializada y (G2) Monolítico con memoria de contexto | Calidad Narrativa Emergente | Nivel de interés, creatividad y atractivo de la narrativa | Nominal | Análisis del Diseño Arquitectónico del Sistema  |
|  |  |  |  | Reactividad significativa a la agencia del jugador |  |  |
|  |  |  |  |  |  |  |
|  |  |  | Enfoque Arquitectónico | Clasificación del Paradigma de Control de la Generación Narrativa (Monolítico-RAG vs. MAS-RAG). |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

5. ## Matriz de consistencia {#matriz-de-consistencia}

   #### ***Tabla 2\. Matriz de consistencia de la investigación.***

| Problema General | Objetivo General | Hipótesis General | Variables | Indicadores | Instrumentos | Metodología |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| ¿Es superior la coherencia narrativa de campañas de Dungeons & Dragons generadas por sistemas multiagente en comparación con sistemas monolíticos de inteligencia artificial? | Comparar la coherencia narrativa de las campañas de Dungeons & Dragons generadas por una arquitectura de sistema multiagente frente a una arquitectura monolítica. | Los sistemas multiagente producen campañas de Dungeons & Dragons con mayor coherencia narrativa que los sistemas monolíticos. | Independiente: Tipo de Arquitectura del Sistema IA | Clasificación del Paradigma de Control de la Generación Narrativa | Análisis del Diseño Arquitectónico del Sistema  | **Enfoque:** Cuantitativo **Tipo de Investigación:** Aplicado **Diseño de Investigación**: Experimental-Comparativo **Población:** Todas las campañas de D\&D generadas por el sistema multiagente **Muestra:** Un número predefinido de campañas bajo condiciones controladas |
|  |  |  | Dependiente: Coherencia Narrativa | Fluidez y sentido lógico de la respuesta inmediata. | Rúbrica de Calidad Narrativa D\&D-IA [(Adaptada de Zhu et al., 2023; Zhou et al., 2022; Pan et al., 2025\)](https://www.zotero.org/google-docs/?F7Dzuo) |  |
|  |  |  |  | Consistencia de personajes a largo plazo |  |  |
| Problemas Específicos | Objetivos Específicos | Hipótesis Específicos |  | Arraigo contextual |  |  |
| ¿Cuál es el nivel de coherencia reactiva que alcanza un sistema monolítico ante las respuestas generadas por el jugador? | Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico. | Los sistemas monolíticos generan respuestas con una coherencia reactiva superior a la media. |  | Consistencia de eventos y estado del mundo a largo plazo |  |  |
| ¿Cuál es el nivel de coherencia longitudinal y preservación del estado del mundo que alcanza un sistema monolítico? | Evaluar la coherencia longitudinal a lo largo de las                campañas generadas por el sistema monolítico. | Los sistemas monolíticos generan respuestas con una coherencia longitudinal a lo largo de la campaña superior a la media. |  | Nivel de interés, creatividad y atractivo de la narrativa |  |  |
| ¿Cuál es el nivel de calidad de la coherencia narrativa emergente en términos de creatividad e interés en una campaña producida por un sistema monolítico? | Evaluar la calidad de la coherencia narrativa emergente en las campañas generadas por el sistema monolítico. | Los sistemas monolíticos generan respuestas con una calidad de la coherencia narrativa emergente superior  a la media. |  |  |  |  |
| ¿En qué medida difiere la coherencia reactiva entre las respuestas generadas por sistemas multiagente y sistemas monolíticos ante las acciones inmediatas del jugador? | Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura. | Los sistemas multiagente generan respuestas con mayor coherencia reactiva que los sistemas monolíticos. |  |  |  |  |
| ¿Cuál es la diferencia en la coherencia longitudinal y la preservación del estado del mundo entre las campañas generadas por sistemas multiagente y monolíticos? | Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas. | Los sistemas multiagente mantienen una mayor coherencia longitudinal a lo largo de la campaña que los sistemas monolíticos. |  |  |  |  |
| ¿Cómo se compara la calidad de la narrativa emergente en términos de creatividad e interés entre las campañas producidas por ambos tipos de arquitectura? | Comparar la calidad de la narrativa emergente producida por la arquitectura multiagente frente a la monolítica.. | Los sistemas multiagente producen una Calidad de Narrativa Emergente superior en comparación con los sistemas monolíticos. |  |  |  |  |

5. # Marco metodológico {#marco-metodológico}

   1. ## Tipo de investigación {#tipo-de-investigación}

   De acuerdo con su orientación o finalidad, la investigación es de tipo aplicada, puesto que busca resolver un problema práctico dentro del campo de la inteligencia artificial y el entretenimiento digital, comparando la efectividad de dos arquitecturas de IA para una tarea específica. De acuerdo con la técnica de contrastación, en cambio, la investigación es de tipo experimental, dado que se manipula deliberadamente la variable independiente (Tipo de Arquitectura del Sistema IA) en dos niveles (monolítico-RAG y multiagente-RAG) mediante un diseño de medidas repetidas (pares emparejados), con el fin de medir el efecto de esta manipulación sobre la variable dependiente (Coherencia Narrativa) y determinar si existe una diferencia estadísticamente significativa entre ambas condiciones.

   2. ## Nivel de madurez tecnológica {#nivel-de-madurez-tecnológica}

   La presente investigación se sitúa en el Nivel de Madurez Tecnológica (TRL) 4-5 [(Mankins, 1995\)](https://www.zotero.org/google-docs/?FJm57D), correspondiente a la validación en laboratorio de tecnología en entorno relevante. Ambas arquitecturas (Multiagente-RAG y Monolítica-RAG) utilizan LLMs de última generación ya validados individualmente (TRL 7-8), pero su aplicación comparativa controlada para la generación de narrativas de D\&D con evaluación sistemática de coherencia constituye una validación experimental novedosa que todavía no ha sido demostrada de manera controlada en la literatura especializada.

   La investigación no busca desarrollar un producto comercial listo para producción, sino establecer evidencia empírica sobre la superioridad arquitectónica de los MAS frente a los sistemas monolíticos en el dominio de la narrativa interactiva de D\&D, sentando las bases para futuros desarrollos de mayor madurez tecnológica.	

   3. ## Método de investigación {#método-de-investigación}

   La investigación adopta un método cuantitativo, con un diseño experimental puro de medidas repetidas (pares emparejados) que compara la Arquitectura Multiagente (grupo experimental) con la Arquitectura Monolítica (grupo de control), con el fin de comparar la coherencia narrativa de las campañas de Dungeons & Dragons generadas por ambas arquitecturas a través de los indicadores y puntuaciones obtenidos de la Rúbrica de Calidad Narrativa D\&D-IA. Dicha rúbrica es una adaptación que sintetiza las métricas validadas de investigaciones específicas del dominio de IA para D\&D [(Pan et al., 2025; Peng et al., 2023; Zhu et al., 2025\)](https://www.zotero.org/google-docs/?qrSROf), y operacionaliza la coherencia narrativa en sus dimensiones de Coherencia Reactiva (Sensatez y Arraigo), Coherencia Longitudinal (Consistencia) y Calidad Narrativa (Interés).

   4. ## Diseño del estudio {#diseño-del-estudio}

   La presente investigación se ajusta a un diseño experimental puro, en el que se emplea un diseño de medidas repetidas con pares emparejados. Se eligió este diseño por su alta robustez metodológica, dado que controla eficazmente la variabilidad extraña introducida por los prompts de inicio y la secuencia de interacciones del jugador; asimismo, al someter a ambas arquitecturas (experimental y control) a las mismas condiciones iniciales e interacciones idénticas —aseguradas mediante el uso de arquetipos de jugador—, se aísla con mayor precisión el efecto de la variable independiente.

      **Gpar(N=27): X₁ → Oa | X2 → Ob** 

   Donde:

   Gpar: Representa el grupo de 27 pares de campañas emparejadas (N=27) donde cada par (campaña G1 y G2) se genera a partir de un único prompt inicial y es sometido a la misma secuencia de interacciones por parte de los investigadores-jugadores.

   Intervención Experimental (X₁): Generación de la campaña utilizando la Arquitectura Multiagente-RAG.

   Intervención de Control (X₂): Generación de la campaña utilizando la Arquitectura Monolítica-RAG.

   Oa y Ob: Representan las mediciones de la variable dependiente (Coherencia Narrativa) para la campaña experimental (Oa) y la campaña de control (Ob) dentro del mismo par donde la comparación estadística fundamental se realiza entre Oa y Ob.

   Instrumento de Medición (O): La medición de los indicadores se realiza utilizando la Rúbrica de Calidad Narrativa D\&D-IA (adaptada de Zhu et al., 2023; Zhou et al., 2022; Pan et al., 2025).

   5. ## Población y muestra {#población-y-muestra}

   La población de esta investigación se define como el universo total y teóricamente infinito de todos los artefactos narrativos interactivos que pueden ser producidos por las dos arquitecturas de inteligencia artificial (Monolítica-RAG y MAS-RAG) bajo las condiciones del estudio. Dado que esta población es inaccesible en su totalidad, se trabajará con una muestra seleccionada mediante un muestreo no probabilístico de tipo intencional por criterios, cuyo tamaño se determinó mediante un análisis de potencia estadística a priori (G\*Power)

      $N\ =\ [\ (z_(1-\alpha )\ +\ z_(1-\beta ))\ /\ d_z\ ]²\ +\ C$

   Donde:

   N: Tamaño de la muestra (número de pares requeridos).

   z\_(1-α): Valor crítico de la distribución normal para el nivel de significancia α \= 0.05 (unilateral) \= 1.645.

   z\_(1-β): Valor crítico correspondiente a la potencia estadística deseada del 0.80 \= 0.842.

   d\_z: Tamaño del efecto medio estandarizado (Cohen's d\_z) establecido en 0.5.

   C: Factor de corrección por ajuste de la distribución t de Student (calculado iterativamente por el software G\*Power).

   Sustitución de parámetros:

   El software G\*Power, ajustando por los grados de libertad mediante la distribución no central t, determinó que, para cumplir con la condición de potencia mínima (0.80) y significancia (0.05) requerida para detectar un efecto medio, se necesitan N \= 27 pares. Cada par estará compuesto por una campaña generada por la arquitectura multiagente (G1) y una campaña generada por la arquitectura monolítica (G2), si bien ambas campañas dentro de un mismo par se generarán a partir del mismo conjunto de prompts base, que definirán el tono y el contexto inicial de la aventura. Adicionalmente, se incorporará una interactividad controlada mediante un Agente Jugador Autónomo basado en LLM, configurado con arquetipos de personaje predefinidos y árboles de decisión que incluyen perfiles de comportamiento divergentes y caóticos propios del rol en Dungeons & Dragons, idénticos para ambas condiciones; de este modo, se asegura que ambos sistemas (G1 y G2) sean forzados a reaccionar a un conjunto de motivaciones e intenciones de jugador coherentes e idénticas, aislando así la arquitectura como la variable independiente principal.

   6. ## Técnicas e instrumentos de recolección de datos {#técnicas-e-instrumentos-de-recolección-de-datos}

   La recolección de datos para esta investigación se lleva a cabo en dos fases distintas, cada una con técnicas e instrumentos específicos. La primera fase corresponde a la generación del corpus de estudio —los N=27 pares de campañas (54 transcripciones, 1,400 turnos cada una)— mediante una técnica de simulación experimental interactiva, en la cual se utilizan los dos sistemas de inteligencia artificial (G1: Multiagente-RAG y G2: Monolítico-RAG) para generar la muestra de forma interactiva a través de un Agente Jugador Autónomo basado en LLM, configurado con arquetipos de personaje predefinidos y árboles de decisión que incluyen perfiles de comportamiento divergentes y caóticos propios del rol en Dungeons & Dragons, con el fin de mitigar el sesgo del investigador durante esta fase de interacción y de asegurar que ambos sistemas reaccionen a la misma secuencia de motivaciones del jugador dentro de cada par.

   La segunda fase, correspondiente a la recolección de datos evaluativos sobre la muestra generada, sufrió una reformulación metodológica sustancial respecto del diseño original. El proyecto contemplaba inicialmente la evaluación documental mediante un panel de cinco Dungeon Masters expertos que aplicarían la Rúbrica de Calidad Narrativa D\&D-IA bajo condiciones de doble ciego, produciendo un puntaje ordinal único por indicador y por evaluador; sin embargo, el asesor y los investigadores acordaron el 14 de setiembre de 2026 migrar a un enfoque cien por ciento determinista para el corpus final, decisión motivada tanto por la restricción de tiempo y presupuesto que imponía capacitar, calibrar y coordinar un panel humano sobre 27 pares de campañas de 1,400 turnos, como por la meta editorial de someter la investigación a una revista indexada del área (IEEE Transactions on Games, IEEE Transactions on Computational Intelligence and AI in Games), cuyo estándar disciplinar privilegia la reproducibilidad de instrumentos automatizados sobre el juicio humano no escalable. El panel de cinco DMs expertos se conserva como evidencia histórica sobre un bloque piloto de tres campañas del sistema monolítico (n \= 15 observaciones, ver Anexo 2), dado que varios de sus hallazgos cualitativos —en particular, la identificación temprana de colisiones de identidad de personajes no jugadores— anticiparon correctamente hallazgos que el corpus determinista completo confirma en el Capítulo 6, pero deja de ser el método vigente para el corpus de 27 pares.

   En su lugar, cada uno de los seis indicadores de la Rúbrica D\&D-IA (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2) se opera mediante una batería de instrumentos deterministas —no un único puntaje ordinal agregado, sino varias métricas complementarias por indicador— aplicados de forma sistemática y reproducible sobre la totalidad del corpus mediante `reporte_validacion.py` (ocho secciones: verificación de campos inmutables, detección de bucles de ubicación, avance de relojes narrativos, centralidad y consistencia de entidades según Papalampidi et al., recall de cambios de estado según el State Graph EM/F1 de Ammanabrolu et al. (2020), tasa de correferencia de entidades según Roemmele y Gordon, gramaticalidad vía LanguageTool, y densidad del grafo de entidades por lema vía spaCy) y `medidas_cierre.py` (medidas descriptivas complementarias: repetición de frases, caracteres no latinos, estabilidad de estilo entre bloques, entidades registradas y latencia por turno). Cada instrumento se clasifica como confirmatorio, confirmatorio condicionado, exploratorio o descriptivo/no usar según su desempeño en una prueba de sensibilidad por perturbación (ficha de instrumentos, Anexo 1), que inyecta defectos sintéticos conocidos sobre el corpus real y verifica si el instrumento reacciona en la dirección pre-especificada antes de correr el análisis sobre los datos reales, evitando así ajustar post-hoc qué instrumentos se reportan como evidencia confirmatoria.

   7. ## Procedimientos de ejecución del estudio {#procedimientos-de-ejecución-del-estudio}

   La ejecución del estudio se articula en cuatro fases metodológicas secuenciales, revisadas respecto del diseño original para reflejar el pivote hacia instrumentos deterministas descrito en el apartado anterior. La primera fase corresponde a la Implementación y Configuración de las Arquitecturas, en la cual se asegura una comparación equitativa al construir ambos sistemas utilizando el mismo Modelo de Lenguaje base (LLM) y la misma implementación técnica de recuperación de información (RAG); la diferencia fundamental entre ambos radica en la arquitectura de gestión de memoria y estado, dado que el grupo de control (G2) implementa una memoria pura de contexto gestionada únicamente por el modelo, mientras que el grupo experimental (G1) integra una arquitectura de agentes especializados (Árbitro, Actor, Mundo, Narrador, Extractor) con una base de memoria externa estructurada (SQLite, ChromaDB y NetworkX). A continuación se lleva a cabo la Generación de la Muestra (N \= 27 pares, diseño Gpar: mismo prompt inicial y misma secuencia de interacciones del Agente Jugador Autónomo dentro de cada par), a una escala de 1,400 turnos por campaña —equivalente a siete sesiones de juego de 200 turnos—, con variación deliberada de tono narrativo, estructura de conflicto y personaje jugador entre pares consecutivos, de modo que la comparación no quede sesgada hacia el estilo particular que mejor maneje una de las dos arquitecturas. Una vez cerrado cada par a escala completa, se ejecuta la fase de Instrumentación Determinista, en la que corren de forma automatizada las ocho secciones de `reporte_validacion.py` y las medidas complementarias de `medidas_cierre.py` sobre el texto normalizado de cada campaña (turnos 2 a 1,400, excluyendo el turno de apertura), produciendo un valor por indicador y por campaña sin intervención humana ni ambigüedad de criterio entre jueces. Finalmente, se culmina con el Análisis Estadístico (Capítulo 5.8), diferenciado según el tipo de objetivo: los objetivos de evaluación (OE-1 a OE-3) se resuelven mediante estadística descriptiva sobre el sistema monolítico, y los objetivos de comparación (OE-4 a OE-6) mediante contraste inferencial pareado entre arquitecturas con un nivel de significancia de 𝞪 \= 0.05.

   8. ## Técnicas de procesamiento y análisis de datos {#técnicas-de-procesamiento-y-análisis-de-datos}

   Una vez recolectados los datos deterministas, se procede a su procesamiento y análisis estadístico, diferenciado según la naturaleza descriptiva o comparativa de cada objetivo específico. Para los objetivos de evaluación (OE-1, OE-2, OE-3), que preguntan por el nivel que alcanza el sistema monolítico en cada dimensión sin exigir una comparación, el análisis es puramente descriptivo: se calcula la mediana, los cuartiles (Q1, Q3) y el rango intercuartílico de cada instrumento sobre las 27 campañas G2, junto con la media, la desviación estándar y la prueba de normalidad de Shapiro-Wilk, reportando también los mismos estadísticos para G1 como referencia comparativa sin que ello constituya, en esta etapa, un contraste de hipótesis. Se optó deliberadamente por no forzar un contraste de una muestra contra un punto medio fijo, como el μ₀ \= 4 que usaba la escala Likert del panel de expertos: a diferencia de un puntaje ordinal acotado entre 1 y 7 con un punto medio interpretable, cada instrumento determinista tiene su propia escala, unidad y sentido de mejora (proporciones acotadas en 0-1, conteos, puntajes normalizados en z), de modo que fijar un punto medio arbitrario para cada uno introduciría un artefacto metodológico sin respaldo teórico; el contraste de hipótesis propiamente dicho se concentra, en cambio, en los objetivos comparativos.

   Para los objetivos de comparación (OE-4, OE-5, OE-6), que sí corresponden al diseño experimental de medidas repetidas con pares emparejados (Gpar) especificado en el Capítulo 5.4, el contraste se realiza mediante la prueba de Rangos con Signo de Wilcoxon exacta (condicional a empates, con exclusión de diferencias nulas) sobre la diferencia G1−G2 dentro de cada uno de los 27 pares, reportando el p-valor bilateral y ambos p-valores unilaterales (a favor de G1 y a favor de G2), el estimador de Hodges-Lehmann de la mediana de la diferencia con su intervalo de confianza del 95 %, y el tamaño del efecto mediante la correlación biserial de rangos pareados (r). Dado que varios instrumentos miden un mismo constructo desde ángulos distintos, la corrección de Holm por comparaciones múltiples se aplica únicamente dentro de la familia de instrumentos clasificados como confirmatorios para cada hipótesis específica, preservando el poder estadístico de los instrumentos exploratorios sin inflar la tasa de error de tipo I en la evidencia que efectivamente decide la hipótesis. La clasificación de cada instrumento como confirmatorio, confirmatorio condicionado, exploratorio o descriptivo se fija antes de correr el análisis sobre el corpus real, mediante la prueba de sensibilidad por perturbación descrita en el Capítulo 5.6, evitando así seleccionar post-hoc qué resultados se presentan como evidencia confirmatoria; todo el análisis inferencial se realiza con un nivel de significancia de 𝛂 \= 0.05.

6. # Presentación de resultados {#presentación-de-resultados}

   Para el capítulo de resultados, DM-IA opera bajo dos arquitecturas comparables: G1 (Sistema Multiagente, con agentes especializados —Árbitro, Actor, Mundo y Narrador— sobre una base de memoria externa estructurada con SQLite, ChromaDB y NetworkX) y G2 (Sistema Monolítico con LightRAG). Conforme al pivote metodológico documentado en el Capítulo 5 (decisión del asesor del 14 de setiembre de 2026), los seis indicadores de la Rúbrica D\&D-IA (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2) ya no se miden mediante un puntaje Likert asignado por un panel de jueces, sino mediante una batería de instrumentos deterministas aplicada sobre el texto normalizado del corpus completo.

   Los resultados de este capítulo corresponden al corpus final: N \= 27 pares de campañas (54 campañas, 75,600 turnos), generadas con el mismo modelo de lenguaje base y el mismo Agente Jugador Autónomo en ambos brazos, medidas mediante `reporte_validacion.py` y `medidas_cierre.py` (ficha completa de instrumentos en el Anexo 1). Como se documentó en el Capítulo 5.8, los objetivos OE-1 a OE-3 —que preguntan por el nivel que alcanza el sistema monolítico (G2) en cada dimensión, sin exigir una comparación— se resuelven mediante estadística descriptiva (mediana, cuartiles, rango intercuartílico, media, desviación estándar y prueba de normalidad de Shapiro-Wilk sobre las 27 campañas G2), reportando los mismos estadísticos de G1 únicamente como referencia de contexto, sin que ello constituya en esta etapa un contraste de hipótesis. El panel de cinco Dungeon Masters expertos que evaluó tres campañas G2 bajo escala Likert (n \= 15 observaciones) durante la fase piloto del proyecto se conserva como Anexo 2 (evidencia histórica), dado que varios de sus hallazgos cualitativos —en particular, la identificación temprana de colisiones de identidad de personajes no jugadores— anticiparon correctamente hallazgos que el corpus determinista de 27 pares confirma a continuación.

   Cada instrumento reportado se clasifica, según la ficha de instrumentos (Capítulo 5.6), en confirmatorio, confirmatorio condicionado, exploratorio o descriptivo/no usar, de acuerdo con su desempeño en una prueba de sensibilidad por perturbación pre-especificada; los instrumentos confirmatorios son los que sostienen la docimasia de las hipótesis comparativas H1d-H1f en los objetivos OE-4 a OE-6, que se presentan a continuación junto con OE-1 a OE-3.

   1. ## Evaluar la coherencia reactiva de las respuestas inmediatas generadas por el sistema monolítico.

      1. ### Definición del objetivo

      OE-1 busca establecer el nivel de coherencia reactiva que el sistema monolítico-RAG (G2) alcanza ante las interacciones del jugador, operacionalizado mediante los instrumentos deterministas de CR-1 (fluidez y corrección de la respuesta inmediata) y CR-2 (arraigo contextual a la acción del jugador), aplicados sobre las 27 campañas G2 del corpus final.

      2. ### Resultados

#### ***Tabla 3\. Estadísticos descriptivos — Coherencia reactiva, sistema monolítico (G2), n \= 27 campañas.***

| Indicador | Instrumento | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk p | ¿Normal? |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CR-1 | Gramaticalidad (LanguageTool) | 0.9992 | 0.9991 | 0.9994 | 0.0003 | 0.9984 | 0.9998 | 0.9992 (0.0004) | 0.3445 | sí |
| CR-1 | Pifia narrada como éxito (% de turnos) | 0.07 % | 0.00 % | 0.14 % | 0.14 % | 0.00 % | 0.50 % | 0.09 % (0.11 %) | \<0.0001 | no |
| CR-1 | Caracteres de otro alfabeto o U+FFFD (%) | 0.07 % | 0.07 % | 0.14 % | 0.07 % | 0.00 % | 0.29 % | 0.10 % (0.08 %) | 0.0045 | no |
| CR-2 | Respuesta a la acción específica (z), confirmatorio | 2.81 | 2.61 | 3.01 | 0.40 | 2.45 | 3.51 | 2.82 (0.27) | 0.2746 | sí |
| CR-2 | Solapamiento con la acción (crudo) | 0.125 | 0.114 | 0.134 | 0.020 | 0.104 | 0.163 | 0.125 (0.014) | 0.2788 | sí |
| CR-2 | Anclaje al escenario (coseno, ventana de 8\) | 0.072 | 0.061 | 0.082 | 0.021 | 0.047 | 0.145 | 0.076 (0.024) | 0.0130 | no |
| CR-2 | Turnos con algún nombre no reconocido | 5.08 % | 3.40 % | 7.72 % | 4.32 % | 2.43 % | 24.23 % | 6.75 % (5.08 %) | \<0.0001 | no |

*Nota. Elaboración propia a partir de `reporte_validacion.py`/`medidas_cierre.py` sobre las 27 campañas G2 del corpus final (2026-09-21). Tabla reducida a los instrumentos de mayor relevancia interpretativa; la ficha completa (Capítulo 5.6) reporta además los instrumentos descriptivos/no usar.*

      3. ### Análisis descriptivo

      El único instrumento de CR-2 validado como confirmatorio mediante la prueba de sensibilidad por perturbación —la respuesta a la acción específica normalizada en z— sitúa a G2 en 2.82 de media, con dispersión moderada (RIQ \= 0.40) y sin evidencia de asimetría marcada (Shapiro-Wilk no rechaza normalidad, p \= 0.27). La gramaticalidad se mantiene prácticamente en el techo de la escala (0.9992 de mediana), consistente con el hallazgo cualitativo del panel piloto de que la fluidez local no era, en general, un problema del sistema monolítico. El indicador exploratorio de turnos con algún nombre no reconocido —proxy imperfecto de arraigo, que no distingue nombres inventados de personajes no jugadores legítimos nuevos— muestra una mediana de 5.08 % con una cola larga hacia arriba (máximo 24.23 %), y se reporta como exploratorio, no como evidencia confirmatoria, precisamente por esa limitación de precisión.

      4. ### Discusión de resultados

      A diferencia de la evaluación piloto por panel (n \= 15, tres campañas), que había encontrado a CR-2 significativamente por debajo del punto medio de la escala Likert, el instrumento confirmatorio del corpus completo no tiene un punto de referencia externo contra el cual declarar a G2 "deficiente" o "aceptable" en términos absolutos: su valor solo adquiere sentido interpretativo pleno frente a G1, contraste que corresponde a OE-4 (H1d). Lo que sí permite establecer el análisis descriptivo de las 27 campañas es que el arraigo contextual de G2, medido por el único instrumento confirmatorio disponible, es una magnitud estable y de baja dispersión relativa (coeficiente de variación ≈ 10 %) a lo largo de escenarios, tonos narrativos y personajes jugadores distintos — es decir, el comportamiento de G2 en esta dimensión es consistente, no errático, con independencia de si resulta o no comparativamente superior a G1.

      5. ### Conclusiones

      Sobre las 27 campañas del corpus final, el sistema monolítico-RAG (G2) exhibe una coherencia reactiva estable: gramaticalidad cercana al techo de la escala, y un arraigo contextual (CR-2a en z) de magnitud consistente entre campañas (Mdn \= 2.81, RIQ \= 0.40). No se emite un juicio de suficiencia o deficiencia en términos absolutos para este objetivo, dado que los instrumentos deterministas carecen de un punto medio teórico no arbitrario contra el cual contrastarse (Capítulo 5.8); dicho juicio comparativo se resuelve en OE-4 mediante el contraste pareado G1-G2.

      6. ### Recomendaciones

      Se recomienda auditar manualmente una muestra de los turnos marcados por el indicador exploratorio de "nombre no reconocido" para separar nombres efectivamente inventados de personajes no jugadores legítimos introducidos por el propio sistema, antes de usar esa cifra como evidencia sustantiva en la discusión general de la tesis.

   2. ## Evaluar la coherencia longitudinal a lo largo de las campañas generadas por el sistema monolítico.

      1. ### Definición del objetivo

      OE-2 evalúa la capacidad del sistema monolítico-RAG (G2) para mantener la integridad fáctica y la consistencia narrativa a lo largo de campañas de 1,400 turnos, mediante los instrumentos deterministas de CL-1 (consistencia de personajes: centralidad y consistencia de atributos según Papalampidi et al., y tasa de correferencia de entidades según Roemmele y Gordon) y CL-2 (consistencia de eventos y estado del mundo: recall de cambios de estado según Ammanabrolu et al., mención de personajes no jugadores inactivos, y ciclos de ubicación).

      2. ### Resultados

#### ***Tabla 5\. Estadísticos descriptivos — Coherencia longitudinal, sistema monolítico (G2), n \= 27 campañas.***

| Indicador | Instrumento | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk p | ¿Normal? |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CL-1 | Papalampidi C: coherencia de entidad | 1.67 | 0.92 | 2.29 | 1.38 | 0.00 | 3.33 | 1.60 (0.88) | 0.6394 | sí |
| CL-1 | Papalampidi V: consistencia de atributos | 0.058 | 0.048 | 0.079 | 0.031 | 0.030 | 0.151 | 0.067 (0.032) | 0.0016 | no |
| CL-1 | Entity Coreference Rate | 0.998 | 0.998 | 0.998 | 0.001 | 0.997 | 0.999 | 0.998 (0.000) | 0.2287 | sí |
| CL-2 | Jericho: recall de cambios de estado narrados | 0.22 | 0.13 | 0.36 | 0.23 | 0.00 | 0.50 | 0.24 (0.16) | 0.1312 | sí |
| CL-2 | PNJ inactivo mencionado (% de turnos) | 0.21 % | 0.00 % | 2.50 % | 2.50 % | 0.00 % | 15.94 % | 2.29 % (3.93 %) | \<0.0001 | no |
| CL-2 | Turno de la primera mención de un PNJ no vivo (1401 \= nunca) | 891 | 380 | 1401 | 1021 | 83 | 1401 | 865 (520) | 0.0005 | no |
| CL-2 | Bucles: ciclos de ubicaciones (fracción de campañas con ciclo) | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 (0.00) | — | — |

*Nota. Elaboración propia a partir de `reporte_validacion.py` sobre las 27 campañas G2. Papalampidi C y V son proxies de identidad y de consistencia de atributos, sin prueba de sensibilidad A2 propia (solo controles); Entity Coreference Rate está saturado cerca de 1 en todo el corpus y se clasifica como descriptivo/no usar (Capítulo 5.6).*

      3. ### Análisis descriptivo

      La centralidad de entidad de Papalampidi (Ci) sitúa a G2 en una mediana de 1.67 sobre un máximo posible de 4.5, con un mínimo de 0.00 — es decir, en al menos una campaña del corpus, ninguna de las entidades sembradas más mencionadas sobrevivió como referente rastreable entre su primera y su última mención. El recall de Jericho-QA (cambios de estado del mundo efectivamente narrados) es bajo en términos absolutos (Mdn \= 0.22), aunque este instrumento carece todavía de prueba de sensibilidad A2 y su n de deltas evaluables varía considerablemente entre campañas, por lo que se reporta como exploratorio. El indicador de PNJ inactivo mencionado tiene una mediana baja (0.21 %) pero una cola derecha marcada (máximo 15.94 %), y la variable censurada "turno de la primera mención de un PNJ no vivo" tiene una mediana de 891 sobre 1,400 posibles, con una proporción notable de campañas donde el valor censurado (1,401 \= nunca ocurre) domina el cuartil superior.

      4. ### Discusión de resultados

      La dimensión longitudinal es, de los tres objetivos de este avance, la que exhibe mayor heterogeneidad entre campañas (coeficientes de variación más altos y desviaciones marcadas de la normalidad en la mayoría de sus instrumentos), lo cual es consistente con la naturaleza acumulativa del fenómeno que mide: los defectos de consistencia de personajes y de estado del mundo se acumulan de forma no lineal a lo largo de 1,400 turnos, y su severidad depende en parte de decisiones narrativas específicas de cada campaña. Como en OE-1, ninguno de estos instrumentos tiene un punto de referencia externo no arbitrario que permita declarar a G2 "deficiente" o "aceptable" de forma absoluta; el contraste inferencial que decide si esta dimensión favorece a una arquitectura sobre la otra corresponde a OE-5 (H1e).

      5. ### Conclusiones

      Sobre las 27 campañas del corpus final, la coherencia longitudinal del sistema monolítico-RAG (G2) es la dimensión de mayor variabilidad entre campañas de este avance de resultados, con evidencia descriptiva de al menos un caso de pérdida total de centralidad de entidad (Papalampidi C \= 0.00) y una mediana de recall de cambios de estado narrados de 0.22. Como en OE-1, no se emite un juicio de suficiencia en términos absolutos; dicho juicio se resuelve en OE-5.

      6. ### Recomendaciones

      Se recomienda investigar la causa exacta del caso de Papalampidi C \= 0.00 mediante lectura directa de la transcripción correspondiente, y completar la prueba de sensibilidad A2 para el recall de Jericho-QA antes de promoverlo de exploratorio a confirmatorio.

   3. ## Evaluar la calidad de la coherencia narrativa emergente en las campañas generadas por el sistema monolítico

      1. ### Definición del objetivo

      OE-3 evalúa la capacidad del sistema monolítico-RAG (G2) para generar narrativa de calidad creativa y para respetar la agencia del jugador, mediante los instrumentos deterministas de QN-1 (diversidad léxica vía TTR, MTLD y MATTR; legibilidad vía Fernández-Huerta y Szigriszt-Pazos; repetición de bigramas y de frases) y QN-2 (usurpación mental, verbal o de decisión del personaje jugador, instrumento `persona2`, confirmatorio condicionado a auditoría de precisión).

      2. ### Resultados

#### ***Tabla 7\. Estadísticos descriptivos — Calidad narrativa emergente, sistema monolítico (G2), n \= 27 campañas.***

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

*Nota. Elaboración propia a partir del paquete de resultados `reporte_v2` sobre las 27 campañas G2. MTLD, MATTR y Szigriszt-Pazos complementan a TTR y Fernández-Huerta sin reemplazarlos (Capítulo 5.6); `persona2` (usurpación) es confirmatorio condicionado a la auditoría de precisión pendiente, no confirmatorio pleno.*

      3. ### Análisis descriptivo

      La diversidad léxica de G2 medida sin controlar por longitud de turno (TTR \= 0.725 de mediana) no es comparable en sentido absoluto con la de otros sistemas sin ese control, dado que TTR decrece mecánicamente con la longitud del texto; MTLD (108.9) y MATTR (0.828), que no dependen de la longitud, ofrecen una lectura más estable de la misma propiedad. La legibilidad se ubica en la banda "normal" tanto por Fernández-Huerta (61.9 de media) como por Szigriszt-Pazos (57.7 de media, banda INFLESZ "normal"), dos fórmulas de la misma familia de regresión lineal sobre sílabas y longitud de frase, por lo que su coincidencia no debe leerse como confirmación independiente. La usurpación de agencia del jugador (`persona2`) tiene una mediana de 3.47 % de los turnos, instrumento condicionado a una auditoría de precisión aún pendiente antes de tratarse como evidencia confirmatoria plena.

      4. ### Discusión de resultados

      A diferencia de CR-1/CR-2 (OE-1) y CL-1/CL-2 (OE-2), varios instrumentos de QN-1 (legibilidad, densidad de grafo) no tienen siquiera un sentido de mejora definido — una legibilidad "más alta" no es necesariamente "mejor" narrativa—, por lo que se reportan explícitamente como descriptivos y no como evidencia de calidad en ninguna dirección. El instrumento de usurpación de agencia (`persona2`) es, de los reportados aquí, el más cercano a admitir una lectura de calidad directa (una tasa más baja de usurpación respeta mejor la agencia del jugador, principio central de QN-2 en la Rúbrica D\&D-IA), pero su condición de "confirmatorio condicionado" exige completar la auditoría de precisión antes de usarlo como evidencia decisiva.

      5. ### Conclusiones

      Sobre las 27 campañas del corpus final, el sistema monolítico-RAG (G2) mantiene una diversidad léxica estable una vez controlada la longitud del turno (MTLD Mdn \= 108.9, MATTR Mdn \= 0.828), una legibilidad en banda "normal" por dos fórmulas convergentes pero no independientes, y una tasa de usurpación de agencia del jugador de 3.47 % de mediana, aún pendiente de auditoría de precisión. Como en OE-1 y OE-2, el juicio comparativo sobre si estos valores favorecen a una arquitectura sobre la otra se resuelve en OE-6.

      6. ### Recomendaciones

      Se recomienda priorizar la auditoría de precisión de `persona2` antes de redactar la docimasia de H1f, dado que es el único instrumento de QN-2 con potencial confirmatorio pleno.

   4. ## Comparar la coherencia reactiva de las respuestas inmediatas generadas por ambos tipos de arquitectura

      1. ### Definición del objetivo

      OE-4 contrasta la coherencia reactiva de G1 frente a G2 mediante el diseño de medidas repetidas con pares emparejados (Gpar, Capítulo 5.4) sobre los 27 pares del corpus final, comparando la diferencia G1−G2 dentro de cada par con la prueba de Rangos con Signo de Wilcoxon exacta (Capítulo 5.8). Este objetivo, junto con OE-5 y OE-6, es el que efectivamente decide las hipótesis específicas comparativas (H1d, H1e, H1f) y, por extensión, informa la hipótesis general de la investigación.

      2. ### Resultados

#### ***Tabla 9\. Comparación pareada G1−G2, 27 parejas — Coherencia reactiva (H1d).***

| Indicador | Instrumento | Uso | Mdn G1 | Mdn G2 | Mdn dif. | HL \[IC 95 %\] | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r | p Holm |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CR-1 | Gramaticalidad | Descriptivo/no usar | 0.9994 | 0.9992 | \+0.0001 | \+0.0001 \[-0.0001, \+0.0003\] | 27 | 0.2176 | 0.1088 | 0.8935 | \+0.28 | — |
| CR-2 | Respuesta a la acción específica (z) | Confirmatorio | 2.70 | 2.81 | \-0.18 | \-0.13 \[-0.25, \-0.03\] | 27 | 0.0319 | 0.9850 | 0.0159 | \-0.47 | 0.0319 |
| CR-2 | Solapamiento con la acción (crudo) | Exploratorio | 0.135 | 0.125 | \+0.009 | \+0.011 \[+0.006, \+0.015\] | 27 | \<0.0001 | \<0.0001 | 1.0000 | \+0.84 | — |
| CR-2 | Anclaje al escenario (coseno) | Exploratorio | 0.143 | 0.072 | \+0.060 | \+0.059 \[+0.035, \+0.082\] | 27 | \<0.0001 | \<0.0001 | 1.0000 | \+0.83 | — |
| CR-2 | Anclaje sin nombres propios | Exploratorio | 0.073 | 0.063 | \+0.012 | \+0.013 \[+0.005, \+0.020\] | 27 | 0.0036 | 0.0018 | 0.9984 | \+0.62 | — |
| CR-2 | Turnos con nombre no reconocido | Exploratorio | 3.00 % | 5.08 % | \-2.00 pp | \-0.79 pp \[-3.04, \+3.70\] | 27 | 0.7676 | 0.3838 | 0.6252 | \-0.07 | — |

*Nota. Elaboración propia a partir de `resultados_tesis.md` (Tabla 9, 2026-09-21). Tabla reducida a los instrumentos de mayor relevancia interpretativa.*

      3. ### Análisis descriptivo

      El único instrumento validado como confirmatorio por la prueba de sensibilidad A2, la respuesta a la acción específica normalizada en z, muestra una diferencia mediana de \-0.18 a favor de G2 (HL \-0.13, IC 95 % \[-0.25, \-0.03\]), estadísticamente significativa (p bilateral \= 0.0319; p unilateral «G2 mejor» \= 0.0159) con un tamaño de efecto moderado (r \= \-0.47). Sin embargo, las tres versiones exploratorias del mismo constructo —arraigo contextual, medido sin normalizar— muestran la dirección opuesta con tamaños de efecto grandes: solapamiento crudo (r \= \+0.84), anclaje al escenario por coseno (r \= \+0.83) y anclaje sin nombres propios (r \= \+0.62), las tres a favor de G1 con p \< 0.01. Gramaticalidad no muestra diferencia significativa (p \= 0.2176).

      4. ### Discusión de resultados

      La coherencia reactiva es, de los tres objetivos comparativos, el único donde la evidencia confirmatoria y la exploratoria apuntan en direcciones opuestas dentro del mismo constructo, y no simplemente donde la evidencia confirmatoria es "delgada": tres mediciones distintas de arraigo contextual arrojan tres conclusiones distintas según se normalice o no el puntaje. Esto sugiere un límite real de validez de constructo antes que una superioridad clara de cualquiera de las dos arquitecturas: la normalización en z que aplica el instrumento confirmatorio controla por variables (longitud de turno, vocabulario disponible) que las versiones crudas no controlan, y no está establecido cuál de las dos lecturas —normalizada o cruda— captura mejor el "arraigo contextual a la acción del jugador" tal como lo define la Rúbrica D\&D-IA original. Se documenta esta discordancia explícitamente, en lugar de reportar solamente el resultado confirmatorio como si fuera la historia completa de la dimensión.

      5. ### Docimasia

      H1d: Los sistemas multiagente generan respuestas con mayor coherencia reactiva que los sistemas monolíticos.

      H0d: No existe diferencia significativa en el nivel de Coherencia Reactiva entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

      Con el único instrumento confirmatorio disponible (CR-2a en z), se rechaza H0d (p \= 0.0319 \< α \= 0.05), pero la dirección del efecto favorece a G2, no a G1: H1d, tal como está formulada, no se sostiene con la evidencia confirmatoria de este corpus. Dado que las versiones exploratorias del mismo indicador muestran la dirección contraria con tamaños de efecto grandes, la conclusión metodológicamente correcta no es "G2 es superior a G1 en coherencia reactiva", sino que la dimensión de arraigo contextual, tal como se opera actualmente, no admite una lectura unívoca a favor de ninguna arquitectura, y que su resolución depende de una decisión de validez de constructo que excede lo que un único corpus puede zanjar.

      6. ### Conclusiones

      La coherencia reactiva es la única de las tres dimensiones comparativas donde la evidencia confirmatoria contradice a la exploratoria dentro del mismo constructo. El instrumento confirmatorio (CR-2a en z) favorece a G2 (p \= 0.0319, r \= \-0.47); las tres versiones exploratorias de arraigo contextual favorecen a G1 con efectos grandes (r entre \+0.62 y \+0.84). H1d no se sostiene con la evidencia confirmatoria disponible.

      7. ### Recomendaciones

      Se recomienda una revisión de validez de constructo de CR-2a antes de la sustentación, decidiendo explícitamente si la normalización en z o la medición cruda captura mejor el arraigo contextual definido por la Rúbrica D\&D-IA original, y documentando el criterio en la ficha de instrumentos.

   5. ## Comparar la coherencia longitudinal a lo largo de las campañas generadas por ambos sistemas

      1. ### Definición del objetivo

      OE-5 contrasta la coherencia longitudinal de G1 frente a G2 mediante el mismo diseño Gpar y la misma prueba de Wilcoxon pareada que OE-4, sobre los indicadores de CL-1 (consistencia de personajes) y CL-2 (consistencia de eventos y estado del mundo).

      2. ### Resultados

#### ***Tabla 11\. Comparación pareada G1−G2, 27 parejas — Coherencia longitudinal (H1e).***

| Indicador | Instrumento | Uso | Mdn G1 | Mdn G2 | Mdn dif. | HL \[IC 95 %\] | n efect. | p bilateral | p unil. «G1 mejor» | p unil. «G2 mejor» | r |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CL-1 | Papalampidi C: coherencia de entidad | Exploratorio | 2.17 | 1.67 | \+0.50 | \+0.58 \[+0.17, \+1.00\] | 25 | 0.0170 | 0.0085 | 0.9919 | \+0.54 |
| CL-1 | Papalampidi V: consistencia de atributos | Exploratorio | 0.074 | 0.058 | \+0.012 | \+0.016 \[-0.001, \+0.032\] | 27 | 0.0859 | 0.0430 | 0.9593 | \+0.38 |
| CL-2 | Jericho: recall de cambios de estado | Exploratorio | 0.21 | 0.22 | \-0.04 | \-0.03 \[-0.13, \+0.08\] | 25 | 0.6387 | 0.6855 | 0.3194 | \-0.11 |
| CL-2 | PNJ inactivo mencionado (% de turnos) | Exploratorio | 3.86 % | 0.21 % | \+3.86 pp | \+4.66 pp \[+0.11, \+8.86\] | 24 | 0.0315 | 0.9854 | 0.0157 | \+0.50 |
| CL-2 | PNJ inactivo como sujeto (refinado) | Exploratorio | 0.00 | 0.00 | \+0.00 | \+0.00 \[-0.36, \+0.00\] | 6 | 0.4375 | 0.2188 | 0.8438 | \-0.43 |

*Nota. Elaboración propia a partir de `resultados_tesis.md` (Tabla 11, 2026-09-21). Ningún instrumento de CL-1/CL-2 alcanzó la clasificación confirmatoria en la prueba de sensibilidad A2.*

      3. ### Análisis descriptivo

      Papalampidi C (centralidad de entidad) favorece a G1 con significación nominal (p \= 0.0170, r \= \+0.54): las entidades sembradas se mantienen, en promedio, mejor rastreadas como referentes narrativos a lo largo de la campaña bajo la arquitectura multiagente. En la dirección opuesta, el indicador de PNJ inactivo mencionado —un personaje no jugador narrado como presente después de que su estado pasara a inactivo— es significativamente más frecuente en G1 que en G2 (p \= 0.0315, r \= \+0.50 en la escala donde menor es mejor, es decir, desfavorable para G1); sin embargo, la versión refinada del mismo indicador, que exige que el personaje inactivo sea sujeto gramatical de la oración y no solo mencionado o referido retrospectivamente, pierde por completo la significación (p \= 0.4375, n \= 6). Ningún instrumento de esta dimensión fue validado como confirmatorio por la prueba de sensibilidad A2.

      4. ### Discusión de resultados

      La coherencia longitudinal presenta el panorama más simétrico de los tres objetivos comparativos: un indicador exploratorio favorece a G1 (centralidad de entidad), otro favorece a G2 (mención de PNJ inactivo en su versión cruda), y ninguno de los dos alcanza el estatus confirmatorio necesario para decidir formalmente H1e. La caída de significación del indicador de PNJ inactivo al exigir que el personaje sea sujeto gramatical de la oración —y no solo mencionado o aludido— es, en sí misma, un hallazgo metodológico relevante: sugiere que buena parte del efecto crudo observado corresponde a referencias retrospectivas legítimas (el grupo recordando o discutiendo a un personaje ausente) más que a errores narrativos de continuidad donde el sistema efectivamente hace actuar a alguien que ya no debería estar presente. Se decidió, en consecuencia, no promover el indicador crudo a confirmatorio condicionado pese a su paralelismo con `persona2`: forzar esa promoción habría sido una decisión a conveniencia, no respaldada por el propio refinamiento del instrumento.

      5. ### Docimasia

      H1e: Los sistemas multiagente mantienen una mayor coherencia longitudinal a lo largo de la campaña que los sistemas monolíticos.

      H0e: No existe diferencia significativa en el nivel de coherencia longitudinal entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

      Ningún instrumento de CL-1 o CL-2 alcanzó la clasificación confirmatoria en la validación por sensibilidad A2 (Capítulo 5.6): no existe, en consecuencia, evidencia confirmatoria disponible para rechazar o no rechazar H0e con el nivel de rigor exigido al resto de las hipótesis específicas de esta tesis. Esta ausencia de instrumento confirmatorio se documenta como una limitación explícita de la dimensión longitudinal, y no se sustituye con evidencia exploratoria ni se resuelve por defecto a favor de H0e ni de H1e.

      6. ### Conclusiones

      La coherencia longitudinal es la única de las tres dimensiones comparativas sin un instrumento confirmatorio disponible para decidir la hipótesis específica correspondiente. La evidencia exploratoria es mixta: centralidad de entidad favorece a G1 (p \= 0.0170); mención cruda de PNJ inactivo favorece a G2 (p \= 0.0315), efecto que desaparece en su versión sintácticamente refinada (p \= 0.4375). H1e queda sin decisión confirmatoria en este corpus.

      7. ### Recomendaciones

      Se recomienda priorizar, para una futura extensión de la investigación, el desarrollo o la validación de un instrumento confirmatorio dedicado a CL-1/CL-2 —candidato más cercano: una versión ampliada del recall de Jericho-QA con prueba de sensibilidad A2 propia—, dado que es la única de las tres dimensiones de la Rúbrica D\&D-IA sin evidencia confirmatoria en el corpus actual.

   6. ## Comparar la calidad de la narrativa emergente producida por la arquitectura multiagente frente a la monolítica

      1. ### Definición del objetivo

      OE-6 contrasta la calidad narrativa emergente de G1 frente a G2 mediante el mismo diseño Gpar, sobre los indicadores de QN-1 (diversidad léxica, legibilidad, repetición) y QN-2 (usurpación de agencia del jugador, instrumento `persona2`).

      2. ### Resultados

#### ***Tabla 13\. Comparación pareada G1−G2, 27 parejas — Calidad narrativa emergente (H1f).***

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

*Nota. Elaboración propia a partir de `resultados_tesis.md` (Tabla 13, 2026-09-21). Palabras por turno: mediana G1 158, G2 116 (diferencia \+41, p\<0.0001) — confusor de longitud que motiva reportar TTR y repetición de bigramas por turno como exploratorios, y sus versiones a 100 palabras como control.*

      3. ### Análisis descriptivo

      Las cinco filas de `persona2` —el único grupo de instrumentos confirmatorios (condicionados) de todo el capítulo— favorecen a G1 de forma unánime y con el tamaño de efecto máximo posible en una prueba pareada (r entre \-0.98 y \-1.00, es decir, G1 obtiene una tasa de usurpación de agencia del jugador menor que G2 en prácticamente los 27 pares sin excepción), con p \< 0.0001 en las cinco filas incluso tras la corrección de Holm dentro de la familia confirmatoria. La diversidad léxica sin controlar por longitud (TTR, bigramas) favorece a G2 con efectos también extremos (r \= ±1.00), pero esta diferencia se explica en gran medida por la diferencia de longitud de turno entre arquitecturas (G1: 158 palabras de mediana; G2: 116): al recalcular ambos instrumentos sobre las primeras 100 palabras de cada turno, la dirección del efecto se invierte para ambos (TTR a 100 palabras favorece a G1, r \= \+0.51; bigramas a 100 palabras favorece a G1, r \= \-0.83), y MTLD —que no depende de la longitud— no muestra diferencia significativa entre arquitecturas (p \= 0.8408). La legibilidad (Fernández-Huerta y Szigriszt-Pazos, misma familia de fórmulas) favorece levemente a G2, pero se reporta como descriptiva por no tener un sentido de mejora definido para la calidad narrativa.

      4. ### Discusión de resultados

      La calidad narrativa emergente es la única de las tres dimensiones comparativas con un bloque de instrumentos confirmatorios robusto y consistente: `persona2` mide directamente el principio central de QN-2 en la Rúbrica D\&D-IA —que las decisiones del jugador no sean usurpadas por el sistema—, y lo hace con un efecto de magnitud casi perfecta en las cinco categorías medidas. La diversidad léxica, en cambio, ejemplifica el valor de haber corregido el confusor de longitud de turno antes de escribir esta docimasia (Capítulo 2.5, limitación documentada): el hallazgo inicial de TTR/bigramas favoreciendo a G2 se invierte al controlar por longitud, por lo que reportarlo como confirmatorio habría sido un error metodológico que una revisión posterior habría expuesto. Con el control de longitud aplicado, la diferencia léxica remanente entre arquitecturas es pequeña en magnitud absoluta (0.002 en TTR, 0.0014 en bigramas) aunque estadísticamente detectable, y favorece consistentemente a G1, no a G2.

      5. ### Docimasia

      H1f: Los sistemas multiagente producen una Calidad de Narrativa Emergente superior en comparación con los sistemas monolíticos.

      H0f: No existe diferencia significativa en la Calidad de la Narrativa Emergente entre las campañas generadas por sistemas multiagente y sistemas monolíticos.

      Se rechaza H0f con las cinco filas confirmatorias condicionadas de `persona2` (p \< 0.0001, r entre \-0.98 y \-1.00 en las cinco, Holm \< 0.0001), aceptando H1f: G1 respeta significativamente mejor la agencia del jugador que G2. Esta aceptación queda condicionada a la auditoría de precisión de `persona2`, todavía pendiente, por lo que se trata de un resultado confirmatorio provisional, no definitivo, hasta que dicha auditoría se complete. La evidencia exploratoria de diversidad léxica, una vez controlada la longitud de turno, es consistente con esta misma dirección (favorece levemente a G1), reforzando sin decidir por sí sola la aceptación de H1f.

      6. ### Conclusiones

      De las tres hipótesis específicas comparativas, H1f es la única sostenida por un bloque de instrumentos confirmatorios robusto: `persona2` favorece a G1 en las cinco categorías medidas, con el tamaño de efecto máximo observable en un diseño pareado. La evidencia exploratoria de diversidad léxica, corregida por el confusor de longitud de turno, es consistente con esta dirección, aunque de magnitud pequeña. H1f se acepta, condicionada a la auditoría de precisión pendiente de `persona2`.

      7. ### Recomendaciones

      Se recomienda completar la auditoría de precisión de `persona2` (fase P2-P4 del plan de cierre de la investigación) como prioridad inmediata antes de la sustentación, dado que es el instrumento que sostiene por sí solo la única hipótesis específica comparativa con evidencia confirmatoria robusta de este corpus.

   7. ## Conclusiones

      El corpus final de 27 pares (54 campañas, 75,600 turnos), medido mediante la batería de instrumentos deterministas descrita en el Capítulo 5, arroja un patrón claro y no uniforme entre las tres dimensiones de la coherencia narrativa. En coherencia reactiva (H1d), el único instrumento confirmatorio disponible favorece a G2, en contradicción directa con las versiones exploratorias del mismo constructo, que favorecen a G1 con efectos grandes; H1d no se sostiene con la evidencia confirmatoria de este corpus, y la discordancia se documenta como un límite de validez de constructo, no como una conclusión zanjada. En coherencia longitudinal (H1e), ningún instrumento alcanzó la clasificación confirmatoria en la validación por sensibilidad A2, por lo que la hipótesis específica queda sin evidencia confirmatoria que la decida, con evidencia exploratoria mixta (centralidad de entidad favorece a G1; mención cruda de PNJ inactivo favorece a G2, efecto que no sobrevive el refinamiento sintáctico del instrumento). En calidad narrativa emergente (H1f), el bloque de instrumentos `persona2` —confirmatorio condicionado a una auditoría de precisión todavía pendiente— favorece a G1 de forma unánime y con el tamaño de efecto máximo observable en las cinco categorías medidas, resultado reforzado por la diversidad léxica exploratoria una vez controlado el confusor de longitud de turno identificado en el Capítulo 2.5.

      En conjunto, la evidencia de este corpus no respalda una superioridad general y uniforme del sistema multiagente sobre el monolítico en las tres dimensiones de la coherencia narrativa por igual, sino una ventaja específica y bien fundamentada en el respeto a la agencia del jugador (H1f), sin evidencia confirmatoria decisiva todavía en coherencia longitudinal (H1e), y con evidencia confirmatoria que favorece al sistema monolítico en el único indicador normalizado de arraigo contextual disponible (H1d) — un hallazgo que matiza sustancialmente la hipótesis general de la investigación y que se retoma con mayor profundidad en una revisión pendiente de las hipótesis específicas H1a-H1c del Capítulo 4, cuya formulación original todavía depende del punto medio de la escala Likert del panel de expertos.

   8. ## Recomendaciones

      Se recomienda: (a) completar la auditoría de precisión de `persona2` como prioridad inmediata, dado que es el único bloque de instrumentos confirmatorios que sostiene una hipótesis específica de este corpus, y su condición de "condicionado" afecta directamente la solidez de H1f; (b) resolver la discordancia de validez de constructo entre CR-2a normalizado y sus versiones crudas antes de presentar H1d ante el jurado, dado que la dirección del hallazgo depende de esa decisión metodológica; (c) desarrollar o validar un instrumento confirmatorio para CL-1/CL-2 en una futura extensión de la investigación, dado que es la única dimensión sin evidencia confirmatoria disponible; y (d) actualizar en una sesión futura el Capítulo 4 (hipótesis específicas H1a-H1c) y las Tablas 1 y 2 del Capítulo 4, que todavía describen el instrumento de medición como la Rúbrica de Calidad Narrativa D\&D-IA aplicada por panel bajo escala Likert, para que reflejen el pivote metodológico documentado en el Capítulo 5.

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
