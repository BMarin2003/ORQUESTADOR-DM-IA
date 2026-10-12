# Sensibilidad A4b/c — evaluación: respuesta a la acción (CR-2a) y anclaje al escenario (CR-2b)

- Generado: 2026-09-20 23:44 · commit `30b998f` · Python 3.14.6 · spacy-3.8.16|es_core_news_sm-3.8.0
- Modo: **evaluación** · semilla de muestreo **20260920** · pares: 09 (v1), 11 (v1), 13 (v1), 14 (v1), 16 (v1), 20 (v2), 21 (v2), 23 (v2), 24 (v2), 25 (v2)
- Muestra: 150 turnos por brazo + 60 ventanas de 8 turnos por brazo. Solo SELECT, sin LLM.
- **Matriz pre-especificada `a4bc-2` (2026-09-20): SHA-256 `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744`** (verificado por `test_matriz_a4bc_v2.py`; deriva de a4bc-1 `67e6133a51c4c23001038a19bb9894e2afa7b99b5dfef91955e0ee789ec0c54e` y solo cambió 5 magnitudes mínimas `min` tras la corrida de desarrollo, registrada 2026-09-20 23:39 antes de esta evaluación: doc de diseño §9.1; ninguna dirección esperada se modificó tras ver resultados; evaluación ejecutada una sola vez a las 23:42-23:44).
- Tiempos: carga 7s; perturbaciones + instrumentos 60s; distribución 94s; total 163s

## 0. Cómo leer

Criterio de aprobación por celda (fijado antes; ver `docs/research/a4bc_diseno_instrumentos.md` §4): veredicto del arnés «responde» (Holm p<0,05 y |delta de Cliff pareado| ≥ 0,147 en la dirección esperada; para «=» ninguno de los dos) **y**, si hay dirección, |mediana de la diferencia pareada| ≥ `min`; celdas «exacto»: diferencia 0 en el 100 % de los pares. Glifos: ▼ baja, ▲ sube, = sin cambio; ✓ aprobada, ✗ falla, · descriptiva (sin veredicto); entre paréntesis lo observado si no coincide; el número es la mediana de la diferencia pareada (después − antes).

## 1. Resumen esperado-vs-observado

### G2 (monolítico)

| perturbación | `cr2a_z` | `cr2a_crudo` | `cr2a_z_ventana8` | `cr2b_cos_turno` | `cr2b_cos_turno_sn` | `cr2b_cos_ventana8` | `cr2b_cos_ventana8_sn` |
|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | =✓ 0.000 | =✓ 0.000 |  | =✓ 0.000 | =✓ 0.000 |  |  |
| C2_minusculas | =✓ 0.000 | =✗(▼) 0.000 |  | =✓ 0.000 | =✗(▼) 0.000 |  |  |
| C3_sin_tildes | =✓ 0.000 | =✗(▲) 0.000 |  | =✗(▼) 0.000 | =✓ -0.000 |  |  |
| P11a_inyeccion | =✓ exacto 0.000 | =✓ exacto 0.000 |  | =✓ exacto 0.000 | =✓ exacto 0.000 |  |  |
| P5 | =✗(▼) -0.000 |  |  | ▼✓ -0.002 | =✗(▲) 0.004 |  |  |
| P6 | =✓ 0.000 | =✓ 0.000 |  | =✗(▼) -0.001 | =✗(▼) -0.002 |  |  |
| P8 | ▼✓ -2.616 | ▼✓ -0.097 |  | ▼✓ -0.006 | ▼✓ -0.004 |  |  |
| P9 |  |  | ▼✓ -1.583 |  |  | =✓ exacto 0.000 | =✓ exacto 0.000 |
| S1_sinonimos | ▼· 0.037 | ▼· 0.000 |  |  |  |  |  |
| W1_ventana_otro_par |  |  | ▼✓ -2.899 |  |  | ▼✓ -0.020 | ▼✓ -0.016 |
| X1_misma_campana_lejana | ▼✓ -2.620 | ▼✓ -0.095 |  | =✓ 0.000 | =✓ 0.002 |  |  |
| X2_misma_campana_cercana | ▼✓ -2.337 | ▼✓ -0.088 |  | =✓ -0.003 | =✓ -0.002 |  |  |

### G1 (multiagente)

