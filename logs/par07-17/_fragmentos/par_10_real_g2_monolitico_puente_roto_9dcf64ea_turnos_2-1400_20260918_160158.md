
# VERTICAL SLICE — Par 10 (real) · G2 (Monolítico) · Puente Roto (monolithic)

- **DM:** `google/gemma-4-31B-it`
- **jugador:** `google/gemma-4-31B-it` (Isolde, desvío 65)
- **turno:** 2

## Turno 2 — 1/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2388 ms

> "Pareces haber visto un fantasma al mencionarlo."
> Observo detenidamente sus reacciones y el movimiento de su mandíbula.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 19+2=21

### [4] DM

  8433 ms

> Yara exhala un suspiro lento, intentando suavizar la línea de su mandíbula, pero el gesto es insuficiente. Al sostenerte la mirada, notas que sus pupilas se dilatan ligeramente y que el rictus de sus labios no es de miedo, sino de una resignación amarga. El movimiento rítmico de su mandíbula no es un tic nervioso, sino el hábito de quien ha masticado palabras no dichas durante demasiado tiempo; hay una carga de culpa y una urgencia contenida que choca frontalmente con la calma que intenta proyectar ante los refugiados.
> —A veces los fantasmas son los únicos que nos dicen la verdad —responde ella con una voz que ha perdido parte de su firmeza, mientras sus dedos aprietan con demasiada fuerza el borde de una manta de lana basta. Se vuelve hacia el grupo de personas que esperan, marcando una distancia física deliberada entre tú y ella.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1412 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 3 — 2/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2308 ms

> "No me sirven las metáforas, Yara. Dime qué es lo que no estás diciendo."
> Intento acercarme a ella para recuperar ese espacio que ha intentado crear, buscando obligarla a mirarme de nuevo.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 15+2=17

### [4] DM

  6310 ms

> Yara retrocede un paso, pero no huye; se queda anclada al sitio, permitiendo que acortes la distancia. Cuando sus ojos vuelven a encontrarse con los tuyos, la máscara de serenidad se agrieta. No es solo cansancio lo que ves en sus pupilas, sino una angustia sorda, el peso de una mentira que la está consumiendo por dentro. Hay una discordancia evidente entre su discurso público de esperanza y la tensión eléctrica que recorre sus hombros.
> —No es una metáfora —susurra, bajando la voz tanto que el viento del paso casi se lleva sus palabras—. Es hambre. Mucha más hambre de la que he admitido. Si la gente supiera cuánto queda realmente en los silos, el campamento se despedazaría antes del amanecer.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  7076 ms · 1 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ evento yara_sorem · secret_entrusted
  ✓ delta yara_sorem · npc.secret_revealed = Yara ya sabe que el campamento tiene comida para menos días de los que le ha dicho a nadie

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  ✗ PNJ inexistente: yara_sorem
  ✗ entidad inexistente: yara_sorem

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 4 — 3/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3377 ms

> "Así que nos estás mintiendo a todos para evitar que nos matemos."
> Me acerco más a ella, bajando el tono para que nadie más nos oiga.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 19+2=21

### [4] DM

  10440 ms

> Yara cierra los ojos un instante, y el aire que expulsa es un gemido ahogado. Al abrirlos, la mirada ya no es la de una líder, sino la de alguien que se siente acorralada por el tiempo. No hay rastro de orgullo en su postura; solo una rendición silenciosa ante la verdad que acabas de desnudar.
> —No es una mentira, es un escudo —responde en un hilo de voz, mientras sus dedos se cierran con fuerza sobre la tela de su túnica—. El pánico es un incendio que consume más rápido que la inanición. Si me odian por haberles mentido, puedo soportarlo, siempre y cuando haya alguien vivo para hacerlo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  4318 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta yara_sorem · npc.secret_revealed = Yara ya sabe que el campamento tiene comida para menos días de los que le ha dicho a nadie

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  ✗ entidad inexistente: yara_sorem

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 5 — 4/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1896 ms

> "El odio es más fácil de gestionar que el hambre, pero el pánico mata igual."
> Me cruzo de brazos, observándola con frialdad.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 16+2=18

### [4] DM

  6854 ms

> Yara se tensa ante tu frialdad, y el ligero temblor de sus manos delata que tu observación ha dado en el blanco. No intenta rebatir tus palabras; en su lugar, baja la cabeza, dejando que un mechón de pelo oculte su expresión mientras el silencio se prolonga entre ambos.
> Al observar sus gestos y el modo en que evita sostenerte la mirada, notas que su desesperación no nace del miedo a ser descubierta, sino de una fatiga crónica. Sus hombros caen y hay una fragilidad en su voz que sugiere que ya no tiene planes de contingencia; se ha quedado sin opciones y tú eres, ahora mismo, la única variable que no puede controlar.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1312 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 6 — 5/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3826 ms

> "No me interesa tu cansancio, sino lo que oculta. Habla ahora y quizá pueda ayudarte."
> Me inclino hacia ella, manteniendo la presión psicológica para obligarla a mirarme.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 20+2=22  CRÍTICO

### [4] DM

  9928 ms

> Yara se encoge bajo tu presión, pero al verse obligada a sostenerte la mirada, sus ojos se cristalizan. No hay malicia en ellos, solo un terror gélido y pragmático. En el instante en que sus pupilas se dilatan, percibes que su silencio no es una táctica de negociación, sino un muro construido para evitar que el pánico se propague; notas que el peso de su secreto es una carga física que la está consumiendo, y que la mentira que sostiene frente a su gente es la única cosa que mantiene el orden en el campamento.
> —No hay tiempo para juegos —susurra con una voz quebrada, rindiéndose por completo—. No es lo que oculto yo, sino lo que ya no tenemos. Las reservas están vacías, mucho más de lo que he dicho. Si la gente se entera de que la comida se ha acabado, el campamento se convertirá en un matadero antes del amanecer. Por favor... si puedes hacer algo, hazlo ahora.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  768 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 7 — 6/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2338 ms

> "Así que el hambre es lo que realmente nos tiene aquí."
> Suelto la presión sobre ella y doy un paso atrás, analizando su expresión para ver si hay algún otro detalle que oculte.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 8+2=10

### [4] DM

  9800 ms

> Yara exhala un suspiro tembloroso mientras recupera el espacio personal, encogiéndose sobre sí misma. Se limpia rápidamente el rastro de una lágrima con el dorso de la mano, pero no aparta la vista de ti; su postura es la de alguien que acaba de entregar su única arma y ahora se siente desnuda ante el interlocutor.
> A pesar de su vulnerabilidad, no percibes ninguna otra señal de engaño ni omisiones deliberadas en su lenguaje corporal. Su desesperación parece absoluta y genuina; el terror que emana no es por ella misma, sino por el vacío que aguarda en los graneros del campamento.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1508 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 8 — 7/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2769 ms

> "No me interesa tu miedo, sino lo que hay en esos graneros."
> Me alejo un paso para darle aire, pero mantengo la mirada fija en ella mientras busco cualquier detalle que se le haya escapado.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 3+2=5

### [4] DM

  6607 ms

> Yara retrocede instintivamente cuando te alejas, aprovechando el espacio para abrazarse a sí misma, aunque no rompe el contacto visual. Sus hombros permanecen hundidos y su respiración es errática, como si el peso de la responsabilidad la estuviera aplastando físicamente frente a ti.
> Al observar sus gestos y su reacción, no logras extraer ninguna información adicional ni detectar ninguna grieta en su relato. Solo ves a una mujer rota que ha puesto su esperanza en alguien que acaba de decirle que su miedo no tiene valor.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2619 ms · 1 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ evento yara_sorem · ideal_violated

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  ✗ PNJ inexistente: yara_sorem

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 9 — 8/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2766 ms

> "No he dicho que tu miedo no valga nada, sino que no me sirve para resolver esto."
> Me quedo observándola en silencio, buscando algún rastro de algo que no haya mencionado.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 15+2=17

### [4] DM

  7740 ms

> Yara parpadea, procesando tus palabras con una expresión de amarga comprensión. No hay ira en su rostro, sino una resignación profunda; asiente lentamente, aceptando que la utilidad es la moneda de cambio en esta conversación. El silencio se prolonga entre ambos, roto únicamente por el viento que sacude las lonas del campamento.
> Mientras la observas, notas que Yara evita mirar hacia el centro del asentamiento, donde se encuentran las reservas. Hay una tensión específica en su mandíbula y un tic nervioso en sus dedos que no coincide con la desesperación de quien simplemente teme el hambre, sino con la angustia de quien oculta una verdad más urgente. Sus ojos reflejan una carga solitaria, un secreto que guarda con celo incluso mientras se desmorona frente a ti.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1448 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 10 — 9/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2304 ms

> "Hablemos de lo que te pone así de nerviosa. No son solo las reservas, ¿verdad?"
> Me inclino hacia ella, tratando de leer sus gestos y captar cualquier señal de lo que oculta.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 14+2=16

### [4] DM

  12170 ms

