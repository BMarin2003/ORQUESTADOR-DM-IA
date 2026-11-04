# Cambios al documento de tesis — validación humana v2

Cada bloque indica dónde va y qué texto reemplaza. Va junto con `QN2_v3b_para_documento.md` (persona2 v3b, H1c y H1f), que sigue vigente salvo lo que aquí se indica para la Tabla OE6-8. Los evaluadores se rotulan E1 a E5 en todo el documento.

---

## 1. Metodología, procedimiento: validación humana de los instrumentos

**Reemplaza**, en el párrafo que empieza «A partir de esta prueba, cada instrumento se clasificó…», desde «De manera complementaria, los instrumentos cuya validez depende de interpretar el texto…» hasta el final del párrafo, por:

> De manera complementaria, los instrumentos cuya validez depende de interpretar el texto se contrastaron con el juicio de cinco evaluadores humanos externos al equipo investigador, todos con experiencia como directores de juego, dado que la participación de los autores en la validación introduciría un sesgo, real o percibido, incompatible con el diseño. Los evaluadores etiquetaron de forma ciega, sin conocer el brazo ni el veredicto de los detectores, una muestra estratificada de 982 ítems que comprendió cuatro preguntas formuladas con el mismo criterio que aplica cada instrumento: la usurpación de la agencia del personaje jugador (persona2; 400 turnos), el personaje no jugador inactivo narrado como activo (200 turnos), el reflejo narrativo de los cambios de estado registrados (Jericho-QA; 200 cambios) y la respuesta a la acción específica del jugador (150 turnos), más 32 ítems de control con respuesta inequívoca, intercalados al azar y no distinguibles de los demás. Cada evaluador recibió los ítems en un orden aleatorio propio y un libro de códigos con la definición operativa, los casos que cuentan y los que no cuentan, y la procedencia bibliográfica de cada instrumento. Los criterios de exclusión se fijaron antes del etiquetado: un evaluador se excluía de una pregunta si fallaba más del 20 % de sus ítems de control o si respondía la misma opción en todos sus ítems. La referencia de cada ítem fue la mayoría de los evaluadores retenidos en la pregunta correspondiente.

**Reemplaza** el párrafo que empieza «Asimismo, durante la validación del detector de personajes no jugadores inactivos se excluyó…» por:

> Asimismo, la integridad de cada registro de etiquetado se verificó antes del análisis, comprobando que el orden de los ítems correspondiera al código del evaluador y que el archivo conservara el formato generado por el formulario. En aplicación de los criterios de exclusión prefijados, E1 se excluyó de las preguntas de usurpación de la agencia y de cambios de estado, E4 de la pregunta de usurpación de la agencia y E5 de la pregunta de cambios de estado, por superar el umbral de fallos en los ítems de control. Los resultados con los cinco evaluadores, sin exclusiones, se reportan como análisis de sensibilidad.

**Reemplaza**, en el párrafo siguiente, la primera oración («Del mismo modo, en la validación externa de persona2… inferior al azar.») por:

> Del mismo modo, la regla de conteo de persona2 excluye las atribuciones que el jugador declaró en su propia acción y las inferencias que resultan de una prueba de habilidad declarada, criterio que se aplicó también a la definición de la pregunta de usurpación en el libro de códigos.

## 2. Metodología, aspectos éticos (5.7.5)

**Reemplaza** el párrafo que empieza «La investigación no involucró a personas como sujetos experimentales…» por:

> La investigación no involucró a personas como sujetos experimentales, dado que las campañas se generaron mediante la interacción entre las arquitecturas y un agente jugador autónomo, por lo que el corpus no contiene datos personales. La participación humana se limitó a los cinco directores de juego que, de forma voluntaria, actuaron como evaluadores externos en la validación de los instrumentos, quienes firmaron un consentimiento informado escrito antes de realizar la tarea (Anexo X), en el que se describen el propósito del estudio, la naturaleza de la tarea, el carácter voluntario de la participación, la posibilidad de retirarse en cualquier momento y el tratamiento confidencial de sus respuestas. Los evaluadores se identifican en el documento y en el repositorio únicamente mediante códigos (E1 a E5), sin registrar datos que permitan reconocerlos. El etiquetado se realizó sin conocer el brazo ni el veredicto de los detectores, y los criterios de exclusión se fijaron antes del etiquetado y se aplicaron como se describe en el apartado 5.7.4.

## 3. Metodología, análisis estadístico

**Reemplaza**, en el párrafo que empieza «Dado que el motor incorporó el avance determinista…», la oración «Por su parte, la precisión y la exhaustividad de los detectores…» hasta el final del párrafo, por:

