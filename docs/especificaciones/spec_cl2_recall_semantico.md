# CL-2 recall semántico (instrumento exploratorio con pgvector)

## Qué es y qué no es

Es un instrumento **nuevo de medición** para la coherencia longitudinal (indicador CL-2), aplicado al corpus ya generado de 27 pares (54 campañas, 75,600 turnos). Es la versión semántica de Jericho-QA: evalúa los mismos eventos, pero reconoce cuando un cambio de estado se narró con otras palabras.

No cambia la generación, no regenera campañas y no modifica ninguna tabla del corpus. Tampoco compara gestores de memoria: la investigación compara arquitecturas de dirección de juego (G1 frente a G2) con la misma memoria estructurada, y una comparación de gestores de memoria sería otro proyecto.

**Clasificación: EXPLORATORIO.** La clasificación de instrumentos de la tesis se fijó antes del contraste de hipótesis (apartado 5.8.5) y no se reabre. Aunque este instrumento pase su prueba de sensibilidad, no decide H1e en esta tesis; su resultado alimenta las recomendaciones.

## Por qué existe

Jericho-QA es léxico: busca raíces como «muert…» o «desconf…». La prueba de sensibilidad ya cerrada mostró que distingue muertes y desapariciones del azar (30–32 % frente a 7–9 %), pero casi no distingue los cambios de actitud (21 % frente a 17–19 %), que son el 55 % de los eventos. Por eso H1e quedó sin instrumento confirmatorio. La hipótesis de trabajo es que buena parte de esos cambios se narran con paráfrasis que un léxico cerrado no ve.

## Definición

1. **Eventos.** Los mismos que Jericho-QA: `Campaña.deltas_narrables()` con su mismo filtro. Entran `npc.status` (dead, missing, captured), `quest.status` (completed, failed, abandoned) y `npc.affinity` solo cuando cruza de banda (excluida la banda neutral). Una prueba verifica que el conteo coincide con `jericho_qa_recall`.
2. **Ventana.** El turno del delta y el siguiente, igual que Jericho (`ventana=1`). El texto es la narración normalizada (`normalizar_turno`).
3. **Fragmentos.** Cada oración de cada turno (1..1400) se convierte en un vector con **BAAI/bge-m3**, de 1024 dimensiones y normalizado. El commit exacto del modelo queda fijado en el manifiesto. Los vectores se guardan en la tabla aditiva `medicion_oraciones` (pgvector).
4. **Consulta.** Una oración declarativa neutra por estado, con el nombre de la entidad, por ejemplo «Yenna Roldós ha desaparecido.».
5. **Puntuación de una ventana.** La máxima similitud coseno entre la consulta y las oraciones de la ventana.
6. **Decisión sin umbral arbitrario.** Se usa un nulo exacto y determinista: se calcula la misma puntuación en todas las ventanas de la misma campaña situadas a más de 5 turnos del evento. El evento cuenta como **reconocido** si su ventana real supera el percentil 95 de ese nulo. Por construcción, una ventana al azar se reconoce alrededor del 5 % de las veces. Como el nulo sale de la misma campaña, también absorbe la diferencia de longitud de turno entre G1 (158 palabras) y G2 (116).
7. **Medidas por campaña.** Recall semántico (fracción de eventos reconocidos), mediana del margen (puntuación real menos el percentil 95 del nulo) y mediana de z.
8. **Búsqueda exacta.** Las consultas agregan con `max()` y `GROUP BY` sobre el índice B-tree `(campaign_id, turn_id)`, sin índice aproximado (HNSW). Mismos datos, mismo resultado.

## Por qué una tabla aparte y no `narrative_chunks`

`narrative_chunks` pertenece a la capa de generación, y el experimento nunca la usó. Llenarla ahora haría dudar de si los brazos la leyeron. Además tiene un índice HNSW aproximado que, medido en una base de prueba, multiplica por unas 30 veces el costo de inserción (20,000 vectores: 340 s con HNSW frente a 10 s sin él). `medicion_oraciones` es aditiva, porque no altera ninguna tabla existente, y mantiene el principio del esquema: `tenant_id` en la fila y RLS.

## Prueba de sensibilidad (A2), prerregistrada

Las expectativas se sellan con SHA-256 antes de correr. Las perturbaciones se aplican en memoria, sin escribir en la base. La estadística es la de `experimento/scripts/sensibilidad/estadistica.py`: diferencia pareada del margen, delta de Cliff pareado ≥ 0.147, prueba de signos exacta y Holm por familia.

