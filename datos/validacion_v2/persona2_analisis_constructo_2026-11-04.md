# persona2: análisis del constructo «usurpación de la agencia» con contexto D&D (04/11/2026)

Base empírica: volcado de **todos** los hallazgos primarios del detector congelado en las 54 campañas. Se excluyen los
201 turnos de la partición de prueba para no contaminarla y los hallazgos declarados por el jugador (R1).
Quedan 1 229 hallazgos. Archivos: `_trabajo/_volcado_v4.jsonl` y `_trabajo/_analisis_volcado.py`.

## 1. El problema de fondo: ¿qué decide si algo es usurpación?

Hay dos criterios posibles:
- **Criterio de imposición:** el DM impone algo al PJ (una emoción, un pensamiento, un efecto). Es el criterio implícito de persona2 v2.
- **Criterio de autoría:** el DM toma una decisión que le corresponde al jugador.

El ejemplo de la estatua en la mansión del vampiro muestra que el primer criterio falla. El DM impone herida y mareos al fallar una prueba, con efectos que duran, y aun así es su atribución legítima: está narrando el resultado. **Imponer consecuencias no es usurpar.** Usurpar es ejercer por el jugador la parte del juego que le pertenece.

El ciclo de juego de D&D 5e (PHB 2014, «How to Play», p. 6; ⚠ verificar página) reparte la autoría:
1. El DM describe el entorno.
2. **Los jugadores describen lo que quieren hacer.**
3. El DM narra los resultados de las acciones.

La usurpación es el DM ocupando el paso 2. Todo lo que es paso 3 (resultado, información, consecuencias, estados) es suyo, aunque se narre desde dentro del PJ («comprendes», «te frustras», «te sientes expuesto»).

## 2. Lo que muestra el corpus

| Grupo | G1 | G2 | Lectura según el criterio de autoría |
|---|---|---|---|
| COGNICIÓN tras una tirada (R2) | 32 | 775 | Resultado de la prueba (paso 3) |
| COGNICIÓN o EMOCIÓN con d20 = 1 o 20 (RC) | 7 | 256 | Resultado extremo (paso 3) |
| Perspectiva de PNJ, diálogo, sujeto PNJ (R7–R9) | 2 | 22 | Error del detector |
| **Siguen contando en v4** | 17 | 117 | Revisados a mano: ver abajo |
| Hallazgos sin ninguna tirada en el turno | 0 | 2 | — |

**Revisión manual de los que siguen contando.** Se revisaron una muestra aleatoria de 12 y los 18 de VOLICIÓN con lemas de decisión (decidir, elegir, querer, rendirse, atreverse, disponerse, aceptar). Casi todos son falsos positivos de **cinco tipos nuevos**:

| Tipo | Ejemplo real | Por qué no es usurpación |
|---|---|---|
| Esfuerzo o inicio de lo declarado | «te esfuerzas por analizar…» (29 casos), «te obligas a apartar la vista» (15), «te dispones a investigar» | Es la manera de ejecutar lo que el jugador declaró («trato de…», «intento…») |
| Referencia retrospectiva a una decisión declarada | «has decidido ocultar el objeto», «en el momento en que decidiste retirarte», «el rincón que has elegido» | El jugador sí lo decidió; el DM lo recuerda |
| Decisión abierta | «aguarda a ver qué decides hacer», «o aceptas la tarifa… o te marcharás» | Ofrece la decisión; no la toma |
| Sensación física | «un olor… que te irrita las fosas nasales» | Sensorial, no emoción (error de léxico) |
| Creencia o mirada de un PNJ (variantes de R8 y R9) | «convencido de que ya te has rendido», «una mirada… que te recorre con desprecio» | Es el PNJ quien cree o desprecia |

**Hallazgo clave:** con un criterio de autoría, **la usurpación explícita es un evento casi inexistente en ambas arquitecturas**. La diferencia que antes se atribuía a la usurpación (G1 0.00 % frente a G2 0.37 %) es, en gran parte, una **diferencia de estilo narrativo**: G2 narra el resultado de las pruebas **desde la mente del PJ** («comprendes que…», «reconoces…», «crees haber visto…») unas 25 veces más que G1. En narratología esto se llama **focalización interna** (Genette, 1972, *Figures III*; ⚠ verificar edición en español). Es real, medible y distingue a las arquitecturas, **pero no es usurpación**.

