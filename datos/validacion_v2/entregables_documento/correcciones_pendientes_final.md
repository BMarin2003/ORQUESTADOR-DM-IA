# Correcciones pendientes — tesis versión final (01/11/2026)

Este archivo es para el Claude de Corall. Debe aplicarse sobre `Documento_de_Tesis_Marin_Mostacero_final.docx` con **las mismas reglas del prompt anterior** (`prompt_correcciones_tesis.md`):

- reemplazo textual;
- mismo formato y estilos;
- campos de Zotero intactos (las citas existentes se copian como campo y las nuevas se resaltan en amarillo);
- nada de «pendiente», «faltante» ni «por completar».

Adjunta también `cambios_complemento_conclusiones.md`.

Las líneas en negrita («Reemplaza…», «Agrega…») son instrucciones; solo va al documento el texto citado con «>» y las tablas.

---

## 1. Aplicar `cambios_complemento_conclusiones.md`

Aplícalo completo. Corrige las Tablas HG-1 y D-1, los apartados 6.1.8, 6.1.9 y 6.1.10, las conclusiones (incluida la de OE-6) y las recomendaciones, que todavía usan las cifras de la versión anterior de persona2 («3.47 %», «ninguna resulta significativa», «calibración pendiente»).

---

## 2. Resumen y abstract

**En el RESUMEN, reemplaza** desde «No se detectó una degradación significativa del sistema monolítico…» hasta el final del párrafo por:

> El sistema monolítico mantuvo estable su coherencia reactiva a lo largo de la campaña (prueba de Page, p = 0.310), pero su respeto por la agencia del jugador se deterioró de forma significativa (p = 0.0105), al pasar de prácticamente ninguna usurpación al inicio a cerca de un turno de cada 200 al final. En coherencia reactiva, el instrumento confirmatorio favoreció al sistema monolítico con un efecto mediano (r = −0.47); en coherencia longitudinal, ningún instrumento alcanzó la clase confirmatoria; y el sistema multiagente usurpó la agencia del jugador en menos turnos que el monolítico en los 27 pares (0.00 % frente a 0.37 % en mediana; r = −1.00), resultado que se mantuvo al corregir las tasas por la precisión del detector frente a cinco evaluadores humanos. En consecuencia, la hipótesis general no se sostiene: con una memoria estructurada común, no se obtuvo evidencia de que la especialización de agentes mejore la coherencia reactiva ni la longitudinal, aunque sí redujo la frecuencia con que el sistema decide por el jugador.

**En el ABSTRACT, reemplaza** desde «No significant degradation of the monolithic system…» hasta el final del párrafo por:

> The monolithic system kept its reactive coherence stable over the campaign (Page test, p = 0.310), but its respect for player agency deteriorated significantly (p = 0.0105), rising from virtually no usurpation at the start to about one turn in every 200 at the end. In reactive coherence, the confirmatory instrument favored the monolithic system with a medium effect (r = −0.47); in longitudinal coherence, no instrument reached the confirmatory class; and the multi-agent system usurped player agency in fewer turns than the monolithic system in all 27 pairs (median 0.00 % versus 0.37 %; r = −1.00), a result that held after correcting the rates for the detector's precision against five human raters. Therefore, the general hypothesis is not supported: with a shared structured memory, there was no evidence that agent specialization improves reactive or longitudinal coherence, although it reduced how often the system decides on the player's behalf.

**En el resumen y en el abstract, reemplaza también** «validados mediante pruebas de sensibilidad por perturbación y auditorías humanas externas» por «validados mediante pruebas de sensibilidad por perturbación y una validación humana ciega con cinco directores de juego», y «validated through perturbation-based sensitivity tests and external human audits» por «validated through perturbation-based sensitivity tests and a blind human validation with five game masters».

---

## 3. Dos párrafos de resultados con cifras anteriores

