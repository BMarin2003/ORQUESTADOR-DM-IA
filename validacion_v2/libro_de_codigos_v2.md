# Libro de códigos — Validación humana v2 (persona2 y PNJ inactivo)

Versión: 1.0 · 2026-10-28 · Estado: **congelado** (ver congelamiento_v2.sha256)

## 0. Principio de la validación

El evaluador humano y el detector responden **la misma pregunta, sobre la misma unidad y con las mismas dos opciones (Sí / No)**. El evaluador aplica la **definición operacional del indicador** tal como la declara la tesis; el detector aplica su **implementación en código**. La validación mide si la implementación reproduce la definición. No se modifica ningún detector, ningún umbral ni ningún resultado del corpus.

- No existe la opción «Dudoso» ni «No aplica». Si el evaluador no está seguro, elige la respuesta que considere más probable.
- El evaluador no ve el veredicto del detector, el brazo (G1/G2) ni el par.
- Cada ítem se responde una sola vez y no se corrige después.

---

## 1. Ítem persona2 — Atribución explícita al personaje jugador

**Procedencia del instrumento (se muestra al evaluador):** detector persona2, elaborado por los autores de la investigación. Operacionaliza la regla del prompt del director de juego, según la cual este «nunca asume, genera ni describe las acciones, el diálogo, los pensamientos o las emociones» del personaje jugador. Se basa en la toma de control del personaje jugador que Zhu et al. (2023) identificaron como el fallo más señalado por los evaluadores de FIREBALL.

> Zhu, A., Aggarwal, K., Feng, A., Martin, L. J., & Callison-Burch, C. (2023). FIREBALL: A dataset of Dungeons and Dragons actual-play with structured game state information. *Proceedings of the 61st Annual Meeting of the ACL*.

**Unidad:** un turno completo: la acción declarada por el jugador y la narración del DM que le responde.

**Pregunta:** *¿La narración del DM atribuye al personaje jugador, en segunda persona («tú») o por su nombre, una decisión, un pensamiento, una emoción o un acto de habla?*

### Responde «Sí» si la narración contiene al menos una de estas atribuciones

| Categoría | Qué cuenta | Ejemplos |
|---|---|---|
| Decisión | El PJ decide, elige, opta, quiere o se obliga a algo | «Decides esperar», «optas por el sendero», «te obligas a mirar» |
| Pensamiento | El PJ piensa, cree, sabe, recuerda, comprende o se da cuenta de algo | «Recuerdas a tu padre», «te das cuenta de que miente», «se te ocurre que…», «tienes la sensación de que…» |
| Emoción | El PJ siente una emoción nombrada | «Sientes miedo», «te invade la ira», «el alivio te recorre», «te asusta el silencio» |
| Habla | El PJ dice, responde, murmura o pronuncia algo | «Respondes que no», «murmuras una plegaria» |

Cuentan **aunque el jugador lo haya declarado** en su acción y **aunque ocurra tras una tirada**. Ejemplo: el jugador escribe «Decido abrir la puerta» y el DM narra «Decides abrir la puerta…» → **Sí**. La pregunta es si la narración hace la atribución, no si la atribución es legítima.

También cuenta cuando el DM nombra al PJ en tercera persona: «Kael decide retroceder» → **Sí**.

### Responde «No» si lo único que aparece es

- **Percepción:** «ves», «oyes», «notas», «percibes», «encuentras», «descubres», «sientes frío», «sientes el dolor del golpe».
- **Reflejos o consecuencias involuntarias:** «tropiezas», «caes», «sangras», «te estremeces».
- **Acciones físicas:** «te acercas», «sacas la daga», «tus dedos recorren el metal». Este ítem no evalúa acciones.
- **El «tú» dentro del diálogo de un PNJ:** —¿Tú crees que es seguro? —pregunta el guardia.
- **Preguntas u opciones al jugador:** «¿Qué haces?», «puedes entrar o esperar».
- **Condicionales e hipótesis:** «si decides quedarte…», «podrías pensar que…».
- **Futuro o condicional:** «recordarás este día», «jurarías que…».
- **«Tú» genérico o impersonal**, que no se refiere al PJ: «cuando sabes que el tiempo se agota, todo se vuelve urgente».
- **Texto fuera de personaje** entre corchetes.
- Cosas que piensan, sienten o dicen **otros personajes**.

---

## 2. Ítem PNJ inactivo — PNJ narrado como activo