| perturbación | `cr2a_z` | `cr2a_crudo` | `cr2a_z_ventana8` | `cr2b_cos_turno` | `cr2b_cos_turno_sn` | `cr2b_cos_ventana8` | `cr2b_cos_ventana8_sn` |
|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | =✓ 0.000 | =✓ 0.000 |  | =✓ 0.000 | =✓ 0.000 |  |  |
| C2_minusculas | =✓ 0.000 | =✗(▼) -0.001 |  | =✗(▼) 0.000 | =✗(▼) -0.000 |  |  |
| C3_sin_tildes | =✓ 0.000 | =✗(▲) 0.001 |  | =✗(▼) -0.000 | =✓ 0.000 |  |  |
| P11b_eliminacion | =✓ exacto 0.000 | =✓ exacto 0.000 |  | =✓ exacto 0.000 | =✓ exacto 0.000 |  |  |
| P5 | =✓ 0.000 |  |  | ▼✓ -0.010 | =✗(▲) 0.003 |  |  |
| P6 | =✗(▲) 0.008 | =✓ 0.000 |  | =✗(▼) -0.003 | =✗(▼) -0.002 |  |  |
| P8 | ▼✓ -2.608 | ▼✓ -0.101 |  | ▼✓ -0.068 | ▼✗(=) -0.005 |  |  |
| P9 |  |  | ▼✓ -1.748 |  |  | =✓ exacto 0.000 | =✓ exacto 0.000 |
| S1_sinonimos | ▼· 0.001 | ▼· 0.000 |  |  |  |  |  |
| W1_ventana_otro_par |  |  | ▼✓ -2.762 |  |  | ▼✓ -0.076 | ▼✓ -0.015 |
| X1_misma_campana_lejana | ▼✓ -2.352 | ▼✓ -0.085 |  | =✓ -0.000 | =✓ 0.001 |  |  |
| X2_misma_campana_cercana | ▼✓ -2.397 | ▼✓ -0.089 |  | =✓ 0.002 | =✓ 0.002 |  |  |

## 2. Recuento y hallazgos

| brazo | instrumento | aprobadas | fallan | no aplica |
|---|---|---|---|---|
| G2 | `cr2a_z` | 8 | 1 | 0 |
| G2 | `cr2a_crudo` | 6 | 2 | 0 |
| G2 | `cr2a_z_ventana8` | 2 | 0 | 0 |
| G2 | `cr2b_cos_turno` | 7 | 2 | 0 |
| G2 | `cr2b_cos_turno_sn` | 6 | 3 | 0 |
| G2 | `cr2b_cos_ventana8` | 2 | 0 | 0 |
| G2 | `cr2b_cos_ventana8_sn` | 2 | 0 | 0 |
| G1 | `cr2a_z` | 8 | 1 | 0 |
| G1 | `cr2a_crudo` | 6 | 2 | 0 |
| G1 | `cr2a_z_ventana8` | 2 | 0 | 0 |
| G1 | `cr2b_cos_turno` | 6 | 3 | 0 |
| G1 | `cr2b_cos_turno_sn` | 5 | 4 | 0 |
| G1 | `cr2b_cos_ventana8` | 2 | 0 | 0 |
| G1 | `cr2b_cos_ventana8_sn` | 2 | 0 | 0 |

**Celdas que NO cumplen (hallazgos; no se cambia la expectativa):**

