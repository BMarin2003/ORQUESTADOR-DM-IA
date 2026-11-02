# Revisión post-jurado: cifras de verificación (solo lectura)

Fecha: 2026-10-19. Sin regenerar el corpus, sin LLM y sin tocar datos ni scripts existentes. La base estaba apagada: CR-2a(z) se recalculó turno a turno desde la caché de lemas (`scripts/instrumentos/_cache/{R,A}_<campaign_id>.pkl`) con `respuesta_accion.medir`, y reproduce **exactamente** lo publicado (diferencia 0 en z y en n_z de los 378 bloques de `sensibilidad_a4bc_distribucion_27.csv`). Estadísticos con las funciones de la tesis (`comparar_v1_v2.hodges_lehmann`, `rank_biserial_pareada`, `resultados_tesis.wilcoxon_uni` exacto), IC 95 % bootstrap de parejas (semilla 20260920, B = 10,000).

## 1. Turnos computables de CR-2a y el turno 1

- `scripts/brechas/oe4_cr2a_descomposicion.py` usa `correr_a4bc.cargar_campanas`, que toma `turn_id >= 1` (línea 138): **sí incluye el turno 1**. El turno 1 es computable en las 27 campañas de cada brazo: 37,798 = 37,771 + 27 (G1) y 37,790 = 37,763 + 27 (G2). Sin él, ambos quedan por debajo del máximo de 37,773.
- **Afecta a las tablas de CR-2a(z)**: el valor por campaña de la tesis (`consolidar.py`, fuente `a4bc`) es la media de los 7 bloques de 200 turnos, y el bloque 1 (turnos 1–200) incluye el turno 1. El efecto es pequeño y no cambia ninguna decisión.

| CR-2a(z), 27 pares | Con turno 1 (publicado) | Sin turno 1 |
| --- | --- | --- |
| Mdn G1 / Mdn G2 | 2.704 / 2.809 | 2.705 / 2.811 |
| HL [IC 95 %] | −0.133 [−0.254, −0.027] | **−0.136 [−0.255, −0.028]** |
| p bilateral | 0.0319 | **0.0299** |
| p unilateral H1d (G1 > G2) | 0.985 | 0.986 |
| r biserial de rangos | −0.471 | **−0.476** |
| OE-1 · G2 por campaña: Mdn (RIQ) | 2.809 (0.404) | 2.811 (0.402) |
| OE-1 · G2 bloque 1 → bloque 7 (Mdn) | 2.768 → 2.742 | **2.785** → 2.742 |
| OE-1 · Page (H1a, decrece) | z = 0.50, p = 0.310 | **z = 0.67, p = 0.253** |

Redondeado a dos decimales cambian: HL −0.13 → **−0.14**, IC [−0.25, −0.03] → **[−0.26, −0.03]**, p 0.032 → **0.030**, r −0.47 → **−0.48**, Page p 0.310 → **0.253** y bloque 1 2.768 → **2.785**. Las decisiones se mantienen (H0a no se rechaza; H1d no se sostiene, leve a favor de G2).

## 2. Sensibilidad por perturbación (anexo)

Regla fijada de antemano: un instrumento numérico «cambia» si p de Holm < 0.05 **y** |δ de Cliff pareado| ≥ 0.147; uno booleano, con McNemar exacta y Holm (sin δ). «Confirm.» = celdas con dirección pre-especificada que respondieron / total (G1 + G2); «controles» = celdas «sin cambio» que se mantuvieron.

