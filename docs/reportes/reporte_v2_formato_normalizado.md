# Instrumentos numéricos recalculados sobre texto normalizado (v2) — G1 vs G2, Par07-27

- Generado: 2026-09-20 21:19 · commit `30b998f` (árbol de trabajo con cambios sin confirmar) · semilla de bootstrap **20260920** (B = 10000, remuestreo de parejas)
- **DESCRIPTIVO y POST HOC.** Este informe corrige un artefacto de formato del *instrumento* y mide cuánto cambian las comparaciones G1-vs-G2; **no declara ningún ganador**. La corrección se decidió DESPUÉS de ver el hallazgo de sensibilidad (`docs/reportes/sensibilidad_baseline.md`, P11), no estaba pre-especificada. Las pruebas de Wilcoxon son solo referencia (n = 21 parejas; los turnos dentro de una campaña no son independientes).
- Datos: 42 campañas (21 parejas, Par07-27), turnos 1-1400 por campaña en `datos_v2/par<NN>_<G1|G2>.csv`; las medias usan los turnos ≥ 2 (el turno 1 se compara con el lore, no con un turno del DM, como en la línea base).

## 1. El artefacto y su corrección

G1 escribe cada turno como `narrativa / mecanica / presion` (etiquetas en líneas solas) más una línea de tirada («Percepción: Éxito (10 vs CD 10)»); G2 nunca. `normalizar_turno(dm, brazo)` (`scripts/reporte_v2/normalizacion.py`) deja en G1 solo la prosa (narrativa + presion), quita el bloque `mecanica`, las etiquetas y cualquier línea de tirada suelta; en G2 (y en el lore, turno 0) es la identidad salvo `.strip()`. **No** modifica `prosa()` de `validacion_generar.py`.

Residuos de formato medidos sobre **3000 turnos G1 reales** (muestra aleatoria con semilla 20260920 de los 21×1399 turnos 2-1400) y, como confirmación, sobre la población completa de G1 (29379 turnos):

| texto | muestra: turnos con algún residuo | etiquetas | línea de tirada | encabezados | patrón «Habilidad: Éxito/Fallo (N vs CD M)» | JSON crudo | población: con algún residuo |
|---|---|---|---|---|---|---|---|
| G1 crudo | 3000/3000 (100.00%) | 3000 | 2890 | 0 | 2211 | 0 | — |
| G1 tras `prosa()` | 22/3000 (0.73%) | 22 | 22 | 0 | 8 | 0 | 225/29379 (0.77%) |
| G1 tras `normalizar_turno` | 0/3000 (0.00%) | 0 | 0 | 0 | 0 | 0 | 0/29379 (0.00%) |

G2 crudo (muestra de 3000): 0 turnos con algún residuo. `normalizar_turno` difiere de `prosa` en 22 turnos de la muestra y 225 de la población: **`prosa()` no era suficiente** porque solo reconoce las etiquetas en minúscula y sin adorno; deja `**narrativa**`/`**mecanica**` en negrita (sobre todo el Par 12), «Mecanica»/«Mecánica» capitalizadas (p. ej. Par 18, 21) y los 3 turnos en que el modelo devolvió el JSON crudo (Par 13, 17, 26). Decisión de diseño: el bloque `presion` se **conserva** (es prosa dirigida al jugador, como en `prosa()`, que se usó en la validación humana ciega); ver limitaciones.

Turnos con residuo tras `prosa()` por pareja (población G1): Par 08: 34, Par 10: 13, Par 11: 6, Par 12: 108, Par 13: 5, Par 16: 1, Par 17: 1, Par 18: 6, Par 19: 2, Par 21: 1, Par 22: 21, Par 24: 26, Par 26: 1.

## 2. Sanidad

**G2 (la normalización es la identidad): v2 = v1 en 29400 turnos × 8 columnas → 0 discrepancias.** (v1 = valor guardado por el motor en `turn_validation`; comparación a los decimales de cada columna; bandera y recuento exactos.)