**OE-3: reemplaza**, en el párrafo que empieza «En conjunto, la Tabla OE3-10 muestra…», el fragmento «y una usurpación explícita de la agencia del personaje jugador de 3.47 % de los turnos en mediana, con una dispersión mayor (RIQ = 3.40 %; máx. = 11.40 %)» por:

> y una usurpación de la agencia del personaje jugador de 0.37 % de los turnos en mediana, con una dispersión relativa mayor (RIQ = 0.33 %; máx. = 1.28 %)

**OE-6: reemplaza** el párrafo que empieza «En las Tablas OE6-4 y OE6-5, las cinco filas de persona2…» por:

> En las Tablas OE6-4 y OE6-5, persona2, el único instrumento confirmatorio condicionado del capítulo, favorece a G1 en los 27 pares y con el tamaño de efecto máximo posible en una prueba pareada (r = −1.00): la usurpación total tiene una mediana de 0.00 % en G1 frente a 0.37 % en G2 (HL = −0.37 pp, IC 95 % [−0.47, −0.29]; p < 0.0001). Por categoría, la usurpación de decisiones promedia 0.01 % en G1 frente a 0.17 % en G2, y la de emociones, 0.02 % frente a 0.27 % (r = −1.00 y p < 0.0001 en ambas), en tanto que la de habla es prácticamente nula en ambos brazos y la de pensamiento es nula por la regla de conteo, dado que el agente jugador declara siempre la habilidad que emplea. Es decir, el sistema monolítico decide o siente por el personaje jugador en cerca de uno de cada 270 turnos, mientras que el multiagente prácticamente no lo hace.

Si las Tablas OE6-4 y OE6-5 todavía muestran filas de persona2 con los valores anteriores (3.47 %, «pensamiento» 2.38 %, etc.), reemplázalas con las de `QN2_v3b_para_documento.md` (Tabla OE6-6), conservando el formato. Si no puedes ubicarlas sin ambigüedad, inclúyelas en el informe.

---

## 4. Apartado nuevo 5.8.6: escalas de los instrumentos y decisión con varios instrumentos

Este apartado responde a la observación del asesor sobre la normalización y sobre cómo se decide una hipótesis cuando la dimensión tiene varios instrumentos.

**Agrega**, después del apartado 5.8.5 (Reglas de decisión) y con el mismo estilo de título, el apartado:

**5.8.6. Escalas de los instrumentos y decisión con varios instrumentos**

> Los instrumentos de una misma dimensión miden aspectos distintos en escalas distintas, como proporciones de turnos, puntuaciones normalizadas, similitudes o índices de diversidad, y no comparten un mismo sentido de mejora. Por ello, el estudio no los normaliza ni los combina en un índice compuesto, dado que cualquier ponderación sería arbitraria y su resultado dependería de la escala elegida y no del constructo. En su lugar, cada instrumento se contrasta en su propia escala y la decisión se toma mediante una regla fijada antes del análisis.
>
> En primer lugar, la clasificación obtenida en la prueba de sensibilidad (apartado 5.6.3) determina qué instrumentos deciden: solo los confirmatorios y los confirmatorios condicionados forman la familia confirmatoria de cada hipótesis, en tanto que los exploratorios orientan la interpretación sin intervenir en la decisión. En segundo lugar, cuando la familia confirmatoria incluye más de un instrumento, los valores p se ajustan mediante la corrección de Holm (Holm, 1979), y la hipótesis nula se rechaza si al menos un instrumento resulta significativo en el sentido de la hipótesis alternativa tras el ajuste, sin que ningún otro lo sea en el sentido contrario. En el corpus estudiado, cada dimensión con instrumentos confirmatorios contó con uno solo: la respuesta a la acción específica para H1a y H1d, y persona2 para H1c y H1f, mientras que la coherencia longitudinal no contó con ninguno, por lo que H1b y H1e se declararon sin decisión confirmatoria.
>
> Por último, dado que las pruebas empleadas operan sobre rangos, el resultado de cada contraste no depende de la unidad ni de transformaciones monótonas de la escala del instrumento, de modo que la ausencia de normalización no afecta las decisiones. La hipótesis general, a su vez, se decide a partir de H1d, H1e y H1f mediante la prueba de unión-intersección descrita en el apartado 6.1.10 (Berger & Hsu, 1996), sin combinar los valores de los instrumentos.

