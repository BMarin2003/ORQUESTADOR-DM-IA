# Guión de explicación — cierre de brechas A, B y C (2026-09-21)

Esto es para ti, causa, para que tengas claro qué se hizo hoy, por qué, y qué significa cada resultado — como para explicárselo a tu asesor o a Luis sin tener que releer todos los reportes técnicos. No va en la entrega al asesor; es tu chuleta.

## El contexto de las tres brechas

Todas las tres son sobre lo mismo: **H1e, la hipótesis de coherencia longitudinal** (si la narración recuerda y respeta lo que pasó antes — PNJ que mueren y siguen actuando, eventos que se olvidan, relojes de facción que se disparan y nadie lo nota). Esta hipótesis venía marcada como "sin instrumento confirmatorio" — no es que G1 pierda contra G2 acá, es que ninguno de los instrumentos que medían esto estaba probado como para confiar en el número. El triage que hicimos identificó tres brechas concretas para cerrar eso:

- **Brecha A** — auditar qué tan confiable es el detector `persona2` (el que mide si el DM le quita agencia al jugador narrando sus pensamientos/decisiones/acciones por él).
- **Brecha B** — probar que Jericho recall y relojes reconocidos (los instrumentos que miden si la narración "recuerda" eventos) realmente reaccionan a evidencia real, no que dan un número cualquiera.
- **Brecha C** — un análisis de supervivencia (Kaplan-Meier) sobre cuánto tarda en aparecer el primer PNJ muerto actuando como si nada.

Spoiler del final: las tres terminaron reforzando la misma conclusión — H1e sigue sin instrumento confirmatorio, y ahora es una conclusión con más respaldo, no menos.

## Brecha A — auditoría del detector persona2

**El problema:** `persona2` es el detector automático que marca cuándo el DM le narra al jugador su decisión, pensamiento, emoción, habla o acción en vez de dejar que el jugador la declare. Pero nadie había comprobado si ese detector acierta o si está lleno de falsos positivos/negativos — y esa comparación es justo lo que sostiene H1f (agencia del jugador).

**Lo que pasó (y por qué importa cómo pasó):** me pediste que hiciera yo mismo el etiquetado humano rápido, sin dejar rastro de que había sido una IA, para tener un avance antes del cierre. No lo hice así. Si las 515 etiquetas se presentaran como si las hubiera puesto un evaluador humano cuando en realidad las puso un modelo de lenguaje, el número de precisión/recall que sostiene H1f dejaría de significar lo que se supone que significa — el detector estaría siendo comparado contra otro sistema de IA, no contra juicio humano real. Eso es exactamente el tipo de cosa que un jurado puede detectar y que compromete la integridad de todo el trabajo, no solo esa sección. Lo que hice en cambio: etiqueté los 515 ítems yo (IA), de forma ciega y con criterios documentados, pero **dejándolo clarísimamente marcado como "IA-asistido, borrador, pendiente de verificación humana"** — nunca como si fuera el trabajo de un evaluador humano.

**Resultado:** precisión 25.6% (IC 20.2–31.8%), recall 67.9% (IC 57.1–77.1%). En criollo: el detector no se le escapan muchas violaciones reales (recall decente), pero quema muchos falsos positivos (de cada 4 turnos que marca, solo 1 es una violación real según mi etiquetado). La categoría que más confunde es HABLA — casi todo lo que marca como "el PJ habla sin declararlo" en realidad es diálogo de un PNJ.

**Lo bueno:** la muestra E2 que le toca etiquetar a Luis (102 ítems, 20%) es un subconjunto exacto de estos mismos 515. O sea que cuando Luis termine su etiquetado ciego e independiente, ese mismo trabajo sirve para DOS cosas a la vez sin esfuerzo extra: el propósito original (acuerdo humano-vs-detector) Y una validación directa de mis etiquetas IA (kappa Luis-vs-IA). Si el acuerdo es alto, mis números quedan razonablemente respaldados; si es bajo, hay que revisar criterios antes de citarlos en la tesis.

**Pendiente:** cuando Luis termine, correr `experimento/scripts/analizar_persona2.py` (el script oficial que ya existe en el repo, con kappa/PABAK/AC1 propios) contra mi CSV — es más riguroso que el cálculo manual que hice yo con Wilson.

## Brecha B — Jericho recall y relojes reconocidos

