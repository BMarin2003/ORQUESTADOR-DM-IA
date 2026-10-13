# Sensibilidad por perturbación — línea base (instrumentos deterministas tal como están hoy)

- Generado: 2026-09-20 18:43 · commit `30b998f` (árbol de trabajo con cambios sin confirmar en `orquestador/`: los instrumentos se leen del árbol tal cual) · Python 3.14.6
- Semilla de muestreo: **20260920** · pares: 09 (v1), 11 (v1), 13 (v1), 14 (v1), 16 (v1), 20 (v2), 21 (v2), 23 (v2), 24 (v2), 25 (v2)
- Muestra: 150 turnos por brazo (turnos 2–1400) + 60 ventanas de 8 turnos por brazo para P9; LanguageTool sobre 50 turnos por brazo y solo en P6, P8, P11a/b, P12 (lento).
- **Hash SHA-256 de la tabla ESPERADO pre-especificada** (perturbaciones.py, escrita antes de correr nada): `735308b36bf7e81e00da31e5fca53a193e4415ed7409906ff348c7eb6765a61b` (verificado por un test). Tras un primer humo con pocas muestras se añadieron solo dos variantes, P1_accion_sin_tirada, P2_accion_sin_tirada (149 de 150 turnos reales llevan tirada y `qn2_pj_accion_revisar` solo mira turnos sin ella); hash de la tabla completa: `d42cecefbb524af467f31e27bc9911bca61bb2c69806013aa96df07993b0dffc`. Ninguna expectativa se modificó tras ver resultados.
- Tiempos: carga de datos 0s; fidelidad 7s; perturbaciones + instrumentos 208s; estadística 6s; total 221s

## 0. Cómo leer este informe

Dirección esperada = la de un instrumento **válido para su constructo** (p. ej. un detector de usurpación debe dispararse ante usurpación, sea en 3.ª o en 2.ª persona; barajar palabras no debe cambiar el TTR). Veredictos: **responde** (observado = esperado), **no responde** (se esperaba cambio y no se detecta), **dirección opuesta**, **cambio inesperado** (control «sin cambio» que se mueve: artefacto del instrumento) y **no aplica** (menos de 10 pares válidos, o el instrumento depende de datos que no son texto: `cl1_campo_inmutable_alterado` depende de los deltas del extractor). Reglas de decisión fijadas de antemano: numérico «cambia» si p ajustado (Holm) < 0,05 **y** |delta de Cliff pareado| ≥ 0,147 (Romano et al. 2006); booleano «cambia» si p McNemar exacta ajustada (Holm) < 0,05. Holm por brazo dentro de cada familia (confirmatoria = dirección pre-especificada ≠ «sin cambio»; control = «sin cambio»). Los pares sin expectativa son descriptivos (solo en el CSV).

Glifos de las matrices: esperado ● se dispara · ▲ sube · ▼ baja · = sin cambio; veredicto ✓ responde · ✗ no responde · ↔ dirección opuesta · ! cambio inesperado · – no aplica; entre paréntesis lo observado cuando no coincide; «~» tras ✓ = responde pero detecta menos de la mitad de los casos inyectados (anotación añadida al ver los resultados; no cambia el veredicto).

## 1. Prueba de fidelidad (recálculo sobre texto vs. `turn_validation`)

Turnos recalculados: **300** de la muestra aleatoria + **92** turnos con marca positiva guardada (ambos lotes y brazos). Numéricos a 3 decimales (`qn1_legibilidad_fh` es `numeric(6,2)`: 2 decimales); booleanos y `cr2_nombres_no_reconocidos` por igualdad exacta.

| columna | muestra: coinciden | positivos: coinciden |
|---|---|---|
| `qn1_ttr` | 300/300 | 92/92 |
| `qn1_ngram_repeticion` | 300/300 | 92/92 |
| `qn1_legibilidad_fh` | 300/300 | 92/92 |
| `cl2_lugar_jaccard_similarity` | 300/300 | 92/92 |
| `cr2_entidad_grafo_densidad` | 300/300 | 92/92 |
| `qn2_pj_piensa_narrado` | 300/300 | 92/92 |
| `cl2_pnj_inactivo_actua` | 300/300 | 92/92 |
| `cr1_veredicto_contradice_narracion` | 300/300 | 92/92 |
| `cl2_pc_hp_contradice_narracion` | 300/300 | 92/92 |
| `qn2_pj_accion_revisar` | 300/300 | 92/92 |
| `cr2_nombres_no_reconocidos` | 300/300 | 92/92 |
| `meta_comentario` | 300/300 | 92/92 |
| `comenta_reglas` | 300/300 | 92/92 |

Discrepancias totales: **0**.

Control de la propia prueba (mutaciones deliberadas del contexto en 60 turnos): con la escena anterior equivocada (turno t−2) el Jaccard deja de coincidir en 60/60; sin los PNJ en el gazetteer el grafo de entidades deja de coincidir en 9/60. Es decir, la coincidencia no es trivial.

Prevalencia de marcas guardadas (todas las campañas de los dos lotes; contexto para la potencia de los booleanos):

| brazo | turnos | cl2_pnj_inactivo_actua | qn2_pj_piensa_narrado | qn2_pj_accion_revisar | cl2_pc_hp | cr1 | cr2 (≥1 nombre) | meta_comentario | comenta_reglas |
|---|---|---|---|---|---|---|---|---|---|
| G1 | 29400 | 2564 | 4 | 0 | 0 | 139 | 29357 | 0 | 0 |
| G2 | 29400 | 816 | 0 | 0 | 0 | 21 | 1682 | 132 | 26 |

