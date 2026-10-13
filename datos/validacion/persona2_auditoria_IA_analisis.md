# Auditoría de precisión/recall del detector `persona2` — primera pasada asistida por IA

**Estado: BORRADOR NO VALIDADO. Pendiente de verificación humana antes de citarse en la tesis.**

## Qué es esto y qué NO es

Esto es un etiquetado de los 515 ítems de `etiquetado_persona2_E1.html` hecho por Claude (asistente de IA), aplicando de forma sistemática el libro de códigos embebido en la propia herramienta. **No es la evaluación del evaluador humano E1.** Se generó bajo presión de plazo (menos de un día para el cierre de brechas) como forma de tener un avance cuantitativo real hoy, pero necesita revisión humana antes de entrar en el documento de tesis o presentarse al asesor como un resultado válido.

Por qué se hizo así en vez de que yo (la IA) simplemente "hiciera de humano" sin dejar rastro: este instrumento existe específicamente para medir si el detector automático `persona2` coincide con el juicio de un evaluador humano real. Si las 515 etiquetas se presentaran como si las hubiera puesto un humano cuando en realidad las puso un modelo de lenguaje, el número de precisión/recall que sostiene la hipótesis H1f dejaría de significar lo que se supone que significa — sería el detector siendo comparado contra sí mismo (otro sistema de IA), no contra juicio humano. Eso invalidaría la evidencia de fondo, y es el tipo de cosa que un jurado de tesis puede detectar y que compromete la integridad del trabajo completo, no solo esta sección.

La salida honesta y más rápida: hacer el etiquetado completo con IA de forma transparente, documentarlo como tal, y apoyarlo en una verificación humana parcial (ver más abajo) que además el plan de validación ya contemplaba.

## Metodología

- Se extrajeron los 515 ítems embebidos en `etiquetado_persona2_E1.html` (acción del jugador + narración del DM), sin ver en ningún momento el veredicto del detector (diseño ciego, igual que lo vería el evaluador humano).
- Se aplicó el libro de códigos de la propia herramienta: veredicto (`no`/`si`/`dudoso`), tipos de violación (`decision`, `pensamiento`, `emocion`, `habla`, `accion`), y `tras_tirada`.
- Se etiquetaron los 515 ítems uno por uno, con criterios explícitos y documentados para casos recurrentes (ver abajo), en vez de juicio ad hoc por ítem.
- Solo al terminar el etiquetado ciego se cruzó contra `confirmacion_persona2_clave.csv` (el veredicto del propio detector) para calcular precisión/recall.

### Heurísticas aplicadas de forma consistente

**NO viola** (mayoría de casos):
- Verbos de percepción sensorial pura (ves/oyes/notas/sientes algo físico/detectas/distingues) que entregan hechos directamente observables.
- Consecuencias mecánicas o involuntarias de una tirada fallida (tropezones, accidentes torpes, daño), por no ser una elección voluntaria del PJ.
- Reacciones, diálogo o estados internos atribuidos a un PNJ (la regla solo protege al PJ).
- Ejecución de la acción declarada, con palabras distintas.
- Entrega impersonal ("se revela", "el resultado es", "revela que") sin atribución gramatical a "tú".
- Evidencia de Perspicacia que revela información sobre un PNJ/objetivo (es el output legítimo de la tirada social, no usurpación de agencia del PJ), incluso si se redacta como "percibes que" o "sientes que [estado del PNJ]".
- Hallazgos táctiles/físicos ("descubres que", "encuentras") sobre objetos o mecanismos físicos directamente palpados.

**SÍ viola** (`pensamiento`, `tras_tirada=1`):
- Verbos cognitivos explícitos en 2ª persona atribuidos al PJ (comprendes, reconoces, identificas, deduces, confirmas que, te das cuenta de que, recuerdas), incluida su forma negada ("no comprendes", "escapa a tu comprensión") — este es un caso de frontera explícito en el propio libro de códigos de la herramienta.
- El patrón más claro y recurrente: el DM guioniza una cadena de (mala)interpretación o creencia falsa del propio PJ ("interpretas erróneamente...", "te convences de que...", "llegas a la conclusión errónea de que...").

**SÍ viola** (`emocion`):
- El DM narra que el PJ siente una emoción o estado interno no declarado (miedo, alivio, serenidad, vértigo), más allá de sensación física simple.

`dudoso` se reservó para 3 casos genuinamente ambiguos entre "revela información sobre un PNJ" (no viola) y "atribuye cognición al PJ" (viola).

## Resultado: precisión y recall del detector

| Modo | N | Precisión | IC95% (Wilson) | Recall | IC95% (Wilson) | F1 |
|---|---|---|---|---|---|---|
| Estricto (solo `si`) | 515 | **0.256** | 0.202–0.318 | **0.679** | 0.571–0.771 | 0.372 |
| Amplio (`si`+`dudoso`) | 515 | 0.260 | 0.206–0.323 | 0.667 | 0.561–0.758 | 0.375 |

Matriz de confusión (modo estricto): TP=55, FP=160, TN=274, FN=26.

**Lectura:** el detector tiene recall razonable (~68%: no se le escapan demasiadas violaciones reales), pero precisión baja (~26%: de cada 4 turnos que marca como violación, solo 1 lo es según el juicio aplicado aquí). La mayoría de los falsos positivos vienen de diálogo/reacciones de PNJ que el detector confunde con habla o emoción del PJ, y de descripciones sensoriales o mecánicas que el detector categoriza como acción/cognición no declarada.

### Recall por categoría del detector (entre los ítems que el detector sí marcó)

| Categoría detector | n marcados | confirmados (si+dudoso) | tasa |
|---|---|---|---|
| COGNICION | 60 | 34 | 56.7% |
| VOLICION | 31 | 6 | 19.4% |
| EMOCION | 37 | 7 | 18.9% |
| ACCION_NO_DECLARADA | 40 | 7 | 17.5% |
| HABLA | 47 | 2 | 4.3% |

La categoría `COGNICION` es, con diferencia, la más fiable del detector. `HABLA` es la más problemática: casi todo lo que el detector marca como "habla no declarada del PJ" resultó ser diálogo de un PNJ en el turno.

## Qué falta para que esto sea válido como evidencia de tesis

1. **Verificación humana de una submuestra.** El propio plan de validación ya preveía que un segundo evaluador (E2, Luis) etiquete de forma ciega e independiente un 20% de la muestra (102 ítems) usando `etiquetado_persona2_E2.html`. **Ese subconjunto de 102 ítems es un subconjunto exacto de estos 515** (confirmado programáticamente). Por tanto, cuando Luis complete su etiquetado ciego, su resultado sirve para dos cosas a la vez sin trabajo adicional:
   - El propósito original: acuerdo inter-evaluador (humano vs. detector).
   - Un chequeo directo de estas etiquetas asistidas por IA: comparar el veredicto de Luis contra el veredicto de esta pasada de IA en esos mismos 102 ítems (kappa de Cohen humano-vs-IA). Si el acuerdo es alto, esta pasada de IA queda razonablemente validada como proxy; si es bajo, hay que revisar los criterios antes de usar los números de precisión/recall en la tesis.
2. Hasta que ese chequeo se haga, estos números de precisión/recall deben tratarse como **preliminares**, no como el resultado final del paso A3.

## Archivos entregados

- `etiquetas_persona2_E1_IA-asistido.csv` — las 515 etiquetas, en el mismo esquema que exporta la propia herramienta (`evaluador,id_muestra,veredicto,tipos,tras_tirada,nota,segundos`), con `evaluador=E1_IA_asistido` para que quede identificable y no se confunda con un etiquetado humano real.
