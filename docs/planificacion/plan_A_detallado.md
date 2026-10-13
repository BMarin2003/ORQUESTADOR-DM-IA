# Plan A detallado: validación de los instrumentos deterministas sin evaluadores humanos

Estado al 2026-09-20 (noche). Complementa `docs/plan_validacion.md` y `docs/matriz_cobertura_rubrica_instrumentos.md`.
Fuentes de método: `docs/research/r1_segunda_persona_agencia.md` (2.ª persona y agencia) y `docs/research/r2_sensibilidad_y_auditoria.md`
(sensibilidad y auditoría). Todo lo que hicieron los subagentes fue verificado antes de aceptarse (pruebas ejecutadas, cifras recalculadas,
referencias comprobadas por muestreo).

## 1. Estado por paso

| Paso | Qué | Estado |
|---|---|---|
| A1 | Matriz de cobertura rúbrica ↔ instrumentos | hecho |
| A2 | Sensibilidad por perturbación, línea base con los instrumentos actuales | hecho y verificado (`docs/reportes/sensibilidad_baseline.md`, 123 pruebas, fidelidad 0 discrepancias en 392 turnos); falta re-correr con los instrumentos nuevos |
| A3 | Auditoría de precisión y recall por etiquetado del investigador | herramientas listas y probadas (hoja ciega + análisis); **pendiente el visto bueno del asesor y el etiquetado** de la muestra de confirmación de `persona2` |
| A4a | Recalcular los instrumentos numéricos con texto sin artefacto de formato | **hecho y verificado** (`experimento/scripts/reporte_v2/`, 48 pruebas; ver `docs/reportes/reporte_v2_formato_normalizado.md`). `cr1` y `cl2_pnj_inactivo_actua` recalculados también (2026-09-21, `docs/reportes/reporte_v2_booleanos.md`): fidelidad 0 discrepancias en 58 800 turnos; la diferencia de `cr1` entre brazos era artefacto de formato (110 de 139 marcas de G1 eran la línea mecánica) |
| A4b/c | Instrumentos nuevos: respuesta a la acción específica (CR-2a) y anclaje al escenario (CR-2b) | **hecho y verificado** (matriz a4bc-2 con SHA-256 `e1570cad…`, 109 pruebas propias; evaluación única: 64 aprobadas, 18 fallan, 4 descriptivas; ver sección 3c) |
| A4d | Detector de usurpación en 2.ª persona (`experimento/scripts/instrumentos/persona2.py`) | **v2b congelado** (100 pruebas, determinista, hashes registrados); tasas sobre 26 293 turnos por brazo fuera de desarrollo: primaria G1 0.2 % y G2 4.0 %, secundaria G1 0.7 % y G2 7.2 % (precisión aún sin medir); **enchufado al arnés A2** (ver sección 3b) |
| A5 | Declarar como límite lo no medible | pendiente |

## 2. Hallazgos de A2 (línea base, n = 150 turnos por brazo)

1. **Los tres detectores de 3.ª persona** (`qn2_pj_piensa_narrado`, `qn2_pj_accion_revisar`, `cl2_pc_hp_contradice_narracion`) marcan **100 %**
   con el nombre del PJ y **0 %** con la misma usurpación en 2.ª persona, en G1 y en G2. El punto ciego está medido con inyecciones controladas.
2. `qn2_pj_accion_revisar` casi no puede dispararse: 149 de 150 turnos llevan tirada y su condición es «sin tirada».
3. **Artefacto de formato:** 7 de 9 controles invariantes se rompen al inyectar el formato de G1 en texto de G2, y 6 de 9 al quitarlo en G1. TTR,
   n-gramas, Fernández-Huerta, Jaccard, densidad de grafo y gramaticalidad no son comparables entre brazos tal como están.