| Instrumento | Perturbación objetivo | Expectativa | \|δ\| de Cliff | p Holm | Confirm. / controles | Clase |
| --- | --- | --- | --- | --- | --- | --- |
| CR-2a respuesta a la acción (z) | P8 narración de otro par; X1/X2 respuesta de otro turno de la misma campaña | baja | 0.77–0.88 | ≤ 1.4e−22 | 6/6 · 10/12 | **C** |
| CR-2a solapamiento crudo | P8, X1, X2 | baja | 0.76–0.91 | ≤ 1.0e−21 | 6/6 · 6/10 | E |
| CR-2b anclaje al escenario (v8) | W1 ventana de 8 turnos de otro par | baja | 0.60–0.70 | ≤ 1.3e−5 | 2/2 · 2/2 | E |
| CR-2b anclaje sin nombres (v8) | W1 | baja | 0.37–0.57 | ≤ 0.012 | 2/2 · 2/2 | E |
| Nombres no reconocidos | P5 nombres inventados; P8 | se dispara | McNemar | G2 ≤ 8.1e−6; G1 no responde | 2/4 · 40/48 | E |
| Gramaticalidad (LanguageTool) | P6 corrupción gramatical; P12 palabras de otro alfabeto | baja | 0.12–1.00 | P6 3.4e−14; P12 0.31 | 2/4 · 0/4 | D |
| Pifia narrada como éxito | P10 pifia con narración de éxito | se dispara | McNemar | ≤ 4.9e−44 | 2/2 · 38/42 | D |
| Caracteres de otro alfabeto | — (no evaluado en A2) | — | — | — | — | D |
| Coherencia de entidad C / consistencia V | solo control P9 (permutación de turnos vecinos) | sin cambio | — | — | — · 2/2 cada uno | E |
| Tasa de correferencia (ECR) | solo control P9 | sin cambio | — | — | — · 2/2 | D |
| PNJ inactivo mencionado | P3 PNJ muerto/desaparecido que actúa o habla | se dispara | McNemar | ≤ 7.1e−38 | 8/8 · 35/40 | E |
| PNJ inactivo refinado | P3 | se dispara | McNemar | no significativo en 4 celdas | 4/8 · — | E |
| Jericho-QA recall | JQ1 insertar el cambio (F→V); JQ2 quitarlo (V→F) | cambia | tasa | 40/40 y 40/40 (100 %) | 80/80 · — | E |
| Relojes reconocidos (no figura en la Tabla 1) | RJ1 (F→V); RJ2 (V→F), solo pares 18–27 | cambia | tasa | 7/7 y 16/16 | 23/23 · — | — |
| Supervivencia (1.ª mención de PNJ no vivo) | sin A2 propia: deriva de PNJ inactivo | — | — | — | — | E |
| Ciclos de ubicación (bucles) | P9 | sube | 0.00–0.07 | 1 | 0/2 · — | D |
| MTLD · MATTR | solo control P9 | sin cambio | — | — | — · 2/2 cada uno | E |
| TTR | P7 párrafo duplicado (baja); P12 (sube) | baja / sube | 1.00 | ≤ 4.9e−44 | 4/4 · 2/6 | E |
| Repetición de bigramas | P7 | sube | 1.00 | ≤ 4.9e−44 | 2/2 · 0/4 | E |
| Legibilidad Fernández Huerta · Szigriszt-Pazos | solo controles | sin cambio | — | — | — · 3/6 cada uno | D |
| persona2 (usurpación explícita) | DIR: usurpación inyectada en 2.ª y 3.ª persona (Wilson LI ≥ 0.80); INV: textos que no violan la regla (≤ 5 %) | se dispara / no se dispara | tasa | DIR 7/10 celdas (fallan 2p decisión, pensamiento y emoción); INV 4/4 | 11/14 | **CC** |

Hashes SHA-256 de las expectativas (fijadas antes de correr):

