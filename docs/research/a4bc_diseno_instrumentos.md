# A4b/c — Diseño y pre-especificación de dos instrumentos deterministas: respuesta a la acción (CR-2a) y anclaje al escenario (CR-2b)

Escrito el 2026-09-20. Estado de la matriz: **congelada** (`a4bc-1`); cualquier cambio va en el apéndice «post hoc» (sección 9).

## 0. Estado y orden de trabajo (para poder retomar)

Orden fijado: (1) este documento y la matriz con su hash; (2) pruebas; (3) `lemas_es.py`, `respuesta_accion.py`, `anclaje_escenario.py`; (4) enchufe al arnés y corrida de DESARROLLO; (5) congelar; (6) corrida de EVALUACIÓN; (7) informe `docs/reportes/sensibilidad_a4bc.md`. El estado vivo está en el «Registro de avance» de la sección 9.

| paso | archivo | estado |
|---|---|---|
| matriz + hash | `experimento/scripts/instrumentos/matriz_a4bc.py`, `test_matriz_a4bc.py` (7 pruebas) | HECHO (escrita 2026-09-20 21:21, antes de programar los instrumentos) |
| este documento | `docs/research/a4bc_diseno_instrumentos.md` | HECHO |
| léxico común | `experimento/scripts/instrumentos/lemas_es.py` + `test_lemas_es.py` | pendiente (ver sección 9) |
| CR-2a | `respuesta_accion.py` + `test_respuesta_accion.py` | pendiente |
| CR-2b | `anclaje_escenario.py` + `test_anclaje_escenario.py` | pendiente |
| perturbaciones nuevas | `perturbaciones_a4bc.py` + prueba | pendiente |
| corridas | `correr_a4bc.py` | pendiente |
| informe | `docs/reportes/sensibilidad_a4bc.md` | pendiente |

Solo se crean archivos nuevos (más una caché en `experimento/scripts/instrumentos/_cache/`). No se edita el arnés (`experimento/scripts/sensibilidad/`), ni `persona2.py`, ni la base (solo SELECT; conexión `read_only`). Sin LLM ni APIs.

## 1. Constructo y datos

Rúbrica D&D-IA v2, CR-2 (arraigo contextual): **(a)** la respuesta del DM está anclada en la acción específica del jugador en ese turno; **(b)** está anclada en el estado del mundo, sin introducir cosas ajenas. Hasta hoy no había instrumento para (a); para (b) `cr2_entidad_grafo_densidad` y `grafo_lema_densidad` no distinguen una narración de otro escenario (`docs/reportes/sensibilidad_baseline.md`, secciones 3c y 4: P8 «no responde», diferencia pareada casi siempre 0).

Datos: `turn_log(campaign_id, turn_id, player_buffer, dm_output)`; 21 pares = 42 campañas × 1400 turnos (+ turno 0 = lore). En los 58 800 turnos de los dos lotes `player_buffer` tiene siempre exactamente 1 entrada. La acción del jugador tiene casi siempre la forma `"diálogo entre comillas"` + prosa en 1.ª persona + `{Habilidad}` (en una muestra aleatoria de 1 209 turnos: 1 186 «mixta», 23 solo prosa, 0 solo etiqueta, 0 solo diálogo). El narrador escribe sobre todo en 2.ª persona (G2) o en impersonal (G1, con etiquetas `narrativa/mecanica/presion`).

### 1.1 Muestras: desarrollo y evaluación DISJUNTAS

- **Evaluación** = la muestra del arnés (`datos.plan_muestra`, semilla 20260920): pares 09, 11, 13, 14, 16 (lote v1) y 20, 21, 23, 24, 25 (lote v2); 15 turnos por par y brazo = **150 turnos por brazo** + 6 ventanas de 8 turnos por par y brazo = 60 ventanas por brazo.
- **Desarrollo** = los otros 11 pares: 07, 08, 10, 12, 15, 17, 18, 19, 22, 26, 27. Sirve para (i) elegir decisiones de diseño y (ii) fijar las magnitudes mínimas. La evaluación **no se toca** hasta congelar.
- Transparencia: antes de escribir la matriz miré, SOLO en pares de desarrollo, (a) qué tipo de clave léxica separa mejor la acción real de acciones ajenas, y (b) los tamaños de efecto de P8/X1/X2 y W1 con un borrador del cálculo (sección 5). Ningún instrumento se ejecutó sobre los pares de evaluación antes de fijar el hash. Los descriptivos de deriva (paso 5 del encargo) usan las 42 campañas, incluidas las de desarrollo; son descriptivos, sin veredicto.

## 2. Definiciones operacionales

### 2.1 Preprocesamiento común (`lemas_es.py`)