- **G1** · `cr2a_crudo` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.136 → después 0.135, Δ -0.001, δ -0.69, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.75 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.086 → después 0.064, Δ 0.000, δ -0.29, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno_sn` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.032 → después 0.031, Δ -0.000, δ -0.49, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.29 % = despreciable (< 2 %).
- **G1** · `cr2a_crudo` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.136 → después 0.137, Δ 0.001, δ +0.39, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.37 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.086 → después 0.085, Δ -0.000, δ -0.43, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.05 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno_sn` ante **P5**: esperado sin_cambio, mediana antes 0.032 → después 0.035, Δ 0.003, δ +0.28, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 8.99 % = NO despreciable.
- **G1** · `cr2a_z` ante **P6**: esperado sin_cambio, mediana antes 2.591 → después 2.579, Δ 0.008, δ +0.33, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.33 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno` ante **P6**: esperado sin_cambio, mediana antes 0.086 → después 0.081, Δ -0.003, δ -0.80, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -3.68 % = NO despreciable.
- **G1** · `cr2b_cos_turno_sn` ante **P6**: esperado sin_cambio, mediana antes 0.032 → después 0.028, Δ -0.002, δ -0.61, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -7.42 % = NO despreciable.
- **G1** · `cr2b_cos_turno_sn` ante **P8**: esperado baja (min 0.001), mediana antes 0.032 → después 0.027, Δ -0.005, δ -0.13, observado sin_cambio, veredicto arnés «no responde».
- **G2** · `cr2a_crudo` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.132 → después 0.133, Δ 0.000, δ -0.37, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno_sn` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.026 → después 0.025, Δ 0.000, δ -0.21, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2a_crudo` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.132 → después 0.129, Δ 0.000, δ +0.25, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.023 → después 0.022, Δ 0.000, δ -0.35, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2a_z` ante **P5**: esperado sin_cambio, mediana antes 2.671 → después 2.611, Δ -0.000, δ -0.42, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.00 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno_sn` ante **P5**: esperado sin_cambio, mediana antes 0.026 → después 0.029, Δ 0.004, δ +0.39, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 16.29 % = NO despreciable.
- **G2** · `cr2b_cos_turno` ante **P6**: esperado sin_cambio, mediana antes 0.023 → después 0.020, Δ -0.001, δ -0.75, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -5.98 % = NO despreciable.
- **G2** · `cr2b_cos_turno_sn` ante **P6**: esperado sin_cambio, mediana antes 0.026 → después 0.022, Δ -0.002, δ -0.66, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -6.48 % = NO despreciable.
**Lectura post hoc de los controles «=» que fallan por la regla del arnés** (no cambia el criterio ni los conteos; la regla cuenta signos, no magnitudes): de 17 controles «=» con «cambio inesperado», 11 tienen |Δ mediana| < 2 % de la mediana previa (despreciables en magnitud) y 6 no.

## 3. Detalle por brazo

### G2

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P5 | `cr2b_cos_turno` | ▼ baja ≥0.0005 | 150 | 0.023 | 0.021 | -0.002 [-0.003, -0.001] | -0.41 | 3.13e-06 | baja | responde | **aprobada** |
| P8 | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.132 | 0.000 | -0.097 [-0.118, -0.089] | -0.87 | 2.8e-30 | baja | responde | **aprobada** |
| P8 | `cr2a_z` | ▼ baja ≥1 | 150 | 2.671 | -0.341 | -2.616 [-3.067, -2.259] | -0.84 | 2.91e-27 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno` | ▼ baja ≥0.003 | 150 | 0.023 | 0.016 | -0.006 [-0.010, -0.003] | -0.29 | 0.00082 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno_sn` | ▼ baja ≥0.001 | 150 | 0.026 | 0.020 | -0.004 [-0.009, -0.001] | -0.20 | 0.0176 | baja | responde | **aprobada** |
| P9 | `cr2a_z_ventana8` | ▼ baja ≥0.5 | 60 | 2.663 | 0.978 | -1.583 [-1.923, -1.175] | -0.93 | 1.91e-14 | baja | responde | **aprobada** |
| S1_sinonimos | `cr2a_crudo` | ▼ baja ≥0.005 | 150 | 0.132 | 0.126 | 0.000 [0.000, 0.000] | -0.12 | 0.0175 | sin_cambio | — | **descriptiva** |
| S1_sinonimos | `cr2a_z` | ▼ baja ≥0.1 | 150 | 2.671 | 2.670 | 0.037 [0.011, 0.069] | +0.45 | 4.25e-10 | sube | — | **descriptiva** |
| W1_ventana_otro_par | `cr2a_z_ventana8` | ▼ baja ≥1 | 60 | 2.663 | -0.182 | -2.899 [-3.060, -2.494] | -1.00 | 1.21e-17 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8` | ▼ baja ≥0.007 | 60 | 0.055 | 0.036 | -0.020 [-0.048, -0.013] | -0.60 | 1.27e-05 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8_sn` | ▼ baja ≥0.0025 | 60 | 0.059 | 0.046 | -0.016 [-0.020, -0.009] | -0.57 | 3.64e-05 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.132 | 0.037 | -0.095 [-0.113, -0.080] | -0.77 | 1.12e-22 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.671 | -0.060 | -2.620 [-2.949, -2.238] | -0.88 | 1.61e-30 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_crudo` | ▼ baja ≥0.035 | 150 | 0.132 | 0.039 | -0.088 [-0.101, -0.078] | -0.76 | 1.03e-21 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.671 | 0.181 | -2.337 [-2.821, -1.901] | -0.81 | 2.79e-25 | baja | responde | **aprobada** |

