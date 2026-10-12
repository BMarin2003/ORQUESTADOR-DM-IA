# Contexto para preparar la sustentación — Tesis DM-IA (G1 multiagente vs G2 monolítico)

> **Para Claude:** este archivo resume todo el trabajo previo de una tesis ya terminada. Úsalo como fuente de verdad.
> No inventes cifras: todo número que vaya a una lámina debe salir de aquí o de la tesis (`TESIS_ajustada_2026-10-10.docx`).
> Habla con Bryan en español peruano casual ("causa"), directo y técnico. Él prefiere pasos incrementales y confirmados.

---

## 0. La tarea

Hacer el **deck de sustentación (.pptx)** para una exposición de **máximo 15 minutos**, antes de las preguntas del jurado.

- Debe ser **expositivo**: poco texto, una idea por lámina. Si una lámina necesita párrafos, está mal.
- Máximo profesionalismo visual. Es un campo de nicho (narrativa **interactiva**, en **segunda persona** y en **español**), así que el deck tiene que hacer entender y defender todo en esos 15 minutos.
- Debe incluir notas del orador por lámina con el guion, y láminas de respaldo (backup) después del cierre para las preguntas.
- Ya existe un deck anterior de 33 láminas, demasiado largo y textual: `docs/Sustentacion_MAS_vs_Monolitico_v2.pptx`. Sirve como fuente de contenido, **no** como plantilla.
- Figuras ya hechas, reutilizables: `docs/figuras/fig1_diseno.png` (diseño experimental) y `docs/figuras/fig2_arquitecturas.png` (ciclo del turno G1/G2).

---

## 1. Datos de la tesis

- **Título:** Comparación de la Coherencia Narrativa en Campañas de Dungeons & Dragons generadas por Sistemas Multiagente versus Sistemas Monolíticos
- **Autores:** Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David
- **Asesor:** Dr. Cueva Chávez, Walter Manuel (confirmado: se usa el grado de la plantilla oficial UPAO).
- **Universidad Privada Antenor Orrego (UPAO)**, Facultad de Ingeniería, Escuela de Ingeniería de Sistemas e Inteligencia Artificial. Trujillo, 2026.
- **Tipo:** aplicada · cuantitativa · nivel explicativo · diseño **experimental de medidas repetidas con pares emparejados**.

---

## 2. El problema en 3 líneas

1. Un LLM como director de juego (DM) pierde contexto, contradice hechos previos y **decide por el jugador** a medida que la campaña se alarga.
2. La literatura propone dividir el trabajo entre agentes especializados (sistema multiagente, MAS), pero **no hay una comparación controlada** contra un sistema monolítico en juegos de rol de mesa.
3. Hay menos aún en **español** y en narrativa **en segunda persona** ("tú entras en la taberna…"), donde las herramientas y los datasets son mayormente en inglés.

**Pregunta general:** ¿es superior la coherencia narrativa de las campañas generadas por un MAS frente a un sistema monolítico?

---

## 3. Diseño experimental

| Elemento | Valor |
|---|---|
| Muestra | **27 pares = 54 campañas × 1,400 turnos = 75,600 turnos** |
| Unidad de análisis | El par: el mismo escenario se genera con G1 y con G2 |
| G1 (tratamiento) | Arquitectura **multiagente** |
| G2 (control) | Arquitectura **monolítica**: una sola llamada al modelo por turno |
| Constante dentro del par | Modelo `google/gemma-4-31B-it` (un solo proveedor, con huella verificada antes de cada tanda), misma base de datos del estado, mismo extractor, mismo mecanismo de dados, mismo personaje jugador, mismo agente jugador, misma extensión |
| Jugador | **Agente jugador autónomo** (LLM) con arquetipo y agenda. Usó Hermes-3-70B en los pares 1–3 y los primeros turnos de los pares 4–6, y Gemma después; jugador y DM comparten modelo en 24 de 27 pares, siempre igual en ambos brazos |
| Variación entre pares | Ambientación, tono, conflicto y personaje jugador distintos (27 personajes: 8 principistas, 14 de moral ambigua y 5 sin escrúpulos) |
| Potencia | G\*Power, unilateral, dz = 0.5, α = 0.05 → N = 27, potencia 0.81 con la t pareada y ≈0.79 con Wilcoxon |
| Pruebas | **Page** (tendencia en 7 bloques de 200 turnos de G2) para H1a–H1c; **Wilcoxon pareado** (G1 − G2) para H1d–H1f; Holm dentro de cada familia confirmatoria |