## 2. Resumen: instrumento × perturbación (esperado, veredicto)

### G2 (monolítico, narra en 2.ª persona)

| instrumento | P1 decision | P2 decision | P1 pensamiento | P2 pensamiento | P1 emocion | P2 emocion | P1 habla | P2 habla | P1 accion | P2 accion | P1 accion_sin_tirada | P2 accion_sin_tirada | P3 dead_actua | P3 dead_habla | P3 missing_actua | P3 missing_habla | P4 2p | P4 3p | P5 | P6 | P7 | P8 | P9 | P10 | P11a inyeccion | P11b eliminacion | P12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `meta_comentario` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ | =✓ | =– |  |
| `comenta_reglas` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ | =✓ | =– |  |
| `cr1_veredicto_contradice_narracion` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | ●✓ |  |  |  |
| `qn2_pj_piensa_narrado` | ●✗(=) | ●✓ | ●✗(=) | ●✓ | ●✗(=) | ●✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ |  |  |  |
| `qn2_pj_accion_revisar` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | ●– | ●– | ●✗(=) | ●✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ |  |  |  |
| `cl2_pnj_inactivo_actua` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | ●✓ | ●✓ | ●✓ | ●✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  | =✓ |  |  | =✓ |
| `cl2_pc_hp_contradice_narracion` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | ●✗(=) | ●✓ | =✓ | =✓ | =✓ | =✓ |  | =✓ |  |  | =✓ |
| `cr2_nombres_no_reconocidos` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | ●✓ | =✓ | =✓ | ●✓~ |  | =✓ | =!(●) | =– | =✓ |
| `cl2_pnj_inactivo_refinado` |  |  |  |  |  |  |  |  |  |  |  |  | ●✓~ | ●✓~ | ●✓~ | ●✓~ |  |  |  |  |  |  |  |  |  |  |  |
| `cl2_lugar_jaccard_similarity` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ | =✓ | ▼✓ |  |  | =!(▼) | =– |  |
| `cr2_entidad_grafo_densidad` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✓ | =✓ |  | ▼✗(=) |  |  | =!(▼) | =– |  |
| `qn1_ttr` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ | ▼✓ |  |  |  | =!(▲) | =– | ▲✓ |
| `qn1_ngram_repeticion` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✓ |  |  |  | =!(▼) | =– |  |
| `qn1_legibilidad_fh` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  | =!(▲) | =– |  |
| `cr2_n_nombres_no_reconocidos` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✓ |  |  | ▲✓ |  |  |  |  |  |
| `grammaticality_lt` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✓ |  |  |  |  | =!(▼) | =– | ▼✗(=) |
| `grafo_lema_densidad` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✗(=) |  |  |  |  |  |
| `entity_coreference_rate` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |  |  |  |
| `ventana_jaccard_medio` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✓ |  |  |  |  |
| `ventana_entity_coreference_medio` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |
| `ventana_coherencia_C` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |
| `ventana_consistencia_V` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |
| `ventana_bucles_visitas` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✗(=) |  |  |  |  |
| `ventana_bucles_ciclos` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✗(=) |  |  |  |  |

### G1 (multiagente, con etiquetas de formato)

| instrumento | P1 decision | P2 decision | P1 pensamiento | P2 pensamiento | P1 emocion | P2 emocion | P1 habla | P2 habla | P1 accion | P2 accion | P1 accion_sin_tirada | P2 accion_sin_tirada | P3 dead_actua | P3 dead_habla | P3 missing_actua | P3 missing_habla | P4 2p | P4 3p | P5 | P6 | P7 | P8 | P9 | P10 | P11a inyeccion | P11b eliminacion | P12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `meta_comentario` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ | =– | =✓ |  |
| `comenta_reglas` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ | =– | =✓ |  |
| `cr1_veredicto_contradice_narracion` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | ●✓ |  |  |  |
| `qn2_pj_piensa_narrado` | ●✗(=) | ●✓ | ●✗(=) | ●✓ | ●✗(=) | ●✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ |  |  |  |
| `qn2_pj_accion_revisar` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | ●– | ●– | ●✗(=) | ●✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ |  |  | =✓ |  |  |  |
| `cl2_pnj_inactivo_actua` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | ●✓ | ●✓ | ●✓ | ●✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =!(▼) |  | =✓ |  |  | =✓ |
| `cl2_pc_hp_contradice_narracion` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | ●✗(=) | ●✓ | =✓ | =✓ | =✓ | =✓ |  | =✓ |  |  | =✓ |
| `cr2_nombres_no_reconocidos` | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =– | =– | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | =✓ | ●✗(=) | =✓ | =✓ | ●✗(=) |  | =✓ | =– | =!(▼) | =✓ |
| `cl2_pnj_inactivo_refinado` |  |  |  |  |  |  |  |  |  |  |  |  | ●✗(=) | ●✗(=) | ●✗(=) | ●✗(=) |  |  |  |  |  |  |  |  |  |  |  |
| `cl2_lugar_jaccard_similarity` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ | =✓ | ▼✓ |  |  | =– | =!(▼) |  |
| `cr2_entidad_grafo_densidad` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✓ | =✓ |  | ▼✗(=) |  |  | =– | =!(▲) |  |
| `qn1_ttr` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ | ▼✓ |  |  |  | =– | =!(▼) | ▲✓ |
| `qn1_ngram_repeticion` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✓ |  |  |  | =– | =!(▲) |  |
| `qn1_legibilidad_fh` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  | =– | =✓ |  |
| `cr2_n_nombres_no_reconocidos` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✓ |  |  | ▲✓ |  |  |  |  |  |
| `grammaticality_lt` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✓ |  |  |  |  | =– | =!(▲) | ▼✗(=) |
| `grafo_lema_densidad` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✗(=) |  |  |  |  |  |
| `entity_coreference_rate` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |  |  |  |
| `ventana_jaccard_medio` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▼✓ |  |  |  |  |
| `ventana_entity_coreference_medio` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |
| `ventana_coherencia_C` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |
| `ventana_consistencia_V` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | =✓ |  |  |  |  |
| `ventana_bucles_visitas` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✗(=) |  |  |  |  |
| `ventana_bucles_ciclos` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ▲✗(=) |  |  |  |  |

