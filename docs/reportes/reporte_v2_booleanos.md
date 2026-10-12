# A4a (parte 2): `cr1` y `cl2_pnj_inactivo_actua` sobre texto normalizado

Generado por `scripts/reporte_v2/recalcular_booleanos.py` (solo SELECT, sin LLM). Corrección **posterior (post hoc)** al instrumento, aplicada igual a los dos brazos; descriptiva, no declara ganador.
v1 = lo que el motor guardó en `turn_validation`; v2 = el mismo detector sobre el turno normalizado (sin etiquetas ni línea mecánica de G1). Unidad: la campaña (tasa de turnos con la marca) y la pareja (21 parejas, G1 − G2).

## Fidelidad del recálculo

Recalcular sobre texto **crudo** con el contexto del arnés reproduce lo guardado: **0 discrepancias en 117 600 comparaciones** (2 instrumentos × 58 800 turnos).

| instrumento | brazo | turnos | marcas v1 | marcas v2 | 1→0 | 0→1 |
|---|---|---|---|---|---|---|
| cr1_veredicto_contradice_narracion | G1 | 29400 | 139 | 29 | 110 | 0 |
| cl2_pnj_inactivo_actua | G1 | 29400 | 2564 | 2558 | 6 | 0 |
| cr1_veredicto_contradice_narracion | G2 | 29400 | 21 | 21 | 0 | 0 |
| cl2_pnj_inactivo_actua | G2 | 29400 | 816 | 816 | 0 | 0 |

## G1 vs G2 antes y después (Hodges-Lehmann de G1 − G2 sobre 21 parejas; Holm sobre estos dos instrumentos)

| instrumento | tasa G1 v1→v2 | tasa G2 v1→v2 | HL v1 → v2 | rank-biserial v1 → v2 | p Holm v1 → v2 | lectura |
|---|---|---|---|---|---|---|
| cr1: veredicto de la tirada contradice la narración (pifia + verbo de éxito) | 0.47 % → 0.10 % | 0.07 % → 0.07 % | +0.39 pp → +0.04 pp | +1.00 → +0.35 | 3.81e-06 → 0.326 | desaparece |
| cl2_pnj_inactivo_actua: aparece el nombre de un PNJ muerto o desaparecido | 8.73 % → 8.71 % | 2.78 % → 2.78 % | +5.11 pp → +5.11 pp | +0.45 → +0.45 | 0.0826 → 0.165 | sin cambio material |

## Lectura

- **`cr1`: la diferencia entre brazos era un artefacto de formato.** De 139 marcas en G1, 110 desaparecen al normalizar. Todas son la línea mecánica de G1 («Fallo (2 vs CD 15). No logras leer…»): el detector busca «logras» sin mirar la negación y la línea mecánica siempre narra el resultado. En G2 no cambia nada (21 → 21). La diferencia G1 > G2 (Holm 3.8e-6) pasa a 0.10 % vs 0.07 % (Holm 0.33).
- **`cr1` sigue siendo de baja precisión.** Lectura rápida de las marcas que sobreviven (heurística de negación, no auditoría): 28 de 29 en G1 y 16 de 21 en G2 solo contienen «no logras/no consigues…», es decir, no son narración de éxito. Con tasas de 0.1 % y 0.07 % no hay evidencia de contradicciones entre veredicto y narración en ningún brazo, pero el detector no las mide bien.
- **`cl2_pnj_inactivo_actua` no cambia por la normalización** (6 de 2 564 marcas en G1). La diferencia G1 8.7 % vs G2 2.8 % se mantiene (HL +5.1 pp), y con Holm sobre dos instrumentos no llega a significativa (0.08 → 0.17, n = 21).
- **Advertencia sobre `cl2_pnj_inactivo_actua`:** marca que el nombre de un PNJ con estado distinto de «alive» aparece en el texto, no que ese PNJ *actúe*. Mencionar a un PNJ muerto en un recuerdo o un diálogo también dispara. Su precisión no está medida (auditoría A3 pendiente) y la línea base de A2 mostró que la variante refinada solo ve nombres de una palabra. No se debe leer como «G1 resucita más PNJ» sin auditarla.
- Habría que declarar ambos como instrumentos de baja precisión y no usar `cr1` v1 como evidencia contra G1.