> Yara se tensa visiblemente, encogiéndose ligeramente bajo tu mirada. El tic de sus dedos se detiene en seco y exhala un suspiro tembloroso que parece vaciarle los pulmones. No intenta negarlo; la precisión de tu observación ha roto el dique de su resistencia, dejándola expuesta en medio del ruido sordo de las lonas agitadas por el viento.
> —No es que no haya comida —susurra, bajando la voz hasta convertirla en un hilo apenas audible—, es que no queda casi nada. Mucho menos de lo que he hecho creer al Consejo y a los míos. Si se enteran de que el fondo se ha agotado antes de tiempo, el pánico quemará este campamento antes de que llegue la primera nevada.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  9218 ms · 1 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ evento yara_sorem · secret_entrusted
  ✓ delta yara_sorem · npc.secret_revealed = Yara ya sabe que el campamento tiene comida para menos días de los que le ha dicho a nadie

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  ✗ PNJ inexistente: yara_sorem
  ✗ entidad inexistente: yara_sorem

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 11 — 10/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1802 ms

> "No me interesa el pánico del Consejo, sino cómo vamos a solucionar esto."
> Me acerco más a ella para que nadie más nos oiga y trato de descifrar si me está ocultando algo más.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 5+2=7

### [4] DM

  8094 ms

> Yara se inclina hacia ti, permitiendo que la cercanía cree una burbuja de privacidad mientras el viento golpea las lonas a su alrededor. Sus ojos, cargados de una fatiga antigua, te miran con una mezcla de alivio y desesperación, como quien encuentra un anclaje en medio de una tormenta.
> —Lo solucionaremos buscando fuera, entonces —responde con voz ronca, aunque mantiene la mirada fija en la tuya, sin vacilar ni mostrar signos de reticencia—. No hay más secretos, solo hambre y un invierno que no perdona. Si tienes una idea, soy toda oídos.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  976 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 12 — 11/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2707 ms

> "El invierno es el menor de nuestros problemas si no tenemos donde refugiarnos."
> Me separo un poco para mirarla a la cara y evalúo si me está ocultando algo más sobre la situación del lugar.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 6+2=8

### [4] DM

  5638 ms

> Yara sostiene tu mirada, sus hombros caídos y el rostro curtido por el frío parecen reflejar una honestidad brutal. No hay tics nerviosos ni vacilaciones en su expresión; solo una resignación cansada que encaja perfectamente con el relato de miseria que ha compartido hasta ahora.
> —El refugio es lo que tenemos —dice, lanzando una mirada fugaz hacia las lonas que crujen violentamente bajo el viento—. Es precario, sí, pero es lo único que separa a mi gente de la nieve. Si buscas algo más sólido, tendrías que mirar hacia donde nadie quiere volver.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1224 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 13 — 12/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1704 ms

> "¿Y qué es exactamente lo que nadie quiere volver a ver?"
> Me cruzo de brazos, analizando su reacción mientras busco cualquier indicio de que oculte algo más que cansancio.
> {Perspicacia}

### [3] DADOS (deterministas, del sistema)

  Perspicacia: 5+2=7

### [4] DM

  6250 ms

> Yara suspira, y el vapor de su aliento se disipa rápidamente en el aire gélido. No desvía la mirada ni muestra signos de inquietud; su postura permanece pesada, anclada en esa misma resignación agotada. Se limita a señalar con un gesto vago hacia el horizonte, donde las cumbres nevadas parecen morder el cielo gris.
> —Las tierras bajas, más allá del desfiladero —responde con voz plana—. Donde estaban los antiguos asentamientos antes de que el frío se volviera eterno. Dicen que los muros aún siguen en pie, pero que el silencio que hay allí dentro es más peligroso que la ventisca. Nadie baja allí por gusto, y mucho menos sin un motivo que valga el riesgo de no regresar.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1429 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 14 — 13/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1697 ms

> "El silencio no me asusta tanto como pasar hambre."
> Me quedo observando el horizonte que señala Yara, tratando de distinguir algún rastro de esos muros entre la nieve.
> {Supervivencia}

### [3] DADOS (deterministas, del sistema)

  Supervivencia: 17+4=21

### [4] DM

  7442 ms

> Tus ojos recorren la línea blanca y quebrada del horizonte, filtrando el ruido visual de la ventisca y las sombras engañosas del relieve. Entre la bruma gélida y el gris plomizo del cielo, detectas una irregularidad geométrica que no pertenece a la naturaleza: una silueta vertical, oscura y dentada, que rompe la curva de la montaña. Son los restos de una muralla, un colmillo de piedra negra que emerge de la nieve como un recordatorio mudo de lo que alguna vez fue un refugio.
> Yara observa tu mirada fija en aquel punto y una sombra de duda cruza su rostro. No se mueve, pero sus hombros se tensan ligeramente mientras el viento sacude su ropa raída.
> —Tienes buen ojo —murmura, casi para sí misma—. Pero recuerda que aquel silencio no es vacío, es espera.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2735 ms · 1 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ evento yara_sorem · competence_shown

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  ✗ PNJ inexistente: yara_sorem

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 15 — 14/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1798 ms

> "Si hay muros, hubo suministros. Y donde hay suministros, hay algo que vender."
> Me adelanto hacia la silueta de piedra negra, manteniendo la guardia.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 15+4=19

### [4] DM

  7678 ms

> Tus pasos hunden la bota en la nieve compacta mientras avanzas hacia el colmillo de piedra. A medida que la distancia se acorta, la muralla se revela como una estructura de basalto erosionada, cuyos bloques se han separado dejando grietas profundas donde el hielo ha crecido como dedos blancos. El viento aúlla entre las piedras, pero tu atención capta algo distinto: un rastro tenue de hollín que mancha la nieve en la base de un arco derruido y el brillo metálico de una cadena oxidada que cuelga, balanceándose rítmicamente, de un saliente superior.
> Yara se queda unos pasos atrás, observando el perímetro con cautela. Sus ojos no buscan tesoros, sino cualquier movimiento que emerja de las sombras de la piedra negra. No interviene, permitiendo que lideres la aproximación, aunque su mano no se aleja de la empuñadura de su arma.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1662 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 16 — 15/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1491 ms

> "Hollín... alguien ha estado calentándose aquí."
> Me acerco al arco derruido para examinar el rastro y la cadena.
> {Supervivencia}

### [3] DADOS (deterministas, del sistema)

  Supervivencia: 13+4=17

### [4] DM

  7230 ms

> Te inclinas sobre la nieve, donde el contraste del gris oscuro contra el blanco es nítido. El hollín no es producto de un fuego improvisado y apresurado, sino los restos de una pequeña fogata circular, cuidadosamente delimitada por piedras para contener el calor. Las cenizas aún conservan un rastro de tibieza bajo la capa de escarcha, lo que indica que quien estuvo aquí no se ha marchado hace más de unas pocas horas.
> Al levantar la vista hacia la cadena, notas que el metal no ha sido cortado, sino que el eslabón superior se ha desgastado hasta romperse por la tensión. En el suelo, justo debajo del punto donde la cadena golpea rítmicamente el basalto, hay una marca profunda y lineal en la piedra, como si algo pesado hubiera sido arrastrado hacia el interior del arco, dejando un surco que desaparece en la penumbra de la estructura.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  966 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 17 — 16/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3835 ms

> "No ha sido un accidente."
> Me pongo en cuclillas para analizar la marca del surco en el basalto, intentando determinar el peso y la naturaleza de lo que fue arrastrado.
> {Supervivencia}

### [3] DADOS (deterministas, del sistema)

  Supervivencia: 18+4=22

### [4] DM

  8649 ms

> El surco en el basalto es profundo y los bordes de la piedra están astillados, lo que indica una masa considerable, probablemente superior a los doscientos kilos, que no ha sido deslizada, sino anclada y arrastrada con una fuerza bruta y constante. La naturaleza de la marca no es la de un metal liso, sino la de algo orgánico y rugoso; quedan atrapados en las grietas del surco pequeños fragmentos de queratina endurecida y rastros de una mucosidad espesa que, pese al frío, se resiste a congelarse por completo.
> La dirección del rastro es absoluta: el objeto no vagó por el arco, sino que fue tirado con determinación hacia la oscuridad del interior. El peso era tal que el basalto, una de las piedras más duras de la región, ha cedido, dejando una hendidura que sugiere que lo que sea que pasó por aquí no caminaba, sino que se deslizaba pesadamente sobre su propio vientre o una estructura similar.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1183 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 18 — 17/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1651 ms

> "Algo muy pesado y muy asqueroso ha pasado por aquí."
> Me inclino para observar los fragmentos de queratina y trato de identificar a qué criatura pertenecen.
> {Naturaleza}

### [3] DADOS (deterministas, del sistema)

  Naturaleza: 1+1=2  PIFIA

### [4] DM

  6083 ms

> Al intentar analizar los fragmentos de queratina, tu concentración flaquea y el movimiento es torpe. Al inclinarte, tu mano resbala sobre la mucosidad viscosa y espesa que recubre el basalto; el contacto es repentino y el material, sorprendentemente adherente, se pega a tu piel con una consistencia aceitosa y un olor penetrante a descomposición marina que te provoca una arcada instantánea.
> En el forcejeo por recuperar el equilibrio y limpiar la sustancia, aplastas accidentalmente los pequeños fragmentos de queratina contra la piedra, triturándolos en un polvo grisáceo e irreconocible. El rastro, que antes ofrecía pistas tangibles, ahora es solo una mancha borrosa de detritos y limo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1875 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 19 — 18/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1975 ms