> Por su parte, el desempeño de los detectores frente a la referencia humana se describió mediante la matriz de confusión, el porcentaje de acuerdo y el kappa de Cohen (Cohen, 1960), la precisión con intervalos de confianza de Wilson (Wilson, 1927) y la exhaustividad ponderada por estrato, dado que la muestra se estratificó según la salida de cada detector; en este caso, cada ítem pesa el tamaño de su estrato en el corpus dividido por su tamaño en la muestra, y los intervalos de confianza de la exhaustividad y del kappa se obtuvieron por remuestreo estratificado (2,000 réplicas). Para la respuesta a la acción, cuyo instrumento produce un valor continuo, se estimó el área bajo la curva ROC frente a la referencia humana, con intervalo de confianza por remuestreo, y la correlación biserial puntual, sin fijar un umbral. El acuerdo entre evaluadores se estimó mediante el kappa de Fleiss (Fleiss, 1971) y el alfa de Krippendorff (Krippendorff, 2004).

> Referencia nueva: Krippendorff, K. (2004). *Content analysis: An introduction to its methodology* (2nd ed.). Sage.

---

## 4. OE-3: persona2

**Tabla OE3-1, columna Clasificación de QN-2:** «Confirmatorio condicionado (precisión de 50.0 % frente a la referencia humana)».

**Texto de la Tabla OE3-9:** se usa el de `QN2_v3b_para_documento.md`, sin la última oración sobre la precisión de 33.3 %.

**Nota de la Tabla OE3-10, reemplaza la frase sobre persona2 por:** «…y persona2 se clasifica como confirmatorio condicionado, dado que su precisión frente a la referencia humana fue de 50.0 %.»

**Interpretación (párrafo que empieza «A diferencia de las dimensiones reactiva y longitudinal…»), reemplaza desde «Por el contrario, la usurpación de la agencia…» hasta el final del párrafo por:**

> Por el contrario, la usurpación de la agencia admite una lectura de calidad inequívoca, dado que una tasa menor implica un mayor respeto por las decisiones del jugador, y su presencia sistemática resulta relevante si se considera que la toma del control del personaje fue el fallo que los evaluadores de FIREBALL señalaron con mayor frecuencia (Zhu et al., 2023), aunque la mitad de las marcas del detector no corresponde a una usurpación según el juicio humano, como se detalla en el análisis de brechas de este objetivo.

**Análisis de brechas de OE-3: reemplaza los dos párrafos que siguen al primero (desde «Para completar el cierre, tres directores de juego…») por:**

> Para cerrarla, cinco directores de juego externos al equipo investigador etiquetaron de forma ciega 400 turnos estratificados según la salida del detector, más 10 ítems de control. Tres evaluadores superaron los criterios de calidad prefijados en esta pregunta (E2, E3 y E5), con un acuerdo alto entre ellos (κ de Fleiss = 0.85; α de Krippendorff = 0.85; 92.5 % de ítems unánimes), lo que proporciona una referencia humana fiable.
>
> Frente a esa referencia, la precisión de persona2 fue de 50.0 % (6 de 12 turnos marcados; IC 95 % de Wilson 25.4–74.6 %), de 1 de 1 en G1 y de 5 de 11 en G2 (45.5 %; IC 95 % 21.3–72.0 %). La revisión de las marcas del detector mostró que sus falsos positivos típicos corresponden a sensaciones físicas que su léxico asocia con emociones, como «el polvo te irrita la garganta», y a condicionales que no distingue de una atribución efectiva. En los turnos que el detector no marcó, en cambio, los evaluadores señalaron con frecuencia la narración del resultado de la acción del jugador sin atribución explícita, como «el cuerpo se desliza» o «la respuesta cae en el vacío», casos que el libro de códigos excluye, por lo que la exhaustividad del detector no se estima a partir de esta referencia. En consecuencia, persona2 se mantiene como confirmatorio condicionado, con una precisión conocida que se emplea en el análisis de sensibilidad de H1f (Tabla OE6-8), y la brecha queda cerrada en lo que respecta a la concordancia del detector con un juicio humano fiable.

---

## 5. OE-5: validación humana de PNJ inactivo y Jericho-QA

**Reemplaza** los párrafos desde «Para cerrarla, se extrajo del corpus una muestra estratificada de 60 turnos…» hasta el final del análisis de brechas, **incluida la Tabla OE5-7**, por:

> Para cerrarla, cinco directores de juego externos al equipo investigador etiquetaron de forma ciega dos preguntas formuladas con el mismo criterio de cada instrumento. Para el detector de personajes no jugadores inactivos se usaron 200 turnos: 100 en que el detector marcaba al personaje como activo, 50 en que el personaje se mencionaba sin ser marcado y 50 en que no se mencionaba; junto a cada turno se mostraba el estado del personaje registrado en la base de datos. Para Jericho-QA se usaron 200 cambios de estado, 100 reconocidos y 100 no reconocidos por el instrumento, con la narración del turno del cambio y del siguiente. Los cinco evaluadores superaron los criterios de calidad en la primera pregunta y tres (E2, E3 y E4) en la segunda.

