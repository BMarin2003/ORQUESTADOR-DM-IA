# A2: Jericho recall y relojes reconocidos

SHA-256 de las expectativas (fijadas antes de correr): `783c4e43a46cdad513f599f212548912915754a0e141c89c9440a89cdcf71856`

Semilla: 20260921. n objetivo por perturbación: Jericho 40, relojes 16.

| perturbación | instrumento | n | confirmatorias | tasa |
|---|---|---|---|---|
| JQ1 | jericho_recall | 40 | 40 | 100.0% |
| JQ2 | jericho_recall | 40 | 40 | 100.0% |
| RJ1 | relojes_reconocidos | 7 | 7 | 100.0% |
| RJ2 | relojes_reconocidos | 16 | 16 | 100.0% |

Confirmatoria = el instrumento cambió en la dirección pre-especificada (JQ1/RJ1: reconocido False->True; JQ2/RJ2: reconocido True->False). «sin_cambio» = no confirmatoria: revisar la fila en el CSV (oración insertada/oraciones quitadas) antes de sacar conclusiones -- puede ser un fallo real del instrumento (la hipótesis que este A2 existe para probar) o un problema de la propia oración/plantilla.

Límite: los relojes de facción solo existen en Par18-27 (Par01-17 sin avance de reloj); RJ1/RJ2 se muestrean solo de esas 10 parejas.