- Línea base: `735308b36bf7e81e00da31e5fca53a193e4415ed7409906ff348c7eb6765a61b`; tabla completa: `d42cecefbb524af467f31e27bc9911bca61bb2c69806013aa96df07993b0dffc`
- Matriz a4bc-2: `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744` (deriva de a4bc-1 `67e6133a51c4c23001038a19bb9894e2afa7b99b5dfef91955e0ee789ec0c54e`)
- Extensión Szigriszt/MTLD/MATTR: `59998b1645cb9148a1c22515f4976c41241b983142460bcde18706a0f462b825`
- Jericho y relojes: `783c4e43a46cdad513f599f212548912915754a0e141c89c9440a89cdcf71856`
- persona2: `3ac6a23c0f361578f6198265b742383b4a293d0542e3df41f7d204711fcf4f87` Fuentes: `sensibilidad_ext_sz_mtld.csv` (contiene la línea base), `sensibilidad_a4bc.csv`, `sensibilidad_jericho_relojes.md`, `persona2_equivalencia.md`.

## 3. Robustez sin los pares 01–06 (cambio del agente jugador)

Fuente: `docs/resultados/por_campana_largo.csv`. p unilateral en el sentido de H1 (CR-2a: G1 > G2; persona2: G1 < G2).

| Instrumento | Pares | Mdn G1 | Mdn G2 | HL [IC 95 %] | p unilateral (H1) | p bilateral | r |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CR-2a(z) | 01–27 (n = 27) | 2.704 | 2.809 | −0.133 [−0.254, −0.027] | 0.985 | 0.0319 | −0.47 |
| CR-2a(z) | **07–27 (n = 21)** | 2.664 | 2.733 | −0.160 [−0.290, −0.031] | 0.977 | **0.0502** | −0.49 |
| persona2 total | 01–27 (n = 27) | 0.17 % | 3.47 % | −3.66 pp [−4.87, −2.74] | 7.5e−9 | 1.5e−8 | −1.00 |
| persona2 total | **07–27 (n = 21)** | 0.17 % | 3.32 % | −3.36 pp [−4.54, −2.51] | 4.8e−7 | 9.5e−7 | −1.00 |

Lectura: persona2 no cambia (G1 menor en 21/21). En CR-2a se mantienen la dirección y el tamaño (r −0.49), pero sin los pares 01–06 la diferencia bilateral queda en el límite (p = 0.050): la «ventaja leve de G2» depende en parte de esos pares. H1d no se sostiene en ningún caso (p unilateral ≈ 0.98).

## 4. Jericho-QA recall en G2 (n = 27, incluye el Par 08)

Fuente: `por_campana_largo.csv`, clave `jericho_recall`; Par 08 = 0.200.

| Mdn | Q1 | Q3 | RIQ | Mín. | Máx. | Media | DE | Shapiro-Wilk p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.200 | 0.134 | 0.352 | 0.218 | 0.000 | 0.500 | 0.235 | 0.161 | 0.141 |

## 5. Fuentes de dos afirmaciones

- **(a) Análisis exploratorio del último tramo de 100 turnos:** existe. `docs/reportes/degradacion/ultimo_bloque.md` (lo genera `scripts/degradacion/ultimo_bloque.py`; medias en `ultimo_bloque_medias.csv`). Cifra clave: en G2, CR-2a(z) toca su mínimo en el bloque 14 (turnos 1,301–1,400), con media 2.654, pero el salto no es significativo (A_salto −0.030, p = 0.348, Holm 1.000); ningún indicador empeora tras Holm.
- **(b) «Escenas de muerte formulaicas» señaladas por un evaluador:** **no existe**. No aparece en `docs/`, `scripts/`, `validacion/` (ni en las notas libres de las etiquetas E1–E4), `entregas/` ni en la tesis. Lo más cercano: el descriptor genérico «formulaico» del nivel 2 de QN-1 en la Rúbrica D&D-IA, y las celdas `muerte_2p`/`muerte_3p` del arnés de persona2 (inyección sintética, no un comentario de evaluador).

## 6. MATTR en OE6-6: n efectivo = 25

No faltan datos: los 27 pares tienen MATTR por campaña. **Dos pares empatan exactamente**, porque el valor se guarda con 3 decimales: Par 02 (0.826 vs 0.826) y Par 17 (0.826 vs 0.826). Wilcoxon descarta las diferencias nulas (rangos medios, ceros fuera), por eso n efectivo = 25.