**Procedencia del instrumento (se muestra al evaluador):** detector de PNJ inactivo (versión refinada), elaborado por los autores de la investigación. Contrasta la narración con el estado persistido del mundo, siguiendo el principio de verificar lo que el sistema narra frente al estado real registrado (Ammanabrolu et al., 2020). También sigue la idea de evaluar la consistencia fáctica de un personaje como la detección de enunciados que contradicen lo ya establecido (Welleck et al., 2019).

> Ammanabrolu, P., Cheung, W., Tu, D., Broniec, W., & Riedl, M. O. (2020). Bringing stories alive: Generating interactive fiction worlds. *Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment, 16*(1), 3–9.
> Welleck, S., Weston, J., Szlam, A., & Cho, K. (2019). Dialogue natural language inference. *Proceedings of the 57th Annual Meeting of the ACL*.

**Unidad:** un turno completo del DM. Junto al turno se muestra un **hecho confirmado por la base de datos**, por ejemplo: «*Valerius* figura como **desaparecido** desde el turno 114».

**Pregunta:** *En este turno, ¿se narra a ese PNJ actuando, hablando o decidiendo en el presente de la escena, como si estuviera activo?*

### Responde «Sí»

- El PNJ realiza una acción, habla o decide en la escena actual: «Valerius se acerca y te tiende la mano», «—Seguidme —ordena Valerius».
- Cuenta también si se le nombra de forma abreviada o descriptiva («Elian» por «Elian Thorne», «la criatura») y queda claro que es el mismo PNJ.

### Responde «No»

- **Recuerdo o mención retrospectiva:** «todavía os preguntáis qué le pasó a Valerius».
- **Otros hablan de él:** «el tabernero jura que vio a Valerius en el puerto».
- **Se constata su estado:** «encontráis el cuerpo de Valerius», «Valerius fue capturado al amanecer». Aquí el PNJ es sujeto de una oración pasiva, pero no actúa.
- **Forma ya asumida como no viva:** «el fantasma de Valerius».
- **El PNJ no aparece en el turno.**

Se juzga solo el turno y el hecho dado; no hace falta conocer el resto de la campaña.

---

## 2b. Ítem Jericho-QA — Cambio de estado reflejado en la narración

**Procedencia del instrumento (se muestra al evaluador):** recuerdo de cambios de estado (Jericho-QA), elaborado por los autores de la investigación. Adapta a la campaña de rol el principio de verificar el conocimiento que un sistema narrativo tiene del mundo comparándolo con su estado real (Ammanabrolu et al., 2020), en la línea del entorno de ficción interactiva Jericho (Hausknecht et al., 2020).

> Hausknecht, M., Ammanabrolu, P., Côté, M.-A., & Yuan, X. (2020). Interactive fiction games: A colossal adventure. *Proceedings of the AAAI Conference on Artificial Intelligence, 34*(05), 7903–7910.

**Unidad:** un cambio de estado registrado en la base de datos en el turno N, junto con los turnos N y N + 1 del DM. Es la misma ventana que usa el código (`ventana=1`).

**Hechos posibles:** un PNJ pasó a estar fallecido, desaparecido o capturado; o la disposición de un PNJ hacia el personaje jugador pasó a ser hostil, recelosa, fría, cordial, leal o devota.

**Pregunta:** *¿La narración de estos dos turnos refleja ese cambio?*

- **Sí:** la narración cuenta o muestra de forma reconocible el cambio para esa entidad. Ejemplos: narra su muerte, su desaparición o su captura; o muestra a ese PNJ con la actitud nueva («te mira con abierta hostilidad», «te trata con una calidez que antes no tenía»).
- **No:** el cambio no se narra; se narra otra cosa; o la actitud que se muestra no corresponde a la nueva disposición.
- Se juzga la entidad del hecho, no a otros personajes del turno.

## 2c. Ítem respuesta a la acción — Respuesta anclada en la acción específica

**Procedencia del instrumento (se muestra al evaluador):** respuesta a la acción específica, elaborada por los autores de la investigación. Mide si la respuesta del DM se ancla en lo que el jugador declaró en ese turno, comparándola con respuestas a acciones de otros turnos de la misma campaña, a partir de la exigencia de que un DM automatizado responda a la contribución concreta del jugador (Callison-Burch et al., 2022).

> Callison-Burch, C., Tomar, G. S., Martin, L. J., Ippolito, D., Bailis, S., & Reitter, D. (2022). Dungeons and Dragons as a dialog challenge for artificial intelligence. *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing*, 9379–9393.

**Unidad:** un turno: la acción declarada por el jugador y la respuesta del DM. El evaluador ve el mismo texto que lee el instrumento.

**Pregunta:** *¿La respuesta del DM responde a la acción específica que declaró el jugador en este turno?*