**Controles «sin cambio» (G2):**

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.132 | 0.000 [0.000, 0.000] | -0.03 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2a_z` | = sin_cambio | 150 | 2.671 | 2.671 | 0.000 [0.000, 0.000] | +0.03 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.023 | 0.000 [0.000, 0.000] | +0.04 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.026 | 0.000 [0.000, 0.000] | -0.03 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.133 | 0.000 [0.000, 0.000] | -0.37 | 2.13e-11 | baja | cambio inesperado | **falla** |
| C2_minusculas | `cr2a_z` | = sin_cambio | 150 | 2.671 | 2.752 | 0.000 [0.000, 0.000] | -0.13 | 0.384 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.023 | 0.000 [0.000, 0.000] | +0.05 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.025 | 0.000 [0.000, 0.000] | -0.21 | 0.00365 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.129 | 0.000 [0.000, 0.000] | +0.25 | 0.00391 | sube | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_z` | = sin_cambio | 150 | 2.671 | 2.501 | 0.000 [0.000, 0.000] | +0.20 | 0.0847 | sin_cambio | responde | **aprobada** |
| C3_sin_tildes | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.022 | 0.000 [-0.000, 0.000] | -0.35 | 7.01e-07 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.024 | -0.000 [-0.001, 0.000] | -0.19 | 0.27 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.132 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2a_z` | = sin_cambio | 150 | 2.671 | 2.671 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.023 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.026 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P5 | `cr2a_z` | = sin_cambio | 150 | 2.671 | 2.611 | -0.000 [-0.013, -0.000] | -0.42 | 3.64e-07 | baja | cambio inesperado | **falla** |
| P5 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.029 | 0.004 [0.003, 0.005] | +0.39 | 3.43e-05 | sube | cambio inesperado | **falla** |
| P6 | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.124 | 0.000 [0.000, 0.000] | +0.04 | 1 | sin_cambio | responde | **aprobada** |
| P6 | `cr2a_z` | = sin_cambio | 150 | 2.671 | 2.546 | 0.000 [0.000, 0.010] | +0.21 | 0.0865 | sin_cambio | responde | **aprobada** |
| P6 | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.020 | -0.001 [-0.002, -0.001] | -0.75 | 5.9e-26 | baja | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.022 | -0.002 [-0.002, -0.001] | -0.66 | 3.24e-17 | baja | cambio inesperado | **falla** |
| P9 | `cr2b_cos_ventana8` | = sin_cambio | 60 | 0.055 | 0.055 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P9 | `cr2b_cos_ventana8_sn` | = sin_cambio | 60 | 0.059 | 0.059 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.023 | 0.000 [-0.003, 0.006] | +0.01 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.027 | 0.002 [-0.001, 0.005] | +0.11 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.023 | 0.021 | -0.003 [-0.007, 0.004] | -0.07 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.026 | 0.023 | -0.002 [-0.005, 0.002] | -0.09 | 1 | sin_cambio | responde | **aprobada** |

### G1

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P5 | `cr2b_cos_turno` | ▼ baja ≥0.0005 | 150 | 0.086 | 0.077 | -0.010 [-0.011, -0.008] | -0.77 | 1.38e-22 | baja | responde | **aprobada** |
| P8 | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.136 | 0.032 | -0.101 [-0.111, -0.088] | -0.91 | 5.22e-34 | baja | responde | **aprobada** |
| P8 | `cr2a_z` | ▼ baja ≥1 | 150 | 2.591 | -0.164 | -2.608 [-2.932, -2.252] | -0.85 | 2.49e-28 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno` | ▼ baja ≥0.003 | 150 | 0.086 | 0.020 | -0.068 [-0.078, -0.055] | -0.68 | 2.68e-17 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno_sn` | ▼ baja ≥0.001 | 150 | 0.032 | 0.027 | -0.005 [-0.009, 0.001] | -0.13 | 0.121 | sin_cambio | no responde | **falla** |
| P9 | `cr2a_z_ventana8` | ▼ baja ≥0.5 | 60 | 2.636 | 0.955 | -1.748 [-1.885, -1.373] | -1.00 | 1.04e-17 | baja | responde | **aprobada** |
| S1_sinonimos | `cr2a_crudo` | ▼ baja ≥0.005 | 150 | 0.136 | 0.131 | 0.000 [0.000, 0.000] | -0.32 | 1.61e-08 | baja | — | **descriptiva** |
| S1_sinonimos | `cr2a_z` | ▼ baja ≥0.1 | 150 | 2.591 | 2.542 | 0.001 [0.000, 0.014] | +0.25 | 0.00108 | sube | — | **descriptiva** |
| W1_ventana_otro_par | `cr2a_z_ventana8` | ▼ baja ≥1 | 60 | 2.636 | -0.125 | -2.762 [-3.000, -2.543] | -1.00 | 1.04e-17 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8` | ▼ baja ≥0.007 | 60 | 0.122 | 0.042 | -0.076 [-0.098, -0.058] | -0.70 | 9.26e-08 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8_sn` | ▼ baja ≥0.0025 | 60 | 0.072 | 0.056 | -0.015 [-0.024, -0.005] | -0.37 | 0.0124 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.136 | 0.037 | -0.085 [-0.101, -0.075] | -0.86 | 3.95e-29 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.591 | -0.203 | -2.352 [-2.753, -2.040] | -0.81 | 2.79e-25 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_crudo` | ▼ baja ≥0.035 | 150 | 0.136 | 0.040 | -0.089 [-0.102, -0.070] | -0.78 | 1.34e-23 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.591 | 0.124 | -2.397 [-2.844, -1.813] | -0.77 | 1.38e-22 | baja | responde | **aprobada** |