> "Maldita sea..."
> Me limpio la mano frenéticamente en la ropa, haciendo una mueca de asco por el olor. Me quedo mirando el polvo grisáceo, intentando ver si queda algún resto aprovechable.
> {Investigación}

### [3] DADOS (deterministas, del sistema)

  Investigación: 9+-1=8

### [4] DM

  4642 ms

> Te frotas la mano contra la tela, pero el aceite pálido se extiende por el tejido, dejando una mancha grasienta que se resiste a desaparecer y un aroma a pescado putrefacto que parece impregnarse en tu propia piel. El olor es denso, casi tangible, saturando el aire húmedo de la zona.
> Al inclinarte sobre la piedra para examinar los restos, solo encuentras una masa amorfa de polvo gris mezclado con el limo viscoso. Los fragmentos que antes tenían una estructura definida han desaparecido por completo, fundiéndose en una costra opaca y sin forma que no revela nada sobre el origen de la criatura.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  948 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 20 — 19/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3856 ms

> "Maldita sea, qué asco."
> Me alejo de la piedra y miro a mi alrededor buscando cualquier rastro de ese aceite o restos similares en las paredes o el suelo.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 14+4=18

### [4] DM

  5370 ms

> Te alejas de la piedra, el hedor a pescado putrefacto siguiéndote como una sombra. Al recorrer la zona con la mirada, notas que el aceite pálido no es un accidente aislado; hay finas vetas irisadas que serpentean entre las grietas del suelo, como venas grasientas que conducen hacia la oscuridad de un conducto de drenaje cercano. 
> En la pared lateral, a la altura de tu pecho, encuentras una serie de marcas profundas y paralelas grabadas en la roca, como si algo con garras pesadas se hubiera impulsado con fuerza para trepar. El rastro de limo viscoso es más espeso allí, goteando lentamente hacia el suelo y dejando un camino brillante que se pierde en la penumbra del pasillo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1873 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 21 — 20/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1545 ms

> "Vaya asco de lugar."
> Me acerco a las marcas de las garras y trato de analizar la profundidad y el patrón de los arañazos.
> {Supervivencia}

### [3] DADOS (deterministas, del sistema)

  Supervivencia: 4+4=8

### [4] DM

  4869 ms

> Te inclinas sobre la roca, pero el rastro es confuso. Las marcas son profundas, sí, pero el limo viscoso ha rellenado los surcos y ha erosionado los bordes, borrando cualquier detalle que permita distinguir el número de dedos o la fuerza exacta del impacto. 
> El patrón parece errático, más una serie de sacudidas violentas que un ascenso coordinado. Al intentar analizar el rastro, un goteo lento cae desde el techo, aterrizando con un sonido húmedo justo al lado de tu bota; es el mismo aceite pálido, denso y con ese penetrante olor a descomposición marina.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2030 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 22 — 21/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1240 ms

> "Huele a muerte y a mar..."
> Me pongo en guardia y miro rápidamente hacia arriba, buscando el origen de ese goteo.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 15+4=19

### [4] DM

  6890 ms

> Tus ojos recorren la superficie irregular del techo, donde la oscuridad se funde con la piedra húmeda. Entre las estalactitas y las grietas del techo, distingues una silueta pálida y alargada que se mimetiza con el color de la roca. Una criatura de extremidades excesivamente largas y piel traslúcida se aferra a la bóveda, suspendida justo encima de ti; el aceite pálido escurre de sus poros y de una mandíbula que permanece entreabierta, goteando rítmicamente sobre el suelo.
> La criatura permanece inmóvil, congelada en el instante en que tu mirada la encuentra. Sus ojos, dos orbes lechosos y sin pupilas, reflejan la tenue luz del entorno mientras emite un siseo vibrante que hace eco en las paredes de la gruta.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1458 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 23 — 22/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1607 ms

> "Maldita sea..."
> Doy un salto rápido hacia atrás para alejarme de su alcance y desenvaino mi arma.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 9+2=11

### [4] DM

  4889 ms

> Al intentar el salto, tu bota resbala en una capa de limo y humedad que cubre el suelo de la gruta. El movimiento, torpe y precipitado, te impide ganar la distancia necesaria y terminas retrocediendo apenas unos pasos, tropezando con tus propios pies mientras el arma sale de su funda con un sonido metálico y seco.
> La criatura, al notar que el objetivo no se ha alejado lo suficiente, reacciona al instante. El siseo se convierte en un chillido agudo que rebota en las paredes y, con un movimiento fluido y antinatural, se desprende del techo, cayendo en picado hacia ti con las garras extendidas.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  770 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 24 — 23/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1402 ms

> "¡Maldita sea!"
> Intento recuperar el equilibrio rápidamente y doy un paso lateral para esquivar el impacto del salto de la criatura mientras sujeto mi arma con fuerza.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 7+2=9

### [4] DM

  4704 ms

> El pie sigue patinando sobre el limo traicionero y el cuerpo no responde con la agilidad necesaria. El intento de desplazamiento lateral resulta torpe, dejándote en una posición vulnerable y desequilibrada justo cuando la criatura alcanza el suelo.
> El impacto es seco y violento. Las garras de la bestia se clavan en tu hombro y pecho, aprovechando tu falta de estabilidad para derribarte contra la roca húmeda de la gruta con un golpe sordo. El chillido del monstruo resuena ahora directamente sobre ti, inundando el espacio con un aliento fétido.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  999 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 25 — 24/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1104 ms

> "¡Quítate de encima, asquerosa!"
> Intento empujar la criatura con fuerza para crear espacio y ponerme de pie rápidamente.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 1+1=2  PIFIA

### [4] DM

  7476 ms

> El esfuerzo es desesperado, pero el limo bajo tu espalda traiciona cualquier punto de apoyo. Al intentar empujar la bestia, tus manos resbalan violentamente sobre su piel viscosa y el impulso te lanza hacia atrás, golpeando tu nuca contra el borde afilado de la roca. El golpe te deja aturdido y el movimiento, lejos de alejar a la criatura, la ha dejado en una posición aún más ventajosa, anclando su peso muerto sobre tu torso.
> La bestia aprovecha el vacío de tu resistencia y el desequilibrio absoluto para hundir más sus garras en tu carne, emitiendo un ronroneo gutural y húmedo. Estás completamente inmovilizado contra el suelo frío, con el rostro a escasos centímetros de sus fauces abiertas y el olor a putrefacción asfixiándote.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2043 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta Isolde · character.conditions = aturdido

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3874: Isolde.conditions = aturdido

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 26 — 25/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  4358 ms

> "¡Quita... tu asqueroso peso de encima!"
> Intento clavar mis dedos en los ojos de la criatura para obligarla a retroceder.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 20+1=21  CRÍTICO

### [4] DM

  6465 ms

> Tus dedos se hunden con una precisión brutal y violenta en las cuencas oculares de la bestia. El impacto es seco, un estallido de fluido viscoso que salpica tu rostro mientras la criatura lanza un alarido agudo, un chillido que vibra en tus propios dientes. El dolor instaantáneo y devastador rompe el agarre del monstruo; su cuerpo se convulsiona en un espasmo eléctrico, perdiendo todo el equilibrio y lanzándose hacia atrás con un impulso desesperado.
> La bestia rueda por el limo, alejándose de ti varios metros mientras se retuerce y araña el suelo, cegada y desorientada. Por primera vez desde que comenzó la lucha, el peso asfixiante ha desaparecido, dejándote el torso libre y el aire regresando a tus pulmones en bocanadas gélidas.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1253 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 27 — 26/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2508 ms

> "No volverás a tocarme."
> Me pongo en pie rápidamente y saco mi arma para rematar a la criatura mientras está desorientada.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 3+1=4

### [4] DM

  5552 ms

> El impulso de levantarte es brusco, pero el limo traicionero bajo tus botas actúa como un lubricante viscoso. En el momento en que intentas ganar verticalidad para desenvainar, tu pie resbala violentamente hacia un lado, provocando que pierdas el equilibrio. El movimiento te lanza hacia adelante, dejándote caer pesadamente sobre el suelo húmedo y frío, mientras el arma permanece aún fuera de tu alcance inmediato.
> La criatura, aunque ciega y retorciéndose en un frenesí de dolor, reacciona al sonido del impacto de tu cuerpo contra el barro. Emite un gruñido gutural y comienza a azotar el aire y el suelo a tu alrededor con sus extremidades, tanteando desesperadamente el espacio para localizar la fuente del ruido.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  940 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 28 — 27/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  995 ms

> "Maldición..."
> Intento deslizarme rápidamente por el limo para alcanzar mi arma sin hacer ruido.
> {Sigilo}

### [3] DADOS (deterministas, del sistema)

  Sigilo: 13+4=17

### [4] DM

  4783 ms