| instrumento | turnos comparados | discrepancias | máx. \|v1 − v2\| |
|---|---|---|---|
| `qn1_ttr` | 29400 | 0 | 0 |
| `qn1_ngram_repeticion` | 29400 | 0 | 0 |
| `qn1_legibilidad_fh` | 29400 | 0 | 0 |
| `cl2_lugar_jaccard_similarity` | 29400 | 0 | 0 |
| `cr2_entidad_grafo_densidad` | 29400 | 0 | 0 |
| `cr2_n_nombres_no_reconocidos` | 29400 | 0 | 0 |
| `cr2_nombres_no_reconocidos` | 29400 | 0 | 0 |
| `grammaticality_lt` | 2940 | 0 | 0 |

**Control en G1:** recalcular G1 sobre el texto CRUDO con el mismo contexto reconstruido reproduce v1 en 29400 turnos × 7 columnas → 0 discrepancias. Es decir, toda diferencia v1 → v2 en G1 se debe a la normalización del texto, no a la reconstrucción del contexto.

## 3. Medias por brazo (media de las 21 campañas de cada brazo; entre paréntesis, la desviación típica entre campañas)

| instrumento | G1 v1 | G2 v1 | G1 v2 | G2 v2 | Δ G1 (v2 − v1) | Δ G2 (v2 − v1) |
|---|---|---|---|---|---|---|
| TTR (type/token) (`qn1_ttr`) | 0.691 (0.00923) | 0.726 (0.00669) | 0.68 (0.00882) | 0.726 (0.00669) | -0.0109 | 0 |
| Repetición de bigramas (`qn1_ngram_repeticion`) | 0.0297 (0.00369) | 0.0182 (0.0015) | 0.0289 (0.00352) | 0.0182 (0.0015) | -0.00079 | 0 |
| Legibilidad Fernández-Huerta (`qn1_legibilidad_fh`) | 60.5 (2.61) | 61.4 (2.47) | 60.1 (2.73) | 61.4 (2.47) | -0.482 | 0 |
| Jaccard con la escena anterior (`cl2_lugar_jaccard_similarity`) | 0.216 (0.00957) | 0.172 (0.00587) | 0.192 (0.00896) | 0.172 (0.00587) | -0.0244 | 0 |
| Densidad del grafo de entidades (`cr2_entidad_grafo_densidad`) | 0.175 (0.0748) | 0.26 (0.13) | 0.229 (0.0911) | 0.26 (0.13) | 0.0536 | 0 |
| N.º de nombres no reconocidos (`cr2_n_nombres_no_reconocidos`) | 2.29 (0.339) | 0.0936 (0.0697) | 0.152 (0.333) | 0.0936 (0.0697) | -2.14 | 0 |
| Turnos con algún nombre no reconocido (`cr2_nombres_no_reconocidos`) | 0.999 (0.00255) | 0.0571 (0.0374) | 0.0891 (0.16) | 0.0571 (0.0374) | -0.909 | 0 |
| Gramaticalidad (LanguageTool) (`grammaticality_lt`) | 0.989 (0.00127) | 0.999 (0.000352) | 0.999 (0.000396) | 0.999 (0.000352) | 0.0107 | 0 |

`cr2_nombres_no_reconocidos` es la proporción de turnos con al menos un nombre no reconocido; `grammaticality_lt` usa solo 1 de cada 10 turnos (los turnos múltiplos de 10) y su v1 es LanguageTool sobre el texto crudo recalculado aquí (no se guarda en `turn_validation`).

## 4. Diferencia pareada G1 − G2 por pareja, antes (v1) y después (v2) de normalizar

n = 21 parejas. HL = Hodges-Lehmann; r = correlación rank-biserial pareada (+1 = G1 > G2 en todas las parejas); IC bootstrap 95 % remuestreando parejas; p = Wilcoxon exacto bilateral; p Holm = ajustado sobre la familia de instrumentos dentro de cada versión.