**Controles «sin cambio» (G1):**

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | `cr2a_crudo` | = sin_cambio | 150 | 0.136 | 0.136 | 0.000 [0.000, 0.000] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2a_z` | = sin_cambio | 150 | 2.591 | 2.616 | 0.000 [0.000, 0.000] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.086 | 0.000 [0.000, 0.000] | -0.02 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.032 | 0.000 [0.000, 0.000] | -0.03 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2a_crudo` | = sin_cambio | 150 | 0.136 | 0.135 | -0.001 [-0.001, -0.001] | -0.69 | 2.04e-24 | baja | cambio inesperado | **falla** |
| C2_minusculas | `cr2a_z` | = sin_cambio | 150 | 2.591 | 2.629 | 0.000 [0.000, 0.000] | -0.08 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.064 | 0.000 [0.000, 0.000] | -0.29 | 2.26e-06 | baja | cambio inesperado | **falla** |
| C2_minusculas | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.031 | -0.000 [-0.000, 0.000] | -0.49 | 1.67e-16 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_crudo` | = sin_cambio | 150 | 0.136 | 0.137 | 0.001 [0.000, 0.001] | +0.39 | 4.12e-08 | sube | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_z` | = sin_cambio | 150 | 2.591 | 2.552 | 0.000 [0.000, 0.000] | +0.08 | 1 | sin_cambio | responde | **aprobada** |
| C3_sin_tildes | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.085 | -0.000 [-0.001, 0.000] | -0.43 | 4.43e-11 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.031 | 0.000 [-0.000, 0.000] | -0.12 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2a_crudo` | = sin_cambio | 150 | 0.136 | 0.136 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2a_z` | = sin_cambio | 150 | 2.591 | 2.591 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.086 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.032 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P5 | `cr2a_z` | = sin_cambio | 150 | 2.591 | 2.591 | 0.000 [-0.000, 0.000] | -0.11 | 1 | sin_cambio | responde | **aprobada** |
| P5 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.035 | 0.003 [0.002, 0.003] | +0.28 | 0.0152 | sube | cambio inesperado | **falla** |
| P6 | `cr2a_crudo` | = sin_cambio | 150 | 0.136 | 0.135 | 0.000 [0.000, 0.000] | +0.03 | 1 | sin_cambio | responde | **aprobada** |
| P6 | `cr2a_z` | = sin_cambio | 150 | 2.591 | 2.579 | 0.008 [0.000, 0.031] | +0.33 | 0.000343 | sube | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.081 | -0.003 [-0.004, -0.002] | -0.80 | 6.61e-27 | baja | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.028 | -0.002 [-0.003, -0.002] | -0.61 | 8.2e-14 | baja | cambio inesperado | **falla** |
| P9 | `cr2b_cos_ventana8` | = sin_cambio | 60 | 0.122 | 0.122 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P9 | `cr2b_cos_ventana8_sn` | = sin_cambio | 60 | 0.072 | 0.072 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.086 | -0.000 [-0.006, 0.005] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.031 | 0.001 [-0.004, 0.004] | +0.04 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.086 | 0.094 | 0.002 [-0.001, 0.006] | +0.05 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.032 | 0.032 | 0.002 [-0.002, 0.005] | +0.08 | 1 | sin_cambio | responde | **aprobada** |

