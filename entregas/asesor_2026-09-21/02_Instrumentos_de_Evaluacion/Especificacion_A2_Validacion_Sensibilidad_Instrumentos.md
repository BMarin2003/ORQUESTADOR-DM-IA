# Especificación A2 — Validación de sensibilidad para los instrumentos deterministas

## Qué es la validación A2

Antes de usar cualquier instrumento determinista (CR-1, CR-2, CL-1, CL-2, QN-1, QN-2 y sus variantes) como evidencia formal de una hipótesis, cada uno pasa por una prueba de sensibilidad: se inyectan defectos sintéticos conocidos (barajar turnos, insertar ruido de formato, permutar el orden, etc.) sobre el corpus real y se verifica si el instrumento reacciona en la dirección esperada. Solo los instrumentos que superan esta prueba se clasifican como **confirmatorios** y pueden alimentar la docimasia formal de hipótesis (con corrección de Holm). Los que no la superan, o que no tienen una perturbación definida que los ponga a prueba, quedan como **exploratorios** (se reportan, pero no sostienen una decisión de hipótesis por sí solos) o **descriptivos / no usar**.

Los reportes completos de esta validación (corridas contra las 27 parejas reales) están en `03_Resultados_y_Analisis/Validacion_Sensibilidad_A2/`.

## Extensión A2 para los tres instrumentos nuevos: Szigriszt-Pazos, MTLD y MATTR

Estado al cierre del corpus (2026-09-21): corrido y verificado contra datos reales.

### Cómo se implementó

La validación de estos tres instrumentos nuevos se hizo en un runner independiente que registra las expectativas nuevas y verifica por assert que la tabla de línea base original (`Sensibilidad_Baseline.md`) no se alteró — así se evita mezclar la validación pre-especificada con la de los instrumentos añadidos después. Resultado: las 870 celdas de la línea base salieron idénticas (0 diferencias) y las 133 pruebas de sensibilidad pasan.

### Dos hallazgos de la validación, ambos documentados explícitamente (no ocultados)

1. **P11a/P11b (inyección de formato) no son invariantes por construcción para legibilidad — solo P6 (barajar) lo es.** La perturbación P11a añade o quita texto (etiquetas de formato), lo que cambia el conteo real de sílabas/palabras/frases. Verificado: `qn1_legibilidad_sz` bajo P11a en G2 sube +1.505 puntos [IC 95%: 1.320, 1.755], p = 1.27×10⁻¹³ — un "cambio inesperado" casi idéntico al ya documentado para Fernández-Huerta (+1.625, p = 5.66×10⁻¹⁵) bajo la misma perturbación. Es el mismo artefacto de formato ya conocido en la línea base, ahora confirmado también para Szigriszt-Pazos — no es un fallo del instrumento nuevo.
2. **El control de MTLD en G1 (perturbación P9, permutar orden) es débil, no limpio.** Mediana de diferencia +2.0, delta pareado de Cliff = 0.433 (por encima del umbral de efecto 0.147), p sin ajustar = 0.0011, pero p con corrección de Holm = 0.175 (no pasa el umbral de 0.05). Con solo 60 ventanas y la corrección por multiplicidad, el veredicto formal es "responde" (control OK), pero es un "no se pudo rechazar", no una confirmación limpia de ausencia de sesgo. Se documenta así explícitamente en vez de presentarlo como control limpio.

### Resultado consolidado

| Instrumento | Perturbación | Resultado | Lectura |
|---|---|---|---|
| Legibilidad Szigriszt-Pazos | P6 (barajar) | Δ = 0.0 en los dos brazos | invariante exacto, como se esperaba |
| Legibilidad Szigriszt-Pazos | P11a (inyectar formato) | +1.5 en G2, p < 0.0001 | mismo artefacto de formato que Fernández-Huerta — control roto, esperado |
| MTLD (ventana) | P9 (permutar orden) | "responde" en los dos brazos, pero débil en G1 (δ=0.43, p_Holm=0.17, n=60) | pasa el control formal, pero no descarta sesgo real por tamaño de muestra |
| MATTR (ventana) | P9 (permutar orden) | "responde" limpio en los dos brazos (δ ≤ 0.17) | control sólido |

### Clasificación final

- **Fernández-Huerta y Szigriszt-Pazos:** descriptivo / no usar (legibilidad no tiene un sentido de "mejora" definido por la rúbrica original — nunca hubo celda confirmatoria posible).
- **MTLD y MATTR:** exploratorio (el control P9 no es suficiente para promoverlos a confirmatorio; MATTR quedó con un control más limpio que MTLD).

Diseñar una perturbación con repetición inyectada es la única vía identificada para subir MTLD/MATTR a confirmatorio; se documenta como trabajo futuro, no realizado en esta tesis: MTLD/MATTR ya cumplieron su propósito metodológico central (mostrar que la ventaja de TTR/bigramas por turno tenía un confusor de longitud — ver `Especificacion_MTLD_MATTR.md`).