1. **Limpieza de formato**: `prosa(texto, "G1")` de `experimento/scripts/validacion_generar.py` sobre TODO texto antes de medir. Para G1 quita las etiquetas y el bloque `mecanica` (deja `narrativa` y `presion`); en un texto de G2 sin etiquetas es solo `strip()` (idéntico a `prosa(t, "G2")`). Se usa siempre la variante «G1» para que un texto con formato inyectado (P11a en G2) se limpie igual; por eso P11 es un invariante exacto por construcción.
2. **Lematización**: spaCy `es_core_news_sm` 3.8.0 (spaCy 3.8.16), con `parser` y `ner` desactivados (no se usan; bastan `tok2vec`, `morphologizer`, `attribute_ruler`, `lemmatizer`).
3. **Unidad léxica** («lema de contenido»): token con POS en el conjunto de la variante, `is_stop` falso, lema = primera palabra del lema de spaCy (los clíticos salen como «tomar él»), **clave = minúsculas sin tildes** (NFD sin marcas), solo letras, longitud ≥ 3.
4. **POS**: `respuesta_accion` usa {NOUN, VERB, ADJ}. `anclaje` con nombres usa {NOUN, VERB, ADJ, PROPN}. `anclaje` «sin nombres» (sn) usa {NOUN, VERB, ADJ} menos los lemas que aparecen en los nombres del escenario (localizaciones, facciones, PNJ, PJ) de los fixtures.
5. Limitación medida del etiquetador (en desarrollo): spaCy `sm` etiqueta mal los verbos de 2.ª persona («acercas» sale ADJ/`acerca`, «Examinas» sale PROPN) y todo texto en mayúsculas como PROPN. Los verbos de la acción (1.ª persona, «acerco» → `acercar`) casi nunca casan con los de la respuesta (2.ª persona): en desarrollo, solo VERB da una probabilidad de superar al nulo de 0,60 y solo NOUN+ADJ de 0,91. El puntaje lo sostienen sustantivos y adjetivos. Se conservan los verbos (lo pide la definición) y se documenta. Probé una clave por prefijo de 5-6 letras (truncación, Mayfield & McNamee 2003) y no mejoró de forma apreciable (0,91 igual): se descarta.

### 2.2 `respuesta_accion` (CR-2a)

**Entrada**: acción `A` = texto de `player_buffer` (entradas unidas por salto de línea) sin etiquetas de tirada (`\{[^}]*\}`); respuesta `R` = `prosa(dm_output)` del MISMO turno.

**Tratamiento explícito de la acción degenerada**:
- `solo_tag`: tras quitar `{…}` no queda texto: **no computable (None)**. No se inventa señal a partir del nombre de la habilidad («Percepción» no describe qué hizo el jugador).
- `solo_dialogo`: todo el texto restante está entre comillas (`"…"`, `«…»`) o son líneas que empiezan por raya (—). Se **calcula** con los lemas del diálogo (el DM sí responde a lo que el jugador dice), pero se marca `clase="solo_dialogo"` y se reporta aparte en los agregados.
- `mixta` (diálogo + prosa) y `accion` (solo prosa): se usan **todos** los lemas (el diálogo es parte de lo que el jugador declaró en ese turno).
- Si `|A| < 3` lemas o `|R| < 3` lemas: **None** (clase `insuficiente`); con tan pocos lemas el coeficiente no es interpretable.

**Puntaje crudo**: coeficiente de Ochiai (coseno sobre conjuntos binarios de lemas): `crudo = |A ∩ R| / sqrt(|A|·|R|)`. Normaliza por la longitud de ambos textos.

**Calibración por nulo de permutación (restringida)**: la MISMA respuesta `R` se empareja con acciones `A'` de otros turnos de la misma campaña:
- Reserva: turnos `x` de la campaña con acción válida (≥ 3 lemas), `x ≠ t` y `|x − t| > 2` (la acción del turno siguiente reacciona a esta respuesta y la anterior comparte escena; se excluyen para no inflar el nulo).
- Emparejamiento por longitud: banda `| |A'| − |A| | ≤ max(1, round(0,15·|A|))`; si la banda tiene menos de 40 turnos se toman los 40 más próximos en longitud. Se toma una muestra sin reemplazo de hasta 150, con semilla `sha1(campaña|turno)` (determinista).
- `z = (crudo − media_nulo) / max(sd_nulo, 0,01)` (el piso 0,01 evita dividir por 0 con nulos degenerados); `percentil` = fracción del nulo por debajo del observado con rangos medios en empates; `p_perm = (1 + #{nulo ≥ observado}) / (1 + m)` (Phipson & Smyth 2010: un p de permutación nunca es 0).
- **Salida principal = `z`** (`cr2a_z`); `cr2a_crudo` se registra para mostrar qué aporta la calibración. `cr2a_z_ventana8` = media de los `z` no nulos de los 8 turnos de la ventana (cada respuesta con la acción de su turno, `t..t+7`).
- El nulo es **de campaña completa** (no local). Una respuesta que solo continúa la escena obtiene z > 0 (comparte escena con las acciones): el z mide «esta respuesta pertenece a ESTA acción antes que a las de otros turnos de la campaña». Un nulo local (turnos a 3-25) sería más estricto; queda como trabajo futuro y X2 (donante a 3-10 turnos) mide el mismo fenómeno.