| instrumento | versión | mediana | HL [IC95] | r [IC95] | W+ / W− | p Wilcoxon | p Holm |
|---|---|---|---|---|---|---|---|
| `qn1_ttr` | v1 | -0.0359 | -0.035 [-0.0381, -0.0315] | -1.00 [-1.00, -1.00] | 0.0 / 231.0 | 9.5e-07 | 7.6e-06 |
| `qn1_ttr` | v2 | -0.0441 | -0.046 [-0.0495, -0.0422] | -1.00 [-1.00, -1.00] | 0.0 / 231.0 | 9.5e-07 | 7.6e-06 |
| `qn1_ngram_repeticion` | v1 | 0.0108 | 0.0114 [0.00979, 0.0131] | +1.00 [1.00, 1.00] | 231.0 / 0.0 | 9.5e-07 | 7.6e-06 |
| `qn1_ngram_repeticion` | v2 | 0.0101 | 0.0106 [0.00921, 0.0122] | +1.00 [1.00, 1.00] | 231.0 / 0.0 | 9.5e-07 | 7.6e-06 |
| `qn1_legibilidad_fh` | v1 | -1.21 | -1.17 [-2.32, 0.162] | -0.43 [-0.84, 0.04] | 66.0 / 165.0 | 0.089 | 0.089 |
| `qn1_legibilidad_fh` | v2 | -1.57 | -1.57 [-2.91, -0.217] | -0.53 [-0.91, -0.07] | 54.0 / 177.0 | 0.032 | 0.160 |
| `cl2_lugar_jaccard_similarity` | v1 | 0.0447 | 0.0436 [0.0408, 0.047] | +1.00 [1.00, 1.00] | 231.0 / 0.0 | 9.5e-07 | 7.6e-06 |
| `cl2_lugar_jaccard_similarity` | v2 | 0.0192 | 0.019 [0.0166, 0.0229] | +1.00 [1.00, 1.00] | 231.0 / 0.0 | 9.5e-07 | 7.6e-06 |
| `cr2_entidad_grafo_densidad` | v1 | -0.056 | -0.0706 [-0.118, -0.0483] | -0.94 [-1.00, -0.77] | 7.0 / 224.0 | 1.8e-05 | 3.6e-05 |
| `cr2_entidad_grafo_densidad` | v2 | -0.0176 | -0.026 [-0.0596, 0.000412] | -0.45 [-0.83, 0.01] | 64.0 / 167.0 | 0.076 | 0.304 |
| `cr2_n_nombres_no_reconocidos` | v1 | 2.14 | 2.13 [2.08, 2.21] | +1.00 [1.00, 1.00] | 231.0 / 0.0 | 9.5e-07 | 7.6e-06 |
| `cr2_n_nombres_no_reconocidos` | v2 | -0.0307 | -0.0189 [-0.0457, 0.0543] | -0.16 [-0.69, 0.32] | 97.0 / 134.0 | 0.539 | 1.000 |
| `cr2_nombres_no_reconocidos` | v1 | 0.948 | 0.947 [0.936, 0.958] | +1.00 [1.00, 1.00] | 231.0 / 0.0 | 9.5e-07 | 7.6e-06 |
| `cr2_nombres_no_reconocidos` | v2 | -0.0172 | -0.00393 [-0.0232, 0.0382] | -0.04 [-0.61, 0.44] | 111.0 / 120.0 | 0.892 | 1.000 |
| `grammaticality_lt` | v1 | -0.0107 | -0.0108 [-0.0113, -0.0102] | -1.00 [-1.00, -1.00] | 0.0 / 231.0 | 9.5e-07 | 7.6e-06 |
| `grammaticality_lt` | v2 | 4.29e-05 | 7.86e-05 [-7.86e-05, 0.000296] | +0.22 [-0.27, 0.67] | 141.0 / 90.0 | 0.388 | 1.000 |

## 5. ¿Qué conclusiones G1-vs-G2 cambian al normalizar?