> Tus dedos raspan el limo frío mientras te desplazas con movimientos cortos y calculados, aprovechando la viscosidad del suelo para deslizarte como una sombra. El ruido del barro succionando tu ropa es mínimo, fundiéndose con el eco de los espasmos de la criatura.
> El monstruo lanza un zarpazo violento que corta el aire a escasos centímetros de tu hombro, pero sus sentidos no logran fijar tu posición exacta. Mientras la bestia vuelve a gruñir, desorientada y azotando el vacío, sientes el frío metal de la empuñadura bajo la palma de tu mano.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  989 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 29 — 28/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1138 ms

> "Ahora."
> Aprovecho la desorientación de la bestia para lanzarme hacia adelante y clavar mi hoja en su costado.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 5+2=7

### [4] DM

  4238 ms

> Te lanzas hacia adelante con un impulso brusco, pero el limo traicionero cede bajo tu peso en el peor momento. Tu pie se hunde profundamente en un remolino de barro viscoso, rompiendo el ritmo de tu carga y dejándote desequilibrado justo cuando intentas cerrar la distancia.
> La bestia, aunque desorientada, siente la vibración del suelo y el chapoteo repentino. Gira la cabeza con un movimiento espasmódico, sus ojos nublados fijándose en tu figura tambaleante mientras lanzas un tajo que solo araña superficialmente su piel coriácea, sin lograr hundir la hoja en su costado.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  926 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 30 — 29/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1850 ms

> "¡Maldito pantano!"
> Intento sacar el pie con fuerza para recuperar el equilibrio y retroceder rápidamente, alejándome del alcance de la bestia.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 8+1=9

### [4] DM

  5110 ms

> El barro succiona tu bota con una fuerza gélida y obstinada, envolviendo tu tobillo en un abrazo viscoso. Al tirar con fuerza, el terreno no cede; el sonido es un chapoteo sordo y húmedo que resuena en el silencio del pantano, dejándote anclado al suelo mientras luchas por no caer de espaldas.
> La bestia aprovecha tu vulnerabilidad. Al verte atrapado y tambaleante, emite un gruñido gutural que vibra en tu pecho y lanza una embestida brusca, cerrando la distancia que intentabas recuperar con un movimiento rápido y pesado.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  988 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 31 — 30/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1455 ms

> "¡Maldito seas!"
> Intento zafar mi bota con un tirón violento mientras busco algún apoyo sólido en el barro para no caer.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 9+1=10

### [4] DM

  4852 ms

> El tirón es brusco, pero el barro se resiste con una tenacidad asquerosa, manteniendo la bota anclada en el fondo viscoso. En el esfuerzo por liberar la pierna, tu equilibrio se quiebra y el cuerpo se inclina peligrosamente hacia atrás, dejando tu pecho expuesto y el centro de gravedad perdido en el fango.
> El gruñido de la bestia se convierte en un bufido triunfal. Aprovechando tu torpeza y la falta de apoyo, la criatura impacta contra ti con toda su masa, el golpe es seco y pesado, proyectándote contra el suelo húmedo mientras el olor a animal rancio y pantano te inunda los sentidos.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2573 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 32 — 31/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1428 ms

> "¡Maldita sea!"
> Intento rodar rápidamente sobre el barro para salir de debajo de la bestia y recuperar la posición.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 11+2=13

### [4] DM

  4830 ms

> El cuerpo se desliza sobre la superficie viscosa con un chapoteo sordo. El movimiento es lo suficientemente rápido para evitar quedar aplastado bajo el peso del animal, pero el barro actúa como un lubricante traicionero que te deja patinando en el suelo, manchando tu ropa y piel de una costra grisácea y fría.
> La bestia, frustrada por haber perdido su presa, lanza un bufido que expulsa gotas de saliva espesa. Se detiene un instante, con las patas hundidas en el fango, y clava sus ojos brillantes en ti mientras rasca el suelo, preparando un nuevo impulso.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1156 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 33 — 32/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3515 ms

> "No me vas a comer hoy, bicho asqueroso."
> Me impulso con fuerza para ponerme de pie rápidamente mientras busco algún punto de apoyo firme en el terreno.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 8+1=9

### [4] DM

  3520 ms

> Tus botas resbalan violentamente sobre el limo grisáceo mientras intentas ganar altura. El impulso es insuficiente y el terreno, traicionero y blando, cede bajo tu peso, dejándote en una posición vulnerable y tambaleante, medio agachado y con las manos hundidas en la viscosidad fría del suelo.
> La bestia aprovecha tu falta de equilibrio. Lanza un bramido gutural que hace vibrar el aire y carga contra ti, impulsada por la frustración, con los cascos golpeando el barro en un ritmo acelerado y ensordecedor.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1091 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 34 — 33/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1447 ms

> "¡Maldita sea!"
> Intento impulsarme hacia atrás rápidamente para salir del limo y evitar el impacto directo de la carga.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 12+2=14

### [4] DM

  5251 ms

> Tus músculos se tensan y, con un empujón desesperado, logras liberar las manos del limo justo a tiempo. El movimiento es brusco y torpe, pero suficiente para desplazar tu centro de gravedad hacia atrás mientras el suelo vuelve a ceder bajo tus pies.
> La bestia impacta con un estruendo sordo donde hace un instante estabas tú. El animal no logra frenar su inercia y, debido a la viscosidad del terreno, patina violentamente, clavando sus cascos en el barro y derrapando hacia un lado. El bramido se convierte en un bufido de confusión mientras intenta recuperar la estabilidad, dejándote un breve instante de respiro en el aire cargado de olor a azufre y tierra mojada.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2762 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 35 — 34/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1828 ms

> "Maldita sea..."
> Aprovecho que la bestia está desestabilizada para alejarme rápidamente del punto de impacto, buscando terreno más firme donde apoyarme.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 9+1=10

### [4] DM

  4907 ms

> Tus pies resbalan en la superficie aceitosa mientras intentas ganar distancia. El barro se resiste, succionando tus botas y obligándote a luchar contra la densidad del terreno en cada paso. Logras desplazarte unos metros, pero el movimiento es lento y torpe, dejándote aún en una zona donde el suelo vibra y cede bajo tu peso.
> La bestia recupera el equilibrio con un sacudón violento de sus hombros. Lanza un bufido que expulsa vapor caliente por sus fosas nasales y gira la cabeza hacia ti, fijando sus ojos brillantes en tu posición. Sus cascos arañan la superficie viscosa, buscando tracción para cargar de nuevo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  886 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 36 — 35/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1526 ms

> "No me atraparás en este lodo."
> Intento buscar rápidamente algún punto de apoyo firme o una irregularidad en el terreno para impulsarme fuera de la zona aceitosa.
> {Supervivencia}

### [3] DADOS (deterministas, del sistema)

  Supervivencia: 9+4=13

### [4] DM

  5126 ms

> Tus ojos recorren frenéticamente el entorno mientras el barro sigue succionando tus botas. Apenas logras distinguir algunas protuberancias oscuras bajo la capa de aceite y limo, pero el terreno es traicionero y uniforme; no hay ninguna roca prominente ni raíz robusta que te permita un impulso seguro. Cada intento de buscar un punto de apoyo solo te hunde unos centímetros más en la viscosidad.
> La bestia aprovecha tu vacilación. Con un bramido que hace vibrar el aire, clava sus cascos en una zona ligeramente más densa y lanza una embestida brutal, desplazando una ola de lodo negro hacia ti mientras acorta la distancia con una velocidad aterradora.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1143 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 37 — 36/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2020 ms

> "¡Maldita sea!"
> Intento echarme hacia atrás con un movimiento brusco para evitar el impacto directo de la ola de lodo y la embestida.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 9+2=11

### [4] DM

  5251 ms

> El movimiento es torpe y desesperado. Al intentar impulsarte hacia atrás, el limo se aferra a tus botas con una fuerza succionadora, frenando tu inercia justo cuando la masa de lodo negro te golpea de lleno. La ola te envuelve, cegándote momentáneamente y empujándote contra la viscosidad del suelo.
> A través del chapoteo y el hedor a aceite, el impacto es inevitable. El animal no se detiene; su masa muscular y el impulso de la embestida te alcanzan mientras intentas recuperar el equilibrio, golpeándote con la brutalidad de un ariete de carne y hueso.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1231 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 38 — 37/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1295 ms

> "¡Maldita sea!"
> Intento hacerme un ovillo para amortiguar el golpe y trato de impulsarme hacia un lado para salir de la trayectoria del animal.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 20+2=22  CRÍTICO

### [4] DM

  5908 ms

> El impacto es inminente, pero el movimiento es fluido y preciso. En el instante en que la masa del animal se cierne sobre ti, te encoges con un reflejo eléctrico, transformando la caída en un giro coordinado. El cuerpo del animal choca contra el aire donde estabas hace un segundo, y aprovechas la inercia del golpe para impulsarte lateralmente, deslizándote sobre el limo negro como si el barro fuera hielo.
> El animal, incapaz de corregir su trayectoria debido a la velocidad y la viscosidad del terreno, pasa de largo con un bufido violento, hundiendo sus patas en el fango mientras intenta frenar. Te encuentras ahora a unos metros de distancia, jadeando, con la ropa empapada en aceite y lodo, pero fuera del alcance inmediato de la bestia.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1063 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 39 — 38/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  16 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1800 ms

