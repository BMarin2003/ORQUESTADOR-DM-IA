# Resumen para Luis: validación humana v2 y persona2 v3b (28/10 al 01/11/2026)

**Para qué es este documento.** Cuenta qué se hizo, qué se decidió y por qué, y qué te toca a ti. El proceso completo está en el repositorio, en la rama `cierre-brechas-2026-10`, carpeta `validacion_v2/`, y su `README.md` dice dónde está cada archivo. En la tesis va solo el resultado, su interpretación y una oración por cada decisión que cambió algo.

---

## 1. Qué se hizo: resumen en 6 líneas

1. **Validación humana nueva.** Cinco directores de juego etiquetaron a ciegas 982 ítems en cuatro preguntas, cada una con el mismo criterio que su instrumento. La muestra incluía ítems de control y criterios de exclusión fijados antes de etiquetar.
2. **Se revisó la integridad de cada registro.** Varios archivos estaban copiados o coordinados entre evaluadores y se descartaron. Al final quedaron 5 evaluadores válidos.
3. **persona2 pasó a la versión v3b:** ya no cuenta lo que el jugador declaró ni los pensamientos que son resultado de una tirada. Con v3b, **H1c pasa a sostenerse** y **H1f se mantiene**.
4. **B, C y D quedaron con resultados definitivos:** los detectores son conservadores (alta precisión, baja exhaustividad), pero el error no favorece a ningún brazo.
5. **A (persona2):** la precisión es de 50 % y el acuerdo entre evaluadores es alto. La exhaustividad no se puede estimar con esta ronda (sección 5).
6. **Textos listos para pegar en la tesis**, más un prompt para el Claude de Corall que los aplica respetando el formato y Zotero.

---

## 2. Diseño de la validación v2

| Pregunta | Instrumento | Ítems | Cómo se muestreó |
|---|---|---|---|
| A | persona2 (usurpación de la agencia del PJ) | 400 + 10 controles | 100 marcados por el detector y 300 no marcados |
| B | PNJ inactivo (refinado) | 200 + 10 controles | 100 marcados, 50 mencionados sin marcar y 50 sin mención |
| C | Jericho-QA (cambio de estado reflejado) | 200 + 7 controles | 100 reconocidos y 100 no reconocidos |
| D | Respuesta a la acción (z continuo) | 150 + 5 controles | 100 al azar y 50 de la cola baja (z ≤ percentil 10) |

- **Total: 982 ítems.** Cada evaluador los veía en un orden aleatorio propio, calculado a partir de su código.
- **Exclusión prefijada:** se excluye a un evaluador **solo de la pregunta** en la que falle más del 20 % de los controles, o en la que responda siempre lo mismo. No se usa el tiempo de respuesta.
- **Referencia de cada ítem:** la mayoría de los evaluadores retenidos en esa pregunta.
- **Métricas:**
  - detector frente a la referencia: matriz 2×2, % de acuerdo, κ de Cohen, precisión (IC de Wilson) y exhaustividad **ponderada por estrato** (cada ítem pesa el tamaño de su estrato en el corpus dividido por su tamaño en la muestra; IC por remuestreo estratificado de 2,000 réplicas);
  - D: AUC y correlación biserial puntual, sin umbral;
  - entre evaluadores: κ de Fleiss y α de Krippendorff.
- **Consentimiento:** escrito y firmado por los 5. Los firmados quedan **fuera de git**, en `privado_no_publicar/`, porque tienen DNI y correo.

---

## 3. Integridad de los registros: qué se descartó y por qué

El formulario baraja los ítems según el código que escribe el evaluador y exporta el CSV en ese orden. Por eso se puede comprobar si un archivo salió del formulario con su propio código.

| Registro | Qué pasó | Decisión |
|---|---|---|
| E2 original (30/10) | Formato distinto al del formulario, orden interno y respuesta constante por pregunta | Descartado |
| E1–E4 originales | Venían **en el orden de E5** y coincidían 96–97.5 % con E5, con diferencias que no se repetían entre ellos: eran copias de E5 con algunos cambios | Descartados |
| E1, segunda y tercera versión | La primera era la misma copia reordenada. La segunda tenía un orden que no corresponde a ningún código y había sido editada fuera del formulario | Descartado; se buscó otro evaluador |
| Versiones «corregidas» de E6–E9 | E7, E8 y E9 cambiaron **los mismos ~20 ítems en la misma dirección**, lo que indica que se coordinaron | Descartadas; se usa la primera entrega, que sí es independiente |

Todos los descartados están en `respuestas/descartados/`, con su `LEEME.md`. **En la tesis no se cuentan estos detalles**: basta una oración que diga que se verificó la integridad de cada registro.