«Conclusión» de un instrumento = signo y tamaño de HL(G1 − G2) y si es significativa (Wilcoxon con Holm < 0,05). Reglas fijadas antes de mirar la tabla: **cambia de signo** (HL de signo opuesto); **desaparece** (significativa en v1 y no en v2); **cambia de tamaño** (mismo signo pero |HL v2 − HL v1| > 50 % de |HL v1|); **aparece** (no significativa en v1 y sí en v2). Δr = r(v2) − r(v1) con IC bootstrap (mismas parejas remuestreadas) como medida sin unidades del cambio.

| instrumento | HL v1 → HL v2 | r v1 → r v2 | Δr [IC95] | significativa v1 → v2 (Holm) | resultado |
|---|---|---|---|---|---|
| `qn1_ttr` | -0.035 → -0.046 | -1.00 → -1.00 | +0.00 [0.00, 0.00] | sí → sí | **sin cambio material** |
| `qn1_ngram_repeticion` | 0.0114 → 0.0106 | +1.00 → +1.00 | +0.00 [0.00, 0.00] | sí → sí | **sin cambio material** |
| `qn1_legibilidad_fh` | -1.17 → -1.57 | -0.43 → -0.53 | -0.10 [-0.26, 0.00] | no → no | **sin cambio material** |
| `cl2_lugar_jaccard_similarity` | 0.0436 → 0.019 | +1.00 → +1.00 | +0.00 [0.00, 0.00] | sí → sí | **cambia de tamaño (>50 %)** |
| `cr2_entidad_grafo_densidad` | -0.0706 → -0.026 | -0.94 → -0.45 | +0.49 [0.16, 0.87] | sí → no | **desaparece** (además: cambia de tamaño (>50 %)) |
| `cr2_n_nombres_no_reconocidos` | 2.13 → -0.0189 | +1.00 → -0.16 | -1.16 [-1.69, -0.68] | sí → no | **cambia de signo** (además: desaparece) |
| `cr2_nombres_no_reconocidos` | 0.947 → -0.00393 | +1.00 → -0.04 | -1.04 [-1.61, -0.56] | sí → no | **cambia de signo** (además: desaparece) |
| `grammaticality_lt` | -0.0108 → 7.86e-05 | -1.00 → +0.22 | +1.22 [0.73, 1.67] | sí → no | **cambia de signo** (además: desaparece) |

**Resumen (8 instrumentos):** 3 cambian de signo; 4 pierden la significancia (desaparecen); 2 cambian de tamaño en más de un 50 % con el mismo signo; 0 aparecen (no significativos antes, significativos después); 3 sin cambio material. (Una misma conclusión puede llevar varias banderas; la columna «resultado» muestra la de mayor precedencia: signo > desaparece > tamaño > aparece.)

## 6. Diferencias por pareja (G1 − G2)