> "Maldita bestia..."
> Me pongo en pie rápidamente, tratando de limpiar el lodo de mis ojos, y busco el punto más firme del terreno para no volver a resbalar.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 14+4=18

### [4] DM

  6127 ms

> Te incorporas con rapidez, el lodo espeso resbalando por tu piel como una capa de petróleo frío. Al limpiar tus ojos, la visión se aclara y el entorno se revela con nitidez: el terreno es una trampa de sedimentos inestables, pero a tu derecha, donde el limo se vuelve más grisáceo y aparecen algunas raíces expuestas de árboles petrificados, la tierra se siente compacta y sólida.
> Desde esa posición, notas que la bestia lucha por liberarse del fango, sus patas delanteras hundiéndose hasta los codos en el barro viscoso. El animal emite un bramido sordo, pero tu mirada capta algo más: unos metros detrás de la criatura, medio oculta por una cortina de juncos marchitos, asoma la esquina de una estructura de piedra tallada, demasiado geométrica para ser una formación natural.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1856 ms · 0 eventos · 0 deltas · 1 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ creación location: estructura de piedra tallada

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → creada: location estructura de piedra tallada

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 40 — 39/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1897 ms

> "Vaya suerte tienes, bicho."
> Ignoro a la criatura y me dirijo con cuidado hacia la estructura de piedra, tratando de no hundirme.
> {Sigilo}

### [3] DADOS (deterministas, del sistema)

  Sigilo: 17+4=21

### [4] DM

  3820 ms

> Te deslizas entre los juncos marchitos con la fluidez de una sombra, evitando que el chapoteo del lodo delate tu avance. El ruido del bramido sordo de la bestia, que sigue forcejeando desesperadamente en el fango, sirve como la cortina sonora perfecta para cubrir tus pasos.
> Llegas hasta la estructura de piedra sin que la criatura note tu presencia. Se trata de un pilar octogonal de granito oscuro, grabado con runas que parecen haber sido desgastadas por siglos de humedad, pero que aún conservan una geometría severa. El pilar marca la entrada a lo que parece ser un pasadizo descendente, cuya boca está parcialmente colmatada por sedimentos y raíces petrificadas.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1956 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta estructura de piedra tallada · location.detail = observed

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3905: estructura de piedra tallada.detail = observed

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 41 — 40/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2576 ms

> "Veamos qué esconden estas piedras."
> Me acerco al pilar y paso los dedos sobre las runas desgastadas, intentando descifrar su significado.
> {Historia}

### [3] DADOS (deterministas, del sistema)

  Historia: 16+-1=15

### [4] DM

  4552 ms

> Tus yemas recorren los surcos fríos del granito, sintiendo la aspereza de la piedra erosionada por los siglos. A medida que sigues el trazo de las incisiones, la geometría severa comienza a cobrar sentido en tu mente; no son simples adornos, sino una inscripción formal de advertencia y propiedad.
> Las runas pertenecen a un dialecto arcaico de la región, tallado para perdurar. El texto identifica este lugar como un "Sello de Custodia", una marca que designaba los límites de un antiguo almacén subterráneo destinado a proteger suministros vitales durante los inviernos más crudos. La inscripción advierte que solo aquellos con el "derecho de sangre o el sello del Consejo" deberían descender, sugiriendo que el pasadizo no fue diseñado para ser una tumba, sino una despensa fortificada.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1963 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✗ evidencia no literal: «el texto identifica este lugar como un "Sello de C»
  nada que escribir (correcto si el turno no cambió el mundo)
  ⚠ nombres no reconocidos: Custodia

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 42 — 41/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1647 ms

> "Suministros vitales... espero que algo de eso haya sobrevivido al tiempo."
> Sigo examinando la piedra buscando cualquier mecanismo oculto o una palanca que abra el acceso.
> {Investigación}

### [3] DADOS (deterministas, del sistema)

  Investigación: 4+-1=3

### [4] DM

  3751 ms

> Tus dedos se deslizan una vez más sobre la superficie gélida del granito, presionando las hendiduras y buscando cualquier relieve que ceda o una fisura que sugiera un mecanismo. Sin embargo, la piedra se mantiene imperturbable; el granito es macizo y cualquier resquicio que pudiera albergar una palanca está colmatado de polvo mineral y líquenes secos que no se mueven ni un milímetro bajo tu tacto.
> La superficie permanece muda, devolviéndote solo la sensación de una roca antigua y cerrada que no revela ningún secreto a simple vista. El viento sopla entre las grietas de la montaña, silbando sobre la inscripción que sigue advirtiendo sobre el derecho de sangre y el sello del Consejo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  997 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 43 — 42/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1172 ms

> "No voy a dejar que un poco de piedra me detenga."
> Me alejo un paso para observar la inscripción desde otro ángulo, buscando alguna pista visual que haya pasado por alto.
> {Investigación}

### [3] DADOS (deterministas, del sistema)

  Investigación: 11+-1=10

### [4] DM

  4084 ms

> Te retraes unos pasos, entornando los ojos para analizar la disposición de las letras y la geometría de la losa. El granito grisáceo es monótono, y aunque estudias la curvatura de los grabados y el desgaste de los bordes buscando alguna irregularidad o señal oculta, la inscripción se mantiene exactamente como parecía al principio: un aviso severo y plano.
> El viento vuelve a azotar la pared de roca, levantando una pequeña nube de polvo que se deposita sobre las letras, emborronando el sello del Consejo por un instante. No hay relieves anómalos, ni marcas de uso que sugieran una entrada oculta en el perímetro inmediato de la piedra.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  736 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 44 — 43/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1744 ms

> "Nada de mecanismos, entonces."
> Me alejo de la losa y empiezo a recorrer el perímetro de la pared de roca, buscando cualquier grieta o rastro de paso que el viento no haya borrado.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 4+4=8

### [4] DM

  2777 ms

> Tus pasos resuenan sordos contra el suelo pedregoso mientras recorres la extensión de la pared. El viento sigue soplando con fuerza, silbando entre los salientes de roca y llenando tu vista de partículas de arena que dificultan la observación de los detalles más finos.
> La pared de piedra se presenta como una masa compacta y uniforme, fundiéndose con la montaña en una continuidad gris y fría. No percibes ninguna fisura inusual, ni marcas de roce que sugieran el paso de personas, ni huecos que el viento haya dejado al descubierto. Para tus ojos, la roca es un muro infranqueable y mudo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  791 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 45 — 44/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1745 ms

> "No puede ser tan simple."
> Me acerco a la superficie y paso la mano con cuidado por la piedra, buscando cualquier relieve o corriente de aire que el viento no haya camuflado.
> {Investigación}

### [3] DADOS (deterministas, del sistema)

  Investigación: 17+-1=16

### [4] DM

  5491 ms

> Tus dedos recorren la superficie fría y áspera, sintiendo la vibración del viento contra la roca. Al principio solo percibes la rugosidad natural de la piedra, pero al llegar a una zona donde la pared se curva ligeramente hacia adentro, detectas una anomalía: una fina línea vertical, casi invisible, donde la piedra no encaja perfectamente. No es una grieta natural; los bordes son demasiado rectos, sugiriendo un corte deliberado que ha sido camuflado con polvo y sedimentos durante años.
> Al presionar con más fuerza en ese punto, sientes que el aire que se filtra no es el viento errático del exterior, sino una corriente constante, tenue y gélida, que emana desde el interior de la montaña. La piedra no cede al tacto, pero la junta es lo suficientemente clara como para marcar el contorno de una puerta oculta que se funde con el entorno.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1762 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta estructura de piedra tallada · location.detail = observed

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3910: estructura de piedra tallada.detail = observed

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 46 — 45/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2499 ms

> "Vaya, así que no somos los primeros en esconder cosas aquí."
> Sigo recorriendo el contorno de la junta con los dedos, buscando cualquier muesca, palanca o mecanismo oculto que permita abrir la puerta.
> {Investigación}

### [3] DADOS (deterministas, del sistema)

  Investigación: 15+-1=14

### [4] DM

  4915 ms

> Tus yemas se deslizan con cuidado por el perímetro de la junta, apartando el polvo acumulado. Al llegar a la parte superior derecha, el tacto cambia: no hay una palanca, sino una pequeña hendidura circular, del tamaño de una moneda, tallada profundamente en la roca y oculta tras una saliente natural. Al introducir el dedo, notas que el mecanismo tiene un ligero juego, permitiendo que el disco de piedra gire un cuarto de vuelta con un chasquido seco y metálico que resuena en el silencio del desfiladero.
> Un siseo prolongado escapa de la rendija mientras la presión del aire se equilibra. La losa de piedra no se desliza, sino que pivota lentamente sobre un eje central, revelando una oscuridad absoluta que engulle la luz del exterior. Desde el interior, el aroma a aire estancado y salitre húmedo te golpea el rostro, trayendo consigo un silencio sepulcral que parece absorber el ruido del viento.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  2857 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta estructura de piedra tallada · location.detail = observed

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3913: estructura de piedra tallada.detail = observed

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 47 — 46/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  17 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1989 ms

