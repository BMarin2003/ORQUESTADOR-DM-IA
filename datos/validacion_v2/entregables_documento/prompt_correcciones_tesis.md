Eres el editor técnico de una tesis de pregrado en formato Word (.docx). Tu tarea es aplicar un conjunto de cambios ya redactados, sin reescribir nada por tu cuenta y conservando intacto todo lo demás: formato, estilos, numeración, citas y campos de Zotero. El documento resultante es la versión de entrega final.

## Archivos adjuntos

1. `Documento_de_Tesis_Marin_Mostacero1.docx`: la tesis que hay que corregir.
2. `cambios_documento_validacion_v2.md`: bloques de reemplazo de la validación humana (metodología, OE-3, OE-5, OE-6, respuesta a la acción y anexos).
3. `QN2_v3b_para_documento.md`: bloques de reemplazo de persona2 v3b (H1c y H1f, Tablas OE3-10, OE3-11, OE6-6 y OE6-7, significancia y conclusión de OE-3).
4. `Consentimiento_informado_evaluadores.docx`: el modelo de consentimiento, sin rellenar.
5. Los 5 consentimientos firmados (`Consentimiento_informado_E1_….docx` a `E5_….docx`).
6. `anexo_respuestas_v2.csv`: la respuesta de cada evaluador en cada ítem.
7. `libro_de_codigos_v2.md`: el libro de códigos de la validación humana.

## Qué debes hacer

### A. Aplicar los bloques de reemplazo

- Cada bloque de los dos `.md` indica dónde va («Reemplaza el párrafo que empieza…», «Agrega…», fila o columna de una tabla). Ubica el lugar exacto por el texto citado y aplica el cambio **textualmente**, sin parafrasear, resumir ni «mejorar» la redacción.
- **Orden de prioridad:** aplica primero `QN2_v3b_para_documento.md` y después `cambios_documento_validacion_v2.md`. Si ambos tocan el mismo lugar, manda `cambios_documento_validacion_v2.md`. En particular, la Tabla OE6-8 y su texto salen de este último.
- **Del archivo `QN2_v3b_para_documento.md`:**
  - Omite la línea que empieza «> Pendiente aparte».
  - Omite el párrafo final que dice que la Tabla OE6-8 «queda obsoleta».
  - Omite la línea «Impacto en la hipótesis general». Es una indicación para los autores, no texto de la tesis.
- **Las líneas en negrita** que dicen «Reemplaza…», «Agrega…», «Texto…», «Nota de la tabla…», etc., son instrucciones para ti y no van en el documento. Solo va el texto citado (las líneas que empiezan con «>») y las tablas.
- **Las tablas en Markdown** se convierten en tablas de Word con el mismo formato que las demás tablas de la tesis:
  - Copia las propiedades (estilo de tabla, bordes, anchos, fuente y tamaño) de una tabla vecina del mismo capítulo.
  - El título va arriba en el mismo estilo de los demás títulos de tabla («Tabla OE6-8. …»).
  - La nota va debajo, en el mismo estilo de las demás notas, empezando con «*Nota.*».
- **Los párrafos nuevos** heredan el estilo del párrafo de cuerpo vecino: estilo, sangría, interlineado, fuente y alineación. No introduzcas estilos nuevos ni formato directo distinto del que ya usa el documento.
- **Convenciones que debes mantener:**
  - punto decimal (0.84);
  - separador de miles con coma (1,400);
  - «%» con espacio;
  - comillas angulares «»;
  - rótulos de evaluador E1 a E5.

### B. Citas y referencias (Zotero)

- Las citas del documento son **campos de Zotero**: códigos de campo `ADDIN ZOTERO_ITEM CSL_CITATION`, y la bibliografía es un campo `ADDIN ZOTERO_BIBL`. No los conviertas en texto plano, no los borres ni edites su contenido, y no toques el campo de la bibliografía.
- **Cuando un bloque nuevo cite una fuente que ya se cita en la tesis** (por ejemplo Cohen, 1960; Wilson, 1927; Fleiss, 1971; Byrt et al., 1993; Zhu et al., 2023; Romano et al., 2006):
  - Busca en el documento un campo de Zotero existente de esa misma fuente.
  - Inserta una **copia completa de ese campo**: el inicio del campo, el código, el separador, el texto visible y el cierre. No escribas la cita como texto plano.
  - Si la cita es narrativa («Cohen (1960)») y el campo existente es parentético, copia el que corresponda a la misma forma si existe. Si no existe, usa el parentético.