| instrumento | versión | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `qn1_ttr` | v1 | -0.0227 | -0.0403 | -0.036 | -0.0281 | -0.0501 | -0.0395 | -0.0307 | -0.0447 | -0.0359 | -0.0375 | -0.0438 | -0.031 | -0.0295 | -0.0436 | -0.0415 | -0.0359 | -0.0299 | -0.0251 | -0.0281 | -0.0325 | -0.0305 |
| `qn1_ttr` | v2 | -0.033 | -0.0515 | -0.0407 | -0.0385 | -0.0619 | -0.0509 | -0.0358 | -0.0517 | -0.0489 | -0.0508 | -0.055 | -0.0437 | -0.0403 | -0.0541 | -0.0528 | -0.0481 | -0.0411 | -0.0406 | -0.0404 | -0.0411 | -0.0441 |
| `qn1_ngram_repeticion` | v1 | 0.00976 | 0.0122 | 0.0159 | 0.0121 | 0.0191 | 0.00991 | 0.00516 | 0.0108 | 0.0166 | 0.0134 | 0.00788 | 0.00963 | 0.00747 | 0.0148 | 0.016 | 0.0106 | 0.0092 | 0.00681 | 0.00814 | 0.0134 | 0.0125 |
| `qn1_ngram_repeticion` | v2 | 0.00881 | 0.0116 | 0.0122 | 0.011 | 0.0188 | 0.00982 | 0.00291 | 0.00868 | 0.0162 | 0.0135 | 0.00748 | 0.0101 | 0.00692 | 0.0138 | 0.015 | 0.0101 | 0.00874 | 0.00807 | 0.0074 | 0.0114 | 0.0125 |
| `qn1_legibilidad_fh` | v1 | 1.37 | -2.46 | 6.89 | -3.57 | 1.45 | -1.21 | 8.19 | -0.165 | -2.83 | -4.15 | -1.12 | -8.28 | 0.644 | -1.96 | -0.655 | -1.48 | -0.675 | -2.55 | -3.96 | 1.58 | -2.48 |
| `qn1_legibilidad_fh` | v2 | 0.851 | -3.31 | 6.72 | -3.91 | 0.873 | -1.57 | 7.98 | -1.13 | -3.12 | -4.69 | -1.98 | -8.62 | 0.451 | -3.54 | -0.963 | -2.45 | -1.29 | -1.21 | -5.11 | 1.76 | -3.3 |
| `cl2_lugar_jaccard_similarity` | v1 | 0.0447 | 0.0383 | 0.0466 | 0.039 | 0.0484 | 0.0396 | 0.0312 | 0.0413 | 0.0618 | 0.0454 | 0.0364 | 0.0314 | 0.0458 | 0.0476 | 0.0452 | 0.0409 | 0.0405 | 0.0575 | 0.045 | 0.0436 | 0.0595 |
| `cl2_lugar_jaccard_similarity` | v2 | 0.0203 | 0.0139 | 0.0241 | 0.0149 | 0.0236 | 0.016 | 0.0117 | 0.0172 | 0.0359 | 0.0195 | 0.0128 | 0.00812 | 0.0204 | 0.0226 | 0.0192 | 0.0161 | 0.0164 | 0.033 | 0.0193 | 0.0179 | 0.0333 |
| `cr2_entidad_grafo_densidad` | v1 | -0.19 | 0.0424 | -0.232 | -0.0816 | -0.15 | -0.0526 | -0.266 | -0.0508 | -0.056 | -0.0335 | -0.084 | 0.0217 | -0.184 | -0.0551 | -0.00138 | -0.0457 | -0.0459 | -0.0743 | -0.0787 | -0.137 | -0.0325 |
| `cr2_entidad_grafo_densidad` | v2 | -0.11 | 0.0908 | -0.174 | -0.00792 | -0.0627 | 0.0192 | -0.187 | 0.0423 | -0.0284 | -0.00164 | -0.0512 | 0.0576 | -0.113 | -0.00955 | 0.0304 | -0.0176 | -0.00841 | -0.0364 | -0.0282 | -0.0736 | 0.00922 |
| `cr2_n_nombres_no_reconocidos` | v1 | 2.05 | 2.22 | 2.18 | 2.1 | 3.47 | 2.03 | 2.18 | 2.2 | 2.02 | 2.01 | 2.12 | 2.38 | 2.24 | 1.92 | 2.03 | 2.19 | 2.14 | 2.06 | 2.16 | 2.48 | 2.01 |
| `cr2_n_nombres_no_reconocidos` | v2 | -0.0908 | -0.103 | 0.0872 | -0.06 | 1.33 | -0.0272 | -0.0522 | 0.0422 | -0.0529 | -0.0429 | -0.05 | 0.299 | 0.172 | -0.147 | -0.0329 | 0.0543 | -0.0122 | -0.0457 | -0.0257 | 0.0122 | -0.0307 |
| `cr2_nombres_no_reconocidos` | v1 | 0.938 | 0.927 | 0.97 | 0.967 | 0.926 | 0.949 | 0.941 | 0.976 | 0.946 | 0.961 | 0.957 | 0.803 | 0.97 | 0.902 | 0.948 | 0.919 | 0.967 | 0.946 | 0.959 | 0.971 | 0.927 |
| `cr2_nombres_no_reconocidos` | v2 | -0.0457 | -0.0522 | 0.0908 | -0.0293 | 0.64 | -0.0214 | -0.0172 | 0.0343 | -0.0315 | -0.025 | -0.0279 | 0.108 | 0.105 | -0.0858 | -0.02 | 0.0801 | -0.00858 | -0.0222 | -0.0143 | 0.000715 | 0.0129 |
| `grammaticality_lt` | v1 | -0.0113 | -0.0096 | -0.0113 | -0.0101 | -0.0107 | -0.0105 | -0.00713 | -0.0112 | -0.0114 | -0.0114 | -0.0102 | -0.0101 | -0.0119 | -0.0103 | -0.0117 | -0.0113 | -0.0106 | -0.00811 | -0.012 | -0.0101 | -0.0125 |
| `grammaticality_lt` | v2 | 0.000229 | -0.000121 | -0.000864 | 0.000143 | -2.14e-05 | -3.57e-05 | -8.57e-05 | 0.000114 | 0.000357 | 4.29e-05 | 0.000743 | 0.000514 | -0.000164 | 0.000757 | -0.000271 | 0.000157 | 7.14e-06 | 0.000986 | 0.00045 | -0.000914 | -0.000164 |