## 3. Propuesta de definición positiva (decir cuándo SÍ es usurpación)

Hay usurpación cuando el narrador atribuye al PJ, como algo que el PJ hace o asume por sí mismo y que el jugador **no declaró**, alguna de estas tres cosas:
- **(a) Una decisión nueva**, que no es la ejecución, el esfuerzo ni el recuerdo de lo declarado: «decides retirarte», «aceptas el trato», «te rindes».
- **(b) Palabras nuevas:** «le dices que…», «respondes: —…», cuando el jugador no las dijo.
- **(c) Una postura propia que orienta decisiones futuras:** una creencia o convicción, la fe o los valores, afecto u hostilidad hacia alguien (amor, odio, gratitud, desprecio, culpa, lealtad). Excepción: que sea el efecto de un crítico o una pifia (regla de mesa acordada).

**No es usurpación:**
- La información que entrega una prueba, con éxito o fallo.
- Las emociones del propio resultado: frustración, alivio, sorpresa, sentirse expuesto. En la tipología de Ortony, Clore & Collins (1988) son emociones *basadas en eventos*.
- Estados físicos, heridas y condiciones, aunque duren.
- El esfuerzo o la forma de ejecutar lo declarado.
- Lo que creen o sienten los PNJ.

Esta definición resuelve los casos que discutimos:
- V865859 («frustración de haber estado tan cerca»): resultado, **no cuenta**.
- La estatua del vampiro (herida y mareo): consecuencia, **no cuenta**.
- «Decides huir presa del pánico»: el pánico es resultado, pero **decidir huir** es (a), **cuenta**.
- «Te asaltan dudas sobre tu fe» con un d20 normal: (c), **cuenta**. Con pifia: no cuenta, por RC.

Sobre la propuesta de «contar solo cuando no se declara habilidad»: en el corpus el agente declara tirada en el 99 % de los turnos. Con esa regla el instrumento dejaría de medir. Además, la tirada no autoriza al DM a decidir o hablar por el PJ (a y b). La definición positiva conserva la idea central de esa propuesta (con una tirada, la narración es resultado) sin vaciar el instrumento.

## 4. Cómo se defiende algo interpretativo (trazabilidad)

1. **Constructo anclado en tres fuentes:**
   - El ciclo de juego del PHB, que establece quién es autor de qué.
   - FIREBALL (Zhu et al., 2023): los jugadores rechazan que el modelo controle a su PJ.
   - La tipología OCC (Ortony et al., 1988), que separa las emociones de resultado de las actitudes.
2. **La misma regla para el detector y para los humanos:** un árbol de decisión de 3 preguntas en el libro de códigos v3. Los evaluadores ven la acción, el d20, el total y la narración.
3. **Acuerdo por rama:** κ y α separados para (a), (b) y (c). Si el acuerdo en (c) sale bajo, eso es un hallazgo que se reporta, no un fracaso.
4. **Análisis de sensibilidad o multiverso** (Steegen, Tuerlinckx, Gelman & Vanpaemel, 2016, *Perspectives on Psychological Science*, 11(5), 702–712). H1c y H1f se reportan bajo tres definiciones: v2b literal (imposición), v3b y v4 (autoría). Si la conclusión cambia según la definición, eso se declara. El jurado ya no puede decir «eligieron la definición que les convenía»: se muestran todas.
5. **Congelamiento antes de mirar la partición de prueba** (hash y commit).

## 5. Consecuencias para la tesis (decisión de los autores)

- Con v4, H1f probablemente **deja de sostenerse**, o queda sin potencia por la escasez de eventos.
- Se propone separar persona2 en dos indicadores:
  - **QN-2a, usurpación de la agencia (v4, autoría):** confirmatorio o condicionado, según la validación humana.
  - **QN-2b, focalización interna en el PJ:** proporción de turnos en que el resultado se narra desde la mente del PJ (R2 + RC). Es descriptivo o exploratorio y conserva la diferencia G1/G2 como hallazgo de estilo, sin llamarla usurpación.
- Hay que agregar las reglas del punto 2 (v4.1):
  - R10: esfuerzo o inicio de lo declarado.
  - R11: referencia retrospectiva a una decisión declarada.
  - R12: decisión abierta, pregunta o disyuntiva.
  - R13: sensación física.
  - Ampliar R8 (mirada) y R9 («convencido de que»).
  - Para EMOCIÓN: contar solo emociones hacia agentes (actitudes OCC).