**Evaluadores válidos y rótulos en la tesis:**

| En la tesis | Código usado en el formulario | Persona |
|---|---|---|
| E1 | E5 | Fabricio |
| E2 | E6 (el CSV vino rotulado «E3») | Jorge |
| E3 | E7 | (ver nota) |
| E4 | E8 | (ver nota) |
| E5 | E9 | (ver nota) |

> **Nota.** Esta correspondencia es privada y no se publica. Confirmen entre ustedes qué persona corresponde a cada código del formulario, porque los consentimientos se numeraron aparte. Las filas de E3 a E5 las completan ustedes.

**Retenidos por pregunta, según los controles:**

| Pregunta | Retenidos |
|---|---|
| A | E2, E3, E5. E1 falló 5/10 y E4 falló 3/10, así que se excluyen |
| B | Los 5 |
| C | E2, E3, E4. E1 y E5 fallaron 2/7, así que se excluyen |
| D | Los 5 |

---

## 4. Resultados de B, C y D (definitivos)

| Instrumento | Precisión [IC 95 %] | Exhaustividad ponderada [IC 95 %] | κ detector–referencia | α entre evaluadores |
|---|---|---|---|---|
| B · PNJ inactivo | 96.0 % [90.2–98.4] | 6.3 % [4.4–8.8] | 0.47 | 0.55 |
| C · Jericho-QA | 89.0 % [81.4–93.7] | 34.0 % [30.5–38.2] | 0.27 | 0.55 |
| C · solo cambios de condición | 87.9 % | 40.5 % | 0.26 | — |
| C · solo cambios de afinidad | 90.5 % | 28.3 % | 0.27 | — |
| D · respuesta a la acción | AUC 0.84 [0.74–0.92]; r_pb 0.40 | — | — | 0.31 |

**Cómo se interpretan:**
- **B y C son conservadores.** Cuando marcan algo, casi siempre es real, pero se les escapa la mayor parte de los casos.
- **Lo que importa para G1 contra G2 es que la pérdida es parecida en los dos brazos.**
  - En B, cuando el PNJ estaba mencionado pero no marcado, los humanos lo vieron actuar en 37 de 40 casos de G1 y en 10 de 10 de G2.
  - En C, entre los cambios no reconocidos, los humanos los vieron narrados en 60 % de G1 y 62 % de G2.
  - Por tanto, las tasas absolutas están subestimadas, pero el error no favorece a ninguna arquitectura.
  - B y C **siguen siendo exploratorios**, y H1e sigue sin decisión confirmatoria.
- **Auditoría de afinidad** (la hizo Bryan, con 30 cambios): la narración refleja el cambio registrado solo en 12 de 30 (40 %). Eso explica por qué Jericho-QA rinde menos en afinidad. En la tesis no se presenta como error del extractor, solo como el dato de la auditoría.
- **D:** el z separa bien las respuestas que los humanos ven ancladas a la acción. En la cola baja, 54 % se juzgaron ajenas a la acción, frente a 15 % en los turnos al azar. El α bajo se debe a la prevalencia (85 % de respuestas Sí), que es la paradoja conocida del κ (Byrt et al., 1993).

---

## 5. persona2: de v2b a v3b y lo que pasó con la pregunta A

### 5.1 La decisión v3b

- **Qué cambia:** v3b usa el mismo detector congelado (el hash se verifica), con una regla de conteo más estricta. **No cuenta lo que el jugador declaró en su acción** ni **los pensamientos que resultan de una tirada declarada**, porque en D&D el resultado de una prueba de habilidad se entrega como conocimiento del personaje y no es una toma de control.
- **Por qué:** al revisar los controles de A, Bryan observó que «Decido abrir la puerta» → «Decides abrir la puerta», o «{Investigación}» → «te das cuenta de que…», no le quitan autonomía al jugador. Al contrario, le devuelven lo que declaró o el resultado de su tirada.
- **Efecto en las hipótesis:**
  - **H1c pasa a sostenerse:** Page p = 0.0105; Wilcoxon B1–B7 p = 0.012; ρ̄ = +0.18, pequeño; r = +0.53, grande. Pasa de 0.00 % al inicio a 0.50 % al final, es decir, a un turno de cada 200.
  - **H1f se mantiene:** Mdn G1 0.00 % frente a G2 0.37 %; HL −0.37 pp [−0.47, −0.29]; p < 0.0001; r = −1.00.
  - **En la tesis:** una oración en 5.6.3 y, en la nota de la tabla, la cifra con v2b, con la que H1c daba p = 0.089.
- **Efecto secundario:** como el agente jugador siempre declara una habilidad, la categoría *pensamiento* queda en 0 en todo el corpus. En la práctica, persona2 mide decisión, emoción y habla.