**Por qué NO embeddings ni un modelo semántico**: (i) *auditabilidad*: cada punto del puntaje se traza a lemas concretos compartidos; (ii) *determinismo y licencias*: un modelo de vectores añade otro artefacto de pesos con versión, licencia propia y posible no-determinismo de hardware (no verificado aquí: NO VERIFICADO), mientras que spaCy `sm` con versión fijada es determinista en CPU; (iii) el requisito de la tesis es medición 100 % determinista sin LLM. Límite del enfoque léxico: **no ve sinónimos ni paráfrasis** («tomar el pulso» frente a «medir el latido»), ni anáfora («él» por el paciente), ni negación («no encuentras el pulso» puntúa alto); además hereda los errores del etiquetador (2.ª persona). Por eso S1 (sinónimos) se reporta como descriptivo y el instrumento se declara **cota inferior** de la responsividad.

### 2.3 `anclaje_escenario` (CR-2b)

**Referencia del escenario** (por par): lemas de (a) el lore (turno 0, `dm_output`) y (b) los campos descriptivos de `world_parNN.json` (localizaciones: `name`, `description_canonical`, `sketch_text`, valores de texto de `culture_overrides`; facciones: `name`, `description`; misiones: `title`, `description`; relojes: `agenda`) y de `personas_parNN.json` (por PNJ: `name`, `species`, `social_role`, `appearance`, `internal_contradiction`, `traits`, `taboos`). Se excluyen los campos de autoría o ocultos para el jugador (`_arquetipo`, `_nota`, `voice_notes`, `secrets`, `knowledge`...) y los numéricos.

**Peso**: TF-IDF sobre lemas con vocabulario ajustado al corpus: `idf(t) = ln((1+N)/(1+df(t))) + 1`, con `N = 42` campañas y `df(t)` = nº de campañas cuya narración (turnos ≥ 1, tras `prosa`) contiene el lema `t`; `tf` sublineal `1 + ln(tf)`. Los términos genéricos (presentes en casi todas las campañas) pesan ≈ 1 y los específicos (presentes solo en las 2 campañas del par) ≈ 4. Hay un `idf` distinto para cada variante (con nombres / sn), calculado con su propio conjunto de lemas.

**Puntaje**: coseno entre el vector de la narración y el de la referencia.
- `cr2b_cos_turno`: narración de un turno.
- `cr2b_cos_ventana8`: suma de los conteos de lemas de 8 turnos consecutivos (cada turno se lematiza por separado; el orden de los turnos no importa).
- Variantes `_sn`: sin nombres propios (POS sin PROPN) y sin lemas de nombres del escenario, tanto en la narración como en la referencia. Sirve para comprobar que el coseno no se reduce al atajo de mencionar nombres.
- Diagnóstico de validez (descriptivo): identificación del escenario propio por argmax del coseno entre las 21 referencias (azar = 1/21 = 4,8 %; en desarrollo: 41 % por turno y 50 % por ventana de 8).

## 3. Perturbaciones

Reutilizadas del arnés (`experimento/scripts/sensibilidad/perturbaciones.py`): **P5** (nombres inventados), **P6** (barajar palabras en minúscula en ~30 % de oraciones), **P8** (narración de otro par), **P9** (permutación de una ventana de 8), **P11a/P11b** (inyectar/quitar formato de G1).

Nuevas (`experimento/scripts/instrumentos/perturbaciones_a4bc.py`; solo cambian el texto de la respuesta; la acción y el escenario quedan fijos):
- **X1_misma_campana_lejana**: sustituye la respuesta por la de otro turno de la MISMA campaña a 50 o más turnos (control positivo de respuesta_accion; control «sin cambio» de anclaje).
- **X2_misma_campana_cercana**: ídem a 3-10 turnos (misma escena).
- **C1_reorden_oraciones**: reordena aleatoriamente las oraciones de la narración (control invariante). Interpreto «reordenar sinónimos» del encargo como reordenar contenido léxico sin sustituirlo; la sustitución real por sinónimos es S1.
- **C2_minusculas** / **C3_sin_tildes**: todo el texto en minúsculas / sin tildes (controles invariantes de mayúsculas y tildes).
- **S1_sinonimos**: sustituye unas 40-60 palabras frecuentes por sinónimos de un diccionario mínimo escrito a mano. Cuantifica el límite léxico; sin veredicto.
- **W1_ventana_otro_par**: sustituye las 8 respuestas de una ventana por 8 turnos consecutivos de otro par (control positivo de ventana; P9 mantiene las acciones fijas y desalinea respuestas).

## 4. MATRIZ DE EXPECTATIVAS PRE-ESPECIFICADA

Fuente de verdad: `experimento/scripts/instrumentos/matriz_a4bc.py` (`MATRIZ`; `hash_matriz()`). Dirección en el vocabulario del arnés (↓ baja, ↑ sube, = sin cambio). `≥x` = magnitud mínima de |mediana de la diferencia pareada (después − antes)|; unidades: z (cr2a_z, cr2a_z_ventana8), puntos de Ochiai (cr2a_crudo), puntos de coseno (cr2b_*). «exacto» = diferencia 0 en el 100 % de pares. «(desc.)» = sin veredicto.