Si el documento tiene un índice general con los subapartados de 5.8, agrega la entrada 5.8.6.

---

## 5. Normalidad de las diferencias G1 − G2

**Agrega** al final del apartado 5.8.3, después del párrafo existente, el siguiente párrafo y la tabla. Usa para la tabla el siguiente número libre de la serie de tablas del capítulo 4 y 5, es decir, el que siga a la última «Tabla N.» numerada sin prefijo de objetivo.

> La prueba de Shapiro-Wilk (Shapiro & Wilk, 1965) aplicada a las diferencias G1 − G2 de los 27 pares muestra que la distribución se aparta de la normalidad en el instrumento confirmatorio de la calidad narrativa emergente y en varios exploratorios, como se resume en la Tabla N, lo que justifica el uso de la prueba de rangos con signo de Wilcoxon, que no requiere normalidad. En el instrumento confirmatorio de la coherencia reactiva, cuyas diferencias son compatibles con la normalidad, la prueba t para muestras relacionadas conduce a la misma decisión (t(26) = −2.38; p bilateral = 0.025; p unilateral en el sentido de H1d = 0.988; dz = −0.46), de modo que la elección de una prueba no paramétrica común a toda la batería no modifica ninguna conclusión.

**Tabla N. Prueba de normalidad de Shapiro-Wilk sobre las diferencias G1 − G2 por instrumento, n = 27 pares.**

| Ind. | Instrumento | Uso | n | W | p | ¿Normal? |
|---|---|---|---|---|---|---|
| CR-2 | Respuesta a la acción específica (z) | Confirmatorio | 27 | 0.983 | 0.9225 | sí |
| CR-2 | Solapamiento con la acción (crudo) | Descriptivo | 27 | 0.985 | 0.9472 | sí |
| CR-2 | Anclaje al escenario (coseno, ventana de 8) | Exploratorio | 27 | 0.970 | 0.6026 | sí |
| CR-2 | Anclaje sin nombres propios | Exploratorio | 27 | 0.986 | 0.9664 | sí |
| CL-1 | Papalampidi C: coherencia de entidad | Exploratorio | 27 | 0.971 | 0.6363 | sí |
| CL-1 | Papalampidi V: consistencia de atributos | Exploratorio | 27 | 0.968 | 0.5585 | sí |
| CL-2 | Jericho-QA: recuerdo de cambios de estado | Exploratorio | 26 | 0.965 | 0.5110 | sí |
| CL-2 | PNJ inactivo mencionado | Exploratorio | 27 | 0.932 | 0.0781 | sí |
| CL-2 | PNJ inactivo como sujeto (refinado) | Exploratorio | 27 | 0.364 | < 0.0001 | no |
| QN-1 | TTR a 100 palabras | Exploratorio | 27 | 0.948 | 0.1947 | sí |
| QN-1 | Bigramas a 100 palabras | Exploratorio | 27 | 0.904 | 0.0163 | no |
| QN-1 | MTLD | Exploratorio | 27 | 0.921 | 0.0415 | no |
| QN-1 | MATTR | Exploratorio | 27 | 0.907 | 0.0196 | no |
| QN-2 | Usurpación de la agencia del PJ (persona2) | Confirmatorio condicionado | 27 | 0.848 | 0.0011 | no |

