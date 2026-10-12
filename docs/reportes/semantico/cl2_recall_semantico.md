# CL-2 recall semántico (EXPLORATORIO)

Instrumento nuevo de medición sobre el corpus ya generado: no cambia la generación ni regenera campañas. Mismos eventos que Jericho-QA; reconoce paráfrasis por similitud (bge-m3, pgvector, búsqueda exacta) y decide contra el nulo exacto de cada campaña (percentil 95 de todas sus ventanas a más de 5 turnos). Tasa de reconocimiento esperada por azar: ~5 %. Hasta que pase su prueba A2 (sensibilidad_semantico.py) no decide hipótesis.

Eventos evaluados: 790 en 54 campañas.

## Recall por familia (todas las campañas)

| Familia | n | recall semántico | recall Jericho (mismos eventos) |
|---|---|---|---|
| npc.status | 354 | 0.359 | 0.316 |
| npc.affinity | 434 | 0.293 | 0.210 |
| quest.status | 2 | 0.000 | 1.000 |

## Acuerdo con Jericho-QA (mismos eventos)

| Ambos | Solo semántico | Solo Jericho | Ninguno |
|---|---|---|---|
| 76 | 178 | 129 | 407 |

«Solo semántico» son eventos narrados sin el lexema que Jericho busca (paráfrasis) o falsos positivos; la prueba A2 y una revisión humana de una muestra deben decir cuál de los dos predomina.

## Comparación pareada G1 - G2 (parejas con al menos 3 eventos en ambos brazos)

| Medida | n pares | Mdn G1 | Mdn G2 | HL [IC 95 %] | r | p bilateral (Wilcoxon exacto) |
|---|---|---|---|---|---|---|
| recall_sem | 22 | 0.028 | 0.389 | -0.297 [-0.382, -0.213] | -0.94 | 0.0000 |
| z_mediana | 22 | 0.642 | 1.400 | -0.902 [-1.190, -0.634] | -0.95 | 0.0000 |
| recall_jericho | 22 | 0.236 | 0.218 | +0.008 [-0.104, +0.121] | +0.05 | 0.8486 |

Uso: EXPLORATORIO. Sin corrección de Holm y sin decisión sobre H1e (regla del apartado 5.8.5 de la tesis).

Límites declarados: (1) depende de un modelo de embeddings (versión fijada en el manifiesto); (2) la consulta incluye el nombre de la entidad, así que parte de la similitud puede venir del nombre y no del cambio de estado (la A2 lo controla con SC2); (3) solo recall, igual que Jericho: no mide afirmaciones de estado no respaldadas por la base.