**Dos tipos de hipótesis:**
- **H1a–H1c** (OE-1 a OE-3): ¿se degrada G2 a lo largo de la campaña?
- **H1d–H1f** (OE-4 a OE-6): ¿supera G1 a G2?
- **Hipótesis general:** se sostiene solo si se sostienen H1d, H1e y H1f.

---

## 4. El sistema DM-IA

**Núcleo común a los dos brazos:**
- Base de datos **PostgreSQL** con el estado del mundo: PNJ, disposición, conocimiento, lugares, relojes de facción, misiones y el historial de cambios con su evidencia.
- Contexto de escena armado con **consultas SQL exactas** más la última escena narrada.
- Agente jugador, dados deterministas (d20 + modificador), verificador de la narración y extractor de cambios de estado (lista cerrada de tipos + **cita literal obligatoria**).

**G2:** un director de juego que en una sola llamada arbitra, interpreta a los PNJ, mueve el mundo y escribe la prosa.

**G1:** el trabajo se reparte en roles:
- Enrutador (código, sin modelo).
- Árbitro (código; usa el modelo solo si hace falta juicio).
- **Actor de PNJ** (modelo; recibe solo la ficha y lo que conoce *ese* PNJ).
- Agente del mundo (código + modelo).
- **Narrador** (modelo; es la única prosa que ve el jugador).

**Lo que NO hubo:** ninguna recuperación por similitud (RAG/vectores) en la generación. Las tablas vectoriales quedaron vacías. pgvector se usó **solo después**, como capa de medición de un instrumento exploratorio.

**Los tres candados contra la alucinación del estado:**
1. Solo 19 campos se pueden modificar (lista blanca).
2. Todo cambio extraído necesita una cita literal del turno.
3. Los números los pone una tabla de magnitudes según la personalidad del PNJ, no el modelo. Ejemplo: el mismo soborno ofende a un PNJ de principios y no ofende a uno corrupto.

**La base en cifras:** 77,413 turnos registrados · 17,908 cambios de estado con evidencia · 387 PNJ · 947 hechos conocidos por PNJ · 1,725 lugares · 2,890 objetos.

---

## 5. Instrumentos

- La **Rúbrica D&D-IA** (3 dimensiones, 6 indicadores) define los constructos:
  - CR-1: fluidez · CR-2: arraigo a la acción
  - CL-1: consistencia de personajes · CL-2: consistencia de eventos y del mundo
  - QN-1: interés y diversidad · QN-2: respeto a la agencia del jugador
- **Pivote (14 set 2026, acordado con el asesor):** el panel Likert de 5 DM no era viable sobre 75,600 turnos. Se midió con una **batería de instrumentos deterministas**, reproducibles y con el mismo resultado en cada ejecución. El panel quedó como **estudio piloto** (3 campañas preliminares; orientó el diseño de los instrumentos).
- **Validación de cada instrumento** con una **prueba de sensibilidad por perturbaciones**:
  - Se inyectan defectos de efecto conocido.
  - Las expectativas se fijan antes, protegidas con SHA-256.
  - Se exige delta de Cliff ≥ 0.147 y significancia con corrección de Holm.
- **Clasificación de los instrumentos:**
  - **Confirmatorio:** sostiene la decisión.
  - **Confirmatorio condicionado:** pasó la prueba, pero su concordancia con el juicio humano no quedó establecida.
  - **Exploratorio:** orienta, no decide.
  - **Descriptivo:** sin contraste.
- **Confirmatorios finales:**
  - CR-2: *respuesta a la acción específica (z)*, que es el solapamiento acción–respuesta normalizado contra un nulo de acciones ajenas.
  - QN-2: **persona2** (usurpación explícita de la agencia), **confirmatorio condicionado**.
  - **CL-1 y CL-2 no tienen ningún confirmatorio.**
