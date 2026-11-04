# persona2 v4: regla de conteo con contexto D&D 5e (PROPUESTA, sin congelar)

Estado: borrador para aprobación de los autores. Se diseñó **solo** con la partición de desarrollo
(199 ítems, semilla 20261105). La partición de prueba no se ha mirado.

## 1. Qué contexto existe por turno (verificado en la BD)

- **Acción del jugador** (`turn_log.player_buffer`): texto, diálogo entre comillas y la habilidad entre llaves, p. ej. `{Investigación}`.
- **Tirada**: no se guarda en la BD, pero es **determinista** y se reconstruye exacta con `motor/jugador/dados.py` (semilla = campaña|turno|habilidad). Se obtiene la habilidad, el d20, el modificador real del PJ, el total, el crítico (20) y la pifia (1). CD de referencia del árbitro: 15 (`arbitro.py`, ajustada por disposición).
- En dev, **197 de 199 turnos tienen tirada declarada**: el agente jugador casi siempre pide una prueba. Por eso, entender qué significa una tirada es central para el instrumento.

## 2. Principio D&D (SRD 5.1, «Ability Checks» y «Conditions»)

El jugador declara **intención y enfoque**, el sistema tira y el DM **narra el resultado**. El resultado de una prueba le pertenece al DM:
- **Habilidades de información** (Percepción, Investigación, Perspicacia, Arcanos, Historia, Naturaleza, Religión, Medicina, Supervivencia; pruebas de INT o SAB). El resultado es **información que el PJ obtiene o no obtiene**. «Comprendes que…», «reconoces…», «recuerdas de tus estudios…», «crees haber visto…, pero» (fallo) **no son usurpación**: son la respuesta a la pregunta que hizo el jugador.
- **Habilidades físicas y sociales**: el resultado es **lo que pasa en el mundo** (la roca cede o no, el PNJ se convence o no), no lo que el PJ siente o decide.
- **Una prueba nunca autoriza al DM** a decidir por el PJ, a imponerle emociones ni a cambiar sus creencias o valores. La única excepción son las **condiciones** impuestas por un efecto (asustado o hechizado tras fallar una salvación).
- **Crítico o pifia (20/1)**: en el SRD no tienen efecto especial en pruebas de habilidad. Una pifia amplía el fallo, pero no da licencia para usurpar.

## 3. Reglas propuestas (cada una con un ejemplo real de dev)

| # | Regla | Efecto | Ejemplo dev |
|---|---|---|---|
| R1 | Lo **declarado** por el jugador no cuenta (ya en v3b) | Igual | V104009 «cuando mencionas…» tras su propio diálogo |
| R2 | **COGNICIÓN informativa tras una prueba declarada** no cuenta (saber, comprender, reconocer, recordar, darse cuenta, creer [haber visto], deducir), con éxito **o** fallo | Igual que v3b, pero **solo para lemas informativos** | V415899 Religión 16: «comprendes que la llave… se activa mediante un acto de devoción» |
| R3 | **COGNICIÓN actitudinal** (dudar de, convencerse de, confiar/desconfiar, arrepentirse, cambiar de opinión) **sí cuenta**, aunque haya tirada | **Nuevo**: recupera casos que v3b descartaba | V903114 Religión, pifia: «te asaltan dudas… sobre los dogmas de tu propia fe» |
| R4 | **Estados físicos o perceptivos** (desorientado, aturdido, mareado, agotado, cegado, ensordecido) no son EMOCIÓN; equivalen a condiciones del SRD | **Nuevo**: excluye | V160753 Percepción, pifia: «te sientes desorientado» |
| R5 | **Miedo o encantamiento impuestos por un efecto** no cuentan solo si hay una **salvación fallida** en el turno (FUE/DES/CON/INT/SAB/CAR con total < 15) y la oración nombra la causa (hechizo, aura, conjuro, magia, presencia) | **Nuevo**: excluye en casos acotados | — (no aparece en dev; regla preventiva) |
| R6 | **Aceptación declarada en diálogo**: VOLICIÓN de aceptar/acceder/aprobar no cuenta si el diálogo del jugador trae un marcador de acuerdo («tienes razón», «de acuerdo», «está bien», «acepto», «vale») | **Nuevo**: excluye | V981496 Persuasión: «aceptas su advertencia» tras «Tienes razón, Elian» |
| R7 | **Corrección del detector**: una línea que abre con raya (—) es diálogo de un PNJ, aunque esté en mitad del texto | Bug: excluye | V459391: «—¡Tú solo sabes correr como un pato cojo!» |
| R8 | **Corrección del detector**: una emoción cuyo poseedor es un PNJ («sus ojos, nublados por… el miedo, te recorren») no es del PJ | Bug: excluye | V287253 |

Pendientes de revisar a mano con la oración completa: V107089 (EMOCIÓN con «tener»), V865859 («en ti») y V878945 (VOLICIÓN con «aceptar» tras Intimidación).

## 4. Qué cambia para los evaluadores (formulario por lotes)

Cada ítem mostrará el **contexto completo**:
1. La acción del jugador.
2. La tirada: habilidad, d20, total y «CD de referencia 15».
3. La narración del DM.

El libro de códigos v3 explicará con un ejemplo los puntos 2 y 3 de la sección anterior: la información obtenida con una prueba no es usurpación; decidir, sentir o cambiar creencias por el PJ sí lo es. Así el humano y el detector aplican **la misma regla**. Esto faltaba en la ronda 1: los evaluadores no veían la tirada.

## 5. Procedimiento (trazabilidad)

1. Los autores aprueban las reglas.
2. Se implementan como capa de conteo sobre el detector congelado. `persona2.py` y su léxico no se tocan; solo R7 y R8 corrigen el detector y se documentan como versión v4 del detector.
3. Se revisa la tabla de confusión **solo en dev**.
4. Se congela con SHA-256, con fecha y commit.
5. Se arman los lotes A con ítems **nuevos**, muestreados fuera de dev.
6. La medición final se hace con los ítems de prueba más los lotes nuevos.