4. `cr2_nombres_no_reconocidos` marca 99.9 % de los turnos de G1 (G2: 5.7 %): saturado, no detecta nombres inventados.
5. `cr2_entidad_grafo_densidad` y `grafo_lema_densidad` **no distinguen una narración de otro escenario** (P8): son insensibles a la deriva.
6. `cl2_pnj_inactivo_refinado` detecta ~10 % (G2) y ~2 % (G1) de los PNJ inactivos inyectados: solo ve nombres de una palabra.
7. `ventana_bucles_*` no reaccionan a la permutación de turnos; la expectativa «sube» pudo ser un exceso de la pre-especificación (pendiente de revisar).
8. Sí responden como se pre-especificó: `cr1` ante pifia+éxito, TTR y n-gramas ante párrafo duplicado, Jaccard ante otro par, gramaticalidad ante barajar palabras.
9. Un error de pre-especificación reconocido y conservado: la expectativa «sin cambio» de `cl2_pnj_inactivo_actua` ante P8 (sustituir el texto borra marcas reales).

## 3. Hallazgos sobre la 2.ª persona

- No existe base directa para un detector determinista de usurpación de agencia en 2.ª persona (R1). Es aporte propio de la tesis: el detector en español
  con sujeto omitido, la condición «no declarado por el jugador» y los léxicos.
- spaCy `es_core_news_sm` etiqueta `Person=2` solo en el 14 % de los hallazgos de 2.ª persona: el reconocimiento por léxico es imprescindible.
- **Definición de la métrica:** se propone medir el **cumplimiento de la regla de oro del prompt del DM** (no describir decisiones, pensamientos, emociones ni
  diálogo del PJ), que es un criterio objetivo, y no «usurpación de agencia» en sentido general.
- La categoría de acciones físicas «no declaradas» da precisión cercana a 0 en la muestra de desarrollo (7 de 7 filas leídas eran la ejecución de lo declarado
  con otro verbo). Se rediseña y queda como métrica secundaria experimental; la primaria es mental y verbal.

### 3b. `persona2` en el arnés A2: equivalencia por persona gramatical (2026-09-20)

`experimento/scripts/sensibilidad/correr_persona2.py`, expectativas fijadas antes de correr (SHA-256 `3ac6a23c…`), detector v2b sin modificar (hashes verificados), 150 turnos por brazo,
informe en `docs/reportes/persona2_equivalencia.md`.

- **Control positivo (3.ª persona con nombre):** 100 % en las cuatro categorías y en la muerte del PJ, en G1 y G2. **Habla en 2.ª persona:** 100 %. **Muerte del PJ en 2.ª persona:** 100 %.
- **Controles que no deben marcarse** (percepción, consecuencia mecánica, pregunta u opciones, «tú» en boca de un PNJ): 0/150 en los dos brazos (límite superior 2.5 %).
- **Criterio pre-especificado NO cumplido** en 2.ª persona para decisión (67 % G1 / 76 % G2), pensamiento (80 % / 80 %) y emoción (71 % / 81 %): el límite inferior de Wilson queda bajo 0.80.
- **Causa (diagnóstico posterior, plantilla por plantilla):** 9 de las 12 plantillas dan 100 %. Las tres restantes fallan siempre: «Resuelves quedarte…» (*resolver* no está en el léxico), «Notas cómo la vergüenza…»
  (*notar* se excluye a propósito por ser percepción) y «Te dices que…» (sí se marca, pero como HABLA y no como COGNICIÓN). El recall de cada celda es, en la práctica, la mezcla de plantillas del arnés.
- **Impacto real:** esos patrones casi no existen en el texto real (*resuelves*: 7 de 77 413 turnos; *te dices*: 0; *notas* es sobre todo percepción). El recall natural lo acota la muestra de confirmación
  (100 turnos sin marca con verbo mental de 2.ª persona), no las inyecciones.
- **Decisión:** el detector queda congelado y la limitación se declara (léxico cerrado, sin *resolver* ni *notar* + emoción); no se reescribieron las expectativas ni el detector tras ver el resultado.
- Exploratorias: acción física no declarada inyectada 70 % (G1 y G2), paráfrasis fuera del léxico 61 % (G1) y 66 % (G2). `accion_2p` salió primero 0/0 por usar una plantilla que exige turno sin tirada; se rehízo con `P1_accion_sin_tirada` (el detector no usa la tirada).
- Tasa natural de marcas primarias en los mismos turnos, sin inyectar: G1 0.0 %, G2 4.0 %.

### 3c. Instrumentos nuevos CR-2a (respuesta a la acción) y CR-2b (anclaje al escenario) (2026-09-20)

