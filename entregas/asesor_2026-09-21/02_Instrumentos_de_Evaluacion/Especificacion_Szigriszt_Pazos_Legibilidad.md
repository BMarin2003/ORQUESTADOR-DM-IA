# Especificación — Szigriszt-Pazos y banda INFLESZ (complemento de QN-1, legibilidad)

Estado: implementado y corrido contra las 27 parejas reales.

## Motivación y decisión de diseño

La fórmula de legibilidad usada originalmente (Fernández-Huerta, 1959) se complementó con Szigriszt-Pazos (1993), una adaptación posterior con estudio de validación propio (Barrio-Cantalejo et al., 2008) y banda de interpretación INFLESZ. El cálculo se implementó en la capa de análisis (reutilizando el mismo conteo de sílabas del motor de generación, solo lectura) en lugar de modificar el motor en vivo (`orquestador/vertical_slice.py`), porque el motor no tiene una columna de base de datos para este valor y agregarla habría requerido una migración de esquema que afecta el guardado de cada turno de campañas futuras. Esa decisión de infraestructura queda documentada como mejora pendiente, no como bloqueante de esta tesis: las 27 parejas ya cerradas están correctamente medidas por la capa de análisis, que recalcula todo desde las transcripciones normalizadas.

## Resultado (27 parejas)

| Medida | G1 | G2 | HL (diferencia) | p bilateral |
|---|---|---|---|---|
| Fernández-Huerta | 60.5 | 61.8 | −1.8 | 0.0055 |
| Szigriszt-Pazos | 56.3 (banda "normal") | 57.6 (banda "normal") | −1.8 | 0.0055 |

Ambas fórmulas coinciden casi exactamente (correlación 0.9998) porque son, en esencia, la misma combinación lineal de los mismos dos insumos (sílabas/palabra y palabras/frase) con coeficientes distintos — a diferencia de MTLD frente a TTR, que sí son matemáticamente independientes. Por eso esta comparación no aporta una segunda línea de evidencia estadísticamente independiente: lo que aporta es reemplazar una fórmula de 1959 por una de 1993 con estudio de validación propio, un argumento de rigor bibliográfico, no estadístico.

Ambos brazos caen en la banda INFLESZ "normal" (55–65 puntos); G1 tiene al menos una campaña en la banda "algo difícil" (mínimo 47.3). G2 resulta levemente más legible en las 27 parejas; como la rúbrica original no le asigna un sentido de "mejora" a la legibilidad por sí sola, este resultado se reporta como **descriptivo**, no como evidencia a favor de ninguna arquitectura.

## Clasificación de validación (A2)

Descriptivo / no usar — igual que Fernández-Huerta. Ver `Especificacion_A2_Validacion_Sensibilidad_Instrumentos.md` para el detalle de la prueba de sensibilidad.