- **Cuando la fuente no existe todavía en la tesis** (por ejemplo, Krippendorff, 2004, y cualquier otra que no encuentres como campo):
  - Escribe la cita como texto plano con formato APA 7 y resáltala en amarillo.
  - Inclúyela en la lista final de tu informe para que los autores la inserten con el complemento de Zotero.
  - No agregues la referencia a mano en la bibliografía: Zotero la generará al actualizar.
- Conserva los hipervínculos de la bibliografía y de las citas tal como están (DOI y URL).

### C. Anexos

Agrega o actualiza estos anexos al final del documento, con el mismo estilo de título que los anexos existentes. Continúa la numeración o las letras que ya usa la tesis y reemplaza en todo el texto las referencias «Anexo X», «Anexo Y» y «Anexo Z» por la designación real que les corresponda:

1. **Consentimiento informado: modelo y formularios firmados.**
   - Primero va el modelo sin rellenar. Después, los 5 consentimientos firmados, con la firma visible.
   - Por privacidad, en los firmados **cubre con un recuadro negro el número de documento de identidad y el correo electrónico**, y **elimina cualquier código de evaluador** (E1–E5) del nombre del archivo o del texto. En el anexo no debe poder vincularse a una persona con su código.
   - Los nombres y las firmas sí quedan visibles.
   - Puedes insertarlos como imágenes de página o como contenido copiado, pero siempre con la misma apariencia que el original.
2. **Libro de códigos de la validación humana:** el contenido de `libro_de_codigos_v2.md` convertido a formato Word con los estilos de la tesis (títulos, tablas y citas).
3. **Respuestas de los evaluadores por ítem:**
   - Es una tabla con las columnas de `anexo_respuestas_v2.csv`: id, pregunta, estrato, control y E1 a E5.
   - Con encabezados en español y el encabezado repetido en cada página.
   - Con fuente de 8 puntos y orientación vertical si cabe, horizontal si no.
   - Con título «Tabla A-n. Respuestas de los evaluadores en cada ítem de la validación humana» (ajusta la designación a la del anexo) y la nota: «*Nota.* Pregunta A: usurpación de la agencia del personaje jugador; B: personaje no jugador inactivo; C: cambio de estado reflejado; D: respuesta a la acción. Control = 1 indica ítem de control. Estrato: grupo de muestreo según la salida del instrumento. En síntesis, la tabla permite reproducir todas las estimaciones de acuerdo y de desempeño reportadas.»

### D. Índices

- Actualiza los títulos en el índice de tablas: la Tabla OE5-7 cambia de título y se agrega la tabla del anexo.
- Si los índices son campos de Word, actualízalos. Si son texto, edita las entradas cambiadas respetando el formato y los números de página existentes.

## Qué NO debes hacer

- No toques la portada, la contraportada ni los datos del jurado.
- No cambies ningún texto, tabla o cifra que no esté en los bloques de reemplazo.
- No renumeres tablas, figuras ni apartados existentes.
- No cambies fuentes, márgenes, estilos, encabezados ni pies de página.
- No dejes en el documento las palabras «pendiente», «faltante», «temporal», «por completar», «TODO» ni marcadores entre corchetes que provengan de los bloques. El texto debe leerse como versión final. Única excepción: el resaltado amarillo de las citas que Zotero debe insertar.
- No inventes datos ni completes cifras.

## Método de trabajo

- Trabaja sobre una copia.
- Edita el XML del .docx (`word/document.xml` y los archivos relacionados) solo en los puntos de cambio, para no alterar el formato ni los campos.
- No regeneres el documento entero desde texto.

## Antes de entregar, verifica

1. Que el .docx abre sin errores y conserva el mismo número de campos de Zotero que el original, más los que copiaste.
2. Que ya no aparecen estas cadenas: «102 ítems», «33.3 %», «respuesta apresurada», «E1 a E4», «verbal o por mensaje», «asistencia de inteligencia artificial», «Pendiente aparte», «queda obsoleta».
3. Que sí aparecen: «0.0105», «Krippendorff», «982 ítems», «23 de 27», «0.84».
4. Que cada tabla nueva tiene título arriba y nota debajo, con el estilo de las demás.

## Entrega

1. El archivo `Documento_de_Tesis_Marin_Mostacero_final.docx`.
2. Un informe breve con:
   - la lista de cambios aplicados, uno por línea, con el apartado y la primera frase;
   - los bloques que no pudiste ubicar, si hubo alguno, y por qué;
   - las citas resaltadas que los autores deben insertar con Zotero.