Código en `experimento/scripts/instrumentos/` (`respuesta_accion.py`, `anclaje_escenario.py`, `matriz_a4bc*.py`, `correr_a4bc.py`), diseño y literatura en `docs/research/a4bc_diseno_instrumentos.md`,
evaluación en `docs/reportes/sensibilidad_a4bc.md`. Verificado por mí: hashes de la matriz recalculados, diferencia a4bc-1 → a4bc-2 = 5 magnitudes `min` y ninguna dirección (registrada antes de evaluar),
pares de desarrollo (07, 08, 10, 15, 17, 18, 19, 22, 26, 27) y de evaluación (09, 11, 13, 14, 16, 20, 21, 23, 24, 25) disjuntos, recuento 86 celdas contra el CSV, cifras de deriva recalculadas, `persona2.py` y arnés sin modificar.

- **Direccionales: 25 de 26 aprobadas.** CR-2a cae 2.3–2.9 unidades z ante la respuesta de otro turno, de otro par o una ventana desalineada, en ambos brazos; el anclaje cae ante otro escenario. La única que falla: anclaje por turno sin nombres ante otro escenario en G1 (demasiado ruidoso; la ventana de 8 sí responde).
- **Controles «sin cambio»: 39 de 56 aprobados.** Los 17 que fallan son sobre todo minúsculas, sin tildes, barajar palabras y nombres inventados. Por magnitud, unos 11 mueven la mediana menos de un 2 %; el resto, entre el 5 % y el 25 %
  (mi recuento sobre medianas da ocho por encima del 5 %, el informe cuenta seis). El coseno por turno depende del etiquetador de spaCy y de las mayúsculas: no es invariante al orden de palabras.
- **Error de pre-especificación conservado:** el coseno sin nombres sube 9–16 % ante nombres inventados (la oración de relleno comparte lemas con el escenario).
- **Deriva en ventanas de 200 turnos (descriptivo):** CR-2a es casi plano (G2 2.81 → 2.74; G1 2.87 → 2.68), no capta deriva. El anclaje sí cae (coseno por ventana de 8: G1 0.15 → 0.10, G2 0.10 → 0.07; identificación del escenario G1 77 % → 58 %, G2 58 % → 47 %),
  pero sin nombres queda casi plano: la caída la sostienen sobre todo los nombres propios. No distingue deriva de evolución legítima del mundo.
- **Límites:** perturbaciones sintéticas, sin juicio humano, diccionario de sinónimos mínimo (el límite léxico queda demostrado, no cuantificado). El agente marcó como NO VERIFICADOS los DOI de Lowe 2017 y USR, el coeficiente de Ochiai y el umbral de Romano.
- Discrepancias menores del informe del agente: dice «11 pares» de desarrollo y hay 10; reparte 103 + 129 pruebas donde yo cuento 109 + 123 (mismo total, 232).

### 3d. `cr1` y `cl2_pnj_inactivo_actua` sobre texto normalizado (2026-09-21)

`experimento/scripts/reporte_v2/recalcular_booleanos.py` → `datos/datos_v2/booleanos/`, informe `docs/reportes/reporte_v2_booleanos.md`. El recálculo sobre texto crudo reproduce lo guardado (0 discrepancias en 58 800 turnos).

- **`cr1`:** G1 0.47 % → 0.10 % de turnos; G2 0.07 % → 0.07 %. La diferencia entre brazos (Holm 3.8e-6) desaparece (0.33). Las 110 marcas eliminadas son «Fallo (…). No logras…» de la línea mecánica de G1.
  Las marcas que quedan son casi todas «no logras…» (28 de 29 en G1, 16 de 21 en G2, lectura rápida): el detector ignora la negación y es de baja precisión en ambos brazos.
- **`cl2_pnj_inactivo_actua`:** no cambia (6 de 2 564 marcas en G1). G1 8.7 % vs G2 2.8 %, HL +5.1 pp, Holm 0.17. Mide *mención* de un PNJ inactivo, no que actúe; precisión sin auditar.

### 3e. A2 para Szigriszt-Pazos, MTLD y MATTR (extensión posterior, 2026-09-21)

`experimento/scripts/sensibilidad/correr_extension_sz_mtld.py` → `docs/reportes/sensibilidad_ext_sz_mtld.md` (+ `.csv`). La línea base (hash `735308b3…`) **no se reescribió**: las expectativas nuevas se fijaron antes de correr
(SHA-256 `59998b16…`, en `docs/reportes/sensibilidad_ext_sz_mtld_expectativas.json`) y las 870 celdas previas salieron idénticas (0 difieren).