## 3. Los detectores de 3.ª persona

Los tres detectores que buscan «‹Nombre del PJ› decide/muere/ataca…»: control positivo en 3.ª persona (P2, P4_3p) frente a la misma usurpación en 2.ª persona (P1, P4_2p). Tasas de marca antes → después de la inyección.

**G2**

| detector | categoría | control 3.ª persona con nombre: antes → después | veredicto | usurpación 2.ª persona: antes → después | veredicto |
|---|---|---|---|---|---|
| `qn2_pj_piensa_narrado` | decision | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `qn2_pj_piensa_narrado` | pensamiento | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `qn2_pj_piensa_narrado` | emocion | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `qn2_pj_accion_revisar` | accion | n/a | no aplica | n/a | no aplica |
| `qn2_pj_accion_revisar` | accion_sin_tirada | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `cl2_pc_hp_contradice_narracion` | muerte del PJ con HP>0 | 0.0% → 100.0% (n=135) | responde | 0.0% → 0.0% (n=135) | no responde |

**G1**

| detector | categoría | control 3.ª persona con nombre: antes → después | veredicto | usurpación 2.ª persona: antes → después | veredicto |
|---|---|---|---|---|---|
| `qn2_pj_piensa_narrado` | decision | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `qn2_pj_piensa_narrado` | pensamiento | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `qn2_pj_piensa_narrado` | emocion | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `qn2_pj_accion_revisar` | accion | 0.0% → 100.0% (n=1) | no aplica | 0.0% → 0.0% (n=1) | no aplica |
| `qn2_pj_accion_revisar` | accion_sin_tirada | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |
| `cl2_pc_hp_contradice_narracion` | muerte del PJ con HP>0 | 0.0% → 100.0% (n=150) | responde | 0.0% → 0.0% (n=150) | no responde |

## 3b. Hallazgos automáticos (lo que NO cumplió la expectativa pre-especificada)

- **G2** · `grammaticality_lt` **no responde** ante: P12
- **G2** · `qn2_pj_accion_revisar` **no responde** ante: P1_accion_sin_tirada
- **G2** · `qn2_pj_piensa_narrado` **no responde** ante: P1_decision, P1_emocion, P1_pensamiento
- **G2** · `cl2_pc_hp_contradice_narracion` **no responde** ante: P4_2p
- **G2** · `cr2_entidad_grafo_densidad` **no responde** ante: P8
- **G2** · `grafo_lema_densidad` **no responde** ante: P8
- **G2** · `ventana_bucles_ciclos` **no responde** ante: P9
- **G2** · `ventana_bucles_visitas` **no responde** ante: P9
- **G2** · `cl2_lugar_jaccard_similarity` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · `cr2_entidad_grafo_densidad` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · `cr2_nombres_no_reconocidos` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · `grammaticality_lt` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · `qn1_legibilidad_fh` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · `qn1_ngram_repeticion` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · `qn1_ttr` **cambia sin que debiera** (control roto) ante: P11a_inyeccion
- **G2** · con expectativas «no aplica» (menos de 10 pares válidos): P11b_eliminacion, P1_accion, P2_accion
- **G1** · `grammaticality_lt` **no responde** ante: P12
- **G1** · `qn2_pj_accion_revisar` **no responde** ante: P1_accion_sin_tirada
- **G1** · `qn2_pj_piensa_narrado` **no responde** ante: P1_decision, P1_emocion, P1_pensamiento
- **G1** · `cl2_pnj_inactivo_refinado` **no responde** ante: P3_dead_actua, P3_dead_habla, P3_missing_actua, P3_missing_habla
- **G1** · `cl2_pc_hp_contradice_narracion` **no responde** ante: P4_2p
- **G1** · `cr2_nombres_no_reconocidos` **no responde** ante: P5, P8
- **G1** · `cr2_entidad_grafo_densidad` **no responde** ante: P8
- **G1** · `grafo_lema_densidad` **no responde** ante: P8
- **G1** · `ventana_bucles_ciclos` **no responde** ante: P9
- **G1** · `ventana_bucles_visitas` **no responde** ante: P9
- **G1** · `cl2_lugar_jaccard_similarity` **cambia sin que debiera** (control roto) ante: P11b_eliminacion
- **G1** · `cr2_entidad_grafo_densidad` **cambia sin que debiera** (control roto) ante: P11b_eliminacion
- **G1** · `cr2_nombres_no_reconocidos` **cambia sin que debiera** (control roto) ante: P11b_eliminacion
- **G1** · `grammaticality_lt` **cambia sin que debiera** (control roto) ante: P11b_eliminacion
- **G1** · `qn1_ngram_repeticion` **cambia sin que debiera** (control roto) ante: P11b_eliminacion
- **G1** · `qn1_ttr` **cambia sin que debiera** (control roto) ante: P11b_eliminacion
- **G1** · `cl2_pnj_inactivo_actua` **cambia sin que debiera** (control roto) ante: P8
- **G1** · con expectativas «no aplica» (menos de 10 pares válidos): P11a_inyeccion, P1_accion, P2_accion