| perturbación | `cr2a_z` | `cr2a_crudo` | `cr2a_z_ventana8` | `cr2b_cos_turno` | `cr2b_cos_turno_sn` | `cr2b_cos_ventana8` | `cr2b_cos_ventana8_sn` |
|---|---|---|---|---|---|---|---|
| X1_misma_campana_lejana | ↓ ≥1 | ↓ ≥0.04 |  | = | = |  |  |
| X2_misma_campana_cercana | ↓ ≥1 | ↓ ≥0.04 |  | = | = |  |  |
| P8 | ↓ ≥1 | ↓ ≥0.04 |  | ↓ ≥0.005 | ↓ ≥0.001 |  |  |
| P5 | = |  |  | ↓ ≥0.0005 | = |  |  |
| P6 | = | = |  | = | = |  |  |
| C1_reorden_oraciones | = | = |  | = | = |  |  |
| C2_minusculas | = | = |  | = | = |  |  |
| C3_sin_tildes | = | = |  | = | = |  |  |
| P11a_inyeccion | = exacto | = exacto |  | = exacto | = exacto |  |  |
| P11b_eliminacion | = exacto | = exacto |  | = exacto | = exacto |  |  |
| S1_sinonimos | ↓ ≥0.1 (desc.) | ↓ ≥0.005 (desc.) |  |  |  |  |  |
| P9 |  |  | ↓ ≥1 |  |  | = exacto | = exacto |
| W1_ventana_otro_par |  |  | ↓ ≥1 |  |  | ↓ ≥0.01 | ↓ ≥0.003 |

**Criterio de aprobación** (por celda): veredicto del arnés «responde» (para dirección: Holm p < 0,05 **y** |delta de Cliff pareado| ≥ 0,147 en la dirección esperada; para «=»: ninguno de los dos) **y**, si hay dirección, |mediana de la diferencia| ≥ `min`. Celdas exactas: la diferencia debe ser 0 en el 100 % de los pares. Una celda que no cumpla es un HALLAZGO; no se cambia la expectativa. Para el veredicto se reutilizan `correr_sensibilidad.evaluar` y `estadistica.py` (Holm por brazo y familia, n mínimo 10).

**Nota sobre la regla del arnés en controles «=» no exactos**: `delta_pareado` cuenta signos, no magnitudes; un desplazamiento diminuto pero sistemático (p. ej. al cambiar el contexto del etiquetador) se marcaría «cambio inesperado». Es la regla fijada por el arnés y se acepta; el informe muestra además la mediana de la diferencia para juzgar si el «cambio» es despreciable en magnitud, pero el veredicto formal es el del arnés.

### 4.1 Justificación mecánica por celda (derivada de la definición)

