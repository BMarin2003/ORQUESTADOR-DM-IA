# Especificación — MTLD y MATTR (complemento de QN-1, diversidad léxica)

Estado: implementado, corrido y verificado contra las 27 parejas reales. Sin llamadas nuevas a modelos de lenguaje — recálculo determinista sobre los datos ya generados.

## Motivación

El TTR (Type-Token Ratio) crudo, usado originalmente para QN-1, es sensible a la longitud del texto — con campañas de hasta 1400 turnos esto es un problema real. La literatura reciente recomienda MTLD (McCarthy & Jarvis, 2010) o MATTR (Covington & McFall, 2010) como alternativas más estables porque dependen mucho menos del largo del texto.

## Decisión de diseño: a nivel de bloque/campaña, no de turno

El TTR por turno se calcula sobre unas pocas decenas de palabras — insuficiente para que MTLD sea estable (por debajo de ~50-100 palabras el "factor parcial" domina el resultado y se vuelve ruidoso). Por eso el TTR por turno se dejó intacto, para no perder comparabilidad con los 27 pares ya corridos, y MTLD/MATTR se añadieron a nivel de bloque de 200 turnos y de campaña completa.

Verificación de la implementación con casos hechos a mano: alternar "a b" da MTLD 3.0; repetir una sola palabra da MTLD 2.0. 129 pruebas del arnés de instrumentos (6 nuevas), sin regresiones; 0 diferencias en las columnas preexistentes sobre 54 campañas y 4,158 filas de bloques (el cambio es puramente aditivo).

## Hallazgo principal: la ventaja de G2 en TTR/bigramas por turno era un confusor de longitud

Con las 27 parejas reales, G1 tiene turnos más largos que G2 (mediana 158 vs. 116 palabras). Esa diferencia de longitud por sí sola explica casi toda la ventaja aparente de G2 en TTR y bigramas repetidos por turno:

| Medida | G1 | G2 | Lectura |
|---|---|---|---|
| Palabras por turno (mediana) | 158 | 116 | G1 más largo en las 27 parejas |
| TTR por turno (sin controlar longitud) | 0.679 | 0.725 | G2 mayor — este es el hallazgo que se cae al controlar longitud |
| MTLD | 109.0 | 108.9 | sin diferencia (p = 0.84) |
| MATTR | 0.824 | 0.828 | diferencia mínima a favor de G2 |
| TTR a 100 palabras fijas | 0.741 | 0.739 | diferencia de 0.002 (se invierte a favor de G1) |
| Bigramas repetidos, turno completo | 0.030 | 0.018 | G2 menor |
| Bigramas repetidos, a 100 palabras fijas | 0.0139 | 0.0154 | se invierte: G1 menor en 23 de 27 parejas |

**Consecuencia directa en la docimasia de H1f (calidad narrativa emergente):** TTR y bigramas por turno bajan de "confirmatorio" a "exploratorio" en la clasificación de instrumentos. H1f queda sostenida únicamente por el instrumento `persona2` (usurpación de agencia del jugador, a favor de G1, condicionado a auditoría — ver `03_Resultados_y_Analisis/Auditoria_Persona2_Equivalencia.md`), no por un supuesto trade-off de dos ejes con el mismo peso metodológico. El detalle completo de esta decisión está en `03_Resultados_y_Analisis/` (paquete de resultados OE-6/H1f).

## Límites declarados

- MTLD y MATTR tienen pruebas unitarias, pero su prueba de sensibilidad A2 con datos reales aún no los promueve a confirmatorio (ver `Especificacion_A2_Validacion_Sensibilidad_Instrumentos.md`) — quedan clasificados como exploratorios.
- El control a 100 palabras excluye al 18% de los turnos de G2 (los más cortos) — compara sobre los turnos largos, no sobre la distribución completa.
- MATTR redondea a 3 decimales, lo que generó 2 empates en el corpus.

## Siguiente paso natural (no iniciado en esta tesis)

Diseñar y correr una prueba de sensibilidad A2 con inyección de repetición para poder promover MTLD/MATTR de exploratorio a confirmatorio en una extensión futura del estudio.