## 7. Lectura (redactada a mano sobre las tablas de esta corrida; el script solo la incluye, no la regenera; DESCRIPTIVA, sin ganador)

Número de parejas en las que G1 > G2 (de 21), antes → después de normalizar: TTR 0 → 0; bigramas repetidos 21 → 21; Fernández-Huerta 6 → 6; Jaccard con la escena anterior 21 → 21; densidad del grafo 2 → 6; n.º de nombres no reconocidos 21 → 7; turnos con algún nombre no reconocido 21 → 8; gramaticalidad 0 → 12.

- **Se explican por el formato (el efecto desaparece):** `cr2_nombres_no_reconocidos` (proporción de turnos marcados en G1: 99,9 % → 8,9 %; G2: 5,7 %), su recuento, y la gramaticalidad de LanguageTool (G1 0,989 → 0,999; G2 0,999). Las tres son las «cambia de signo» del resumen, pero conviene leerlas con cuidado: en v2 ninguna es significativa (p Holm = 1) y el IC de r incluye el 0, así que el «cambio de signo» es un HL prácticamente nulo que cae a uno u otro lado del cero, **no** una inversión demostrada. La línea de tirada («Percepción: Éxito…») era lo que se contaba como nombre propio y lo que LanguageTool penalizaba.
- **Densidad del grafo de entidades:** el efecto se reduce un 63 % (HL −0,071 → −0,026) y deja de ser significativo tras Holm (p 3,6e-05 → 0,30), con r −0,94 → −0,45 (IC v2 [−0,83, 0,01]); la dirección (G1 < G2) se mantiene en 15 de 21 parejas. Queda una diferencia no concluyente, no ausente.
- **Jaccard con la escena anterior:** sigue mayor en G1 en 21 de 21 parejas, pero el tamaño baja un 56 % (HL 0,044 → 0,019): más de la mitad de la ventaja de G1 en solapamiento léxico entre turnos consecutivos venía del formato repetido en cada turno.
- **Se mantienen tras normalizar (mismo signo, misma significancia, 21 de 21 parejas):** TTR menor en G1 (HL −0,035 → −0,046, la brecha aumenta un 31 %) y más bigramas repetidos en G1 (0,0114 → 0,0106, −7 %). Fernández-Huerta no es significativo antes ni después (HL −1,17 → −1,57; Wilcoxon sin ajustar p = 0,089 → 0,032, Holm 0,089 → 0,16).
- **Residuos de la diferencia que NO se han normalizado y que pueden intervenir en lo que queda:** G1 escribe el diálogo entre comillas rectas (79 % de los turnos) y casi nunca con raya (0,04 %), G2 usa la raya en el 23,6 % de los turnos y comillas en el 10,3 %; el bloque `presion` solo existe en G1. Estos dos puntos podrían explicar parte de FH, del grafo, del TTR y del Jaccard que siguen distintos; esta corrida no lo mide.
- **No se trata de un nombre no reconocido de formato lo que queda en G1:** el 8,9 % de turnos marcados en G1 v2 está dominado por la pareja 11 (+0,64 respecto a G2), donde el narrador de G1 introduce nombres del mundo que no están en el gazetteer (Aethel, Solis, Sideris, Kaelum…); en la 09, nombres de personas reales (Elena, Julián) y «Dios». Es contenido, no formato.
- **Alcance del hallazgo:** de los 8 instrumentos, 3 cambian de signo (con el matiz anterior), 4 pierden la significancia y 2 cambian de tamaño en más del 50 % con el mismo signo; en TTR, bigramas y Fernández-Huerta la conclusión no cambia materialmente. Todo esto es una corrección post hoc del instrumento y no dice cuál de las dos arquitecturas narra mejor.