- **respuesta / X1_misma_campana_lejana**: La respuesta se sustituye por la de un turno de la MISMA campaña a 50 o más turnos. Por definición el puntaje mide el solapamiento de lemas de contenido con la acción de ESTE turno; la respuesta ajena comparte solo vocabulario genérico y del escenario, que el nulo (misma campaña) ya descuenta, así que el z cae hacia 0.
- **respuesta / X2_misma_campana_cercana**: Respuesta de un turno de la misma campaña a 3-10 turnos (misma escena). Comparte escenario y PNJ pero no las palabras de la acción concreta de este turno: el z debe bajar aunque quizá menos que con una respuesta lejana (continuidad de escena).
- **respuesta / P8**: Respuesta de otro PAR (otro escenario). Sin solapamiento específico con la acción; el solapamiento residual es vocabulario genérico que el nulo descuenta: el puntaje baja.
- **respuesta / P5**: Se añade una oración con dos nombres inventados. Los nombres propios no son lemas de contenido (solo NOUN/VERB/ADJ) y las palabras añadidas alargan R por igual en el observado y en el nulo (misma R): el z no debe moverse. En el crudo no se juzga (crece |R|).
- **respuesta / P6**: Se barajan las palabras en minúscula de ~30 % de las oraciones. El puntaje es una bolsa de lemas: en teoría invariante al orden. Riesgo conocido: el etiquetador de spaCy depende del contexto y puede cambiar el lema de algunas formas; se espera un efecto despreciable.
- **respuesta / C1_reorden_oraciones**: Se reordenan las oraciones de la narración (mismo contenido léxico). La bolsa de lemas es la misma salvo el contexto de etiquetado en las fronteras: invariante.
- **respuesta / C2_minusculas**: Todo el texto en minúsculas. El puntaje normaliza minúsculas en la clave; riesgo conocido: spaCy etiqueta distinto sin mayúscula inicial (nombres propios). Se espera efecto despreciable en NOUN/VERB/ADJ.
- **respuesta / C3_sin_tildes**: Se quitan las tildes de la respuesta. La clave del lema ya se normaliza sin tildes; riesgo conocido: spaCy lematiza distinto formas sin tilde. Se espera efecto despreciable.
- **respuesta / P11a_inyeccion**: Se inyectan etiquetas de formato de G1 y una línea mecánica en un texto de G2. El instrumento aplica prosa(texto, 'G1') antes de medir: la entrada tras la limpieza es idéntica, invariante exacto por construcción.
- **respuesta / P11b_eliminacion**: Se elimina el formato de G1 (prosa). El instrumento ya lo elimina: prosa es idempotente, invariante exacto por construcción.
- **respuesta / S1_sinonimos**: Sustitución por sinónimos de un diccionario mínimo escrito a mano. Una similitud LÉXICA no ve sinónimos: si se cambia un lema compartido con la acción, el solapamiento cae. Es el LÍMITE conocido del enfoque léxico; se cuantifica, sin veredicto (la cobertura del diccionario es pequeña y no está calibrada).
- **ventana_resp / P9**: Se permuta el orden de las 8 respuestas de la ventana dejando las acciones en su sitio: cada respuesta queda emparejada con la acción de OTRO turno de la ventana (misma escena). El z medio de la ventana baja como en X2.
- **ventana_resp / W1_ventana_otro_par**: Las 8 respuestas se sustituyen por 8 turnos consecutivos de otro par: sin solapamiento específico con las acciones; el z medio cae hacia 0.
- **anclaje_turno / P8**: Narración de un turno de OTRO par. El coseno TF-IDF con la referencia de ESTE escenario cae porque los lemas específicos (idf alto) ya no aparecen y aparecen los del otro escenario, que no están en la referencia.
- **anclaje_turno / X1_misma_campana_lejana**: Narración de otro turno de la misma campaña (mismo escenario), a 50 o más turnos. El instrumento mide pertenencia al ESCENARIO, no al turno: en promedio no debe cambiar (la diferencia pareada es simétrica alrededor de 0).
- **anclaje_turno / X2_misma_campana_cercana**: Narración de otro turno de la misma campaña a 3-10 turnos: mismo escenario, mismo vocabulario; diferencia pareada simétrica alrededor de 0.
- **anclaje_turno / P5**: Se añade una oración con dos nombres inventados. En la variante con nombres los lemas nuevos (idf máximo, ausentes de la referencia) entran en el vector de la narración y aumentan su norma sin aumentar el producto escalar: el coseno baja por construcción. Es la parte (b) del constructo («sin introducir cosas ajenas»). Efecto pequeño.
- **anclaje_turno / P6**: Barajar palabras en minúscula de ~30 % de oraciones. Bolsa de lemas: se espera invariancia (riesgo: el etiquetador depende del contexto). Efecto despreciable esperado.
- **anclaje_turno / C1_reorden_oraciones**: Reordenar oraciones: misma bolsa de lemas; invariante salvo contexto de etiquetado.
- **anclaje_turno / C2_minusculas**: Minúsculas: la clave se normaliza; riesgo conocido: los nombres propios en minúscula se etiquetan y lematizan distinto (p. ej. verbo inventado). Se espera efecto despreciable.
- **anclaje_turno / C3_sin_tildes**: Sin tildes: la clave se normaliza; riesgo conocido: spaCy lematiza distinto las formas sin tilde. Se espera efecto despreciable.
- **anclaje_turno / P11a_inyeccion**: Inyección de formato G1: el instrumento aplica prosa() antes de medir: invariante exacto.
- **anclaje_turno / P11b_eliminacion**: Eliminación de formato G1: prosa idempotente: invariante exacto.
- **anclaje_turno_sn / P8**: Sin nombres propios ni lemas de nombres del escenario. Los lemas comunes específicos (niebla, cansancio, dique...) de la narración propia desaparecen con una narración ajena, así que el coseno baja, pero se espera MENOS que con nombres (el atajo de nombrar entidades queda excluido).
- **anclaje_turno_sn / X1_misma_campana_lejana**: Mismo escenario: diferencia pareada simétrica alrededor de 0.
- **anclaje_turno_sn / X2_misma_campana_cercana**: Mismo escenario: diferencia pareada simétrica alrededor de 0.
- **anclaje_turno_sn / P5**: Los nombres inventados se excluyen (nombre propio) y la variante ignora lemas de nombres: sin nombres propios en el vector, la oración añadida apenas cambia el coseno.
- **anclaje_turno_sn / P6**: Bolsa de lemas: invariante salvo contexto de etiquetado.
- **anclaje_turno_sn / C1_reorden_oraciones**: Bolsa de lemas: invariante salvo contexto de etiquetado.
- **anclaje_turno_sn / C2_minusculas**: Clave normalizada; riesgo de etiquetado sin mayúscula. Efecto despreciable esperado.
- **anclaje_turno_sn / C3_sin_tildes**: Clave normalizada; riesgo de lematizado sin tilde. Efecto despreciable esperado.
- **anclaje_turno_sn / P11a_inyeccion**: prosa() previa a la medición: invariante exacto.
- **anclaje_turno_sn / P11b_eliminacion**: prosa() idempotente: invariante exacto.
- **anclaje_ventana / P9**: Permutar el orden de los 8 turnos no cambia la suma de los conteos de lemas de la ventana (cada turno se lematiza por separado): el vector TF-IDF y su coseno son idénticos. Invariante exacto por construcción.
- **anclaje_ventana / W1_ventana_otro_par**: Ventana de 8 turnos de otro par: el coseno con la referencia de este escenario baja (los lemas específicos del otro escenario no están en la referencia).
- **anclaje_ventana_sn / P9**: Suma de conteos por turno: invariante exacto.
- **anclaje_ventana_sn / W1_ventana_otro_par**: Ventana ajena sin nombres: baja, menos que con nombres (se excluye el atajo de nombrar).