> "Vaya, parece que alguien no quería que nadie entrara aquí."
> Saco una antorcha de mi equipo y la enciendo con cuidado antes de asomarme al hueco.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 14+4=18

### [4] DM

  5595 ms

> La llama de la antorcha crepita, proyectando sombras danzantes que se alargan violentamente contra las paredes de piedra bruta. A medida que iluminas el interior, el haz de luz revela un pasillo estrecho y descendente, cuyos muros están recubiertos por una fina capa de salitre que brilla como escarcha bajo el fuego. El suelo es de losas irregulares, desgastadas por un paso antiguo, y el aire se vuelve más denso y frío conforme la luz penetra en la profundidad del hueco.
> A unos pocos metros de la entrada, tu mirada capta un detalle discordante: una serie de marcas talladas en la pared derecha, apenas perceptibles bajo el polvo. No son runas ni lenguaje conocido, sino surcos profundos y erráticos, como si alguien hubiera arañado la piedra con desesperación mientras descendía. Más adelante, el pasillo gira bruscamente hacia la izquierda, dejando el resto del camino sumido en una oscuridad que la antorcha aún no logra domar.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  3439 ms · 0 eventos · 0 deltas · 1 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ creación location: pasillo descendente

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → creada: location pasillo descendente

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 48 — 47/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2717 ms

> "¿Quién demonios ha estado arañando estas paredes?"
> Me acerco a las marcas y paso los dedos sobre los surcos para sentir la profundidad y la dirección del rascado.
> {Investigación}

### [3] DADOS (deterministas, del sistema)

  Investigación: 12+-1=11

### [4] DM

  4993 ms

> Tus dedos recorren la piedra fría y áspera, sintiendo la irregularidad de los surcos. Las marcas son profundas, pero el tacto revela que los bordes están erosionados, suavizados por el tiempo y la humedad del salitre. No hay restos de sangre seca ni fragmentos de uñas en las grietas; solo el vacío de una piedra que fue violentamente marcada hace ya mucho tiempo.
> La dirección del rascado es descendente, siguiendo el flujo del pasillo hacia la oscuridad, pero los trazos son erráticos, solapándose unos sobre otros en un patrón que sugiere más una compulsión o un estado de pánico que un intento de dejar un mensaje legible. El silencio del túnel parece espesarse mientras retiras la mano, y el único sonido que permanece es el chisporroteo rítmico de tu antorcha.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  3083 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 49 — 48/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1144 ms

> "No parece un mensaje, parece un grito."
> Sigo el rastro de los arañazos hacia la oscuridad del pasillo, manteniendo la antorcha en alto.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 5+4=9

### [4] DM

  6667 ms

> Avanzas con la antorcha en alto, proyectando sombras alargadas que danzan violentamente contra las paredes húmedas. El rastro de arañazos se desvanece gradualmente a medida que te adentras en la oscuridad, dejando paso a una superficie de piedra lisa y fría que parece absorber la luz del fuego.
> El silencio se vuelve opresivo, roto únicamente por el eco de tus propios pasos y el goteo distante de agua cayendo sobre piedra. A pesar de tu atención, el pasillo se extiende frente a ti como una garganta negra y vacía, sin que ningún sonido, olor o movimiento rompa la monotonía de la penumbra.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  908 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 50 — 49/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1334 ms

> "Demasiado silencio."
> Me detengo y apoyo la espalda contra la pared, escuchando con atención cualquier sonido que no sea el goteo del agua.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 4+4=8

### [4] DM

  2550 ms

> El silencio persiste, denso y absoluto, envolviéndote mientras esperas. El goteo rítmico del agua continúa en algún punto distante, pero más allá de ese eco metálico, no percibes ningún susurro, rasguño ni respiración que rompa la quietud del túnel.
> La piedra fría contra tu espalda parece transmitir una vibración imperceptible, o quizás es solo el latido de tu propio corazón retumbando en tus oídos. El pasillo sigue extendiéndose hacia adelante, sumido en una oscuridad que la antorcha apenas logra herir.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  845 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 51 — 50/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1129 ms

> "Demasiado silencio."
> Me separo de la pared y avanzo con cautela hacia la oscuridad, tratando de no hacer ruido.
> {Sigilo}

### [3] DADOS (deterministas, del sistema)

  Sigilo: 10+4=14

### [4] DM

  3078 ms

> Tus botas rozan la piedra húmeda con una delicadeza casi quirúrgica, evitando los fragmentos de roca suelta y los charcos que podrían traicionar tu posición. El sonido de tu respiración contenida es lo único que llena el vacío mientras te deslizas hacia el corazón de la penumbra, fundiéndote con las sombras que la antorcha proyecta contra las paredes irregulares.
> El pasillo se mantiene mudo. A medida que avanzas, el aire se vuelve más pesado y cargado de un olor a salitre y moho antiguo, pero ningún eco ni movimiento delata la presencia de algo más en la oscuridad. El camino sigue recto, sumido en una quietud sepulcral que no se altera con tu avance.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1656 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 52 — 51/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1155 ms

> Me detengo un instante para agudizar el oído y olfatear el aire, intentando distinguir si ese olor a moho oculta algo más.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 7+4=11

### [4] DM

  3025 ms

> Te quedas inmóvil, cerrando los ojos para filtrar el silencio y expandir los sentidos. El aire es denso y gélido, pegándose a la piel como una película invisible. El olor a salitre y moho es dominante, una fragancia rancia que llena las fosas nasales y satura cualquier otro rastro olfativo.
> Tus oídos captan el goteo rítmico de alguna filtración lejana y el eco sordo de tu propio corazón, pero más allá de eso, la oscuridad permanece impasible. No percibes ninguna respiración ajena, ni el roce de telas, ni el siseo de algo desplazándose entre las sombras. El pasillo sigue vacío y mudo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1645 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 53 — 52/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1771 ms

> "Demasiado silencio."
> Abro los ojos y avanzo con cautela por el pasillo, manteniendo la espalda pegada a la pared y escuchando cualquier cambio en el goteo.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 3+4=7

### [4] DM

  5021 ms

> Tus pasos son leves, pero el silencio del pasillo es tan absoluto que el roce de tu ropa contra la piedra húmeda suena como un rasguño estridente. Te desplazas pegado al muro, sintiendo la viscosidad del moho en tu espalda y el frío calando a través de las capas de cuero.
> El goteo rítmico continúa, imperturbable, marcando el tiempo en la penumbra. A medida que avanzas, la oscuridad parece tragarse la poca luz que traes contigo, y aunque tus sentidos están alerta, el entorno se vuelve una masa indistinguible de sombras y humedad que no revela nada nuevo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1769 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 54 — 53/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2916 ms

> "Demasiado silencio..."
> Me detengo en seco, apago la luz para no ser un blanco fácil y agudizo el oído, intentando detectar cualquier sonido que no sea el goteo.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 16+4=20

### [4] DM

  6838 ms

> La oscuridad te envuelve por completo, transformando el pasillo en un vacío donde solo existe el tacto del moho y el frío. Al silenciar tu propia respiración, el goteo rítmico se vuelve un metrónomo que resalta, por contraste, una anomalía en el silencio: un roce seco y rítmico, como el de escamas deslizándose sobre piedra, que proviene de unos metros más adelante, justo donde el pasillo hace un giro hacia la derecha.
> Acompañando al arrastre, percibes un siseo tenue, una exhalación húmeda y prolongada que no pertenece a ninguna corriente de aire. El sonido es deliberado y lento, moviéndose con una confianza depredadora que sugiere que algo, en la negrura absoluta, ha detectado tu presencia y ahora comienza a cerrar la distancia.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  769 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 55 — 54/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1154 ms

> Me pego a la pared, tratando de fundirme con la piedra y el frío. Desenvaino mi arma lentamente, evitando cualquier ruido metálico, y aguardo en silencio.
> {Sigilo}

### [3] DADOS (deterministas, del sistema)

  Sigilo: 5+4=9

### [4] DM

  6100 ms

> El roce de las escamas sobre la piedra se detiene bruscamente. Al intentar fundirte con la pared, el roce de tu ropa contra la superficie rugosa y el leve tintineo del metal al salir de la funda resuenan en el vacío del pasillo como campanas. El silencio que sigue es sepulcral, cargado de una tensión eléctrica.
> De repente, el siseo húmedo se transforma en un bufido violento. Desde la negrura del giro a la derecha, una lengua bífida corta el aire, rastreando el calor de tu cuerpo, y un sonido gutural, similar a un gruñido ahogado, vibra en el suelo bajo tus pies. Algo acaba de localizar tu posición exacta y se lanza hacia adelante con un impulso explosivo.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  977 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 56 — 55/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2107 ms

> "¡Maldita sea!"
> Doy un salto hacia atrás para ganar distancia y pongo mi arma en guardia, intentando no entrar en pánico.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 19+2=21

### [4] DM

  3004 ms

