# QN-2 con persona2 v3b: filas y textos para el documento de tesis

Fuente: pipeline oficial (`medidas_cierre`, `page_test`, `consolidar --B 10000`, `resultados_tesis`) con `P2_DIR=persona2_v3b`, 31/10/2026. Las tablas en crudo completas están en `validacion_v2/tabla_OE3-9_v3b.csv` y `validacion_v2/tabla_OE6-4_5_v3b.csv`.

> Pendiente aparte: la columna «p Holm» global del consolidado se corrige después. Aquí solo se reportan los valores p de cada contraste.

---

## 1. Métodos (5.6.3), al final del párrafo de persona2

> En el detector persona2, la regla de conteo excluye las atribuciones que el jugador declaró en su propia acción y las inferencias que resultan de una prueba de habilidad declarada, dado que en Dungeons & Dragons el resultado de dicha prueba se entrega como conocimiento del personaje y no constituye una toma de control; esta regla se adoptó tras la revisión de la validación humana, y con la regla original las decisiones sobre H1f no cambian, mientras que la de H1c no alcanza significancia (p = 0.089).

## 2. Ficha del instrumento (Tabla OE3-1, Tabla OE6-1 y Anexo 1)

- **Qué mide:** porcentaje de turnos en que la narración decide, siente o habla por el personaje jugador sin que este lo haya declarado.
- **Nota de la tabla:** como el agente jugador declara siempre una prueba de habilidad, la categoría *pensamiento* queda absorbida por la regla de conteo y su tasa es nula en todo el corpus. El instrumento mide en la práctica la usurpación de **decisión, emoción y habla**.

---

## 3. OE-3: sistema monolítico (G2)

### Tabla OE3-10, fila QN-2 (estadísticos descriptivos)

| Ind. | Instrumento | n | Mdn | Q1 | Q3 | RIQ | Mín | Máx | Media (DE) | Shapiro-Wilk p | ¿Normal? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QN-2 | Usurpación de la agencia del PJ (persona2) | 27 | 0.37 % | 0.26 % | 0.58 % | 0.33 % | 0.09 % | 1.28 % | 0.43 % (0.26 %) | 0.0071 | no |

**Texto (Tabla OE3-9):**

> En la Tabla OE3-9, la mediana de la usurpación de la agencia del personaje jugador en las 27 campañas G2 es de 0.37 % de los turnos (Q1 = 0.26 %; Q3 = 0.58 %; mín. = 0.09 %; máx. = 1.28 %), con una distribución que se aparta de la normalidad (Shapiro-Wilk p = 0.0071) por la concentración de valores bajos, de modo que el sistema monolítico decide, siente o habla por el personaje jugador en aproximadamente un turno de cada 270. Por bloques, la mediana pasa de 0.00 % en el primer bloque a 0.50 % en el séptimo, valores que en términos absolutos equivalen a cero y a un turno de cada 200, por lo que la evolución debe leerse a partir del contraste de tendencia y no de las medianas, que en tasas tan bajas varían en saltos de un turno.

### Tabla OE3-11, fila QN-2 (contraste de degradación)

| Instrumento | Uso | Dirección de degradación | n | Mdn B1 | Mdn B7 | p Page (unilateral) | p Wilcoxon B1–B7 (unilateral) | ρ̄ | r B1–B7 |
|---|---|---|---|---|---|---|---|---|---|
| Usurpación de la agencia del PJ (persona2) | Confirmatorio condicionado | Aumenta | 27 | 0.00 % | 0.50 % | 0.0105 | 0.0120 | +0.18 (pequeño) | +0.53 (grande) |

### Docimasia de H1c (reemplaza el texto actual)

> La docimasia se realiza mediante la prueba de tendencia de Page sobre los siete bloques de 200 turnos de las 27 campañas G2, unilateral en el sentido de la degradación, y mediante la prueba exacta de Wilcoxon entre el primer y el último bloque. La familia confirmatoria de la dimensión está conformada únicamente por el detector persona2, por lo que no se aplica la corrección de Holm.
>
> Como se aprecia en la Tabla OE3-11, la usurpación de la agencia del personaje jugador aumenta de forma significativa conforme avanza la campaña (Page, p unilateral = 0.0105), resultado que la comparación entre el primer y el último bloque confirma (Wilcoxon, p unilateral = 0.0120), por lo que se rechaza H0c y se sostiene H1c: la calidad narrativa emergente del sistema monolítico, medida a través del respeto por la agencia del jugador, se degrada a lo largo de la campaña.
>
> En cuanto a su magnitud, la tendencia global es pequeña (ρ̄ = +0.18), en tanto que la diferencia entre el primer y el último bloque es grande (r = +0.53), lo que indica que el deterioro no es abrupto, sino una acumulación gradual que se hace evidente al comparar los extremos de la campaña. Su significancia práctica, sin embargo, debe leerse en términos absolutos, dado que la usurpación pasa de prácticamente nula en las primeras sesiones a cerca de un turno de cada 200 en las últimas; se trata, por tanto, de un fallo poco frecuente pero sistemático, que aparece y se acentúa con la extensión de la campaña, en concordancia con la pérdida de adherencia a las instrucciones que la literatura atribuye a los contextos largos (Liu et al., 2024).
>
> Por su parte, los instrumentos exploratorios de QN-1 no muestran degradación (MATTR, p = 0.570), de modo que el deterioro se concentra en el respeto por la agencia del jugador y no en la diversidad léxica de la narración.