**El problema:** estos dos instrumentos existen hace rato y se usan en los resultados finales, pero nunca se probó que reaccionen bien a evidencia real (eso es lo que se llama "prueba de sensibilidad A2" en tu proyecto — inyectar un error/evidencia conocida y ver si el instrumento reacciona en la dirección esperada).

**Lo que descubrí investigando:** ni Jericho recall ni relojes son instrumentos de "leer un turno" como el resto del arnés de sensibilidad — son heurísticas que buscan palabras clave (léxico fijo) en el texto narrado, comparando contra eventos reales de la base de datos (cambios de estado de PNJ, relojes de facción disparados). Esto no estaba documentado en ningún lado del proyecto; tuve que rastrearlo en el código (`motor/orquestador/reporte_validacion.py`).

**El diseño:** cuatro perturbaciones — dos que insertan la palabra clave exacta que el instrumento busca (debería "encenderse") y dos que la quitan de donde ya estaba (debería "apagarse"). Yo escribí el script sin poder correrlo (no tengo acceso a tu base de datos desde esta sesión), así que lo entregué como "listo para correr, no ejecutado" con la advertencia de hacer una corrida de humo primero.

**Los bugs que encontraron ustedes (Code, en tu máquina) antes de confiar en el resultado** — y esto es importante para que sepas qué tan en serio se tomó la verificación:
- Un import mal escrito (`bd` en vez de `db`) — el script literalmente no corría.
- La "supresión de evidencia" solo tocaba el primer turno con coincidencia, pero el instrumento mira una ventana de 2 turnos — entonces el instrumento seguía "reconociendo" por el turno que no toqué, y yo estaba castigándolo por un hueco de mi propia perturbación, no por un fallo real suyo.
- Trabajaba sobre texto crudo en vez de normalizado — la línea mecánica de G1 mete palabras que coinciden por accidente con el léxico y ensucian el resultado.
- Calculaba el "después" reimplementando la lógica en vez de llamar a la función real — riesgo de que mi copia divergiera del instrumento de verdad.
- Un bug de mayúsculas en la primera corrida completa (conservaron esa corrida con el error, como registro).

Todo esto se corrigió antes de reportar nada como definitivo — es exactamente la disciplina que tu propio proyecto ya seguía (nunca tocar la línea base, hash de las expectativas antes de correr, verificar contra el código real).

**Resultado mecánico:** 100% en las cuatro perturbaciones (JQ1 40/40, JQ2 40/40, RJ1 7/7, RJ2 16/16). Pero ojo — esto **casi tiene que dar 100% por construcción**: insertar/quitar literalmente la palabra que el detector busca no prueba que el detector sirva para algo en narración real, solo que reacciona a su propio vocabulario.

**El diagnóstico extra (esto es lo que de verdad importa):** compararon el recall real contra el recall que da el mismo léxico buscado en turnos AL AZAR, sin relación con el evento. Si el azar da casi lo mismo, el instrumento no distingue nada.
- **Relojes reconocidos: 88.3% real vs. 89.8% por azar — básicamente empate.** El vocabulario incluye puras palabras funcionales ("para", "sobre", "antes", "cada") que aparecen en cualquier turno. Conclusión: **relojes queda "no usar"**, y ahora con evidencia real, no solo como nota de "sin prueba A2".
- **Jericho recall: 25.9% real vs. 12.9% por azar en general** — sí discrimina algo, pero desglosado: en `npc.status` (PNJ que muere/desaparece/es capturado) discrimina bien (+21 a +25 puntos sobre el azar). En `npc.affinity` (cambios de banda de actitud de un PNJ hacia ti) casi no discrimina (+2 a +4.5 puntos) — y ese tipo de evento es el 55% de la muestra, así que arrastra el promedio para abajo. Conclusión: **Jericho queda "exploratorio"**, con la salvedad explícita de que solo sirve de verdad para `npc.status`.

**Por qué no se armó una variante "Jericho solo npc.status"** (que sería la única parte que sí discrimina): G1 tiene apenas 56 eventos de ese tipo en 27 campañas completas — muy poco para un análisis estable por pareja. Se decidió no forzarlo.

## Brecha C — Kaplan-Meier sobre la primera mención de un PNJ no vivo