> El impulso del salto es limpio y preciso; tus pies encuentran el apoyo justo en la piedra fría y te lanzas hacia atrás con una agilidad felina, creando un espacio vital entre tú y la amenaza. El aire silba en tus oídos mientras el vacío que antes ocupabas es llenado instantáneamente por una masa de escamas oscuras y músculos tensos que impacta contra el suelo con un golpe seco y pesado.
> Desde la penumbra, emerge una cabeza triangular con ojos verticales que brillan con una hambre ancestral. La criatura se desliza rápidamente, recuperando el equilibrio tras el ataque fallido, y emite un siseo prolongado que eriza el vello de tu nuca mientras se enrosca, preparándose para un nuevo despliegue de velocidad.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1278 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 57 — 56/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1989 ms

> "No hoy, bicho."
> Saco mi arma y busco rápidamente algún punto débil en sus escamas mientras mantengo la distancia.
> {Naturaleza}

### [3] DADOS (deterministas, del sistema)

  Naturaleza: 3+1=4

### [4] DM

  3001 ms

> La criatura se balancea rítmicamente, el cuerpo formando una espiral perfecta que oculta dónde termina la cola y empieza el torso. Intentas analizar el patrón de sus escamas y buscar una fisura en su armadura natural, pero el movimiento errático del animal y el juego de sombras de la cueva confunden tu vista; solo ves una superficie negra, brillante y aparentemente impenetrable que repele la luz.
> El siseo se intensifica, convirtiéndose en un sonido vibrante que resuena en las paredes de piedra. La bestia clava sus garras en el suelo, tensando los músculos de su cuello mientras fija sus pupilas verticales en ti, ignorando cualquier distracción.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  861 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 58 — 57/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1271 ms

> "No me asustas, bicho."
> Aprovecho su tensión para lanzarme hacia un lado y buscar un ángulo de ataque diferente.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 8+2=10

### [4] DM

  3626 ms

> Te lanzas hacia un lado buscando el flanco de la criatura, pero el suelo de la cueva está cubierto de una capa traicionera de limo y sedimentos húmedos. Tu pie resbala en el momento del impulso, rompiendo la fluidez del movimiento y dejándote en una posición torpe y expuesta.
> La bestia reacciona al instante a tu pérdida de equilibrio. El siseo se corta en seco y, con un movimiento látigo de su cuello, lanza un zarpazo veloz hacia donde has quedado vulnerable.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1628 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 59 — 58/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1165 ms

> "¡Maldita sea!"
> Intento reaccionar rápidamente para esquivar el zarpazo mientras trato de recuperar el equilibrio en el limo.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 11+2=13

### [4] DM

  4302 ms

> El zarpazo corta el aire con un silbido húmedo, rozando la tela de tu ropa mientras logras girar el torso en un movimiento brusco y desesperado. El limo cede bajo tu peso, pero consigues clavar los talones y distribuir la carga justo a tiempo para no terminar de espalmarte contra el suelo frío de la cueva.
> La criatura retrae la garra con un chasquido, sus pupilas verticales dilatándose mientras observa tu recuperación. Emitiendo un gruñido gutural, se replantea la distancia, manteniendo su cuerpo bajo y tenso, lista para lanzar un nuevo ataque ahora que el espacio entre ambos se ha reducido.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1262 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 60 — 59/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2604 ms

> "No te acercarás más, bicho."
> Saco mi arma y busco un punto débil en su postura mientras retrocedo con cautela.
> {Percepción}

### [3] DADOS (deterministas, del sistema)

  Percepción: 17+4=21

### [4] DM

  2871 ms

> Al retroceder, el sonido del metal deslizándose fuera de la vaina resuena en las paredes húmedas de la cueva. Mientras mantienes la vista fija en la bestia, notas que su centro de gravedad se desplaza demasiado hacia la derecha; el limo del suelo ha dejado una capa resbaladiza bajo su pata trasera izquierda, que tiembla ligeramente al intentar sostener el peso del animal.
> La criatura lanza un siseo, ignorando tu advertencia, y tensa los músculos del hombro. Sin embargo, el movimiento revela un trozo de piel desgarrada y expuesta en el flanco, una herida antigua que no ha cerrado del todo y que palpita con un rojo vivo bajo la pálida luz del lugar.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1019 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 61 — 60/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1798 ms

> "Tú te has descuidado."
> Aprovecho el desequilibrio de la bestia para lanzarme rápidamente hacia su flanco, intentando clavar mi arma justo en esa herida abierta.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 14+1=15

### [4] DM

  5086 ms

> Te impulsas con fuerza, aprovechando el instante en que la bestia lucha contra la inestabilidad del limo. El aire húmedo silba en tus oídos mientras recorres la distancia en un salto preciso, esquivando el alcance de sus garras y aterrizando con el peso del cuerpo proyectado hacia adelante.
> El arma impacta con un sonido sordo y visceral directamente en la carne expuesta del flanco. La criatura suelta un alarido agudo que reverbera en las paredes de la cueva, mientras un chorro de sangre oscura y espesa salpica el suelo grisáceo. El impacto la desestabiliza aún más, obligándola a retroceder torpemente mientras intenta recuperar el equilibrio.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1130 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 62 — 61/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2170 ms

> "¡Ahora que estás débil!"
> Aprovecho la inestabilidad de la bestia para girar sobre mi eje y clavar mi arma en su costado una vez más.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 4+1=5

### [4] DM

  3724 ms

> El impulso del giro es torpe y el pie resbala en el limo viscoso que cubre el suelo de la cueva. En lugar de un golpe certero, el arma se desliza inofensivamente por el costado de la criatura, rozando la piel sin llegar a penetrar la carne.
> La bestia, aprovechando el desequilibrio y la vulnerabilidad de tu posición, deja de retroceder. Con un gruñido gutural, recupera la compostura y lanza un zarpazo rápido hacia tu pecho mientras aún intentas recuperar la estabilidad.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1997 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 63 — 62/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1917 ms

> "¡Maldito barro!"
> Intento echarme hacia atrás rápidamente para evitar el zarpazo mientras busco apoyo en el suelo.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 10+2=12

### [4] DM

  3685 ms

> El intento de retroceso es insuficiente; el pie vuelve a traicionarte en el limo y el cuerpo no responde con la velocidad necesaria. El zarpazo de la bestia impacta con un sonido sordo y húmedo, desgarrando la ropa y hundiendo las garras en tu pecho.
> La criatura exhala un vapor fétido sobre tu rostro, aprovechando que el golpe te ha dejado parcialmente abatido contra el suelo resbaladizo. Sus ojos brillan con una intensidad depredadora mientras se prepara para descargar otro ataque.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  3303 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta Isolde · character.conditions = abatido

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3946: Isolde.conditions = abatido

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 64 — 63/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1607 ms

> "¡Maldita sea!"
> Intento rodar sobre el limo para salir de debajo de la bestia y ponerme en pie rápidamente.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 15+2=17

### [4] DM

  3439 ms

> Aprovechando la inercia del impacto y la viscosidad del terreno, impulsas tu cuerpo en un giro fluido y desesperado. El limo, que hace un momento era una trampa, ahora actúa como lubricante; deslizas el torso hacia un lado con un movimiento rápido, escapando justo a tiempo de que la bestia descargue su peso sobre ti.
> Te impulsas hacia arriba con un esfuerzo brusco, recuperando la verticalidad mientras el barro gotea de tu ropa desgarrada. La criatura lanza un rugido sordo, confundida por tu repentino desplazamiento, y gira la cabeza con brusquedad para volver a fijar sus ojos brillantes en tu posición.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1317 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 65 — 64/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  4182 ms

> "No me atraparás tan fácil, bicho."
> Aprovecho que la criatura está confundida para retroceder rápidamente hacia el terreno más firme, buscando una ventaja táctica.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 11+2=13

### [4] DM

  6642 ms

> Tus botas resbalan en el fango espeso mientras intentas ganar distancia, luchando contra la succión del terreno que parece querer retenerte. Consigues retroceder unos pasos, aunque el movimiento es torpe y desigual debido a la inestabilidad del suelo, dejándote en una posición menos vulnerable que el centro del lodazal, pero aún lejos de una superficie totalmente segura.
> La bestia recupera la compostura rápidamente. Sus garras arañan el limo con un sonido húmedo y visceral mientras se reorienta hacia ti. Lanza un bufido que expulsa vapor por sus fosas nasales, fijando su mirada en tu figura ahora más distante, y comienza a avanzar con una lentitud pesada y deliberada, cerrando el espacio que acabas de ganar.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1613 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 66 — 65/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2939 ms

> "No te voy a dar el gusto de atraparte."
> Busco rápidamente algún punto de apoyo sólido o una raíz que me permita impulsarme fuera del fango.
> {Supervivencia}

### [3] DADOS (deterministas, del sistema)

  Supervivencia: 1+4=5  PIFIA

### [4] DM

  9413 ms

