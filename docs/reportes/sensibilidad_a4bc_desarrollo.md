# Sensibilidad A4b/c — CORRIDA DE DESARROLLO (calibración de min): respuesta a la acción (CR-2a) y anclaje al escenario (CR-2b)

- Generado: 2026-09-20 23:41 · commit `30b998f` · Python 3.14.6 · spacy-3.8.16|es_core_news_sm-3.8.0
- Modo: **desarrollo** · semilla de muestreo **20260919** · pares: 07 (v1), 08 (v1), 10 (v1), 15 (v1), 17 (v1), 18 (v2), 19 (v2), 22 (v2), 26 (v2), 27 (v2)
- Muestra: 150 turnos por brazo + 60 ventanas de 8 turnos por brazo. Solo SELECT, sin LLM.
- **Matriz pre-especificada `a4bc-2` (2026-09-20): SHA-256 `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744`** (verificado por `test_matriz_a4bc.py`; ninguna expectativa se modificó tras ver resultados).
- Tiempos: carga 7s; perturbaciones + instrumentos 60s; total 68s

## 0. Cómo leer

Criterio de aprobación por celda (fijado antes; ver `docs/research/a4bc_diseno_instrumentos.md` §4): veredicto del arnés «responde» (Holm p<0,05 y |delta de Cliff pareado| ≥ 0,147 en la dirección esperada; para «=» ninguno de los dos) **y**, si hay dirección, |mediana de la diferencia pareada| ≥ `min`; celdas «exacto»: diferencia 0 en el 100 % de los pares. Glifos: ▼ baja, ▲ sube, = sin cambio; ✓ aprobada, ✗ falla, · descriptiva (sin veredicto); entre paréntesis lo observado si no coincide; el número es la mediana de la diferencia pareada (después − antes).

## 1. Resumen esperado-vs-observado

### G2 (monolítico)

| perturbación | `cr2a_z` | `cr2a_crudo` | `cr2a_z_ventana8` | `cr2b_cos_turno` | `cr2b_cos_turno_sn` | `cr2b_cos_ventana8` | `cr2b_cos_ventana8_sn` |
|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | =✓ 0.000 | =✓ 0.000 |  | =✓ 0.000 | =✓ 0.000 |  |  |
| C2_minusculas | =✓ 0.000 | =✗(▼) 0.000 |  | =✓ 0.000 | =✗(▼) 0.000 |  |  |
| C3_sin_tildes | =✓ 0.000 | =✗(▲) 0.000 |  | =✗(▼) -0.000 | =✗(▼) -0.000 |  |  |
| P11a_inyeccion | =✓ exacto 0.000 | =✓ exacto 0.000 |  | =✓ exacto 0.000 | =✓ exacto 0.000 |  |  |
| P5 | =✗(▼) -0.002 |  |  | ▼✓ -0.002 | =✗(▲) 0.004 |  |  |
| P6 | =✗(▲) 0.000 | =✓ 0.000 |  | =✗(▼) -0.003 | =✗(▼) -0.002 |  |  |
| P8 | ▼✓ -2.731 | ▼✓ -0.104 |  | ▼✓ -0.006 | ▼✗(=) -0.002 |  |  |
| P9 |  |  | ▼✓ -1.742 |  |  | =✓ exacto 0.000 | =✓ exacto 0.000 |
| S1_sinonimos | ▼· 0.023 | ▼· 0.000 |  |  |  |  |  |
| W1_ventana_otro_par |  |  | ▼✓ -2.983 |  |  | ▼✓ -0.014 | ▼✗(=) -0.005 |
| X1_misma_campana_lejana | ▼✓ -2.926 | ▼✓ -0.102 |  | =✓ -0.002 | =✓ -0.002 |  |  |
| X2_misma_campana_cercana | ▼✓ -2.103 | ▼✓ -0.077 |  | =✓ 0.003 | =✓ 0.002 |  |  |

### G1 (multiagente)