---

## 4. OE-6: comparación G1 vs. G2

### Tabla OE6-6, fila QN-2 (comparación pareada)

| Ind. | Instrumento | Uso | Mdn G1 (Q1–Q3) | Mdn G2 (Q1–Q3) | Mdn dif. | HL [IC 95 %] | n efect. | p bilateral | p unil. «G1 mejor» | r |
|---|---|---|---|---|---|---|---|---|---|---|
| QN-2 | Usurpación de la agencia del PJ (persona2) | Confirmatorio condicionado | 0.00 % (0.00–0.07 %) | 0.37 % (0.26–0.58 %) | −0.37 pp | −0.37 pp [−0.47, −0.29] | 27 | < 0.0001 | < 0.0001 | −1.00 |

**Desglose por categoría (exploratorio, medias por campaña, para el texto de la Tabla OE6-4/OE6-5):** decisión, G1 0.01 % vs. G2 0.17 % (r = −1.00, p < 0.0001); emoción, G1 0.02 % vs. G2 0.27 % (r = −1.00, p < 0.0001); habla, prácticamente nula en ambos brazos; pensamiento, 0 en ambos brazos por la regla de conteo.

### Docimasia de H1f (reemplaza el texto actual)

> La docimasia se realiza mediante la prueba exacta de rangos con signo de Wilcoxon sobre la diferencia G1 − G2 de los 27 pares, unilateral en el sentido de H1f, con el detector persona2 como único instrumento confirmatorio de la dimensión.
>
> Como se aprecia en la Tabla OE6-7, el sistema multiagente presenta una menor usurpación de la agencia del personaje jugador que el monolítico en los 27 pares (Mdn G1 = 0.00 %; Mdn G2 = 0.37 %; HL = −0.37 pp, IC 95 % [−0.47, −0.29]; Wilcoxon, p unilateral < 0.0001), con un efecto máximo (r = −1.00), por lo que se rechaza H0f y se sostiene H1f.
>
> En términos prácticos, el sistema monolítico decide, siente o habla por el personaje jugador en cerca de uno de cada 270 turnos, mientras que el multiagente prácticamente no lo hace. Esta diferencia es coherente con la arquitectura de G1, en la que el narrador recibe del árbitro la resolución ya determinada de la acción y no tiene que decidir por el jugador para hacer avanzar la escena. Se trata además de la única dimensión en que la especialización de agentes produce una ventaja inequívoca, precisamente sobre el fallo que los evaluadores de FIREBALL señalaron con mayor frecuencia (Zhu et al., 2023).

### Nota de la Tabla OE6-7

> Nota. Con la regla de conteo original del detector, que también contaba las atribuciones declaradas por el jugador y las inferencias derivadas de pruebas de habilidad, H1f se sostiene igualmente (p < 0.0001; r = −1.00) y H1c no alcanza significancia (p = 0.089).

---

## 5. Significancia (6.1.10) y conclusiones

**Filas de la tabla resumen:**

| Hipótesis | Instrumento | Prueba | p | Efecto | Decisión |
|---|---|---|---|---|---|
| H1c | persona2 | Page (degradación) | 0.0105 | ρ̄ = +0.18 (pequeño); r B1–B7 = +0.53 (grande) | Se sostiene |
| H1f | persona2 | Wilcoxon pareado | < 0.0001 | r = −1.00 (grande) | Se sostiene |

**Conclusión de OE-3 (reemplaza la actual):**

> Respecto del tercer objetivo, se concluye que la calidad narrativa emergente del sistema monolítico se degrada a lo largo de la campaña en su componente de respeto por la agencia del jugador, dado que la usurpación del personaje jugador aumenta de forma significativa conforme avanza la campaña (Page, p = 0.0105), aunque en una magnitud absoluta baja, de prácticamente nula al inicio a cerca de un turno de cada 200 al final, mientras que la diversidad léxica se mantiene estable.

**Impacto en la hipótesis general:** ninguno, porque esta depende de H1d, H1e y H1f, y H1f ya se sostenía.

**Tabla OE6-8 (sensibilidad a la precisión del detector):** queda obsoleta. Usa la precisión de la ronda humana anterior, así que se reemplaza con la precisión de v3b frente a la ronda v2 cuando lleguen los evaluadores.
