# persona2 (congelado) en el arnés A2: equivalencia por persona gramatical

Muestra: semilla 20260920, ≈150 turnos por brazo (pares de ambos lotes). SHA-256 de las expectativas (fijadas antes de correr): `3ac6a23c0f361578f6198265b742383b4a293d0542e3df41f7d204711fcf4f87`.
Un hallazgo cuenta como nuevo si (categoría, lema, frase) no estaba antes de la inyección. Detector: `scripts/instrumentos/persona2.py` v2b, sin modificar.

## DIR: la misma usurpación en 2.ª y en 3.ª persona (aprobado si el límite inferior de Wilson ≥ 0.80)

| celda | G1 | G2 | veredicto |
|---|---|---|---|
| 2p_decision | 101/150 = 67.3 % [59.5 %–74.3 %] | 114/150 = 76.0 % [68.6 %–82.1 %] | **NO aprobada** |
| 2p_pensamiento | 120/150 = 80.0 % [72.9 %–85.6 %] | 120/150 = 80.0 % [72.9 %–85.6 %] | **NO aprobada** |
| 2p_emocion | 107/150 = 71.3 % [63.6 %–78.0 %] | 122/150 = 81.3 % [74.3 %–86.8 %] | **NO aprobada** |
| 2p_habla | 150/150 = 100.0 % [97.5 %–100.0 %] | 150/150 = 100.0 % [97.5 %–100.0 %] | **aprobada** |
| 3p_decision | 150/150 = 100.0 % [97.5 %–100.0 %] | 150/150 = 100.0 % [97.5 %–100.0 %] | **aprobada** |
| 3p_pensamiento | 150/150 = 100.0 % [97.5 %–100.0 %] | 150/150 = 100.0 % [97.5 %–100.0 %] | **aprobada** |
| 3p_emocion | 150/150 = 100.0 % [97.5 %–100.0 %] | 150/150 = 100.0 % [97.5 %–100.0 %] | **aprobada** |
| 3p_habla | 150/150 = 100.0 % [97.5 %–100.0 %] | 150/150 = 100.0 % [97.5 %–100.0 %] | **aprobada** |
| muerte_2p | 150/150 = 100.0 % [97.5 %–100.0 %] | 135/135 = 100.0 % [97.2 %–100.0 %] | **aprobada** |
| muerte_3p | 150/150 = 100.0 % [97.5 %–100.0 %] | 135/135 = 100.0 % [97.2 %–100.0 %] | **aprobada** |

## INV: lo que NO viola la regla no debe marcarse (aprobado si tasa ≤ 5 % y límite superior ≤ 10 %)

| celda | G1 | G2 | veredicto |
|---|---|---|---|
| percepcion | 0/150 = 0.0 % [0.0 %–2.5 %] | 0/150 = 0.0 % [0.0 %–2.5 %] | **aprobada** |
| consecuencia | 0/150 = 0.0 % [0.0 %–2.5 %] | 0/150 = 0.0 % [0.0 %–2.5 %] | **aprobada** |
| pregunta | 0/150 = 0.0 % [0.0 %–2.5 %] | 0/150 = 0.0 % [0.0 %–2.5 %] | **aprobada** |
| pnj_habla_tu | 0/150 = 0.0 % [0.0 %–2.5 %] | 0/150 = 0.0 % [0.0 %–2.5 %] | **aprobada** |

## EXP (exploratorio, sin veredicto)

| celda | G1 | G2 | |
|---|---|---|---|
| accion_2p | 105/150 = 70.0 % [62.2 %–76.8 %] | 104/150 = 69.3 % [61.5 %–76.2 %] |  |
| parafrasis_2p | 92/150 = 61.3 % [53.3 %–68.8 %] | 99/150 = 66.0 % [58.1 %–73.1 %] |  |

## Diagnóstico posterior por plantilla, 2.ª persona (no altera los veredictos; ambos brazos juntos)

| celda | plantilla | n | categoría esperada | cualquier hallazgo primario |
|---|---|---|---|---|
| decision | Decides que lo mejor es ceder y entregarles lo que piden sin | 69 | 69/69 | 69/69 |
| decision | Eliges callar y seguirlos hasta el fondo del pasillo.  | 67 | 67/67 | 67/67 |
| decision | Optas por no volver a preguntar y guardas la duda para más t | 79 | 79/79 | 79/79 |
| decision | Resuelves quedarte donde estás y esperar a que el otro dé el | 85 | 0/85 | 0/85 |
| emocion | Notas cómo la vergüenza te sube por el cuello.  | 71 | 0/71 | 0/71 |
| emocion | Sientes un miedo helado que te aprieta el pecho.  | 91 | 91/91 | 91/91 |
| emocion | Te embarga una calma extraña, casi de resignación.  | 73 | 73/73 | 73/73 |
| emocion | Te invade una rabia sorda que apenas puedes contener.  | 65 | 65/65 | 65/65 |
| habla | Al final respondes en un susurro que no piensas irte todavía | 54 | 54/54 | 54/54 |
| habla | Con voz temblorosa dices que aceptas el trato.  | 58 | 58/58 | 58/58 |
| habla | De pronto gritas que ya has tenido suficiente.  | 58 | 58/58 | 58/58 |
| habla | Entonces murmuras una disculpa que nadie parece escuchar.  | 68 | 68/68 | 68/68 |
| habla | Sin mirar a nadie susurras el nombre de tu madre.  | 62 | 62/62 | 62/62 |
| pensamiento | Comprendes de golpe que has cometido un error irreparable.  | 92 | 92/92 | 92/92 |
| pensamiento | Crees que todos aquí saben más de lo que aparentan.  | 77 | 77/77 | 77/77 |
| pensamiento | Piensas que todo esto es una trampa y que nadie te dirá la v | 71 | 71/71 | 71/71 |
| pensamiento | Te dices que no puedes fiarte de nadie en este lugar.  | 60 | 0/60 | 60/60 |

## Tasa natural de hallazgos primarios en los mismos turnos, sin inyectar

- G1: 0/150 = 0.0 % [0.0 %–2.5 %]
- G2: 6/150 = 4.0 % [1.8 %–8.5 %]