## 3c. Lectura de la corrida del 2026-09-20 (redactada a mano sobre estas tablas; no se regenera al volver a correr)

- **Detectores de 3.ª persona (qn2_pj_piensa_narrado, qn2_pj_accion_revisar, cl2_pc_hp_contradice_narracion): ciegos en 2.ª persona, en los dos brazos.** Con el nombre del PJ (P2, P4_3p) marcan 150/150 (135/135 en G2 para P4 por elegibilidad); con la misma usurpación en 2.ª persona (P1, P4_2p) marcan 0/150. Es el fallo conocido, ahora medido; el arnés lo detecta y sirve para verificar los detectores corregidos.
- **qn2_pj_accion_revisar y cl2_pc_hp_contradice_narracion están inertes en los datos reales aunque se corrijan:** 0 marcas guardadas en 58 800 turnos. En el primer caso la puerta `not tiradas` casi nunca se abre (149 de 150 turnos muestreados llevan tirada: P1_accion/P2_accion quedan «no aplica»; solo el turno simulado sin tirada permite ejercitar el regex).
- **cr2_nombres_no_reconocidos está saturado en G1 por el formato:** 29 357 de 29 400 turnos G1 guardados tienen algún «nombre no reconocido» (99,9 %; G2: 5,7 %), porque la línea de tirada («Percepción: Éxito…») y sus mayúsculas cuentan como nombres propios. En la muestra 100 % antes de la perturbación, por eso no puede subir ante nombres inventados (P5 «no responde» en G1); al quitar el formato (P11b) cae a 9,3 %. Con P11a en G2 sube de 6,0 % a 100 %.
- **Artefacto de formato (P11) en todos los numéricos de contenido:** TTR, n-gramas, Fernández-Huerta, Jaccard, densidad de grafo y gramaticalidad cambian de forma significativa al añadir/quitar etiquetas y línea mecánica (7 de 9 controles rotos al inyectar el formato en G2, 6 de 9 al quitarlo en G1; solo meta_comentario y comenta_reglas, y FH en G1, quedan quietos). Las comparaciones G1 vs G2 con estos instrumentos sobre el texto crudo mezclan estilo con formato.
- **pnj_inactivo_refinado (spaCy) detecta ~10 % (G2) y ~2 % (G1) de los PNJ inactivos inyectados como sujeto:** solo cuenta nombres de una palabra (`nombre in tok.text`); los PNJ de varias palabras («Sargento Brea») nunca. El detector crudo `cl2_pnj_inactivo_actua` sí responde (100 % tras la inyección; marca base 4,7 % en G2, 14,0 % en G1).
- **Gramaticalidad (LanguageTool):** techo en ~1,00; baja con P6 (barajar) pero no ve palabras de otro alfabeto (P12 «no responde»): la categoría TYPOS está excluida.
- **Coherencia local:** `ventana_jaccard_medio` baja al permutar (efecto pequeño, −0,015) y `ventana_consistencia_V`/`coherencia_C`/`entity_coreference` se comportan como controles invariantes; `detector_bucles` (visitas/ciclos) no reacciona a la permutación. `cr2_entidad_grafo_densidad` y `grafo_lema_densidad` no distinguen una narración de otro par (P8: diferencias pareadas casi siempre 0; mediana ~0).
- **P8 sobre cl2_pnj_inactivo_actua en G1 figura como «cambio inesperado»** porque mi expectativa «sin cambio» olvidó que sustituir el texto elimina las marcas reales de base (14 % de los turnos G1): 21 marcas desaparecen y ninguna aparece (b=21, c=0). Es un error de la pre-especificación, se conserva y se reporta.
- Instrumentos que SÍ se comportan como se pre-especificó: `cr1` ante pifia+éxito, TTR/n-gramas ante párrafo duplicado, Jaccard ante otro par, gramaticalidad ante barajar, controles exactos de P6 (TTR, FH, Jaccard invariantes) y de P9 (V invariante).

## 4a. Detalle por brazo — G2 (monolítico)

Comparaciones **confirmatorias** (dirección pre-especificada). `Antes/Después`: tasa de marca con IC de Wilson (booleanos) o mediana (numéricos); `Δ`: diferencia pareada con IC (Newcombe / bootstrap); `δ`: delta de Cliff pareado / de dos muestras; `p Holm`: p ajustado.