### 5.2 Qué pasó con la pregunta A

- **El problema:** los 3 evaluadores retenidos coinciden mucho entre ellos (α = 0.85), pero aplicaron un criterio más amplio que el del libro de códigos.
  - Marcaron Sí en narraciones impersonales del resultado de la acción, como «el cuerpo se desliza» o «la respuesta cae en el vacío», que el libro excluye.
  - Marcaron No en atribuciones que el libro cuenta, como «crees reconocer» o «pronuncias». Ellos mismos confirmaron que respondieron por la primera impresión.
- **Lo que sí se puede afirmar:**
  - El constructo de v3b es un **subconjunto** del de la pregunta original, y su desviación iba justo en esa dirección. Por eso los 313 ítems que marcaron No siguen siendo No.
  - De los 12 turnos que marca v3b, en 6 dijeron No. **La precisión de v3b es de 50 %** (IC 25.4–74.6 %): 1 de 1 en G1 y 5 de 11 en G2.
- **Lo que no se puede afirmar:** la exhaustividad. En los 87 ítems que marcaron Sí no se sabe cuáles son atribuciones no declaradas.
- **H1f resiste aun así.** Se repitió el contraste multiplicando la tasa de cada campaña por la precisión de su brazo:
  - con las precisiones estimadas, G1 < G2 en **27 de 27** pares;
  - en el peor escenario, con G2 al 21.3 %, en **23 de 27**;
  - p < 0.0001 en ambos casos. Esta es la nueva Tabla OE6-8.
- **Para el martes quedan tres opciones** (ver el checklist del proyecto):
  1. Volver a etiquetar solo los 87 ítems Sí más 15 controles con el libro v2.1, que corresponde al constructo de v3b, con al menos 3 evaluadores disponibles.
  2. Si no hay evaluadores, una auditoría de ustedes dos por separado, reportando el κ entre ambos.
  3. Reportarlo como limitación, que es lo que ya dicen los textos.
- **Partición desarrollo/prueba:** los 400 ítems de A ya están divididos y congelados (commit `b0bba84`), por si más adelante se reajusta persona2. Así ese ajuste no queda circular.

---

## 6. Qué te toca a ti

1. **Aplicar los cambios a la tesis.** Usa el Claude de Corall con `entregables_documento/prompt_correcciones_tesis.md`, copiado completo, y adjúntale:
   - el docx actual;
   - `entregables_documento/QN2_v3b_para_documento.md`;
   - `entregables_documento/cambios_documento_validacion_v2.md`;
   - `Consentimiento_informado_evaluadores.docx` (el modelo);
   - los 5 consentimientos firmados, que están en el ZIP del Drive o en `privado_no_publicar/`;
   - `anexo_respuestas_v2.csv`;
   - `libro_de_codigos_v2.md`.
2. **Antes de eso, completar los consentimientos:**
   - el de Jorge: apellidos, DNI, correo, ciudad y fecha;
   - el de Sandra: ciudad y fecha. Además, el DNI dice «SMHR98»; si es un documento extranjero, que diga «documento de identidad».
3. **Después de que Corall entregue:**
   - insertar con Zotero las citas que dejó resaltadas en amarillo (por lo menos Krippendorff, 2004) y actualizar la bibliografía;
   - revisar que no quede ninguna palabra marcada como prohibida en el prompt.
4. **Notas de tabla:** el jurado pidió una nota resumen. Las notas actuales explican abreviaturas, pero no resumen. Agreguen una oración del tipo «En síntesis, …» en cada una; las tablas nuevas ya la traen.
5. **Portada:** el jurado y la R.D. dicen «[pendiente]». Déjenlos con el formato que pida la escuela, pero no con esa palabra.
6. **Solicitud de revisión (PDF 05):** dice sublínea «Inteligencia Artificial», y debe decir «Sistemas Inteligentes» si se vuelve a presentar.
7. **Después:** pasarle a Claude **solo las secciones cambiadas** (métodos 5.7 y las brechas de OE-3, OE-5 y OE-6) para revisarlas, no el docx entero, para ahorrar créditos.

---

## 7. Dónde está todo

- **Repositorio:** `github.com/BMarin2003/ORQUESTADOR-DM-IA`, rama `cierre-brechas-2026-10`, último commit `5d6c0c3`. Carpeta `validacion_v2/` y su `README.md`.
- **Drive:** `pruebas_validacion_v2_2026-11-01.zip`, con la carpeta completa y los consentimientos. Compartir solo entre ustedes y el asesor.
- **Checklist de pendientes:** en el proyecto de Claude, `checklist-pendientes-2026-10-30.md`.