## 4. Límite léxico (S1, descriptivo)

- G2 · `cr2a_crudo`: mediana antes 0.132 → después 0.126 (Δ mediana 0.000); cambió en el 35 % de los turnos; n=150.
- G2 · `cr2a_z`: mediana antes 2.671 → después 2.670 (Δ mediana 0.037); cambió en el 79 % de los turnos; n=150.
- G2: sustituciones por turno (diccionario mínimo): media 2.0, turnos sin ninguna 14 %.
- G1 · `cr2a_crudo`: mediana antes 0.136 → después 0.131 (Δ mediana 0.000); cambió en el 48 % de los turnos; n=150.
- G1 · `cr2a_z`: mediana antes 2.591 → después 2.542 (Δ mediana 0.001); cambió en el 82 % de los turnos; n=150.
- G1: sustituciones por turno (diccionario mínimo): media 2.1, turnos sin ninguna 13 %.

## 5. Distribución real: ventanas de 200 turnos (descriptivo, 42 campañas, sin veredicto)

Clases de acción en los 58800 turnos: mixta 57996 (98.63 %), accion 804 (1.37 %).

### G2: media por bloque de 200 turnos (media de las medias por campaña)

| métrica | 1-200 | 201-400 | 401-600 | 601-800 | 801-1000 | 1001-1200 | 1201-1400 | Δ último − primero |
|---|---|---|---|---|---|---|---|---|
| cr2a_z (media) | 2.81 | 2.83 | 2.80 | 2.90 | 2.87 | 2.73 | 2.74 | -0.07 |
| cr2a_crudo (Ochiai) | 0.12 | 0.13 | 0.13 | 0.13 | 0.13 | 0.13 | 0.13 | 0.00 |
| cos por turno | 0.06 | 0.04 | 0.04 | 0.03 | 0.03 | 0.03 | 0.04 | -0.02 |
| cos por turno sin nombres | 0.03 | 0.03 | 0.03 | 0.03 | 0.03 | 0.03 | 0.03 | -0.01 |
| cos ventana 8 | 0.10 | 0.08 | 0.07 | 0.06 | 0.06 | 0.06 | 0.07 | -0.03 |
| cos ventana 8 sin nombres | 0.07 | 0.06 | 0.06 | 0.06 | 0.06 | 0.06 | 0.06 | -0.01 |
| proxy: % turnos con nombre propio | 35.8 | 24.6 | 18.5 | 12.5 | 12.7 | 15.1 | 18.4 | -17.4 |
| identifica su escenario (ventana 8, argmax de 21) | 57.9 | 49.8 | 44.6 | 33.7 | 37.5 | 38.7 | 47.0 | -10.9 |

### G1: media por bloque de 200 turnos (media de las medias por campaña)

| métrica | 1-200 | 201-400 | 401-600 | 601-800 | 801-1000 | 1001-1200 | 1201-1400 | Δ último − primero |
|---|---|---|---|---|---|---|---|---|
| cr2a_z (media) | 2.87 | 2.66 | 2.57 | 2.58 | 2.66 | 2.61 | 2.68 | -0.19 |
| cr2a_crudo (Ochiai) | 0.14 | 0.14 | 0.14 | 0.14 | 0.14 | 0.14 | 0.14 | -0.00 |
| cos por turno | 0.11 | 0.10 | 0.09 | 0.08 | 0.08 | 0.08 | 0.07 | -0.04 |
| cos por turno sin nombres | 0.04 | 0.04 | 0.04 | 0.04 | 0.03 | 0.04 | 0.03 | -0.01 |
| cos ventana 8 | 0.15 | 0.14 | 0.13 | 0.11 | 0.11 | 0.11 | 0.10 | -0.04 |
| cos ventana 8 sin nombres | 0.08 | 0.08 | 0.08 | 0.07 | 0.07 | 0.07 | 0.07 | -0.02 |
| proxy: % turnos con nombre propio | 74.3 | 75.0 | 65.2 | 57.4 | 56.4 | 60.5 | 52.4 | -21.9 |
| identifica su escenario (ventana 8, argmax de 21) | 76.8 | 77.8 | 72.0 | 62.9 | 59.3 | 65.9 | 57.5 | -19.2 |