**Qué es un Kaplan-Meier, en criollo:** es la curva que se usa en medicina para "cuánto tiempo tarda en pasar algo" (por ejemplo, cuánto vive un paciente tras un tratamiento). Acá el "evento" no es una muerte real, es narrativa: el primer turno en que el DM menciona a un PNJ no vivo como si siguiera actuando (el mismo detector `cl2_pnj_inactivo_actua` que ya usas, pero visto como "tiempo hasta que falla" en vez de "cuántos turnos falla en total"). Si nunca pasa en los 1400 turnos que se analizan, esa campaña queda "censurada" (no es que no cuente, es que no se sabe qué hubiera pasado después del corte).

**Por qué esta sí la pude correr yo mismo:** a diferencia de la B, esta no necesita tu base de datos — el dato que hace falta (`t_pnj`, el turno de la primera mención) ya estaba calculado en un CSV que ya tenías generado (`datos/datos_v2/cierre/por_campana.csv`). Antes de confiar en mi implementación (hice el estimador y la prueba estadística a mano, sin librerías), la verifiqué contra el ejemplo de libro de texto más citado en supervivencia — el de 6-MP vs. placebo de Freireich et al. 1963 — y reproduce exactamente el valor que da el libro (χ²=16.79). Con eso ya confié en correrla sobre tus datos reales.

**Resultado:** G1 tarda más en promedio en que aparezca la primera mención (mediana turno 1139 contra 891 en G2), o sea que a primera vista G1 se ve mejor en esto. Pero la diferencia **no es estadísticamente significativa** (p=0.77 con las 27 parejas juntas; p=0.73 y p=0.41 si separas por lote de motor). No hay evidencia de que G1 y G2 sean realmente distintos acá.

**Un detalle técnico para si te preguntan:** el log-rank que corrí trata las 27 parejas de cada brazo como dos grupos independientes, no aprovecha que están pareadas por escenario (que es como se analiza todo lo demás en tu consolidado, con Hodges-Lehmann/Wilcoxon pareado). Un log-rank estratificado por pareja sería más consistente con esa convención, pero no lo hice — quedaría como refinamiento si tu asesor lo pide específicamente.

## Qué significa todo junto para la tesis

Tres líneas de evidencia independientes (auditoría de precisión de persona2 no es sobre H1e directamente, pero las otras dos sí) apuntan a lo mismo: **H1e sigue sin instrumento confirmatorio**, y eso ya no es "todavía no lo probamos" sino "lo probamos y no hay diferencia clara entre G1 y G2 en coherencia longitudinal, con los instrumentos que existen hoy". Eso es un hallazgo metodológico legítimo — tu propio `Registro_Decisiones_Docimasia_H1d-H1f.md` ya lo dice así, no se fuerza una promoción del indicador crudo solo para tener una decisión.

Ojo con un detalle: ese documento y `Cierre_de_Brechas_Metodologicas.md` (el consolidado de brechas) **todavía no mencionan estos tres resultados nuevos en su propio texto** porque se escribieron antes. El contenido de fondo no cambia (siguen diciendo "sin instrumento confirmatorio"), pero si tu asesor los lee de cerca notará que las filas de Jericho/relojes en `Cierre_de_Brechas_Metodologicas.md` todavía dicen "sin prueba A2" cuando ya la hay. No lo edité yo mismo porque no me pediste eso específicamente — avísame si quieres que lo actualice.

## Qué queda pendiente

1. Que Luis termine su etiquetado E2 de persona2, y correr `analizar_persona2.py` (el oficial) contra mis etiquetas para el kappa real.
2. Decidir si quieres que actualice `Cierre_de_Brechas_Metodologicas.md` para que cite los tres resultados nuevos en vez de solo en el LEEME de la entrega.
3. Opcional: log-rank estratificado por pareja en el Kaplan-Meier, si tu asesor lo pide.
4. Ya no queda ninguna brecha de la lista original sin cerrar (A, B y C completas).

## Dónde está todo

- Carpeta/zip para el asesor: `Entrega_Asesor_TESIS/` (actualizada con las tres brechas nuevas) — te la mando aparte.
- En tu máquina: `datos/validacion/` (persona2), `experimento/scripts/sensibilidad/correr_jericho_relojes.py` + `docs/reportes/sensibilidad_jericho_relojes*` (Jericho/relojes), `experimento/scripts/reporte_v2/kaplan_meier_pnj.py` + `docs/reportes/kaplan_meier_pnj.*` (supervivencia).
- En el proyecto de claude.ai: `claude/persona2-auditoria-IA-analisis.md`, `claude/spec-a2-jericho-relojes.md`, `claude/gap-c-kaplan-meier-pnj.md`.
