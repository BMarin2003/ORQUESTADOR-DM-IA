# Diagnóstico posterior: Jericho recall y relojes (no pre-registrado)

Complementa `sensibilidad_jericho_relojes.md` (A2 mecánico, 100 % por construcción). Texto normalizado, semilla 20260921, K = 20 réplicas al azar por evento.

## 1. Jericho recall: recall real frente al recall que da el mismo léxico en un turno cualquiera

| familia | brazo | eventos evaluables | recall real | recall por azar | diferencia |
|---|---|---|---|---|---|
| npc.affinity | G1 | 100 | 21.0 % | 18.9 % | +2.0 pp |
| npc.affinity | G2 | 334 | 21.0 % | 16.5 % | +4.5 pp |
| npc.status | G1 | 56 | 30.4 % | 9.2 % | +21.2 pp |
| npc.status | G2 | 298 | 31.9 % | 7.3 % | +24.6 pp |
| quest.status | G1 | 2 | 100.0 % | 32.5 % | +67.5 pp |
| **todas** | ambos | 790 | 25.9 % | 12.9 % | +13.1 pp |

## 2. Relojes reconocidos (Par18-27)

- Reconocidos de verdad: 53 de 60 (88.3 %). Por azar (mismo vocabulario, ventana de 2 turnos al azar): 89.8 %.
- Con solo palabras de contenido (sin las palabras funcionales del vocabulario): reconocidos 44 de 60 (73.3 %); por azar con ese vocabulario: 61.1 %.
- Relojes reconocidos ÚNICAMENTE por palabras funcionales: 9 de 53 reconocidos (17.0 %).
- Comprobación: la función de coincidencia de este script reproduce al instrumento real en 60 de 60 relojes.

Claves que más reconocen relojes (una vez por reloj reconocido):

| clave | relojes | palabra funcional |
|---|---|---|
| para | 14 | sí |
| sobre | 14 | sí |
| antes | 8 | sí |
| cada | 7 | sí |
| silencio | 6 | no |
| paso | 6 | no |
| noche | 6 | no |
| karhad | 5 | no |
| dragón | 5 | no |
| agua | 5 | no |
| todo | 4 | sí |
| sigue | 4 | sí |

**Lectura.** Si el recall real no supera al del azar por un margen claro, el reconocimiento léxico no distingue un turno con evento de uno cualquiera y no sirve como medida de coherencia longitudinal; el A2 mecánico solo demuestra que el instrumento lee la ventana y responde al léxico, no que ese léxico signifique que el evento se narró.