### 4.2 Hash

SHA-256 del `json.dumps(MATRIZ, sort_keys=True, ensure_ascii=False)` (UTF-8), versión `a4bc-1`, fecha 2026-09-20 (archivo escrito a las 21:21):

```
67e6133a51c4c23001038a19bb9894e2afa7b99b5dfef91955e0ee789ec0c54e
```

Verificado por `test_matriz_a4bc.py::test_hash_de_la_matriz_prespecificada_no_ha_cambiado`. La matriz completa (47 celdas) incluye dirección, magnitud mínima, justificación y criterio; editar cualquier campo cambia el hash.

## 5. Cómo se fijaron las magnitudes mínimas (`min`) y protocolo de congelación

**Regla**: `min` ≈ la mitad (redondeada a la baja) de la mediana del efecto observado en la muestra de DESARROLLO con un borrador del cálculo, para exigir un efecto de tamaño no trivial sin exigir el efecto completo. Borrador de desarrollo (11 pares, 60-80 turnos muestreados por campaña; NO es la evaluación):

| cantidad (mediana de la diferencia pareada después − antes) | efecto en desarrollo | `min` fijado |
|---|---|---|
| cr2a_z, X1 (misma campaña lejana) | −2,62 | 1,0 |
| cr2a_z, X2 (misma campaña cercana) | −2,17 | 1,0 |
| cr2a_z, P8 (otro par) | −2,54 | 1,0 |
| cr2a_crudo, X1 / X2 / P8 | −0,095 / −0,080 / −0,099 | 0,04 |
| cr2b_cos_turno, P8 | −0,0106 | 0,005 |
| cr2b_cos_turno_sn, P8 | −0,0040 | 0,001 (deliberadamente menor que la mitad) |
| cr2b_cos_ventana8, W1 | −0,0202 | 0,01 |
| cr2b_cos_ventana8_sn, W1 | −0,0078 | 0,003 |
| cr2b_cos_turno, X1 (esperado «=») | −0,0007 (media −0,0012) | (control) |
| cr2b_cos_turno, P5 | no medido en desarrollo | 0,0005: estimación aritmética a priori (dos lemas de idf máximo entre ~100), NO calibrada |
| cr2a_z_ventana8, P9 y W1 | no medido en desarrollo | 1,0: heredado del turno (X2 / P8); NO calibrado |
| S1 (desc.) | no medido | 0,1 / 0,005: nominales; sin veredicto |

Con el borrador, el `z` de una respuesta real tiene mediana 2,52 (media 2,67) y tras sustituirla por una ajena queda con mediana −0,30/−0,35 (media ≈ 0, sd ≈ 1): el nulo funciona. Coseno de una narración propia con su referencia: mediana 0,031 (media 0,069) por turno y 0,066 (media 0,103) por ventana de 8.

**Protocolo (obligatorio, en este orden)**:
1. Programar los instrumentos con las definiciones de la sección 2 y las pruebas unitarias.
2. **Correr DESARROLLO** con el código final (`correr_a4bc.py --desarrollo`, pares de la sección 1.1, semilla 20260919). Comprobar que, para cada celda direccional calibrada, `min` ≤ 0,5 × |mediana observada en desarrollo|.
3. Si todas cumplen: el hash queda `a4bc-1` y se pasa a la evaluación. Si alguna no cumple: se crea una versión `a4bc-2` con nuevo hash y **fecha y hora** de registro en el apéndice 9, ANTES de tocar la muestra de evaluación, y se actualiza `test_matriz_a4bc.py` con ambos hashes (el `a4bc-1` se conserva como histórico).
4. Registrar en el apéndice 9 la hora de inicio de la corrida de evaluación.
5. Evaluación (una sola vez por versión). Las celdas que no aprueben se informan como hallazgos.

## 6. Límites conocidos (anticipados)

- **Léxico, no semántico**: sinónimos y paráfrasis invisibles (S1 lo cuantifica); anáfora y negación ignoradas.
- **Etiquetador**: los verbos en 2.ª persona se lematizan mal; la señal viene de sustantivos y adjetivos. El texto en mayúsculas o sin tildes degrada el etiquetado (C2, C3 lo prueban).
- **Estilo G1 frente a G2**: G1 narra en impersonal («los dedos recorren») y G2 en 2.ª persona («recorres con los dedos»); la comparación entre brazos con el mismo instrumento sigue mezclando estilo. El z se calibra dentro de cada campaña, lo que reduce pero no elimina este efecto.
- **Escenas largas**: el nulo de campaña completa da z > 0 a respuestas que solo continúan la escena; z no aísla la «acción específica» de la «escena en curso».
- **Anclaje**: el coseno depende de la referencia (lore + fixtures); mide vocabulario compartido, no «arraigo» en sentido pleno. La ventana de 8 turnos es una elección (desarrollo: identificación 41 % por turno, 50 % por ventana).
- **Deriva**: el anclaje a la referencia inicial cae también si el mundo evoluciona legítimamente (nuevos PNJ y lugares); no distingue deriva de evolución. Solo el caso extremo (narrar otro escenario) es inequívoco.
- **Perturbaciones sintéticas**: un defecto insertado no es un defecto natural; la sensibilidad no es la tasa de error en la naturaleza.
- **Sin validez externa**: no hay correlación con juicio humano (rúbrica) en este trabajo; son instrumentos de validez de contenido.