**Tabla OE5-7. Validación humana de los detectores de personajes inactivos y de Jericho-QA.**

| Instrumento | n | Acuerdo entre evaluadores (α de Krippendorff) | % de acuerdo con la referencia | κ de Cohen [IC 95 %] | Precisión [IC 95 %] | Exhaustividad ponderada [IC 95 %] |
|---|---|---|---|---|---|---|
| PNJ inactivo (refinado) | 200 | 0.55 (5 evaluadores) | 73.5 % | 0.47 [0.41, 0.53] | 96.0 % [90.2, 98.4] | 6.3 % [4.4, 8.8] |
| Jericho-QA | 200 | 0.55 (3 evaluadores) | 63.5 % | 0.27 [0.16, 0.39] | 89.0 % [81.4, 93.7] | 34.0 % [30.5, 38.2] |
| · cambios de condición | 97 | — | 67.0 % | 0.26 [0.07, 0.44] | 87.9 % [77.1, 94.0] | 40.5 % [35.1, 47.7] |
| · cambios de afinidad | 103 | — | 60.2 % | 0.27 [0.13, 0.41] | 90.5 % [77.9, 96.2] | 28.3 % [24.2, 33.7] |

*Nota.* Referencia: mayoría de los evaluadores retenidos en cada pregunta. Precisión con intervalo de Wilson; exhaustividad ponderada por el tamaño de cada estrato en el corpus, con intervalo por remuestreo estratificado (2,000 réplicas). Con los cinco evaluadores, sin exclusiones, Jericho-QA obtiene una precisión de 90.0 % y una exhaustividad de 33.5 %, y los valores del detector de personajes inactivos no cambian. En síntesis, ambos detectores aciertan casi siempre cuando marcan un caso, pero omiten la mayoría de los casos reales, sobre todo el de personajes inactivos.

> Como se observa en la Tabla OE5-7, ambos instrumentos son conservadores: cuando señalan un caso, el juicio humano lo confirma en nueve de cada diez ocasiones o más, pero omiten la mayor parte de los casos reales. En el detector de personajes inactivos, la omisión se concentra en los turnos en que el personaje se menciona sin ser sujeto gramatical, donde los evaluadores lo juzgaron activo en 47 de 50 casos. Lo relevante para la comparación entre arquitecturas es que esa omisión es similar en ambos brazos: en ese estrato, los evaluadores juzgaron activo al personaje en 37 de 40 casos de G1 y en 10 de 10 de G2, y entre los cambios que Jericho-QA no reconoció, los juzgaron reflejados en la narración en el 60 % de G1 y el 62 % de G2. Por tanto, las tasas absolutas de ambos instrumentos están subestimadas, pero el error no favorece a ninguna arquitectura.
>
> En los cambios de afinidad, además, una auditoría de 30 cambios mostró que la narración refleja el cambio registrado solo en 12 casos (40.0 %; IC 95 % de Wilson 24.6–57.7 %), lo que indica que parte de los cambios de afinidad que el extractor registra no tiene un correlato narrativo claro y explica la menor exhaustividad de Jericho-QA en esa familia.
>
> En consecuencia, la brecha queda cerrada, dado que ambos instrumentos cuentan con una estimación de su desempeño frente a un juicio humano externo, ciego y con criterios de calidad prefijados. El detector de personajes inactivos y Jericho-QA se mantienen como exploratorios, porque su baja exhaustividad impide sostener con ellos una hipótesis confirmatoria, y H1e permanece sin decisión confirmatoria.

**Índice de tablas:** cambia el título de la Tabla OE5-7 por «Validación humana de los detectores de personajes inactivos y de Jericho-QA».

---

## 6. OE-6: H1f y Tabla OE6-8

**Docimasia y nota de la Tabla OE6-7:** se usan las de `QN2_v3b_para_documento.md`. Al final del texto de la docimasia se agrega:

> Dado que la precisión del detector frente a la referencia humana fue de 1 de 1 en G1 y de 5 de 11 en G2, se repitió el contraste tras multiplicar la tasa de cada campaña por la precisión estimada de su arquitectura, tal como se presenta a continuación.

**Tabla OE6-8. Análisis de sensibilidad de H1f a la precisión del detector persona2 — Calidad narrativa emergente, n = 27 pares.**

| Escenario | Precisión aplicada G1 | Precisión aplicada G2 | Mdn G1 (% de turnos) | Mdn G2 (% de turnos) | Pares con G1 < G2 | Wilcoxon unilateral |
|---|---|---|---|---|---|---|
| Estimaciones puntuales | 100 % | 45.5 % | 0.00 % | 0.17 % | 27 de 27 | p < 0.0001 |
| Escenario más desfavorable para H1f | 100 % | 21.3 % | 0.00 % | 0.08 % | 23 de 27 | p < 0.0001 |