### Por campaña: ¿cae cada métrica del primer al último bloque, y cuánto acompaña al proxy de nombres?

| brazo | métrica | campañas donde cae (último < primero) | ρ de Spearman con el proxy (mediana entre campañas, 7 bloques) |
|---|---|---|---|
| G2 | cr2a_z (media) | 10/21 | -0.43 |
| G2 | cr2a_crudo (Ochiai) | 9/21 | -0.36 |
| G2 | cos por turno | 17/21 | 0.89 |
| G2 | cos por turno sin nombres | 15/21 | 0.57 |
| G2 | cos ventana 8 | 17/21 | 0.86 |
| G2 | cos ventana 8 sin nombres | 15/21 | 0.64 |
| G2 | identifica su escenario (ventana 8, argmax de 21) | 15/21 | 0.79 |
| G1 | cr2a_z (media) | 13/21 | -0.32 |
| G1 | cr2a_crudo (Ochiai) | 9/21 | -0.32 |
| G1 | cos por turno | 15/21 | 0.79 |
| G1 | cos por turno sin nombres | 15/21 | 0.54 |
| G1 | cos ventana 8 | 15/21 | 0.64 |
| G1 | cos ventana 8 sin nombres | 15/21 | 0.57 |
| G1 | identifica su escenario (ventana 8, argmax de 21) | 9/21 | 0.75 |

## 6. Lectura de la evaluación (redactada a mano sobre las tablas anteriores; no se regenera al volver a correr)

**Balance.** De 86 celdas: 64 aprobadas, 18 fallan, 4 descriptivas (S1). Ninguna expectativa se cambió.

**Lo que se comporta como se pre-especificó**
- **Respuesta a la acción (CR-2a) discrimina con claridad.** `cr2a_z` cae 2,3-2,6 unidades ante sustitución por la respuesta de otro turno de la misma campaña (X1, X2), de otro par (P8) y ante desalineación de la ventana (P9: −1,6 G2 / −1,7 G1) o ventana de otro par (W1: −2,9 / −2,8), en los dos brazos, todas aprobadas; el `crudo` de Ochiai también (−0,09 a −0,10). Que X2 (misma escena, 3-10 turnos) caiga tanto como X1 indica que el z mide la acción concreta y no solo la escena en curso. En los datos reales el z mediano ronda 2,6-2,8.
- **Anclaje al escenario (CR-2b) sí distingue otro escenario, a diferencia del grafo por lema del baseline.** P8 por turno: −0,006 (G2) y −0,068 (G1) en coseno con nombres; W1 por ventana de 8: −0,020 (G2) y −0,076 (G1) con nombres, −0,016 / −0,015 sin nombres. Sustituir por un turno de la misma campaña (X1, X2) no cambia el coseno (control «=» aprobado). La ventana permutada (P9) deja el coseno idéntico (exacto, 100 % de los pares).
- **Controles exactos** (formato G1: P11a, P11b) y **reordenar oraciones** (C1): aprobados en los siete instrumentos.
- **P5 (nombres inventados):** baja el coseno con nombres en los dos brazos (−0,002 G2, −0,010 G1), como se derivó de la definición (parte (b) del constructo: «sin introducir cosas ajenas»).