- **Validación humana solo con evaluadores externos**, nunca los autores. Con la IA solo hubo una pasada asistida de apoyo.

---

## 6. Resultados (cifras para las láminas)

### Degradación de G2 (H1a–H1c): G2 **no se degradó** en 1,400 turnos

| Hipótesis | Instrumento | Bloque 1 → 7 | Page p | Decisión |
|---|---|---|---|---|
| H1a reactiva | Respuesta a la acción (z) | 2.768 → 2.742 | 0.310 | No se rechaza H0 |
| H1b longitudinal | Sin confirmatorio. El aumento de "PNJ inactivo" (p = 0.035) **desaparece al relativizar por exposición** (p = 0.451) | — | — | Sin decisión confirmatoria |
| H1c calidad | persona2 | 3.0 % → 3.5 % | 0.089 (Holm 0.178) | No se rechaza H0 |

Análisis exploratorio del último tramo (turnos 1,301–1,400): **no hay punto de quiebre** al final.

### Comparación G1 vs G2 (H1d–H1f)

**H1d, coherencia reactiva: no se sostiene.**
- El confirmatorio favorece **ligeramente a G2**: Mdn 2.70 vs 2.81; HL −0.13 [−0.25, −0.03]; p bilateral 0.032; r = −0.47.
- Tres versiones crudas favorecían a G1, pero la descomposición mostró que esa ventaja es **genérica**: G1 escribe respuestas más largas (+16 lemas por turno) que se parecen a cualquier acción.
- El componente **específico** no difiere (p = 0.59). **Ninguna arquitectura responde mejor a la acción específica del jugador.**
- G1 sí nombra más su propio mundo (anclaje al escenario, concentrado en nombres propios).

**H1e, coherencia longitudinal: sin decisión confirmatoria.** Evidencia exploratoria mixta:
- Coherencia de entidad: G1 2.17 vs G2 1.67 (p = 0.017).
- "PNJ inactivo mencionado" desfavorece a G1 (p = 0.032), pero la versión refinada no es significativa (p = 0.44).
- Supervivencia (Kaplan-Meier): primera mención de un PNJ no vivo en el turno 1,139 vs 891, p = 0.77.
- Instrumento semántico (bge-m3, 457,613 oraciones): recall 0.08 vs azar 0.05.
- Conclusión: **ningún candidato llegó a confirmatorio.**

**H1f, calidad narrativa: se ACEPTA (condicionada).** Es la única hipótesis comparativa sostenida.
- persona2: G1 **0.17 %** vs G2 **3.47 %** de turnos con usurpación explícita.
- p < 0.0001 tras Holm, r ≈ −1.00 (G1 menor en prácticamente los 27 pares).
- Diversidad léxica: la ventaja aparente de G2 se explica por la longitud (158 vs 116 palabras por turno). A 100 palabras, la diferencia se invierte a favor de G1 y es pequeña.

**Hipótesis general: NO se sostiene.**
> Con una memoria estructurada común, especializar agentes **no mejoró la coherencia medible**, pero **sí redujo que el sistema decida, piense, sienta o hable por el jugador**.

---

## 7. Cierres de brecha (uno por objetivo)

El asesor pidió intentar cerrar huecos aunque no se cerraran del todo.