- **`qn1_legibilidad_sz`:** P6 invariante exacto (Δ = 0,0). P11a en G2 incumple (+1,5), igual que Fernández-Huerta (+1,6): el formato de G1 añade palabras y frases. Era lo predicho; el spec original lo daba por invariante «por construcción», lo cual solo vale para P6.
- **`ventana_mtld`, `ventana_mattr` (P9, control estadístico):** ambos «responden» como sin cambio. En G1 MTLD sube +2,0 de mediana (δ pareado 0,43) sin significancia (Holm 0,17): el control no detecta sesgo, pero tampoco lo descarta con potencia.
- **Clasificación sin cambios:** legibilidad no tiene celda confirmatoria posible en este diseño; MTLD/MATTR necesitarían una perturbación de ventana que inyecte repetición (no existe; decisión aparte).

### 3f. A2 para Jericho recall y relojes reconocidos (2026-09-21)

`experimento/scripts/sensibilidad/correr_jericho_relojes.py` → `docs/reportes/sensibilidad_jericho_relojes.md` (+ `.csv`); diagnóstico posterior en `sensibilidad_jericho_relojes_diagnostico.md`. Expectativas fijadas antes de correr
(SHA-256 `783c4e43…`, en `sensibilidad_jericho_relojes_expectativas.json`); la línea base y las demás extensiones no se tocaron. El script lo escribió otra sesión sin acceso a la base y **nunca se había ejecutado**; se
corrigió antes de la primera corrida (import inexistente, supresión en toda la ventana del instrumento, texto normalizado, resultado «después» con las funciones reales, 27 parejas) y una vez más tras la primera corrida completa
(RJ2 13/16 por un error de mayúsculas en la supresión; la corrida 1 se conserva como `..._corrida1_con_error.*`).

- **A2 mecánico:** JQ1 40/40, JQ2 40/40, RJ1 7/7 (solo hay 7 relojes sin reconocer), RJ2 16/16. Es 100 % por construcción (se inserta o se quita el léxico exacto): comprueba que el instrumento lee la ventana correcta
  y responde al léxico, no que ese léxico signifique que el evento se narró.
- **Diagnóstico posterior (no pre-registrado):** frente a un turno al azar con el mismo léxico, Jericho recall pasa de 12,9 % a 25,9 %: discrimina en `npc.status` (+21 a +25 pp) y casi nada en `npc.affinity`
  (+2 a +4,5 pp; 55 % de los eventos). Los relojes reconocen 88,3 % reales frente a 89,8 % por azar: no discriminan; sin palabras funcionales son 73,3 % frente a 61,1 % por azar, así que no basta con quitarlas.
- **Clasificación:** Jericho sigue «exploratorio» (con la salvedad de npc.affinity); relojes siguen «no usar», ahora con evidencia. H1e sigue sin instrumento confirmatorio.

## 4. Secuencia y dependencias

1. Congelar `persona2` (con registro de los turnos usados en desarrollo) → enchufarlo en el arnés A2 → **equivalencia por persona gramatical** (nombre, pronombre,
   2.ª persona) y controles invariantes → si no pasa, no se usa.
2. A4a: recalcular los instrumentos numéricos sobre texto normalizado y medir cuántas conclusiones G1-vs-G2 cambian.
3. A4b/c: instrumentos nuevos, con expectativas fijadas antes de implementarlos (SHA-256) y validados en el arnés.
4. A3: etiquetar (el investigador, a ciegas) la muestra de confirmación; segundo etiquetador sobre el 20 %: acuerdo positivo/negativo, AC1 y kappa.
5. Recalcular las 42 campañas (y las de Par01-06 si procede) con los instrumentos v2 y emitir el reporte v2, declarado como **corrección posterior (post hoc)**.
6. A5: límites declarados (interés y creatividad, voz del personaje, validez de constructo sin criterio humano).

## 5. Aprobaciones que necesita el asesor antes de correr la parte confirmatoria