## 7. Literatura (solo lo verificado con búsqueda web el 2026-09-20; lo demás, «NO VERIFICADO»)

Métricas de solapamiento léxico y de relevancia en evaluación de diálogo:

- Liu, C.-W., Lowe, R., Serban, I. V., Noseworthy, M., Charlin, L., Pineau, J. (2016). *How NOT To Evaluate Your Dialogue System: An Empirical Study of Unsupervised Evaluation Metrics for Dialogue Response Generation.* EMNLP 2016. DOI 10.18653/v1/D16-1230. https://aclanthology.org/D16-1230/ — verificado (resumen en arXiv 1603.08023): las métricas de solapamiento y de embeddings (BLEU, METEOR, ROUGE, embeddings) correlacionan «muy débilmente» con el juicio humano en Twitter y «nada» en Ubuntu. Implicación aquí: **usar el solapamiento como medida absoluta de calidad sería inválido**; mi puntaje no evalúa «buena respuesta» sino una propiedad estrecha (la respuesta comparte lemas con ESTA acción más de lo que comparte con otras) y se calibra contra un nulo.
- Lowe, R., Noseworthy, M., Serban, I. V., Angelard-Gontier, N., Bengio, Y., Pineau, J. (2017). *Towards an Automatic Turing Test: Learning to Evaluate Dialogue Responses.* ACL 2017. https://aclanthology.org/P17-1103/ — verificado: su modelo aprendido correlaciona con humanos mucho más que métricas de solapamiento como BLEU. DOI: NO VERIFICADO.
- Tao, C., Mou, L., Zhao, D., Yan, R. (2018). *RUBER: An Unsupervised Method for Automatic Evaluation of Open-Domain Dialog Systems.* AAAI 2018. DOI 10.1609/aaai.v32i1.11321. https://ojs.aaai.org/index.php/AAAI/article/view/11321 — verificado: combina una métrica con referencia y otra SIN referencia que relaciona respuesta y consulta con un modelo aprendido.
- Mehri, S., Eskenazi, M. (2020). *USR: An Unsupervised and Reference Free Evaluation Metric for Dialog Generation.* ACL 2020. https://aclanthology.org/2020.acl-main.64/ — verificado: métrica sin referencia y sin supervisión humana, con modelos entrenados que miden cualidades del diálogo. DOI: NO VERIFICADO.
- Nota: los trabajos posteriores sin referencia (RUBER, USR) usan modelos neuronales entrenados; son la alternativa semántica que aquí se descarta por auditabilidad y determinismo (sección 2.2). Que una métrica LÉXICA de «responsividad» mida específicamente lo que reclamo (respuesta a la acción) no está respaldado por estas fuentes: **NO VERIFICADO**; es una decisión de diseño puesta a prueba con las perturbaciones de este documento.

Ponderación TF-IDF y truncación:

- Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. *Journal of Documentation*, 28(1), 11–21. DOI 10.1108/eb026526 — verificado (origen del idf: ponderar los términos por su frecuencia en la colección).
- Salton, G., Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513–523. DOI 10.1016/0306-4573(88)90021-0 — verificado.
- Mayfield, J., McNamee, P. (2003). Single n-gram stemming. SIGIR 2003, pp. 415–416. DOI 10.1145/860435.860528 — verificado (truncar a los 4 primeros caracteres funcionó bien como pseudo-raíz en sus idiomas de prueba; la afirmación para el español: NO VERIFICADO). Aquí probé la truncación en desarrollo y no aportó.

Tests con nulos por permutación y coherencia por permutación:

- Good, P. (2005). *Permutation, Parametric, and Bootstrap Tests of Hypotheses* (3.ª ed.). Springer, Nueva York. ISBN 0-387-20279-X — verificado como referencia bibliográfica (no leí los capítulos).
- Phipson, B., Smyth, G. K. (2010). Permutation P-values should never be zero: calculating exact P-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology*, 9(1), Art. 39. DOI 10.2202/1544-6115.1585 — verificado (p = (1+b)/(1+m), que uso en `p_perm`).
- Barzilay, R., Lapata, M. (2008). Modeling local coherence: an entity-based approach. *Computational Linguistics*, 34(1), 1–34. DOI 10.1162/coli.2008.34.1.1 — verificado (origen de la perturbación por permutación de orden que reutiliza P9).
- Coeficiente de Ochiai (coseno binario) y el umbral |δ| ≥ 0,147 (Romano et al., 2006) heredado del arnés: NO VERIFICADOS aquí.