| OE | Brecha | Resultado |
|---|---|---|
| OE-1 | El indicador de "nombre no reconocido" no distinguía invención de personajes legítimos | **Auditoría censal** de 9,629 marcas. La tasa bruta **sobrestima la invención entre 4 y 11 veces** (en G2 solo el 10.2 % son menciones efímeras candidatas). G1 tiene menos candidatas a invención (0.29 % vs 0.93 % de turnos, p = 0.019, exploratorio). Cerrada en su alcance. |
| OE-2 | El recall de Jericho-QA (cambios de estado) no tenía prueba de sensibilidad | Pasó 4/4 perturbaciones, pero contra el azar **solo discrimina en cambios de condición de personajes** (30–32 % vs 7–9 %). Sigue exploratorio. |
| OE-3 | persona2 sin validación humana | **3 DM externos** etiquetaron a ciegas 102 ítems. Acuerdo nulo (Fleiss −0.09); se aplicó el mismo criterio de calidad que en la otra validación y queda **un evaluador de referencia**. **Precisión 33.3 %** [21.0–48.4], del mismo orden que la pasada asistida (25.6 %). Detecta solo la usurpación **explícita** y tiene exhaustividad baja. **Avanzada, no cerrada**: sigue confirmatorio condicionado. |
| OE-4 | El confirmatorio decía G2 y las versiones crudas decían G1 | Descomposición en componente específico y genérico (ver H1d). Discordancia explicada; se fija el criterio de validez de constructo. |
| OE-5 | Ningún confirmatorio longitudinal | Tres líneas probadas: Jericho, supervivencia y semántico v2. Ninguna llega; queda recomendado un clasificador NLI en español. Aparte, el detector de PNJ inactivo se validó con 3 evaluadores externos (60 turnos → 59 casos únicos). Se excluyó a uno por respuesta apresurada; E1–E3: κ = 0.595, AC1 0.593. Precisión 62.5 %, exhaustividad 40 %. |
| OE-6 | ¿La precisión distinta entre brazos fabrica la ventaja de G1? | Precisión 42.9 % en G1 vs 28.6 % en G2. Corrigiendo cada tasa por su precisión: **G1 < G2 en 27/27 pares** (0.07 % vs 0.99 %); en el peor caso del intervalo, 26/27 (p < 0.0001). **La dirección de H1f es robusta**; la magnitud real en G2 está entre 0.5 % y 1 %. |

---

## 8. Verificaciones que blindan la defensa

- **Costo por arquitectura (objeción "G1 gana porque gasta más"):**
  - Del lado del DM, G1 hace 2.86 llamadas por turno vs 1, usa 2.6× más tiempo de modelo y escribe 1.5× más texto.
  - Pero **dentro de cada brazo, más cómputo va con MÁS usurpación** (Spearman +0.50 a +0.74), que es lo contrario a lo que exige la objeción.
  - La ventaja se atribuye al MAS como paquete. Recomendado: comparar contra un monolítico con el mismo presupuesto de llamadas.
- **Dados:** la semilla incluye el ID de la campaña, así que **las secuencias de los dos brazos no son idénticas**. Pero la suerte no favoreció a ninguno: en 4,824 tiradas comparables coinciden el 4.7 % (el azar da 5 %) y el d20 medio no difiere (Wilcoxon p = 0.946).
- **Potencia:** 0.81 unilateral (es el contraste declarado). El bilateral sería 0.71 y solo se reporta como complemento.
- **Estabilidad del modelo:** manifiesto de huellas verificado antes de cada tanda; un solo proveedor; los dos brazos de un par se generan en simultáneo.

---

## 9. Reglas: lo que NO se dice en el deck

1. **No mencionar RAG, LightRAG, ChromaDB, NetworkX ni recuperación vectorial en la generación.** No se usaron. pgvector aparece solo como capa de medición, si acaso.
2. **No decir que los dos brazos recibieron "la misma secuencia de tiradas".** Recibieron el mismo *mecanismo*, verificado sin sesgo.
3. **No vender a persona2 como validado al 100 %.** Es confirmatorio condicionado, con precisión del 33 % frente al evaluador de referencia, y la dirección es robusta.
4. **No decir que el MAS "es mejor" en general.** La hipótesis general no se sostiene; la ventaja está solo en la agencia del jugador.
5. **Nada de la startup (Runanta/QuestMasters), LoRA ni la plataforma comercial.** Solo lo que se usó en el experimento.
6. La validación humana fue con **evaluadores externos**; los autores nunca etiquetaron.
7. No se regeneró el corpus. El alcance es G1 vs G2 con la misma memoria estructurada.

---

## 10. Storyboard propuesto (15 min ≈ 15 láminas)