*Nota.* La tasa de cada campaña se multiplica por la precisión estimada de su arquitectura frente a la referencia humana (G1: 1 de 1; G2: 5 de 11, IC 95 % de Wilson 21.3–72.0 %). El escenario más desfavorable combina la precisión máxima en G1 con el límite inferior del intervalo de G2. Mdn: mediana. En síntesis, la ventaja de G1 se conserva incluso suponiendo el detector más impreciso posible en G2.

**Reemplaza** el párrafo que empieza «En la Tabla OE6-8, con las estimaciones puntuales…» por:

> En la Tabla OE6-8, con las estimaciones puntuales de la precisión, G1 se mantuvo por debajo de G2 en los 27 pares y, en el escenario más desfavorable para la hipótesis, que aplica a G2 el límite inferior de su precisión y a G1 la precisión máxima, en 23 de los 27 pares (Wilcoxon unilateral, p < 0.0001 en ambos casos). En consecuencia, la aceptación de H1f es robusta al error del detector: aun si la mayor parte de las marcas en G2 fueran falsos positivos, el sistema monolítico seguiría usurpando la agencia del jugador con mayor frecuencia que el multiagente. La magnitud real es menor que la reportada en la Tabla OE6-6, del orden de 0.1 % a 0.2 % de los turnos en G2. Por su parte, la evidencia exploratoria de diversidad léxica no ofrece una dirección uniforme, puesto que el TTR y la repetición de bigramas a 100 palabras favorecen a G1, el MATTR favorece a G2 (r = −0.68) y el MTLD no difiere.

**Análisis de brechas de OE-6: reemplaza los dos párrafos por:**

> La brecha abordada en este apartado se distingue de la de OE-3: no basta con que la precisión de persona2 sea conocida, sino que debe verificarse que no difiera entre arquitecturas al punto de fabricar la ventaja de G1. Frente a la referencia humana, la precisión del detector fue de 1 de 1 en G1 y de 5 de 11 en G2 (45.5 %; IC 95 % de Wilson 21.3–72.0 %), es decir, el detector produce falsos positivos sobre todo en G2, lo que podría inflar la diferencia. Para estimar ese efecto, la tasa de cada campaña se multiplicó por la precisión estimada de su arquitectura y se repitió el contraste pareado: G1 se mantuvo por debajo de G2 en los 27 pares con las estimaciones puntuales y en 23 de 27 en el escenario más desfavorable, con p < 0.0001 en ambos casos (Tabla OE6-8).
>
> Por tanto, la dirección de H1f es robusta al sesgo diferencial del detector, en tanto que su magnitud real es menor que la reportada y se sitúa entre 0.1 % y 0.2 % de los turnos en G2, frente a una usurpación prácticamente nula en G1. La brecha queda cerrada y H1f se sostiene en su dirección, referida a la usurpación explícita que el detector capta.

---

## 7. OE-6 o capítulo de validación: pregunta de respuesta a la acción

**Agrega**, donde se reporta la validación del instrumento de respuesta a la acción específica (CR-2a):

> Para la respuesta a la acción específica, cinco evaluadores juzgaron si la respuesta del director de juego atendía la acción declarada por el jugador en 100 turnos tomados al azar y en 50 de la cola inferior del instrumento. Sobre los turnos al azar, el valor continuo del instrumento discriminó entre las respuestas juzgadas pertinentes y las juzgadas ajenas a la acción con un área bajo la curva de 0.84 (IC 95 % 0.74–0.92; correlación biserial puntual = 0.40), y en la cola inferior los evaluadores juzgaron ajenas a la acción el 54.0 % de las respuestas (27 de 50; IC 95 % de Wilson 40.4–67.0 %), frente al 15 % de los turnos al azar. El acuerdo entre evaluadores fue moderado (α de Krippendorff = 0.31), valor que se explica en parte por la alta prevalencia de respuestas pertinentes (85 %), condición en la que los coeficientes corregidos por azar subestiman el acuerdo observado (Byrt et al., 1993).

---

## 8. Anexos

- **Anexo X.** Consentimiento informado: modelo y formularios firmados, sin código de evaluador.
- **Anexo Y.** Libro de códigos de la validación humana (cuatro preguntas, ítems de control, criterios de exclusión y referencia).
- **Anexo Z.** Tabla de respuestas de cada evaluador por ítem (`anexo_respuestas_v2.csv`), con resumen criptográfico del protocolo.

## 9. Agradecimientos

En «A los directores de juego que participaron de manera voluntaria como evaluadores externos…», no hace falta cambiar nada.
