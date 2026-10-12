# Validación brecha 4 (OE-5/H1e) — resultado

Evaluadores: E1, E2, E3. Casos en la clave: 59.

- ⚠ E2 no respondió 1 de 59 casos todavía (`f8d8e8f27-41d7-4573-a294-c79d2378b6e5_229_Valerius`, export parcial) — 58/59 completo.
- ⚠ **Nota sobre la muestra**: la muestra de 60 turnos generada tiene un caso duplicado
  (`fe1e30d0b-9dd8-454c-b297-44c08204610f_252_autómata` aparece dos veces en `brecha4_clave.csv`,
  idéntico en todos sus campos), por eso son 59 casos únicos y no 60 — describir la muestra en la
  tesis como n=59, no n=60. No es un error de los evaluadores: los tres respondieron exactamente
  igual (mismo veredicto, misma nota, mismos segundos) en ambas apariciones del caso, señal de que
  fue la herramienta de etiquetado la que mostró/exportó el mismo ítem dos veces, no que
  contestaran dos preguntas distintas de forma inconsistente. Es un detalle a corregir en
  `scripts/validacion_brecha4_generar.py` si se vuelve a generar una muestra con esta semilla u
  otra.

## Acuerdo entre evaluadores
- Kappa de Fleiss (3 evaluadores, 3 categorías): **0.138**  (precedente citable: Chen, Wang, Yu & Zhang 2023, AAAI, Fleiss' Kappa=0.671, 4 evaluadores, escala 1-3, consistencia de persona.)

| Par | n común | % acuerdo | kappa Cohen (bin. activo/no) | AC1 de Gwet |
|---|---|---|---|---|
| E1–E2 | 58 | 51.7% | 0.051 | 0.088 |
| E1–E3 | 59 | 79.7% | 0.595 | 0.593 |
| E2–E3 | 58 | 51.7% | -0.020 | 0.119 |

## cl2_pnj_inactivo_actua refinado vs. veredicto humano mayoritario
n=34 (estratos actuando/solo_referenciado con mayoría humana clara). TP=10 FP=6 TN=3 FN=15.
- Precisión: 62.5% (IC95% Wilson 38.6%–81.5%)
- Recall: 40.0% (IC95% Wilson 23.4%–59.3%)

## Jericho recall (estrato 'silencio' — casos donde no reconoció nada)
n=20. De estos, el humano confirma «no hay error» (retrospectivo/no_aplica) en 18 y encuentra «lo narra activo» en 2 — este último grupo son falsos negativos de Jericho (silencio que SÍ escondía un error de continuidad no detectado por el vocabulario léxico).

## Nota metodológica
Jericho recall valida si la TRANSICIÓN de estado se narró; cl2_pnj_inactivo_actua y Kev validan si una mención POSTERIOR trata al PNJ como activo. Son constructos relacionados pero no idénticos — por eso Jericho solo tiene verdad de referencia en el estrato 'silencio' arriba, no en 'actuando'/'solo_referenciado'.