| perturbación | instrumento | esperado | n | antes | después | Δ [IC95] | δ | p Holm | observado | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|
| P10 | `cr1_veredicto_contradice_narracion` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P12 | `grammaticality_lt` | ▼ baja | 50 | 1.000 | 1.000 | 0.000 [0.000, 0.000]  | -0.12 / -0.12 | 0.312 | sin_cambio | **no responde** |
| P12 | `qn1_ttr` | ▲ sube | 150 | 0.730 | 0.737 | 0.007 [0.007, 0.007]  | +1.00 / +0.10 | 4.9e-44 | sube | **responde** |
| P1_accion | `qn2_pj_accion_revisar` | ● se_dispara | 0 | — [0.0%, 100.0%] | — [0.0%, 100.0%] | +0.0 pp [-100.0, +100.0] b=0 c=0 | — | 1 | — | **no aplica** |
| P1_accion_sin_tirada | `qn2_pj_accion_revisar` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P1_decision | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P1_emocion | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P1_pensamiento | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P2_accion | `qn2_pj_accion_revisar` | ● se_dispara | 0 | — [0.0%, 100.0%] | — [0.0%, 100.0%] | +0.0 pp [-100.0, +100.0] b=0 c=0 | — | 1 | — | **no aplica** |
| P2_accion_sin_tirada | `qn2_pj_accion_revisar` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P2_decision | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P2_emocion | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P2_pensamiento | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P3_dead_actua | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 4.7% [2.3%, 9.3%] | 100.0% [97.5%, 100.0%] | +95.3 pp [+90.1, +97.7] b=0 c=143 | — | 4.66e-42 | se_dispara | **responde** |
| P3_dead_actua | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 10.0% [6.2%, 15.8%] | +9.3 pp [+4.7, +15.1] b=0 c=14 | — | 0.00146 | se_dispara | **responde** |
| P3_dead_habla | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 4.7% [2.3%, 9.3%] | 100.0% [97.5%, 100.0%] | +95.3 pp [+90.1, +97.7] b=0 c=143 | — | 4.66e-42 | se_dispara | **responde** |
| P3_dead_habla | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 9.3% [5.6%, 15.1%] | +8.7 pp [+4.2, +14.4] b=0 c=13 | — | 0.00269 | se_dispara | **responde** |
| P3_missing_actua | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 4.7% [2.3%, 9.3%] | 100.0% [97.5%, 100.0%] | +95.3 pp [+90.1, +97.7] b=0 c=143 | — | 4.66e-42 | se_dispara | **responde** |
| P3_missing_actua | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 11.3% [7.2%, 17.4%] | +10.7 pp [+5.8, +16.7] b=0 c=16 | — | 0.000397 | se_dispara | **responde** |
| P3_missing_habla | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 4.7% [2.3%, 9.3%] | 100.0% [97.5%, 100.0%] | +95.3 pp [+90.1, +97.7] b=0 c=143 | — | 4.66e-42 | se_dispara | **responde** |
| P3_missing_habla | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 12.0% [7.7%, 18.2%] | +11.3 pp [+6.3, +17.5] b=0 c=17 | — | 0.000214 | se_dispara | **responde** |
| P4_2p | `cl2_pc_hp_contradice_narracion` | ● se_dispara | 135 | 0.0% [0.0%, 2.8%] | 0.0% [0.0%, 2.8%] | +0.0 pp [-2.8, +2.8] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P4_3p | `cl2_pc_hp_contradice_narracion` | ● se_dispara | 135 | 0.0% [0.0%, 2.8%] | 100.0% [97.2%, 100.0%] | +100.0 pp [+96.1, +100.0] b=0 c=135 | — | 9.64e-40 | se_dispara | **responde** |
| P5 | `cr2_entidad_grafo_densidad` | ▼ baja | 150 | 0.276 | 0.200 | -0.029 [-0.067, -0.002]  | -0.39 / -0.10 | 5.41e-07 | baja | **responde** |
| P5 | `cr2_n_nombres_no_reconocidos` | ▲ sube | 150 | 0.000 | 2.000 | 2.000 [2.000, 2.000]  | +1.00 / +0.97 | 4.9e-44 | sube | **responde** |
| P5 | `cr2_nombres_no_reconocidos` | ● se_dispara | 150 | 6.0% [3.2%, 11.0%] | 100.0% [97.5%, 100.0%] | +94.0 pp [+88.4, +96.8] b=0 c=141 | — | 1.58e-41 | se_dispara | **responde** |
| P6 | `grammaticality_lt` | ▼ baja | 50 | 1.000 | 0.923 | -0.076 [-0.087, -0.061]  | -1.00 / -1.00 | 3.38e-14 | baja | **responde** |
| P7 | `qn1_ngram_repeticion` | ▲ sube | 150 | 0.016 | 0.345 | 0.328 [0.320, 0.334]  | +1.00 / +1.00 | 4.9e-44 | sube | **responde** |
| P7 | `qn1_ttr` | ▼ baja | 150 | 0.730 | 0.486 | -0.245 [-0.252, -0.241]  | -1.00 / -1.00 | 4.9e-44 | baja | **responde** |
| P8 | `cl2_lugar_jaccard_similarity` | ▼ baja | 150 | 0.176 | 0.115 | -0.057 [-0.062, -0.051]  | -0.89 / -0.89 | 1.56e-31 | baja | **responde** |
| P8 | `cr2_entidad_grafo_densidad` | ▼ baja | 150 | 0.276 | 0.167 | 0.000 [-0.070, 0.000]  | -0.12 / -0.11 | 1 | sin_cambio | **no responde** |
| P8 | `cr2_n_nombres_no_reconocidos` | ▲ sube | 150 | 0.000 | 0.000 | 0.000 [0.000, 0.000]  | +0.23 / +0.22 | 4.96e-06 | sube | **responde** |
| P8 | `cr2_nombres_no_reconocidos` | ● se_dispara | 150 | 6.0% [3.2%, 11.0%] | 28.0% [21.4%, 35.7%] | +22.0 pp [+13.7, +30.2] b=6 c=39 | — | 8.13e-06 | se_dispara | **responde** |
| P8 | `grafo_lema_densidad` | ▼ baja | 150 | 0.000 | 0.000 | 0.000 [0.000, 0.000]  | -0.04 / -0.04 | 1 | sin_cambio | **no responde** |
| P9 | `ventana_bucles_ciclos` | ▲ sube | 60 | 0.000 | 0.000 | 0.000 [0.000, 0.000]  | +0.00 / +0.00 | 1 | sin_cambio | **no responde** |
| P9 | `ventana_bucles_visitas` | ▲ sube | 60 | 1.000 | 1.000 | 0.000 [0.000, 0.000]  | +0.03 / +0.01 | 1 | sin_cambio | **no responde** |
| P9 | `ventana_jaccard_medio` | ▼ baja | 60 | 0.168 | 0.153 | -0.015 [-0.023, -0.012]  | -0.73 / -0.60 | 9.37e-08 | baja | **responde** |