*Nota.* Prueba de Shapiro-Wilk sobre la diferencia G1 − G2 de cada par; ¿Normal? = sí cuando p ≥ 0.05. En Jericho-QA, n = 26 porque la campaña G1 del par 08 no registró cambios evaluables. En síntesis, la usurpación de la agencia y varios instrumentos exploratorios se apartan de la normalidad, lo que respalda el uso de pruebas de rangos en toda la batería, y en el único instrumento confirmatorio con diferencias normales la prueba paramétrica conduce a la misma decisión.

---

## 6. Validez de criterio de la comparación con evaluadores (5.6.3)

**Agrega**, al final del párrafo que empieza «De manera complementaria, los instrumentos cuya validez depende de interpretar el texto se contrastaron con el juicio de cinco evaluadores…», la oración:

> La comparación no replica el procedimiento de cada instrumento, sino su definición operativa: evaluadores e instrumento responden la misma pregunta sobre la misma unidad, con los mismos criterios de inclusión y exclusión, de modo que el juicio de directores de juego expertos, que realizan la misma tarea que el sistema evaluado, actúa como criterio externo frente al cual se estima la validez del procedimiento automático, y los ítems de control verifican que todos los evaluadores apliquen esa definición común.

---

## 7. Notas resumen de las tablas (observación del asesor)

Para **cada** tabla del documento cuya nota **no** termine con una oración de síntesis, agrega al final de su nota **una sola oración** que empiece con «En síntesis,» y diga qué muestra la tabla. Reglas:

- **Solo con información que ya está en la tabla** o en el párrafo que la interpreta. No inventes cifras ni conclusiones nuevas.
- Como máximo 35 palabras.
- Mismo estilo de la nota, sin formato nuevo.
- **Tablas de resultados en crudo por campaña o por par:** di qué patrón general se observa. Ejemplo: «En síntesis, G1 presenta valores menores que G2 en la mayoría de los pares.»
- **Tablas de contraste:** di la decisión y la magnitud. Ejemplo: «En síntesis, el contraste no es significativo y el efecto es despreciable, por lo que no se rechaza H0a.»
- **Tablas de desglose de instrumentos:** di cuántos instrumentos son confirmatorios y cuál decide la hipótesis.
- **Tablas de las secciones 1 a 5:** di qué organiza la tabla y para qué sirve, en una oración.
- No toques las notas que ya contienen «En síntesis».
- Al final, lista en el informe las tablas a las que agregaste la oración.

---

## 8. Verificación final

1. **No deben aparecer** las cadenas «3.47 %», «ninguna resulta significativa», «calibración pendiente» ni «auditorías humanas externas».
2. **«0.089» solo puede aparecer** en la oración de 5.6.3 y en la nota de la Tabla OE6-7, que mencionan la regla de conteo anterior, y en el resultado del instrumento semántico («0.115 frente a 0.089»).
3. **Deben aparecer:**
   - «0.0105» en el resumen, OE-3, la Tabla D-1 y las conclusiones;
   - «5.8.6» y «índice compuesto»;
   - la tabla de normalidad;
   - «criterio externo».
4. **Las únicas marcas que pueden quedar** son las citas resaltadas para Zotero y los marcadores de la portada y de los Anexos 5 y 6, que completan los autores.

---

## 9. Lo que completan los autores, fuera de Corall

- **Zotero:** insertar las citas resaltadas, como Krippendorff (2004) y cualquier otra que Corall reporte, y actualizar la bibliografía.
- **Anexo 5:** la R.D. de aprobación del proyecto, cuando exista.
- **Anexo 6:** la constancia del asesor.
- **Portada:** el jurado y la R.D. Mientras no existan, dejar el formato que pida la escuela, sin la palabra «[pendiente]».
- **Consentimientos:** completar los datos de Jorge (apellidos, DNI, correo, ciudad y fecha) y la ciudad y la fecha de Sandra antes de la versión impresa.
- **persona2 rehecho con contexto:** cuando se rehaga la medición, actualizar las cifras de QN-2 en OE-3, OE-6, el resumen, el abstract y las conclusiones con un nuevo bloque de reemplazo.