| perturbación | `cr2a_z` | `cr2a_crudo` | `cr2a_z_ventana8` | `cr2b_cos_turno` | `cr2b_cos_turno_sn` | `cr2b_cos_ventana8` | `cr2b_cos_ventana8_sn` |
|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | =✓ 0.000 | =✓ 0.000 |  | =✓ 0.000 | =✓ 0.000 |  |  |
| C2_minusculas | =✓ 0.000 | =✗(▼) -0.001 |  | =✓ 0.000 | =✗(▼) -0.000 |  |  |
| C3_sin_tildes | =✗(▲) 0.000 | =✗(▲) 0.000 |  | =✗(▼) -0.000 | =✓ -0.000 |  |  |
| P11b_eliminacion | =✓ exacto 0.000 | =✓ exacto 0.000 |  | =✓ exacto 0.000 | =✓ exacto 0.000 |  |  |
| P5 | =✗(▼) -0.000 |  |  | ▼✓ -0.006 | =✓ 0.003 |  |  |
| P6 | =✗(▲) 0.013 | =✗(▲) 0.000 |  | =✗(▼) -0.003 | =✗(▼) -0.003 |  |  |
| P8 | ▼✓ -2.513 | ▼✓ -0.104 |  | ▼✓ -0.029 | ▼✗(=) -0.005 |  |  |
| P9 |  |  | ▼✓ -1.373 |  |  | =✓ exacto 0.000 | =✓ exacto 0.000 |
| S1_sinonimos | ▼· 0.000 | ▼· 0.000 |  |  |  |  |  |
| W1_ventana_otro_par |  |  | ▼✓ -2.651 |  |  | ▼✓ -0.068 | ▼✓ -0.010 |
| X1_misma_campana_lejana | ▼✓ -2.391 | ▼✓ -0.099 |  | =✓ -0.002 | =✓ -0.001 |  |  |
| X2_misma_campana_cercana | ▼✓ -2.089 | ▼✓ -0.081 |  | =✓ 0.000 | =✓ -0.000 |  |  |

## 2. Recuento y hallazgos

| brazo | instrumento | aprobadas | fallan | no aplica |
|---|---|---|---|---|
| G2 | `cr2a_z` | 7 | 2 | 0 |
| G2 | `cr2a_crudo` | 6 | 2 | 0 |
| G2 | `cr2a_z_ventana8` | 2 | 0 | 0 |
| G2 | `cr2b_cos_turno` | 7 | 2 | 0 |
| G2 | `cr2b_cos_turno_sn` | 4 | 5 | 0 |
| G2 | `cr2b_cos_ventana8` | 2 | 0 | 0 |
| G2 | `cr2b_cos_ventana8_sn` | 1 | 1 | 0 |
| G1 | `cr2a_z` | 6 | 3 | 0 |
| G1 | `cr2a_crudo` | 5 | 3 | 0 |
| G1 | `cr2a_z_ventana8` | 2 | 0 | 0 |
| G1 | `cr2b_cos_turno` | 7 | 2 | 0 |
| G1 | `cr2b_cos_turno_sn` | 6 | 3 | 0 |
| G1 | `cr2b_cos_ventana8` | 2 | 0 | 0 |
| G1 | `cr2b_cos_ventana8_sn` | 2 | 0 | 0 |

**Celdas que NO cumplen (hallazgos; no se cambia la expectativa):**