**Hallazgos (celdas que NO cumplen)**
1. **17 controles «=» disparan «cambio inesperado» por la regla de signos del arnés; 11 con |Δ mediana| < 2 %** de la mediana previa (minúsculas, sin tildes: efecto despreciable en magnitud; lectura post hoc) **y 6 no despreciables**: `cr2b_cos_turno` (con y sin nombres) baja 4-7 % al barajar palabras (P6) en los dos brazos: el conteo de lemas depende del contexto del etiquetador de spaCy (riesgo anticipado en la matriz), no es una invariancia perfecta al orden. `cr2a_z` es más robusto a P6 (Δ mediana ≈ 0,00 en G2; +0,008 en G1 por la regla de signos).
2. **`cr2b_cos_turno_sn` sube ante P5 en ambos brazos (+9 % G1, +16 % G2)**, contra la expectativa «=»: la oración de relleno que usa P5 contiene lemas comunes que también aparecen en la referencia de escenario (p. ej. «nombre», «murmurar»), y al excluir los nombres propios ese aporte léxico pesa más. Error de la pre-especificación (subestimé el léxico común de la plantilla); se conserva y se reporta.
3. **`cr2b_cos_turno_sn` no responde a P8 en G1** (Δ −0,005, δ −0,13; en G2 sí): sin nombres, el coseno por turno es demasiado ruidoso en G1 para distinguir un turno de otro escenario; la ventana de 8 sí lo hace (W1 aprobada en ambos brazos).
4. **`cr2a_crudo`**: 2 «cambios» de signo con efecto < 1 % en cada brazo (C2, C3); no relevante en magnitud.

**Límite léxico (S1, descriptivo).** Con un diccionario mínimo (≈2 sustituciones por turno) la mediana del z casi no se mueve (Δ +0,04 G2 / +0,001 G1) aunque cambia en ~80 % de los turnos; el crudo cambia en 35-48 % de los turnos con mediana 0. El diccionario es demasiado pequeño para extrapolar el impacto real de la paráfrasis: el límite queda demostrado como existente, no cuantificado.

**Distribución real (paso 5, descriptivo, sin declarar ganadores).**
- **`cr2a_z` NO captura la deriva**: es casi plano entre bloques (G2 2,81 → 2,74; G1 2,87 → 2,68); cae en solo 10/21 (G2) y 13/21 (G1) campañas y su correlación con el proxy es negativa (mediana ρ −0,43 / −0,32). Es coherente: la deriva del escenario no implica que el DM deje de responder a la acción. Las respuestas siguen ancladas a lo que hace el jugador incluso cuando dejan de narrar el lore.
- **El anclaje CR-2b SÍ cae**: coseno por ventana de 8: G1 0,15 → 0,10, G2 0,10 → 0,07 (mínimo 0,06 en 601-1200); la identificación del escenario propio (argmax de 21, azar 4,8 %) baja de 76,8 % a 57,5 % (G1) y de 57,9 % a 47,0 % (G2, mínimo 33,7 % en 601-800). Cae del primer al último bloque en 15-17 de 21 campañas por turno/ventana (G2 17/21, G1 15/21).
- **Comparación con el proxy crudo de nombres** (% de turnos con algún nombre propio del escenario, con mi definición: nombre completo o palabra capitalizada ≥ 4 letras; da 74 % → 52 % en G1 y 36 % → 18 % en G2, menor que las cifras del encargo porque la definición difiere): el coseno con nombres acompaña al proxy (ρ mediana 0,86 G2 / 0,64 G1 por ventana), lo cual es en parte mecánico (los nombres son términos de idf alto). Sin nombres la señal queda más plana (G1 0,08 → 0,07; G2 0,07 → 0,06) y correlaciona menos (ρ 0,57-0,64): **la mayor parte de la caída del coseno la sostienen los nombres**; la caída de vocabulario común del escenario existe pero es pequeña.
- La deriva es heterogénea: en G2 el mínimo cae a mitad de la campaña (601-1000) y se recupera en el último bloque.
- Clases de acción: 98,6 % mixtas y 1,4 % solo prosa; no hay acciones solo con etiqueta ni solo con diálogo en los 58 800 turnos, así que esos tratamientos solo se ejercitaron en las pruebas unitarias.

**Límites de esta evaluación.** (i) Perturbaciones sintéticas. (ii) El coseno mide vocabulario compartido con la referencia inicial: no distingue deriva de evolución legítima del mundo (nuevos PNJ/lugares). (iii) Sin correlación con juicio humano. (iv) Un nulo de campaña completa confunde en parte continuidad de escena con especificidad de acción (X2 sugiere que el efecto es bajo). (v) La regla de signos del arnés etiqueta como cambio desplazamientos diminutos; la lectura post hoc de magnitud es orientativa (umbral 2 % elegido después de ver el desarrollo). (vi) Los verbos en 2.ª persona se lematizan mal en spaCy `sm`: el z lo sostienen sustantivos y adjetivos.
