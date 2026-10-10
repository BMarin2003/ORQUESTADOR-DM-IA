# cl2_recall_semantico_v2 (EXPLORATORIO, nulo condicionado por mención)

Mismos eventos que Jericho-QA y la v1. Solo cuentan las oraciones que mencionan a la entidad, en la ventana real y en el nulo. Spec y A2 sellada: docs/spec_cl2_recall_semantico_v2.md y sensibilidad_semantico_v2.md.

Universo (eventos que la v1 evaluaba): 790 · evaluables por la v2: 631 (79.9 %).

## Evaluabilidad por brazo y familia

| Brazo | Familia | Universo | Evaluables v2 |
|---|---|---|---|
| G1 | npc.status | 56 | 46 |
| G1 | npc.affinity | 100 | 99 |
| G1 | quest.status | 2 | 0 |
| G2 | npc.status | 298 | 202 |
| G2 | npc.affinity | 334 | 284 |
| G2 | quest.status | 0 | 0 |

## Recall sobre el MISMO subconjunto (evaluables por la v2)

| Familia | n | v2 [IC Wilson 95 %] | v1 | Jericho |
|---|---|---|---|---|
| npc.status | 248 | 0.109 [0.076, 0.154] | 0.335 | 0.294 |
| npc.affinity | 383 | 0.065 [0.045, 0.095] | 0.274 | 0.206 |
| quest.status | 0 | — | — | — |
| todas | 631 | 0.082 [0.063, 0.106] | 0.298 | 0.241 |

## Qué cambió respecto de la v1 (mismos eventos)

| v1 y v2 | solo v1 | solo v2 | ninguno |
|---|---|---|---|
| 52 | 136 | 0 | 443 |

«Solo v1» son reconocimientos que dependían de nombrar a la entidad: la v2 los descarta.

## Acuerdo v2 con Jericho-QA

| Ambos | Solo v2 | Solo Jericho | Ninguno |
|---|---|---|---|
| 14 | 38 | 138 | 441 |

## Por brazo (descriptivo; los eventos evaluables por campaña son pocos)

| Brazo | n evaluables | recall v2 [IC Wilson 95 %] |
|---|---|---|
| G1 | 145 | 0.055 [0.028, 0.105] |
| G2 | 486 | 0.091 [0.068, 0.119] |

Comparación pareada G1 - G2 por par (mínimo 3 eventos evaluables en ambos brazos): n = 20 pares · Mdn G1 0.000 · Mdn G2 0.066 · HL -0.036 [-0.094, +0.010] · p = 0.1704. Descriptivo, sin Holm.

Uso: EXPLORATORIO. No decide H1e (regla del apartado 5.8.5). Sin validación humana: brecha declarada.