- **G1** · `cr2a_crudo` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.129 → después 0.130, Δ -0.001, δ -0.63, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.65 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno_sn` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.031 → después 0.030, Δ -0.000, δ -0.41, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.04 % = despreciable (< 2 %).
- **G1** · `cr2a_crudo` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.129 → después 0.130, Δ 0.000, δ +0.35, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.08 % = despreciable (< 2 %).
- **G1** · `cr2a_z` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 2.274 → después 2.274, Δ 0.000, δ +0.27, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.049 → después 0.049, Δ -0.000, δ -0.51, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.33 % = despreciable (< 2 %).
- **G1** · `cr2a_z` ante **P5**: esperado sin_cambio, mediana antes 2.274 → después 2.274, Δ -0.000, δ -0.23, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.00 % = despreciable (< 2 %).
- **G1** · `cr2a_crudo` ante **P6**: esperado sin_cambio, mediana antes 0.129 → después 0.130, Δ 0.000, δ +0.20, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G1** · `cr2a_z` ante **P6**: esperado sin_cambio, mediana antes 2.274 → después 2.380, Δ 0.013, δ +0.41, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.57 % = despreciable (< 2 %).
- **G1** · `cr2b_cos_turno` ante **P6**: esperado sin_cambio, mediana antes 0.049 → después 0.048, Δ -0.003, δ -0.79, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -6.11 % = NO despreciable.
- **G1** · `cr2b_cos_turno_sn` ante **P6**: esperado sin_cambio, mediana antes 0.031 → después 0.027, Δ -0.003, δ -0.69, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -8.49 % = NO despreciable.
- **G1** · `cr2b_cos_turno_sn` ante **P8**: esperado baja (min 0.001), mediana antes 0.031 → después 0.029, Δ -0.005, δ -0.16, observado sin_cambio, veredicto arnés «no responde».
- **G2** · `cr2a_crudo` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.132 → después 0.132, Δ 0.000, δ -0.39, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno_sn` ante **C2_minusculas**: esperado sin_cambio, mediana antes 0.025 → después 0.025, Δ 0.000, δ -0.24, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2a_crudo` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.132 → después 0.128, Δ 0.000, δ +0.28, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.00 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.024 → después 0.022, Δ -0.000, δ -0.51, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -1.46 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno_sn` ante **C3_sin_tildes**: esperado sin_cambio, mediana antes 0.025 → después 0.024, Δ -0.000, δ -0.27, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.63 % = despreciable (< 2 %).
- **G2** · `cr2a_z` ante **P5**: esperado sin_cambio, mediana antes 2.865 → después 2.849, Δ -0.002, δ -0.42, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -0.06 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno_sn` ante **P5**: esperado sin_cambio, mediana antes 0.025 → después 0.030, Δ 0.004, δ +0.33, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 15.54 % = NO despreciable.
- **G2** · `cr2a_z` ante **P6**: esperado sin_cambio, mediana antes 2.865 → después 2.732, Δ 0.000, δ +0.33, observado sube, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo 0.01 % = despreciable (< 2 %).
- **G2** · `cr2b_cos_turno` ante **P6**: esperado sin_cambio, mediana antes 0.024 → después 0.021, Δ -0.003, δ -0.77, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -10.92 % = NO despreciable.
- **G2** · `cr2b_cos_turno_sn` ante **P6**: esperado sin_cambio, mediana antes 0.025 → después 0.022, Δ -0.002, δ -0.68, observado baja, veredicto arnés «cambio inesperado»; [lectura post hoc] Δ relativo -8.32 % = NO despreciable.
- **G2** · `cr2b_cos_turno_sn` ante **P8**: esperado baja (min 0.001), mediana antes 0.025 → después 0.023, Δ -0.002, δ -0.16, observado sin_cambio, veredicto arnés «no responde».
- **G2** · `cr2b_cos_ventana8_sn` ante **W1_ventana_otro_par**: esperado baja (min 0.0025), mediana antes 0.052 → después 0.049, Δ -0.005, δ -0.10, observado sin_cambio, veredicto arnés «no responde».
**Lectura post hoc de los controles «=» que fallan por la regla del arnés** (no cambia el criterio ni los conteos; la regla cuenta signos, no magnitudes): de 20 controles «=» con «cambio inesperado», 15 tienen |Δ mediana| < 2 % de la mediana previa (despreciables en magnitud) y 5 no.

## 3. Regla de calibración de `min` (doc §5): min ≤ 0,5 × |mediana del efecto en desarrollo|

| brazo | instrumento | perturbación | min | mediana desarrollo | ¿cumple la regla? |
|---|---|---|---|---|---|
| G1 | `cr2b_cos_turno` | P5 | 0.0005 | -0.0055 | sí |
| G1 | `cr2a_crudo` | P8 | 0.04 | -0.1041 | sí |
| G1 | `cr2a_z` | P8 | 1 | -2.5129 | sí |
| G1 | `cr2b_cos_turno` | P8 | 0.003 | -0.0288 | sí |
| G1 | `cr2b_cos_turno_sn` | P8 | 0.001 | -0.0045 | sí |
| G1 | `cr2a_z_ventana8` | P9 | 0.5 | -1.3734 | sí |
| G1 | `cr2a_z_ventana8` | W1_ventana_otro_par | 1 | -2.6513 | sí |
| G1 | `cr2b_cos_ventana8` | W1_ventana_otro_par | 0.007 | -0.0685 | sí |
| G1 | `cr2b_cos_ventana8_sn` | W1_ventana_otro_par | 0.0025 | -0.0098 | sí |
| G1 | `cr2a_crudo` | X1_misma_campana_lejana | 0.04 | -0.0989 | sí |
| G1 | `cr2a_z` | X1_misma_campana_lejana | 1 | -2.3907 | sí |
| G1 | `cr2a_crudo` | X2_misma_campana_cercana | 0.035 | -0.0815 | sí |
| G1 | `cr2a_z` | X2_misma_campana_cercana | 1 | -2.0886 | sí |
| G2 | `cr2b_cos_turno` | P5 | 0.0005 | -0.0021 | sí |
| G2 | `cr2a_crudo` | P8 | 0.04 | -0.1042 | sí |
| G2 | `cr2a_z` | P8 | 1 | -2.7314 | sí |
| G2 | `cr2b_cos_turno` | P8 | 0.003 | -0.0064 | sí |
| G2 | `cr2b_cos_turno_sn` | P8 | 0.001 | -0.0022 | sí |
| G2 | `cr2a_z_ventana8` | P9 | 0.5 | -1.7416 | sí |
| G2 | `cr2a_z_ventana8` | W1_ventana_otro_par | 1 | -2.9830 | sí |
| G2 | `cr2b_cos_ventana8` | W1_ventana_otro_par | 0.007 | -0.0144 | sí |
| G2 | `cr2b_cos_ventana8_sn` | W1_ventana_otro_par | 0.0025 | -0.0054 | sí |
| G2 | `cr2a_crudo` | X1_misma_campana_lejana | 0.04 | -0.1017 | sí |
| G2 | `cr2a_z` | X1_misma_campana_lejana | 1 | -2.9262 | sí |
| G2 | `cr2a_crudo` | X2_misma_campana_cercana | 0.035 | -0.0770 | sí |
| G2 | `cr2a_z` | X2_misma_campana_cercana | 1 | -2.1028 | sí |

**Resultado de la regla: TODAS las celdas calibradas cumplen; el hash queda a4bc-2.**

## 4. Detalle por brazo

### G2

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P5 | `cr2b_cos_turno` | ▼ baja ≥0.0005 | 150 | 0.024 | 0.022 | -0.002 [-0.003, -0.002] | -0.46 | 7.05e-08 | baja | responde | **aprobada** |
| P8 | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.132 | 0.000 | -0.104 [-0.122, -0.091] | -0.87 | 6.88e-31 | baja | responde | **aprobada** |
| P8 | `cr2a_z` | ▼ baja ≥1 | 150 | 2.865 | -0.580 | -2.731 [-3.321, -2.370] | -0.85 | 2.71e-28 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno` | ▼ baja ≥0.003 | 150 | 0.024 | 0.017 | -0.006 [-0.010, -0.003] | -0.25 | 0.00722 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno_sn` | ▼ baja ≥0.001 | 150 | 0.025 | 0.023 | -0.002 [-0.006, -0.000] | -0.16 | 0.12 | sin_cambio | no responde | **falla** |
| P9 | `cr2a_z_ventana8` | ▼ baja ≥0.5 | 60 | 2.901 | 1.355 | -1.742 [-1.900, -1.314] | -0.93 | 1.91e-14 | baja | responde | **aprobada** |
| S1_sinonimos | `cr2a_crudo` | ▼ baja ≥0.005 | 150 | 0.132 | 0.123 | 0.000 [0.000, 0.000] | -0.19 | 0.000422 | baja | — | **descriptiva** |
| S1_sinonimos | `cr2a_z` | ▼ baja ≥0.1 | 150 | 2.865 | 2.820 | 0.023 [0.000, 0.051] | +0.41 | 9.18e-09 | sube | — | **descriptiva** |
| W1_ventana_otro_par | `cr2a_z_ventana8` | ▼ baja ≥1 | 60 | 2.901 | -0.092 | -2.983 [-3.230, -2.628] | -1.00 | 1.21e-17 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8` | ▼ baja ≥0.007 | 60 | 0.058 | 0.039 | -0.014 [-0.039, -0.007] | -0.50 | 0.000538 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8_sn` | ▼ baja ≥0.0025 | 60 | 0.052 | 0.049 | -0.005 [-0.010, 0.006] | -0.10 | 0.519 | sin_cambio | no responde | **falla** |
| X1_misma_campana_lejana | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.132 | 0.000 | -0.102 [-0.116, -0.090] | -0.79 | 9.12e-24 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.865 | -0.515 | -2.926 [-3.747, -2.477] | -0.79 | 2.18e-23 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_crudo` | ▼ baja ≥0.035 | 150 | 0.132 | 0.043 | -0.077 [-0.092, -0.057] | -0.76 | 1.99e-22 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.865 | 0.624 | -2.103 [-2.630, -1.782] | -0.69 | 1e-17 | baja | responde | **aprobada** |