- La matriz de expectativas de A2 y sus umbrales (0.80 de recall inyectado, 90 % en la dirección esperada, |r| ≥ 0.5): son propuestas de R2, no de la literatura.
- Que el etiquetado del investigador se use **solo para auditar los instrumentos** (presencia objetiva de un defecto según un codebook) y no para calificar la calidad narrativa.
- Que las correcciones a los instrumentos se declaren como posteriores y se apliquen por igual a los dos brazos.
- Redefinir la métrica de agencia como cumplimiento de la regla de oro del prompt.

## 6. Carga estimada de etiquetado (supuesto: 40 s por turno)

- Muestra de confirmación de `persona2`: ≈ 300 filas ≈ 3.3 h.
- Precisión de otros detectores (100 marcas cada uno; prioridad: los tres ciegos en G2, luego `cl2_pnj_inactivo_actua` y `cr1`): ≈ 2 h por detector.
- Lo completo de R2 (≈ 3 400 etiquetas, ≈ 38 h) no es viable para una sola persona: hay que priorizar y declarar el resto como límite.

## 7. Amenazas que este plan no cubre

Validez de constructo y consecuencial (no hay criterio humano por diseño), representatividad de las inyecciones sintéticas, recall natural solo acotado,
etiquetador único y autor de los instrumentos, ciego imperfecto (la persona y el estilo delatan el brazo), invarianza de medida entre brazos, dependencia entre turnos
de una misma campaña, errores de LanguageTool y spaCy, y deriva del código (todo cambio de un detector exige una muestra nueva).

## 8. Etiquetado de persona2 (A3): cómo se hace

- **Detector congelado**: `experimento/scripts/instrumentos/persona2.py` v2b y `lexicon_persona2.json`, con sus hashes en `datos/validacion/persona2_congelado.sha256`. Si cambia
  cualquiera de los dos, la muestra de confirmación deja de ser válida y hay que generar otra con una semilla nueva.
- **Muestra de confirmación** (semilla 20260921): 515 turnos que no aparecen en los 6 214 turnos de desarrollo (`datos/validacion/persona2_desarrollo_turnos.csv`): sonda aleatoria de
  200 (100 por brazo, sin filtro), 175 marcas primarias (cognición, emoción, habla, volición), 40 de la categoría experimental de acciones y 100 turnos sin hallazgo
  con un verbo mental de 2.ª persona no marcado. La hoja `confirmacion_persona2_muestra.csv` de E1 muestra la categoría y la frase marcada, lo que sesga: **no se usa para etiquetar**.
- **Hoja de etiquetado correcta**: `python experimento/scripts/etiquetado_persona2.py --evaluador E1` genera `datos/validacion/etiquetado_persona2_E1.html` (515 turnos, orden aleatorio) y
  `--evaluador E2 --fraccion 0.2` el subconjunto estratificado del 20 % (102 turnos) para el segundo etiquetador. Solo muestra la acción del jugador y el turno completo del DM
  (con el formato de G1 normalizado); no muestra brazo, par, campaña, categoría ni frase marcada. Guarda solo en el navegador y exporta un CSV.
- **Orden aleatorio a propósito**: si se para antes de terminar, lo etiquetado sigue siendo una submuestra aleatoria de cada estrato, así que las estimaciones siguen siendo válidas
  (con intervalos más anchos).
- **Análisis**: `python experimento/scripts/analizar_persona2.py --etiquetas etiquetas_persona2_E1.csv [--etiquetas2 etiquetas_persona2_E2.csv]` produce
  `docs/reportes/auditoria_persona2.md`: precisión estricta e indulgente por estrato y brazo, prevalencia y recall sobre la sonda, tasa de falsos negativos, tipos atribuidos y
  acuerdo entre etiquetadores (acuerdo observado, positivo y negativo, kappa, PABAK y AC1). Sus fórmulas están verificadas contra valores conocidos (`experimento/scripts/test_analizar_persona2.py`).
- **Requisito previo**: la aprobación del asesor para usar etiquetado humano solo como auditoría de los instrumentos (sección 5).

- **Nota de normalización**: `prosa()` deja residuos de formato en ~0.7 % de los turnos de G1 (etiquetas en negrita, «Mecánica» capitalizada, JSON crudo). Las hojas actuales no tienen residuos (comprobado), pero al regenerarlas hay que usar `experimento/scripts/reporte_v2/normalizacion.py::normalizar_turno`.