## 8. Referencia rápida de archivos

`experimento/scripts/instrumentos/`: `matriz_a4bc.py`, `test_matriz_a4bc.py`, `lemas_es.py`, `respuesta_accion.py`, `anclaje_escenario.py`, `perturbaciones_a4bc.py`, `correr_a4bc.py` y sus pruebas; caché de lemas en `experimento/scripts/instrumentos/_cache/`. Informe: `docs/reportes/sensibilidad_a4bc.md` (+ `.csv`).

## 9. Apéndice «post hoc» y registro de avance

### 9.1 Versión a4bc-2 (registrada 2026-09-20 23:39, ANTES de correr la evaluación)

- **Qué se vio**: la corrida de DESARROLLO con `a4bc-1` (`docs/reportes/sensibilidad_a4bc_desarrollo_a4bc-1.md`; 11 pares de desarrollo, semilla 20260919, 150 turnos por brazo + 60 ventanas) mostró que, en G2, cinco celdas direccionales tenían un efecto menor que el estimado con el borrador agrupado de ambos brazos, y la regla del §5 (`min` ≤ 0,5 × |mediana|, con el brazo de menor efecto) no se cumplía: cr2b_cos_turno/P8 (G2: −0,0064), cr2b_cos_ventana8/W1 (−0,0144), cr2b_cos_ventana8_sn/W1 (−0,0054), cr2a_crudo/X2 (−0,0770) y cr2a_z_ventana8/P9 (−1,373 en G1; celda no medida en el borrador). La regla se extendió a todas las celdas direccionales medidas en desarrollo.
- **Qué cambió** (`experimento/scripts/instrumentos/matriz_a4bc_v2.py`, solo `min`): cr2a_crudo/X2 0,04 → 0,035; cr2b_cos_turno/P8 0,005 → 0,003; cr2b_cos_ventana8/W1 0,01 → 0,007; cr2b_cos_ventana8_sn/W1 0,003 → 0,0025; cr2a_z_ventana8/P9 1,0 → 0,5. Direcciones, controles, celdas exactas/descriptivas, justificaciones y criterios: sin cambios.
- **Hash a4bc-2**: `e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744` (prueba en `test_matriz_a4bc_v2.py`; `a4bc-1` queda como histórico: `67e6133a…c54e`). Con a4bc-2, la corrida de desarrollo cumple la regla en todas las celdas (`sensibilidad_a4bc_desarrollo.md`).
- **Qué NO se cambió, aunque el desarrollo lo sugería**: en desarrollo varios controles «=» no exactos fallan por la regla del arnés (cuenta signos, no magnitudes), casi todos con un desplazamiento mediano < 2 % (etiqueta post hoc de lectura, añadida al informe; no cambia el criterio ni los conteos), y algunas celdas de la variante `_sn` (P8 por turno; W1 por ventana en G2) no son significativas. Las direcciones esperadas se conservan tal como se pre-especificaron; esos casos se informarán como hallazgos en la evaluación.
- Corrección de descripción: en §5 el efecto del borrador agrupaba ambos brazos; la calibración vigente usa el brazo de menor efecto.

### 9.2 Registro de avance
- 2026-09-20 21:21 — matriz `a4bc-1` y su prueba de hash en disco (antes de programar los instrumentos).
- 2026-09-20 23:1x — documento de diseño redactado.
- 2026-09-20 23:3x — HECHO con pruebas escritas antes (rojo verificado, luego verde): `lemas_es.py`, `respuesta_accion.py`, `anclaje_escenario.py`, `perturbaciones_a4bc.py`, `contexto_a4bc.py`, `correr_a4bc.py` (103+ pruebas); caché de lemas de las 42 campañas (~13 min); corrida de desarrollo a4bc-1 y registro de a4bc-2 (9.1).
- 2026-09-20 23:42-23:44 — corrida de EVALUACIÓN con `a4bc-2` (muestra del arnés, semilla 20260920) EJECUTADA (una vez): `python experimento/scripts/instrumentos/correr_a4bc.py`. Salida: `docs/reportes/sensibilidad_a4bc.md` (+ `.csv`, `_distribucion.csv`). Se ejecuta una sola vez por versión.
- 2026-09-20 23:5x — informe escrito con lectura a mano (`docs/reportes/sensibilidad_a4bc.md` §6). Resultado: 64 celdas aprobadas, 18 fallan, 4 descriptivas. Todos los controles positivos direccionales de cr2a_z/cr2a_crudo/z_ventana8 y de cr2b (cos con y sin nombres, ventana) aprobados salvo `cr2b_cos_turno_sn` ante P8 en G1; fallan sobre todo controles «=» por la regla de signos del arnés (11 de 17 con efecto < 2 %) y `cr2b_cos_turno_sn` ante P5 (sube, error de pre-especificación). cr2a_z no capta la deriva (plano); el anclaje cae, sostenido sobre todo por nombres. ESTADO: completo; pendiente solo revisión humana.