**Controles «sin cambio» (G2):**

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.132 | 0.000 [0.000, 0.000] | -0.03 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2a_z` | = sin_cambio | 150 | 2.865 | 2.865 | 0.000 [0.000, 0.000] | -0.03 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.024 | 0.000 [0.000, 0.000] | +0.02 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.025 | 0.000 [0.000, 0.000] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.132 | 0.000 [-0.000, 0.000] | -0.39 | 1.03e-12 | baja | cambio inesperado | **falla** |
| C2_minusculas | `cr2a_z` | = sin_cambio | 150 | 2.865 | 2.865 | 0.000 [0.000, 0.000] | -0.09 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.023 | 0.000 [0.000, 0.000] | +0.12 | 0.239 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.025 | 0.000 [0.000, 0.000] | -0.24 | 0.000539 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.128 | 0.000 [0.000, 0.001] | +0.28 | 0.000381 | sube | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_z` | = sin_cambio | 150 | 2.865 | 2.737 | 0.000 [0.000, 0.000] | +0.14 | 0.746 | sin_cambio | responde | **aprobada** |
| C3_sin_tildes | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.022 | -0.000 [-0.001, -0.000] | -0.51 | 2.1e-14 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.024 | -0.000 [-0.001, 0.000] | -0.27 | 0.0079 | baja | cambio inesperado | **falla** |
| P11a_inyeccion | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.132 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2a_z` | = sin_cambio | 150 | 2.865 | 2.865 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.024 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11a_inyeccion | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.025 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P5 | `cr2a_z` | = sin_cambio | 150 | 2.865 | 2.849 | -0.002 [-0.017, -0.000] | -0.42 | 4.65e-07 | baja | cambio inesperado | **falla** |
| P5 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.030 | 0.004 [0.003, 0.005] | +0.33 | 0.00147 | sube | cambio inesperado | **falla** |
| P6 | `cr2a_crudo` | = sin_cambio | 150 | 0.132 | 0.130 | 0.000 [0.000, 0.000] | +0.11 | 1 | sin_cambio | responde | **aprobada** |
| P6 | `cr2a_z` | = sin_cambio | 150 | 2.865 | 2.732 | 0.000 [0.000, 0.013] | +0.33 | 0.000188 | sube | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.021 | -0.003 [-0.004, -0.002] | -0.77 | 5.5e-25 | baja | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.022 | -0.002 [-0.003, -0.001] | -0.68 | 2.94e-18 | baja | cambio inesperado | **falla** |
| P9 | `cr2b_cos_ventana8` | = sin_cambio | 60 | 0.058 | 0.058 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P9 | `cr2b_cos_ventana8_sn` | = sin_cambio | 60 | 0.052 | 0.052 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.021 | -0.002 [-0.006, 0.001] | -0.13 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.024 | -0.002 [-0.005, 0.001] | -0.08 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.024 | 0.026 | 0.003 [-0.001, 0.005] | +0.09 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.025 | 0.026 | 0.002 [-0.001, 0.004] | +0.09 | 1 | sin_cambio | responde | **aprobada** |

### G1

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P5 | `cr2b_cos_turno` | ▼ baja ≥0.0005 | 150 | 0.049 | 0.044 | -0.006 [-0.010, -0.003] | -0.59 | 1.17e-12 | baja | responde | **aprobada** |
| P8 | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.129 | 0.033 | -0.104 [-0.112, -0.096] | -0.81 | 2.24e-25 | baja | responde | **aprobada** |
| P8 | `cr2a_z` | ▼ baja ≥1 | 150 | 2.274 | -0.162 | -2.513 [-2.788, -2.279] | -0.73 | 4.8e-20 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno` | ▼ baja ≥0.003 | 150 | 0.049 | 0.021 | -0.029 [-0.081, -0.013] | -0.43 | 7.09e-07 | baja | responde | **aprobada** |
| P8 | `cr2b_cos_turno_sn` | ▼ baja ≥0.001 | 150 | 0.031 | 0.029 | -0.005 [-0.008, -0.000] | -0.16 | 0.06 | sin_cambio | no responde | **falla** |
| P9 | `cr2a_z_ventana8` | ▼ baja ≥0.5 | 60 | 2.661 | 1.154 | -1.373 [-1.684, -1.160] | -1.00 | 1.21e-17 | baja | responde | **aprobada** |
| S1_sinonimos | `cr2a_crudo` | ▼ baja ≥0.005 | 150 | 0.129 | 0.128 | 0.000 [0.000, 0.000] | -0.31 | 2.55e-08 | baja | — | **descriptiva** |
| S1_sinonimos | `cr2a_z` | ▼ baja ≥0.1 | 150 | 2.274 | 2.200 | 0.000 [0.000, 0.006] | +0.27 | 0.000149 | sube | — | **descriptiva** |
| W1_ventana_otro_par | `cr2a_z_ventana8` | ▼ baja ≥1 | 60 | 2.661 | -0.015 | -2.651 [-2.957, -2.415] | -1.00 | 1.21e-17 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8` | ▼ baja ≥0.007 | 60 | 0.107 | 0.043 | -0.068 [-0.122, -0.006] | -0.43 | 0.0032 | baja | responde | **aprobada** |
| W1_ventana_otro_par | `cr2b_cos_ventana8_sn` | ▼ baja ≥0.0025 | 60 | 0.068 | 0.057 | -0.010 [-0.020, -0.006] | -0.37 | 0.0124 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_crudo` | ▼ baja ≥0.04 | 150 | 0.129 | 0.037 | -0.099 [-0.109, -0.082] | -0.77 | 7.65e-23 | baja | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.274 | -0.155 | -2.391 [-2.743, -2.067] | -0.76 | 1.29e-21 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_crudo` | ▼ baja ≥0.035 | 150 | 0.129 | 0.040 | -0.081 [-0.096, -0.066] | -0.81 | 2.24e-25 | baja | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2a_z` | ▼ baja ≥1 | 150 | 2.274 | 0.032 | -2.089 [-2.460, -1.735] | -0.76 | 1.29e-21 | baja | responde | **aprobada** |