> En el frenesí por encontrar un apoyo, tus dedos se clavan con desesperación en lo que parece ser una raíz gruesa y firme bajo la capa de limo. Sin embargo, al aplicar todo tu peso para impulsarte, la madera podrida se deshace instantáneamente en un amasijo de fibras blandas y negras. El forcejeo brusco y el fallo del apoyo te desequilibran violentamente, provocando que pierdas el centro de gravedad y caigas de espaldas con un sonido sordo y húmedo.
> El impacto te hunde más profundamente en el lodazal que el propio peso de tu cuerpo habría logrado. El fango espeso y frío sube rápidamente por tu torso, atrapando tus extremidades en un abrazo viscoso que convierte cualquier intento de movimiento en una lucha agónica contra la succión. La bestia, al verte caer, detiene su marcha un instante y emite un gruñido bajo, vibrante, mientras acelera el paso hacia tu posición ahora indefensa.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1885 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 67 — 66/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  1867 ms

> "¡Maldita sea!"
> Intento zafarme del lodo con movimientos bruscos para liberar los brazos y alcanzar mi arma.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 2+1=3

### [4] DM

  7626 ms

> Tus movimientos bruscos solo logran que el fango actúe como un pistón hidráulico, succionando tus extremidades con una fuerza implacable. Cada sacudida desesperada te hunde unos centímetros más, el limo frío trepando ahora hasta el pecho y apretando tus costillas, dificultando la respiración mientras el arma permanece fuera de tu alcance, atrapada en el abrazo viscoso del lodazal.
> El gruñido de la bestia se transforma en un bufido excitado al notar tu total incapacidad de reacción. La criatura llega a tu borde, clavando sus garras en el terreno firme justo al lado de tu posición, y proyecta una sombra densa sobre ti mientras abre las fauces, dejando escapar un hilo de saliva espesa que cae sobre el barro.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  3991 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta Isolde · character.conditions = atrapada en el lodo

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3957: Isolde.conditions = atrapada en el lodo

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 68 — 67/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  4615 ms

> "¡Atrévete, maldito bicho!"
> Intento buscar desesperadamente algún apoyo sólido o una raíz en el fango para impulsarme y alejarme de sus fauces.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 5+1=6

### [4] DM

  7627 ms

> Tus dedos arañan el limo con desesperación, pero solo encuentras una masa informe y resbaladiza que se deshace entre tus uñas. No hay raíces, ni piedras, ni nada que el fango no haya devorado ya; cada intento de impulsarte solo sirve para compactar el barro alrededor de tu torso, anclándote con más fuerza en esa tumba viscosa.
> La bestia aprovecha tu agotamiento y el vacío de tus manos. Con un movimiento rápido y seco, cierra la distancia, lanzando su peso hacia adelante mientras sus fauces se cierran con un chasquido húmedo sobre tu hombro.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  9536 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta Isolde · character.conditions = herida en el hombro

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3960: Isolde.conditions = herida en el hombro

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 69 — 68/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  2765 ms

> "¡Suéltame, maldita cosa!"
> Intento girar el cuerpo violentamente para zafarme de su agarre y clavarle mi daga en el costado.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 10+2=12

### [4] DM

  8429 ms

> El esfuerzo es brutal, pero el barro actúa como un ancla viscosa que absorbe toda tu inercia. Al intentar girar, el lodo se aferra a tu espalda y piernas, frenando el movimiento justo cuando el cuerpo de la bestia se desplaza contigo, manteniendo la presión de sus mandíbulas sobre tu hombro.
> La daga describe un arco torpe y lento, quedando atrapada en el denso fango antes de alcanzar el costado de la criatura. La bestia emite un gruñido sordo, vibrando contra tu piel, y sacude la cabeza con fuerza para intentar arrancarte un trozo de carne.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1355 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 70 — 69/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  4939 ms

> "¡Suéltame, maldita sea!"
> Intento clavar mis dedos y uñas en los ojos o la nariz de la bestia para obligarla a soltarme.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 6+1=7

### [4] DM

  8173 ms

> Tus dedos se hunden en el barro y la piel rugosa de la criatura, pero el movimiento es torpe y carece de fuerza. En lugar de alcanzar los ojos o la sensible zona de la nariz, tus uñas resbalan inútilmente sobre el hocico endurecido y cubierto de mucosidad de la bestia, sin lograr provocarle el menor malestar.
> Aprovechando tu fallo y la falta de presión, la criatura sacude la cabeza con un movimiento violento y seco. Sientes un tirón brutal en el hombro que te desplaza unos centímetros más hacia el fondo del fango, mientras sus mandíbulas se cierran con renovado vigor sobre tu carne.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1250 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 71 — 70/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3318 ms

> "¡Suéltame, asquerosa!"
> Intento clavar mis talones en el fango para impulsarme y zafarme de sus mandíbulas con un movimiento brusco.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 17+1=18

### [4] DM

  11273 ms

> Tus talones encuentran un punto de apoyo sólido bajo la capa de lodo, permitiéndote coordinar un empujón explosivo. Con un gruñido de esfuerzo, proyectas todo tu peso hacia atrás en un movimiento seco y violento que desequilibra a la bestia. La fuerza del tirón es tan súbita que las mandíbulas de la criatura se abren por la inercia, soltando tu carne con un sonido húmedo y visceral.
> Sientes el aire frío golpear la herida abierta mientras te separas del hocico mucoso. La criatura queda momentáneamente desorientada, sacudiendo la cabeza y emitiendo un siseo gutural, mientras el fango que te rodeaba ahora se desliza pesadamente sobre tu ropa y piel.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1601 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 72 — 71/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3602 ms

> "¡Maldita sea!"
> Me pongo en pie rápidamente, alejándome de la criatura mientras me presiono la herida con la mano para contener la sangre.
> {Acrobacias}

### [3] DADOS (deterministas, del sistema)

  Acrobacias: 2+2=4

### [4] DM

  9138 ms

> El impulso para levantarte es torpe y apresurado. Al intentar impulsarte hacia arriba mientras presionas la herida, tus pies resbalan en el lodo traicionero, que actúa como un lubricante viscoso bajo tus botas. Pierdes el equilibrio casi al instante, tus brazos gesticulan en el aire buscando un apoyo que no existe y terminas cayendo de espaldas con un impacto sordo, hundiendo la parte posterior de tu cuerpo nuevamente en el fango frío.
> La criatura, recuperada de la sorpresa, deja escapar un ronroneo vibrante que hace temblar el suelo bajo ti. Sus ojos amarillentos se fijan en tu posición vulnerable y, con un movimiento fluido y depredador, comienza a cerrar la distancia, deslizándose sobre el barro con una velocidad inquietante.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  1154 ms · 0 eventos · 0 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  nada que escribir (correcto si el turno no cambió el mundo)

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 73 — 72/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3702 ms

> "Maldita sea..."
> Siseo entre dientes mientras intento impulsarme hacia atrás desesperadamente para ganar distancia antes de que llegue a mí.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 1+1=2  PIFIA

### [4] DM

  16686 ms

> El pánico nubla tus movimientos y el barro parece cobrar vida propia para atraparte. Al intentar impulsarte hacia atrás, tus botas no encuentran tracción, sino que se hunden profundamente en el lodo, que succiona tus pies con una fuerza asfixiante. En el esfuerzo desesperado por retroceder, pierdes el control de tu cuerpo y terminas girando sobre ti mismo en un torpe giro, quedando completamente boca arriba y con las piernas agitándose inútilmente en el fango viscoso.
> La criatura se detiene un instante, casi como si disfrutara de tu torpeza. Su ronroneo se transforma en un siseo agudo y hambriento mientras se encorva, tensando los músculos de sus patas traseras. Con un salto explosivo, se lanza hacia adelante, aprovechando tu total incapacidad de movimiento para caer con todo su peso sobre tu pecho.

### [5] VERIFICACIÓN DE LA NARRACIÓN

  sin problemas detectados

### [6] EXTRACTOR

  19486 ms · 0 eventos · 1 deltas · 0 creaciones

### [7] VALIDACIÓN DE LO EXTRAÍDO

  ✓ delta Isolde · character.conditions = derribado

### [8] ESCRITURA

  → turn_validation registrado (sin problemas tier 1-2)
  → delta 3967: Isolde.conditions = derribado

### [9] ESTADO DESPUÉS

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos, 0 secretos revelados
  sin cambios de estado

## Turno 74 — 73/1399 de esta corrida (objetivo final de la campaña: 1400)


### [1] ESTADO Y CONTEXTO (desde Postgres)

  Yara Sorem: alive, aprecio 30.0 (loyal), 1 hechos conocidos
  18 entidades · contexto de 640 caracteres

### [2] JUGADOR — Isolde

  3694 ms

> "¡Quítate de encima, maldita bestia!"
> Intento agarrar la criatura por el cuello o las patas delanteras para apartarla de mi pecho y evitar que me muerda.
> {Atletismo}

### [3] DADOS (deterministas, del sistema)

  Atletismo: 8+1=9

### [4] DM

  66488 ms

> Tus dedos se hunden en el pelaje húmedo y áspero de la bestia, pero el impulso es insuficiente. La criatura es una masa de músculo y hambre que no cede ante tu forcejeo; el peso del animal te aplasta contra el barro frío, expulsando el aire de tus pulmones en un gemido sordo. Tus manos resbalan por su cuello viscoso, incapaces de encontrar un agarre firme que te permita desplazarla.