**Controles «sin cambio»** (G2): 160 conformes, 7 con cambio inesperado, 23 no aplica.

| perturbación | instrumento | esperado | n | antes | después | Δ [IC95] | δ | p Holm | observado | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|
| P11a_inyeccion | `cl2_lugar_jaccard_similarity` | = sin_cambio | 150 | 0.176 | 0.167 | -0.009 [-0.010, -0.009]  | -1.00 / -0.20 | 2.34e-43 | baja | **cambio inesperado** |
| P11a_inyeccion | `cr2_entidad_grafo_densidad` | = sin_cambio | 150 | 0.276 | 0.178 | -0.072 [-0.100, -0.067]  | -0.80 / -0.19 | 2.47e-34 | baja | **cambio inesperado** |
| P11a_inyeccion | `cr2_nombres_no_reconocidos` | = sin_cambio | 150 | 6.0% [3.2%, 11.0%] | 100.0% [97.5%, 100.0%] | +94.0 pp [+88.4, +96.8] b=0 c=141 | — | 1.18e-40 | se_dispara | **cambio inesperado** |
| P11a_inyeccion | `grammaticality_lt` | = sin_cambio | 50 | 1.000 | 0.984 | -0.016 [-0.017, -0.015]  | -1.00 / -1.00 | 2.86e-13 | baja | **cambio inesperado** |
| P11a_inyeccion | `qn1_legibilidad_fh` | = sin_cambio | 150 | 59.240 | 61.135 | 1.625 [1.430, 1.885]  | +0.67 / +0.14 | 5.53e-15 | sube | **cambio inesperado** |
| P11a_inyeccion | `qn1_ngram_repeticion` | = sin_cambio | 150 | 0.016 | 0.015 | -0.001 [-0.001, -0.001]  | -0.73 / -0.05 | 2.51e-31 | baja | **cambio inesperado** |
| P11a_inyeccion | `qn1_ttr` | = sin_cambio | 150 | 0.730 | 0.748 | 0.017 [0.017, 0.018]  | +1.00 / +0.22 | 2.34e-43 | sube | **cambio inesperado** |

## 4b. Detalle por brazo — G1 (multiagente)

Comparaciones **confirmatorias** (dirección pre-especificada). `Antes/Después`: tasa de marca con IC de Wilson (booleanos) o mediana (numéricos); `Δ`: diferencia pareada con IC (Newcombe / bootstrap); `δ`: delta de Cliff pareado / de dos muestras; `p Holm`: p ajustado.