**Controles «sin cambio» (G1):**

| perturbación | instrumento | esperado | n | mediana antes | mediana después | Δ mediana [IC95] | δ pareado | p Holm | observado | veredicto arnés | criterio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1_reorden_oraciones | `cr2a_crudo` | = sin_cambio | 150 | 0.129 | 0.130 | 0.000 [0.000, 0.000] | +0.02 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2a_z` | = sin_cambio | 150 | 2.274 | 2.274 | 0.000 [0.000, 0.000] | +0.03 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.048 | 0.000 [0.000, 0.000] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| C1_reorden_oraciones | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.031 | 0.000 [0.000, 0.000] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2a_crudo` | = sin_cambio | 150 | 0.129 | 0.130 | -0.001 [-0.001, -0.001] | -0.63 | 4.98e-21 | baja | cambio inesperado | **falla** |
| C2_minusculas | `cr2a_z` | = sin_cambio | 150 | 2.274 | 2.274 | 0.000 [0.000, 0.000] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.049 | 0.000 [0.000, 0.000] | -0.02 | 1 | sin_cambio | responde | **aprobada** |
| C2_minusculas | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.030 | -0.000 [-0.000, 0.000] | -0.41 | 2.24e-10 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_crudo` | = sin_cambio | 150 | 0.129 | 0.130 | 0.000 [0.000, 0.001] | +0.35 | 1.34e-06 | sube | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2a_z` | = sin_cambio | 150 | 2.274 | 2.274 | 0.000 [0.000, 0.000] | +0.27 | 0.00225 | sube | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.049 | -0.000 [-0.001, 0.000] | -0.51 | 8.03e-15 | baja | cambio inesperado | **falla** |
| C3_sin_tildes | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.030 | -0.000 [-0.001, 0.000] | -0.17 | 0.547 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2a_crudo` | = sin_cambio | 150 | 0.129 | 0.129 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2a_z` | = sin_cambio | 150 | 2.274 | 2.274 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.049 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P11b_eliminacion | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.031 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P5 | `cr2a_z` | = sin_cambio | 150 | 2.274 | 2.274 | -0.000 [-0.000, 0.000] | -0.23 | 0.0409 | baja | cambio inesperado | **falla** |
| P5 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.035 | 0.003 [0.001, 0.005] | +0.16 | 1 | sin_cambio | responde | **aprobada** |
| P6 | `cr2a_crudo` | = sin_cambio | 150 | 0.129 | 0.130 | 0.000 [0.000, 0.000] | +0.20 | 0.044 | sube | cambio inesperado | **falla** |
| P6 | `cr2a_z` | = sin_cambio | 150 | 2.274 | 2.380 | 0.013 [0.000, 0.026] | +0.41 | 1e-06 | sube | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.048 | -0.003 [-0.004, -0.002] | -0.79 | 4.63e-26 | baja | cambio inesperado | **falla** |
| P6 | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.027 | -0.003 [-0.003, -0.002] | -0.69 | 3.48e-18 | baja | cambio inesperado | **falla** |
| P9 | `cr2b_cos_ventana8` | = sin_cambio | 60 | 0.107 | 0.107 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| P9 | `cr2b_cos_ventana8_sn` | = sin_cambio | 60 | 0.068 | 0.068 | 0.000 [0.000, 0.000] | +0.00 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.042 | -0.002 [-0.007, 0.003] | -0.04 | 1 | sin_cambio | responde | **aprobada** |
| X1_misma_campana_lejana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.031 | -0.001 [-0.006, 0.004] | -0.01 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno` | = sin_cambio | 150 | 0.049 | 0.060 | 0.000 [-0.002, 0.005] | +0.03 | 1 | sin_cambio | responde | **aprobada** |
| X2_misma_campana_cercana | `cr2b_cos_turno_sn` | = sin_cambio | 150 | 0.031 | 0.033 | -0.000 [-0.005, 0.004] | -0.03 | 1 | sin_cambio | responde | **aprobada** |

## 5. Límite léxico (S1, descriptivo)

- G2 · `cr2a_crudo`: mediana antes 0.132 → después 0.123 (Δ mediana 0.000); cambió en el 43 % de los turnos; n=150.
- G2 · `cr2a_z`: mediana antes 2.865 → después 2.820 (Δ mediana 0.023); cambió en el 76 % de los turnos; n=150.
- G2: sustituciones por turno (diccionario mínimo): media 2.0, turnos sin ninguna 17 %.
- G1 · `cr2a_crudo`: mediana antes 0.129 → después 0.128 (Δ mediana 0.000); cambió en el 45 % de los turnos; n=150.
- G1 · `cr2a_z`: mediana antes 2.274 → después 2.200 (Δ mediana 0.000); cambió en el 72 % de los turnos; n=150.
- G1: sustituciones por turno (diccionario mínimo): media 2.1, turnos sin ninguna 13 %.