| # | Min | Lámina | Mensaje único | Visual |
|---|---|---|---|---|
| 1 | 0:30 | Portada | Título, autores, asesor | Limpia |
| 2 | 1:00 | El problema | Un DM de IA olvida, contradice y **decide por ti** | 3 íconos con un ejemplo corto de turno en 2.ª persona |
| 3 | 1:00 | El vacío | Hay MAS vs monolítico en otros dominios, nada controlado en rol de mesa, y menos en español | Mapa "lo que existe / lo que falta" |
| 4 | 0:45 | Pregunta e hipótesis | ¿MAS > monolítico? 3 dimensiones × 2 preguntas | Árbol de H1a–H1f |
| 5 | 1:15 | Diseño | Mismo escenario, dos arquitecturas; todo lo demás constante | `fig1_diseno.png` + "27 pares · 75,600 turnos" |
| 6 | 1:15 | Las dos arquitecturas | La única diferencia es quién narra | `fig2_arquitecturas.png` |
| 7 | 1:00 | Memoria estructurada | 3 candados contra la alucinación | Ejemplo del soborno (principista vs corrupto) |
| 8 | 1:00 | Cómo se midió | Rúbrica → instrumentos deterministas → prueba de perturbación → clasificación | Embudo de 4 pasos |
| 9 | 1:00 | ¿G2 se degrada? | No, en 1,400 turnos | Línea plana de 7 bloques (z 2.768 → 2.742) |
| 10 | 1:15 | Reactiva (H1d) | Empate en lo específico; G1 solo escribe más largo | Barra dividida: específico vs genérico |
| 11 | 1:00 | Longitudinal (H1e) | Ningún instrumento alcanzó a decidir | 3 intentos fallidos, mostrado con honestidad |
| 12 | 1:30 | **Agencia (H1f)** | **0.17 % vs 3.47 %**, y se sostiene al corregir por precisión | Número grande + 27/27 pares |
| 13 | 0:45 | ¿Gana por gastar más? | No: más cómputo va con más usurpación | Dispersión cómputo vs usurpación por brazo |
| 14 | 1:00 | Conclusión | Hipótesis general no sostenida; ventaja específica en agencia | Una frase grande |
| 15 | 0:45 | Aportes y trabajo futuro | Corpus en español, batería validada, NLI en español, jugadores humanos | 3–4 bullets |

**Backup (no se exponen):** dados · potencia · persona2 por evaluador · auditoría de nombres · Jericho por tipo de cambio · Kaplan-Meier · semántico v1/v2 · último bloque · base de datos · rúbrica · instrumentos y clasificación.

---

## 11. Preguntas probables del jurado (respuesta corta)

- **"¿Por qué no evaluaron con humanos?"** El panel no era viable sobre 75,600 turnos. Se priorizó reproducibilidad, y la validación humana externa se hizo donde el instrumento interpreta texto (dos validaciones).
- **"¿Un LLM jugando contra un LLM no sesga?"** El jugador es el mismo en ambos brazos, con dados fuera de su control, y el sesgo se cancela dentro del par.
- **"persona2 tiene 33 % de precisión, ¿cómo aceptan H1f?"** Se corrigió la tasa de cada brazo por su propia precisión y G1 sigue menor en 27/27 pares. Lo que cambia es la magnitud, no la dirección.
- **"¿Y si G1 gana por más cómputo?"** Ver la sección 8: dentro de cada brazo la relación es opuesta.
- **"¿Por qué CR-2 favorece a G2?"** Es una diferencia pequeña; en lo específico hay empate, y la ventaja cruda de G1 es la longitud.
- **"¿Qué aporta si la hipótesis general no se sostiene?"** Un resultado negativo controlado: con buena memoria estructurada, el MAS no aporta coherencia medible pero sí respeto a la agencia, lo que orienta dónde vale especializar. Además deja un corpus y una batería de instrumentos en español.
- **"Validez vs confiabilidad"**: los kappa de la literatura miden confiabilidad; la validez se buscó por perturbación y por contraste con juicio humano externo.

---

## 12. Pendientes que NO son del deck

Los está cerrando Luis en el documento: dedicatorias, DNI/ORCID, número de la R.D., jurado, constancia del asesor.