- **Sí:** la respuesta se ocupa de lo que el jugador intentó hacer o decir: lo resuelve, lo narra o muestra su resultado, aunque sea un fracaso.
- **No:** la respuesta ignora la acción, responde a otra cosa o es tan genérica que serviría para cualquier acción.

**Análisis sin modificar el instrumento:** el instrumento da un valor continuo (z) por turno, calculado y guardado **antes** del etiquetado. No se binariza ni se le fija un umbral. Se reporta el área bajo la curva ROC del z frente a la referencia humana (IC 95 %) y la correlación biserial puntual.

---

## 3. Ítems de control

- 32 ítems en total, mezclados al azar con los demás y no distinguibles: A y B, 5 «Sí» y 5 «No» cada una; C, 5 «Sí» y 2 «No»; D, 5 «Sí».
- Son turnos reales cuya respuesta es inequívoca según este libro de códigos. En C solo dos candidatos «No» resultaron inequívocos, porque en los cambios de disposición la actitud narrada suele ser ambigua incluso para los autores. En D no existen en el corpus respuestas inequívocamente ajenas a la acción, por lo que solo lleva controles «Sí».
- Los autores los seleccionan y responden **antes** de la ronda. Su clave se congela con el resto del protocolo.

## 4. Criterios de exclusión de evaluadores (fijados antes de etiquetar)

Un evaluador se excluye del análisis principal si cumple alguno:

1. Falla más del 20 % de los ítems de control de una pregunta (A y B: más de 2 de 10; C: más de 1 de 7; D: más de 1 de 5). En ese caso se excluye **solo para esa pregunta**.
2. Responde la misma opción en el 100 % de los ítems de una pregunta.

No se usa el tiempo de respuesta como criterio. Los resultados con todos los evaluadores, sin exclusiones, se reportan siempre como análisis de sensibilidad.

## 5. Estándar de referencia y análisis

- **Referencia por ítem:** mayoría de los evaluadores retenidos (3 de 5; si quedan 4, empate = sin referencia y el ítem se reporta aparte).
- **Por detector (preguntas A, B y C):**
  - matriz de confusión 2×2 detector vs. referencia;
  - % de acuerdo y κ de Cohen detector vs. referencia, con IC 95 %;
  - precisión y exhaustividad con IC de Wilson. La exhaustividad se pondera por estrato, porque el muestreo se estratifica según la salida del detector.
- **Pregunta D:** AUC del z frente a la referencia humana, con IC 95 %, y correlación biserial puntual, calculadas **solo sobre los 100 turnos al azar**. Los 50 de la cola baja se reportan aparte, como proporción de respuestas que los humanos juzgan ajenas a la acción. Sin umbral.
- **Entre evaluadores:** κ de Fleiss y α de Krippendorff.
- **Anexo:** tabla cruda con la respuesta de cada evaluador en cada ítem.

## 6. Muestra (a congelar)

| Pregunta / instrumento | Estrato «detector Sí» | Estrato «detector No» | Control |
|---|---|---|---|
| A · persona2 (métrica primaria) | 100 | 300 | 10 |
| B · PNJ inactivo refinado | 100 | 50 mencionado + 50 sin mención | 10 |
| C · Jericho-QA | 100 reconocidos | 100 no reconocidos | |
| C · Jericho-QA (controles) | | | 7 |
| D · respuesta a la acción (z) | 100 al azar + 50 de la cola baja (z ≤ percentil 10) | — | 5 |
| **Total** | | | **982 ítems** |

- Para PNJ, el estrato «No» se extrae de los turnos **elegibles**, es decir, con al menos un PNJ inactivo visible, en los que el detector no marcó «actuando».
- Se excluyen los turnos usados en el desarrollo de persona2 (`persona2_desarrollo_turnos.csv`) y todos los ítems vistos en la validación anterior.
- Asignación proporcional por brazo con tope por campaña: persona2 Sí ≤ 5 y No ≤ 8; PNJ No ≤ 3. PNJ Sí ≤ 30 por campaña y sin proporción por brazo, porque el detector solo se activa en 6 de las 54 campañas. Jericho-QA ≤ 10 por campaña, porque el universo es de solo 750 cambios evaluables. Respuesta a la acción ≤ 4 por campaña.
- Semillas: 20261028 (muestra), 20261029 (candidatos de control), 20261030 (identificadores de control y orden final), 20261031 (preguntas C y D), 20261101 (ajuste de D y candidatos de control C/D), 20261102 (controles C/D y orden final). Cada evaluador ve los ítems en un orden aleatorio propio, derivado de su código.
