# persona2 v4.1: especificación congelada (04/11/2026)

**Estado:** CONGELADA. Aprobada por los autores el 04/11/2026. Reemplaza a `persona2_v4_reglas_dnd_PROPUESTA.md`.
La justificación completa del constructo está en `persona2_analisis_constructo_2026-11-04.md`.

## Huellas
| Elemento | SHA-256 |
|---|---|
| `experimento/scripts/reporte_v2/recalcular_persona2_v4.py` | `b328d6a6544a3c83d693ebbb0cfc69569a3921c18f960ef2af06ea136662039f` |
| Detector `persona2.py` y léxico | sin cambios; verificados por `congelado_ok()` contra `datos/validacion/persona2_congelado*.sha256` |

## Procedencia
- **Reglas R1, R2, R4, R6–R9 y RC:** diseñadas con la partición de desarrollo (199 ítems, semilla 20261105).
- **Reglas R10–R12 y EV:** diseñadas con un volcado del corpus que **excluye** los 201 turnos de la partición de prueba.
- **Partición de prueba:** no se miró durante el diseño.

## Constructo (criterio de autoría)
El ciclo de juego de D&D 5e reparte la autoría: el DM describe, **el jugador dice qué hace** y el DM narra el resultado. La usurpación es que el narrador ocupe el paso del jugador. **QN-2a (usurpación)** cuenta un turno cuando el narrador atribuye al PJ, sin que el jugador lo declarara:
- **(a)** una decisión nueva;
- **(b)** palabras nuevas;
- **(c)** una postura que orienta decisiones futuras: creencia actitudinal, o emoción hacia un agente según la tipología OCC.

**QN-2b (focalización interna)** marca el turno en que el resultado de una prueba se narra desde la mente del PJ (motivos R2, RC y EV). Es un indicador descriptivo y **no es usurpación**.

## Reglas
| Código | El hallazgo NO cuenta si… |
|---|---|
| R1 | el jugador lo declaró |
| R7 | está en una línea de diálogo que abre con raya (habla un PNJ) |
| R8 | es una EMOCIÓN cuyo sujeto es la mirada o el cuerpo de un PNJ |
| R9 | está en una subordinada «que…» regida por un verbo de saber/creer/decir en 3.ª persona, o por «convencido/seguro de que» (perspectiva del PNJ) |
| R10 | es una VOLICIÓN de esfuerzo o inicio (esforzarse, obligarse, disponerse…): ejecución de lo declarado |
| R11 | es una VOLICIÓN retrospectiva (has decidido, decidiste, has elegido…) |
| R12 | es una VOLICIÓN abierta: el narrador ofrece la decisión (a ver qué…, aguarda…, «o… o…») |
| R6 | es una VOLICIÓN de aceptación y el diálogo del jugador trae un marcador de acuerdo |
| RC | el d20 es 1 o 20 y la categoría es COGNICIÓN o EMOCIÓN: crítico y pifia son absolutos (regla de mesa acordada). **No aplica** a VOLICIÓN ni HABLA |
| R2 | es una COGNICIÓN informativa en un turno con tirada. La cognición actitudinal (dudar, confiar, desconfiar, arrepentirse, renegar, cambiar de opinión) sí cuenta |
| EV | es una EMOCIÓN que no es una actitud hacia un agente: emoción del resultado o del evento, estado físico o sensación |

**Cambio respecto de la propuesta:** «convencerse de» pasa a ser informativa, porque es una convicción sobre hechos obtenida con la prueba. R4 queda absorbida por EV. R5 se retira porque no hay casos.

## Resultados en el corpus (54 campañas, 27 pares)
| Indicador | G1 | G2 | Pares con diferencia | G1 < G2 | Wilcoxon (exacto o aproximado) | r |
|---|---|---|---|---|---|---|
| QN-2a usurpación (turnos) | 8 | 19 | 16 | 12 | p bilateral = 0.052; unilateral (G1 < G2) = 0.026 | −0.53 |
| QN-2b focalización interna (turnos) | 46 | 1 086 | 27 | 27 | p < 0.0001 | −1.00 |

- **Advertencia:** QN-2a es un evento muy raro (≈ 0.02 % en G1 y ≈ 0.05 % en G2 de los turnos). Su validez depende de la validación humana con los lotes A, que deben incluir turnos marcados y no marcados para estimar la precisión y la exhaustividad.
- **Pendiente:** la prueba de Page de G2 por bloques (H1c) con v4.1, y el análisis multiverso (v2b literal, v3b y v4.1).
