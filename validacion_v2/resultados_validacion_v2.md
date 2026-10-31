# Validación humana v2 — resultados consolidados

Evaluadores: E1, E2, E3, E4, E5. Referencia por ítem = mayoría de los evaluadores retenidos en cada pregunta. Los ítems de control no entran en el análisis.

## 1. Controles y retención

| Evaluador | A | B | C | D |
|---|---|---|---|---|
| E1 | 5/10 (excluido) | 10/10 | 5/7 (excluido) | 5/5 |
| E2 | 10/10 | 10/10 | 6/7 | 5/5 |
| E3 | 9/10 | 10/10 | 7/7 | 5/5 |
| E4 | 7/10 (excluido) | 9/10 | 6/7 | 5/5 |
| E5 | 8/10 | 10/10 | 5/7 (excluido) | 5/5 |

| Pregunta | Retenidos |
|---|---|
| A | E2, E3, E5 (3) |
| B | E1, E2, E3, E4, E5 (5) |
| C | E2, E3, E4 (3) |
| D | E1, E2, E3, E4, E5 (5) |

## 2. Detector frente a la referencia humana (A, B, C)

| Instrumento | Análisis | n | VP | FP | FN | VN | % acuerdo | κ [IC 95 %] | Precisión [IC Wilson] | Exhaustividad ponderada [IC 95 %] |
|---|---|---|---|---|---|---|---|---|---|---|
| A · persona2 v3b | principal | 400 | 6 | 6 | 81 | 307 | 78.2 | 0.07 [-0.00, 0.16] | 50.0 [25.4, 74.6] | 1.0 [0.3, 1.9] |
| A · persona2 v3b | sin E5 (límite en controles) | 378 | 4 | 6 | 66 | 302 | 81.0 | 0.06 [-0.02, 0.14] | 40.0 [16.8, 68.7] | 0.8 [0.2, 1.8] |
| A · persona2 v3b | sensibilidad: 5 evaluadores | 400 | 5 | 7 | 78 | 310 | 78.8 | 0.06 [-0.02, 0.14] | 41.7 [19.3, 68.0] | 0.8 [0.2, 1.8] |
| B · PNJ inactivo refinado | principal | 200 | 96 | 4 | 49 | 51 | 73.5 | 0.47 [0.41, 0.53] | 96.0 [90.2, 98.4] | 6.3 [4.4, 8.8] |
| B · PNJ inactivo refinado | sensibilidad: 5 evaluadores | 200 | 96 | 4 | 49 | 51 | 73.5 | 0.47 [0.41, 0.53] | 96.0 [90.2, 98.4] | 6.3 [4.4, 8.8] |
| C · Jericho-QA | principal | 200 | 89 | 11 | 62 | 38 | 63.5 | 0.27 [0.16, 0.39] | 89.0 [81.4, 93.7] | 34.0 [30.5, 38.2] |
| C · Jericho-QA | solo estado (npc.status) | 97 | 51 | 7 | 25 | 14 | 67.0 | 0.26 [0.07, 0.44] | 87.9 [77.1, 94.0] | 40.5 [35.1, 47.7] |
| C · Jericho-QA | solo afinidad (npc.affinity) | 103 | 38 | 4 | 37 | 24 | 60.2 | 0.27 [0.13, 0.41] | 90.5 [77.9, 96.2] | 28.3 [24.2, 33.7] |
| C · Jericho-QA | sensibilidad: 5 evaluadores | 200 | 90 | 10 | 64 | 36 | 63.0 | 0.26 [0.15, 0.37] | 90.0 [82.6, 94.5] | 33.5 [30.3, 37.6] |

Exhaustividad ponderada: cada ítem pesa N_estrato / n_estrato (poblaciones en `poblaciones.json`); IC por bootstrap estratificado (2 000 réplicas). κ con IC por el mismo bootstrap.

Auditoría de afinidad (autores, 30 cambios): la narración refleja el cambio en 12/30 (40.0 %, IC Wilson 24.6–57.7 %).

persona2 v2b (versión con que se estratificó) frente a la misma referencia: {'11': 52, '10': 48, '00': 265, '01': 35} (clave «detector,referencia»).

## 3. Pregunta D · respuesta a la acción (z continuo)

| Análisis | n al azar | Ref. «No» | AUC [IC 95 %] | r biserial | Cola baja: «No» / n [IC Wilson] |
|---|---|---|---|---|---|
| principal | 100 | 15 | 0.84 [0.74, 0.92] | 0.40 | 27/50 = 54.0 % [40.4, 67.0] |
| sensibilidad: 5 evaluadores | 100 | 15 | 0.84 [0.74, 0.92] | 0.40 | 27/50 = 54.0 % [40.4, 67.0] |

## 4. Acuerdo entre evaluadores

| Pregunta | Análisis | Evaluadores | κ de Fleiss | α de Krippendorff | % ítems unánimes |
|---|---|---|---|---|---|
| A | principal | 3 | 0.85 | 0.85 | 92.5 |
| A | 5 evaluadores | 5 | 0.60 | 0.60 | 75.5 |
| B | principal | 5 | 0.55 | 0.55 | 57.5 |
| B | 5 evaluadores | 5 | 0.55 | 0.55 | 57.5 |
| C | principal | 3 | 0.55 | 0.55 | 74.0 |
| C | 5 evaluadores | 5 | 0.41 | 0.41 | 61.0 |
| D | principal | 5 | 0.31 | 0.31 | 43.3 |
| D | 5 evaluadores | 5 | 0.31 | 0.31 | 43.3 |