## Limitaciones y decisiones

- Solo se corrige el **formato** (etiquetas, bloque de mecánica, línea de tirada, JSON crudo). Lo que sigue distinguiendo a G1 de G2 tras normalizar puede ser estilo genuino de la arquitectura **o** otros restos de forma que no se han normalizado (el bloque `presion` de G1 no existe en G2; la tipografía del diálogo, abajo). Esas diferencias **no se han ajustado**: se reportan tal cual.
- Tipografía del diálogo (población, turnos 2-1400; NO normalizada): turnos con línea que empieza por raya «—»: G1 0.0% vs G2 23.6%; turnos con diálogo entre comillas rectas: G1 79.2% vs G2 10.3%. Los instrumentos tokenizan por `\w+` (TTR, bigramas, Jaccard) o parten frases por `.!?` (FH, grafo), así que la puntuación afecta sobre todo a FH y al grafo; no se ha medido cuánto.
- `presion` se conserva como prosa (igual que en `prosa()` de la validación ciega). Si se considerara formato, las cifras de G1 v2 cambiarían; no se ha explorado.
- El contexto de cada turno (entidades vigentes, escena anterior) se reconstruye como en `scripts/sensibilidad/datos.py`; el control de sanidad muestra 0 discrepancias con el valor guardado en G1 (texto crudo) y en G2. La «escena anterior» del Jaccard en v2 es el turno previo también normalizado; el lore (turno 0) no se altera.
- La gramaticalidad (LanguageTool) solo se calcula en 1 de cada 10 turnos (turnos múltiplos de 10); v1 y v2 comparten esos turnos. La categoría TYPOS está excluida como en `reporte_validacion.py`.
- Estadística: n = 21 parejas de dos lotes de configuración (Par07-17 y Par18-27); el remuestreo de parejas ignora esa estructura de lotes. Wilcoxon exacto condicional a empates y con ceros descartados; el IC de r y de HL es percentil, no corregido. El criterio «> 50 %» es sobre HL en las unidades de cada instrumento y es inestable cuando |HL v1| es pequeño (véase el IC).
- La familia de Holm es el conjunto de instrumentos de este informe, por versión; no incluye otras comparaciones del proyecto.

## Tiempos de cada etapa

| etapa | tiempo |
|---|---|
| 1. medir residuos de formato (3000 turnos G1 + población; normalizacion.py) | 3.2 s |
| 2a. recalcular 42 campañas × 1400 turnos, sin LanguageTool (recalcular.py) | 131 s |
| 2b. LanguageTool en 1 de cada 10 turnos (2940 turnos por brazo; recalcular.py --con-lt, caché de LT en disco) | 302 s |
| 2c. control G1 (texto crudo = v1) sobre las 21 campañas G1 | 76 s |
| comparación estadística y generación del informe | 13 s |