| Código | Perturbación | Esperado |
|---|---|---|
| SQ1 | En un evento hoy no reconocido, se inserta una paráfrasis del cambio **sin ningún lexema de Jericho** («Yenna ya no respira; su cuerpo quedó tendido…») | El margen sube |
| SQ2 | En un evento hoy reconocido, su ventana se sustituye por una ventana de **otra pareja** | El margen baja |
| SC1 (control) | Se inserta una oración ambiental neutra | Sin cambio |
| SC2 (control) | Se inserta una oración que **nombra** a la entidad sin expresar el cambio | Sin cambio. Si sube, el instrumento responde al nombre y no al estado |

Con la paráfrasis de SQ1 se registra también el veredicto de Jericho, para mostrar su ceguera léxica.

## Cómo correrlo (PowerShell, desde la raíz del repo)

```powershell
docker compose up -d                                   # base levantada
py -m pip install sentence-transformers huggingface_hub
py -m pytest experimento/scripts/semantico/test_semantico.py -q    # pruebas unitarias (sin base ni modelo)

$env:PYTHONUTF8="1"
py experimento/scripts/semantico/embeber_corpus.py --solo-contar   # cuántas oraciones hay (no carga el modelo)
py experimento/scripts/semantico/embeber_corpus.py --pares 07      # prueba con un par: mide el tiempo real
py experimento/scripts/semantico/embeber_corpus.py                 # las 27 parejas (reanudable; horas en CPU)
py experimento/scripts/semantico/recall_semantico.py               # mide y compara G1 - G2
py experimento/scripts/semantico/sensibilidad_semantico.py         # prueba A2
```

- La primera ejecución descarga bge-m3 (unos 2.3 GB) y crea `medicion_oraciones` aplicando `motor/migrations/002_medicion_semantica.sql`.
- Para deshacer todo: `DROP TABLE medicion_oraciones;`

## Salidas

- `datos/datos_v2/semantico/eventos.csv`: un evento por fila, con s_real, q95, margen, z, p empírico, reconocido y el veredicto de Jericho para el mismo evento.
- `datos/datos_v2/semantico/por_campana.csv`: recall semántico y léxico por campaña y por familia.
- `docs/reportes/semantico/cl2_recall_semantico.md`: recall por familia, acuerdo con Jericho y comparación pareada G1 − G2 (Wilcoxon exacto, Hodges-Lehmann con IC bootstrap, r de Kerby).
- `docs/reportes/semantico/sensibilidad_semantico.{md,csv,json}`: la prueba A2, con su hash.
- `docs/reportes/semantico/manifiesto_embeddings.json`: modelo, commit, regla de división y, por campaña, el número de oraciones y el SHA-256 de su contenido.

## Límites declarados

1. Introduce un modelo de embeddings en la medición. La versión queda fijada, pero el resultado depende de ese modelo.
2. La consulta incluye el nombre de la entidad, así que parte de la similitud puede venir del nombre. SC2 lo controla.
3. Mide solo recall, igual que Jericho: no detecta afirmaciones de estado que la base no respalda.
4. La tabla «solo semántico» del informe mezcla paráfrasis reales con posibles falsos positivos. Separarlos exige una revisión humana externa al equipo, que queda como recomendación.
5. Hereda el límite del extractor: si un cambio no quedó registrado en `state_deltas`, no es un evento que se pueda evaluar.

## Texto propuesto para Recomendaciones (tesis)

> Se recomienda desarrollar un instrumento confirmatorio para la coherencia longitudinal que reconozca paráfrasis, dado que el recuerdo léxico de Jericho-QA apenas distingue del azar los cambios de disposición de los personajes no jugadores. Como primer paso se implementó, con carácter exploratorio y sobre el mismo corpus, una versión semántica de dicho recuerdo que compara cada cambio de estado registrado con las oraciones de su ventana de narración mediante representaciones vectoriales (bge-m3 almacenadas en pgvector) y decide contra un nulo exacto construido con las demás ventanas de la misma campaña. Dicho instrumento no altera la generación del corpus ni la clasificación de instrumentos de este estudio, y su promoción a confirmatorio requiere superar su prueba de sensibilidad y una validación humana externa. Cabe precisar que la presente investigación compara arquitecturas de dirección de juego con una misma memoria estructurada, de modo que la comparación entre gestores de memoria, por ejemplo memoria relacional frente a recuperación vectorial, constituye una línea de investigación distinta.
