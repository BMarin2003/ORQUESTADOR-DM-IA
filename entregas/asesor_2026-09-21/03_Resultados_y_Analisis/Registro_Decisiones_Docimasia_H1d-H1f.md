# Registro de decisiones de docimasia — H1d, H1e, H1f (OE-4, OE-5, OE-6)

Corpus cerrado: 27/27 parejas (54 campañas, 75,600 turnos). Este documento registra el razonamiento detrás de las tres decisiones de contraste de hipótesis ya incorporadas en el Capítulo 6 de la tesis (documento principal, carpeta `01_Tesis`), a partir de las Tablas 9, 11 y 13 del paquete de resultados (`Resultados_Tesis_OE1-OE6.md`).

## H1d — Coherencia reactiva (OE-4): no se sostiene con la evidencia confirmatoria

El único instrumento que superó la validación de sensibilidad A2 para este constructo (CR-2a normalizado en z) rechaza H0d, pero en la dirección **contraria** a la hipótesis: favorece a G2 (p bilateral = 0.0319, r = −0.47), no a G1.

Las tres versiones exploratorias del mismo constructo — arraigo contextual — contradicen directamente este resultado, todas a favor de G1 con tamaño de efecto grande:

- Solapamiento crudo (exploratorio): G1 mucho mejor, p < 0.0001, r = +0.84.
- Anclaje al escenario por coseno (exploratorio): G1 mucho mejor, p < 0.0001, r = +0.83 — con la advertencia de que este indicador no distingue "deriva" narrativa de evolución legítima del mundo; un valor alto podría reflejar que el sistema se queda pegado al escenario inicial, no necesariamente una virtud.
- Solapamiento sin nombres propios (exploratorio): G1 mejor, r = +0.62.

**Decisión formal:** se rechaza H0d con el instrumento confirmatorio, pero H1d tal como está planteada (G1 superior a G2) **no queda respaldada** por la evidencia confirmatoria. Se documenta explícitamente como un límite de validez de constructo (la normalización en z controla variables que las versiones crudas no controlan, y no está claro cuál captura mejor "arraigo contextual" tal como lo define la rúbrica original) — no se presenta el resultado confirmatorio aislado como si fuera la historia completa. Se recomienda resolver la discordancia normalizado-vs-crudo antes de la sustentación.

## H1e — Coherencia longitudinal (OE-5): sin decisión confirmatoria

Ningún instrumento de las familias CL-1/CL-2 alcanzó clasificación confirmatoria en la validación de sensibilidad A2. No existe, por tanto, evidencia confirmatoria para rechazar ni para no rechazar H0e.

Evidencia exploratoria disponible (no confirmatoria, se reporta con esa salvedad):

| Instrumento | Mdn G1 | Mdn G2 | p bilateral | n efectivo | Cobertura A2 |
|---|---|---|---|---|---|
| PNJ inactivo **mencionado** (% turnos, versión cruda) | 3.86% | 0.21% | 0.0315 (favorece G1) | 24 | 8/8 |
| PNJ inactivo **como sujeto gramatical** (por 1000 turnos, versión refinada) | 0.00 | 0.00 | 0.4375 (no significativo) | 6 | 4/8 |

La versión cruda del indicador sugiere una diferencia a favor de G1, pero al exigir que el PNJ sea sujeto gramatical de la oración (para distinguir acción narrada real de mención retrospectiva), la diferencia se diluye y deja de ser significativa. Esto muestra que buena parte del efecto crudo era mención/referencia, no acción real narrada.

**Decisión formal:** H1e se documenta explícitamente como **sin instrumento confirmatorio**, citando ambas versiones del indicador para mostrar que el efecto no sobrevive el refinamiento sintáctico. Es un hallazgo metodológico legítimo en sí mismo (evidencia de rigor en la construcción del instrumento), no se fuerza una promoción a conveniencia del indicador crudo solo para tener una decisión. El desarrollo de un instrumento confirmatorio para CL-1/CL-2 queda como trabajo de una extensión futura, no bloqueante para esta tesis.

## H1f — Calidad narrativa emergente (OE-6): se acepta, condicionada

Se rechaza H0f con las 5 filas del instrumento `persona2` (usurpación de la agencia del jugador y sus subcategorías): p < 0.0001 en las 5, r entre −0.98 y −1.00, todas con Holm < 0.0001 — a favor de G1 (G1 usurpa significativamente menos la agencia del jugador que G2).

Este es el único bloque confirmatorio que sostiene H1f de forma completa. Antes de reportarlo como definitivo, se verificó si el hallazgo inicial de TTR/bigramas a favor de G2 (que en un análisis preliminar parecía un segundo eje de trade-off) sobrevivía una prueba de robustez frente a longitud de turno — no sobrevivió (ver `02_Instrumentos_de_Evaluacion/Especificacion_MTLD_MATTR_Diversidad_Lexica.md`): al controlar por longitud, la diferencia léxica se reduce a un valor prácticamente nulo (0.002 en TTR a 100 palabras fijas) y de hecho se invierte a favor de G1 en la mayoría de las parejas.

**Decisión formal:** se acepta H1f, **explícitamente condicionada** a la auditoría de precisión del instrumento `persona2`, todavía pendiente (fase P2-P4 del plan de validación). Se marca como resultado confirmatorio provisional, no definitivo, hasta que esa auditoría se complete. TTR/MTLD/MATTR/bigramas se presentan como evidencia exploratoria y prácticamente nula a igual longitud de turno, no como un segundo eje de la hipótesis con el mismo peso que `persona2`.

## Conclusión general del capítulo de resultados

La evidencia **no respalda una superioridad general y uniforme** de la arquitectura multiagente (G1) sobre la monolítica (G2) en las tres dimensiones evaluadas comparativamente. Hay una ventaja específica y bien fundamentada en H1f (agencia del jugador), ninguna decisión confirmatoria en H1e, y evidencia confirmatoria que de hecho favorece a G2 en el único indicador normalizado disponible para H1d. Esta lectura matizada queda anotada como algo que el Capítulo 4 (hipótesis específicas H1a-H1c, todavía redactadas con el lenguaje del panel Likert previo) deberá reflejar en una revisión metodológica futura, fuera del alcance de esta entrega.

## Prioridades inmediatas identificadas a partir de esta docimasia

1. Completar la auditoría de precisión de `persona2` (fase P2-P4) — es el único bloque confirmatorio que sostiene una hipótesis específica completa (H1f).
2. Resolver la discordancia de validez de constructo en CR-2a (normalizado vs. crudo) antes de la sustentación — afecta la interpretación de H1d.
3. Desarrollar y validar un instrumento confirmatorio para CL-1/CL-2 — trabajo de una extensión futura, no bloqueante para esta tesis (H1e queda documentada como limitación, no como pendiente urgente).