| perturbación | instrumento | esperado | n | antes | después | Δ [IC95] | δ | p Holm | observado | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|
| P10 | `cr1_veredicto_contradice_narracion` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P12 | `grammaticality_lt` | ▼ baja | 50 | 0.988 | 0.988 | 0.000 [0.000, 0.000]  | +0.18 / +0.05 | 0.0625 | sin_cambio | **no responde** |
| P12 | `qn1_ttr` | ▲ sube | 150 | 0.688 | 0.694 | 0.005 [0.005, 0.005]  | +1.00 / +0.10 | 4.9e-44 | sube | **responde** |
| P1_accion | `qn2_pj_accion_revisar` | ● se_dispara | 1 | 0.0% [0.0%, 79.3%] | 0.0% [0.0%, 79.3%] | +0.0 pp [-79.3, +79.3] b=0 c=0 | — | 1 | — | **no aplica** |
| P1_accion_sin_tirada | `qn2_pj_accion_revisar` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P1_decision | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P1_emocion | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P1_pensamiento | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P2_accion | `qn2_pj_accion_revisar` | ● se_dispara | 1 | 0.0% [0.0%, 79.3%] | 100.0% [20.7%, 100.0%] | +100.0 pp [-12.2, +100.0] b=0 c=1 | — | 1 | — | **no aplica** |
| P2_accion_sin_tirada | `qn2_pj_accion_revisar` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P2_decision | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P2_emocion | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P2_pensamiento | `qn2_pj_piensa_narrado` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P3_dead_actua | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 14.0% [9.3%, 20.5%] | 100.0% [97.5%, 100.0%] | +86.0 pp [+79.1, +90.7] b=0 c=129 | — | 7.05e-38 | se_dispara | **responde** |
| P3_dead_actua | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 2.7% [1.0%, 6.7%] | +2.0 pp [-1.1, +5.9] b=0 c=3 | — | 1 | sin_cambio | **no responde** |
| P3_dead_habla | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 14.0% [9.3%, 20.5%] | 100.0% [97.5%, 100.0%] | +86.0 pp [+79.1, +90.7] b=0 c=129 | — | 7.05e-38 | se_dispara | **responde** |
| P3_dead_habla | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 1.3% [0.4%, 4.7%] | +0.7 pp [-2.2, +3.9] b=0 c=1 | — | 1 | sin_cambio | **no responde** |
| P3_missing_actua | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 14.0% [9.3%, 20.5%] | 100.0% [97.5%, 100.0%] | +86.0 pp [+79.1, +90.7] b=0 c=129 | — | 7.05e-38 | se_dispara | **responde** |
| P3_missing_actua | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 2.7% [1.0%, 6.7%] | +2.0 pp [-1.1, +5.9] b=0 c=3 | — | 1 | sin_cambio | **no responde** |
| P3_missing_habla | `cl2_pnj_inactivo_actua` | ● se_dispara | 150 | 14.0% [9.3%, 20.5%] | 100.0% [97.5%, 100.0%] | +86.0 pp [+79.1, +90.7] b=0 c=129 | — | 7.05e-38 | se_dispara | **responde** |
| P3_missing_habla | `cl2_pnj_inactivo_refinado` | ● se_dispara | 150 | 0.7% [0.1%, 3.7%] | 2.0% [0.7%, 5.7%] | +1.3 pp [-1.6, +4.9] b=0 c=2 | — | 1 | sin_cambio | **no responde** |
| P4_2p | `cl2_pc_hp_contradice_narracion` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P4_3p | `cl2_pc_hp_contradice_narracion` | ● se_dispara | 150 | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | +100.0 pp [+96.5, +100.0] b=0 c=150 | — | 4.9e-44 | se_dispara | **responde** |
| P5 | `cr2_entidad_grafo_densidad` | ▼ baja | 150 | 0.141 | 0.132 | -0.019 [-0.024, -0.012]  | -0.51 / -0.08 | 5.98e-10 | baja | **responde** |
| P5 | `cr2_n_nombres_no_reconocidos` | ▲ sube | 150 | 2.000 | 4.000 | 2.000 [2.000, 2.000]  | +1.00 / +0.95 | 4.9e-44 | sube | **responde** |
| P5 | `cr2_nombres_no_reconocidos` | ● se_dispara | 150 | 100.0% [97.5%, 100.0%] | 100.0% [97.5%, 100.0%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P6 | `grammaticality_lt` | ▼ baja | 50 | 0.988 | 0.944 | -0.045 [-0.050, -0.037]  | -1.00 / -1.00 | 3.38e-14 | baja | **responde** |
| P7 | `qn1_ngram_repeticion` | ▲ sube | 150 | 0.025 | 0.291 | 0.261 [0.254, 0.269]  | +1.00 / +1.00 | 4.9e-44 | sube | **responde** |
| P7 | `qn1_ttr` | ▼ baja | 150 | 0.688 | 0.504 | -0.189 [-0.195, -0.184]  | -1.00 / -1.00 | 4.9e-44 | baja | **responde** |
| P8 | `cl2_lugar_jaccard_similarity` | ▼ baja | 150 | 0.215 | 0.141 | -0.074 [-0.082, -0.064]  | -0.96 / -0.96 | 1.97e-38 | baja | **responde** |
| P8 | `cr2_entidad_grafo_densidad` | ▼ baja | 150 | 0.141 | 0.138 | -0.031 [-0.054, 0.000]  | -0.19 / -0.13 | 0.347 | sin_cambio | **no responde** |
| P8 | `cr2_n_nombres_no_reconocidos` | ▲ sube | 150 | 2.000 | 3.000 | 1.000 [1.000, 1.000]  | +0.55 / +0.54 | 1.04e-16 | sube | **responde** |
| P8 | `cr2_nombres_no_reconocidos` | ● se_dispara | 150 | 100.0% [97.5%, 100.0%] | 100.0% [97.5%, 100.0%] | +0.0 pp [-2.5, +2.5] b=0 c=0 | — | 1 | sin_cambio | **no responde** |
| P8 | `grafo_lema_densidad` | ▼ baja | 150 | 0.000 | 0.000 | 0.000 [0.000, 0.000]  | -0.06 / -0.06 | 1 | sin_cambio | **no responde** |
| P9 | `ventana_bucles_ciclos` | ▲ sube | 60 | 0.000 | 0.000 | 0.000 [0.000, 0.000]  | +0.07 / +0.07 | 1 | sin_cambio | **no responde** |
| P9 | `ventana_bucles_visitas` | ▲ sube | 60 | 1.000 | 1.000 | 0.000 [0.000, 0.000]  | +0.07 / +0.01 | 1 | sin_cambio | **no responde** |
| P9 | `ventana_jaccard_medio` | ▼ baja | 60 | 0.209 | 0.194 | -0.015 [-0.018, -0.011]  | -0.87 / -0.47 | 1.64e-11 | baja | **responde** |

**Controles «sin cambio»** (G1): 160 conformes, 7 con cambio inesperado, 23 no aplica.

| perturbación | instrumento | esperado | n | antes | después | Δ [IC95] | δ | p Holm | observado | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|
| P11b_eliminacion | `cl2_lugar_jaccard_similarity` | = sin_cambio | 150 | 0.215 | 0.180 | -0.034 [-0.035, -0.032]  | -1.00 / -0.56 | 2.34e-43 | baja | **cambio inesperado** |
| P11b_eliminacion | `cr2_entidad_grafo_densidad` | = sin_cambio | 150 | 0.141 | 0.194 | 0.037 [0.031, 0.049]  | +0.70 / +0.16 | 1.2e-22 | sube | **cambio inesperado** |
| P11b_eliminacion | `cr2_nombres_no_reconocidos` | = sin_cambio | 150 | 100.0% [97.5%, 100.0%] | 9.3% [5.6%, 15.1%] | -90.7 pp [-94.4, -84.4] b=136 c=0 | — | 3.81e-39 | baja | **cambio inesperado** |
| P11b_eliminacion | `grammaticality_lt` | = sin_cambio | 50 | 0.988 | 1.000 | 0.011 [0.010, 0.012]  | +1.00 / +0.98 | 2.91e-13 | sube | **cambio inesperado** |
| P11b_eliminacion | `qn1_ngram_repeticion` | = sin_cambio | 150 | 0.025 | 0.026 | 0.001 [0.001, 0.001]  | +0.41 / -0.02 | 3.22e-05 | sube | **cambio inesperado** |
| P11b_eliminacion | `qn1_ttr` | = sin_cambio | 150 | 0.688 | 0.680 | -0.014 [-0.016, -0.013]  | -0.63 / -0.18 | 3.39e-13 | baja | **cambio inesperado** |
| P8 | `cl2_pnj_inactivo_actua` | = sin_cambio | 150 | 14.0% [9.3%, 20.5%] | 0.0% [0.0%, 2.5%] | -14.0 pp [-20.5, -8.7] b=21 c=0 | — | 0.000154 | baja | **cambio inesperado** |

## 5. Limitaciones y decisiones de diseño

- Un defecto sintético insertado en una oración no es un defecto natural del DM: mide la capacidad de detección del instrumento ante ese patrón, no su tasa de falsos negativos en la naturaleza.
- P1/P2 (usurpación) se inserta al inicio de un párrafo elegido al azar, con una plantilla por categoría; el léxico de las plantillas está fijado (repertorio de 2–5 oraciones por categoría): un detector nuevo puede reaccionar al repertorio y no a la categoría.
- El estado de PNJ es histórico (reconstruido desde `state_deltas`); el HP del PJ es el ACTUAL (no hay historia de HP en la base) y las tiradas se recalculan con `jugador/dados.py` de hoy. En P3/P4/P10 el contexto se manipula explícitamente (estado del PNJ, tirada) porque en los datos reales casi no hay PNJ muertos activos, muertes de PJ ni pifias narradas como éxito: son controles positivos casi tautológicos para regex (validan el arnés y la ceguera de 2.ª persona, no la calidad del DM).
- P6 baraja solo palabras en minúscula (mayúsculas, cifras y puntuación quedan fijas) para no introducir artefactos de capitalización en el detector de nombres; por construcción TTR, Fernández-Huerta y Jaccard son invariantes (sirven de control de exactitud).
- P8 usa como donante un turno aleatorio (2–1400) de OTRO par del mismo brazo de la muestra (formato G1 con G1, G2 con G2).
- P9: una permutación aleatoria (≠ identidad) por ventana de 8 turnos, no todas las permutaciones (Barzilay & Lapata usan varias). `ventana_consistencia_V` es invariante al orden por construcción (control exacto).
- P11a inyecta «narrativa/mecanica» + una línea «Habilidad: Éxito|Fallo (N vs CD M).»; P11b usa `prosa()` de `validacion_generar.py`. Cualquier cambio en un instrumento que debería mirar solo el contenido es artefacto de formato (p. ej. `cr2_nombres_no_reconocidos` marca «Éxito»/«Percepción» de la línea mecánica).
- `jericho_qa_recall` y `relojes_no_reconocidos` (reporte_validacion.py) dependen de deltas y relojes de la base, no de texto arbitrario: no están en este arnés v1. `cl1_campo_inmutable_alterado` depende de los deltas del extractor. `coherencia_entidad_C`, `consistencia_atributos_V` y `detector_bucles` se evalúan por ventana de 8 turnos (son agregados de campaña: la ventana es una adaptación).
- `entity_coreference_rate` por turno usa como «ya conocidas» las entidades mencionadas en turnos previos (recomputadas desde el texto) con la lista de entidades del turno; el reporte agrega por campaña con la lista final.
- Tamaños de efecto y umbrales (|δ| ≥ 0,147, α = 0,05, n mínimo 10) son convenciones publicadas fijadas antes de ver resultados; con n = 150 y muchas comparaciones el control de multiplicidad (Holm) es por brazo y familia, no global.
- Los detectores de 2.ª persona nuevos se enchufan con `instrumentos_texto.registrar_instrumento(...)` y `perturbaciones.registrar_esperado(...)` ANTES de correrlos; el arnés vuelve a correrse con este mismo script.
