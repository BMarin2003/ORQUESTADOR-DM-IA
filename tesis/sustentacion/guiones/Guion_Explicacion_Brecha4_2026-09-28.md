# Guión — cierre de brecha 4 y estado de brecha 1 (2026-09-28)

Para presentarle esto a tu asesor: qué se hizo, qué salió, qué significa. Directo, sin vueltas.
Primero brecha 4 (cerrada hoy), después el estado de brecha 1 (persona2, todavía en curso).

# Parte 1 — Brecha 4: validación humana de `cl2_pnj_inactivo_actua` (cerrada)

## El punto de partida

`cl2_pnj_inactivo_actua` es el detector que marca cuándo un PNJ que ya "murió" o quedó fuera de
juego sigue apareciendo en la narración como si actuara — eso es el error de continuidad que mide
H1e. El problema: nadie había comprobado si el detector acierta. Tampoco lo podían validar ustedes
mismos (juez y parte), así que hacía falta gente externa al equipo.

## Qué se hizo

Se sacó una muestra de 60 turnos del corpus, repartida entre los tres casos que importan: el
detector dice "está actuando", el detector dice "solo lo mencionan", y Jericho-QA no reconoció
nada. Tres voluntarios externos etiquetaron esos turnos a ciegas — sin ver qué había dicho el
detector — clasificando cada uno como activo, retrospectivo o no aplica.

Un detalle técnico que vale la pena mencionar si preguntan: de los 60 turnos, uno se repitió dos
veces por un problema de la herramienta de etiquetado. Se detectó porque los tres evaluadores
contestaron exactamente igual las dos veces — así que quedaron 59 casos únicos, no 60, y no afecta
ningún resultado.

## Qué salió

El acuerdo entre los tres, en conjunto, fue bajo (kappa de Fleiss = 0.138). Pero no fue parejo:
el par E1–E3 tuvo acuerdo moderado (80%, kappa 0.595) — cerca del valor que reporta la literatura
para este tipo de tarea. E2, en cambio, quedó cerca del azar con los otros dos, y los datos
explican por qué: contestaba en 12 segundos de mediana (contra 60 y 38 de los otros dos), más de
la mitad de sus respuestas en menos de 15 segundos, y todo concentrado en una sola categoría. Se
excluyó del resultado reportado por esa razón, no por descarte arbitrario.

Con E1 y E3, comparando contra el detector: precisión 62.5%, recall 40%. En criollo — cuando el
detector dice que hay un error, casi dos de cada tres veces tiene razón; pero se le escapa más de
la mitad de los errores reales que sí hubo.

## Qué significa para la tesis

No cambia ninguna conclusión que ya tenías — la refuerza. H1e sigue sin instrumento confirmatorio;
esta es la cuarta línea de evidencia independiente (después de persona2 IA-asistido, Jericho/
relojes y Kaplan-Meier) que apunta a lo mismo: no hay diferencia confiable entre G1 y G2 en
coherencia longitudinal con los instrumentos que existen hoy. Esto ya está redactado en el
apartado 6.5.9 de la tesis y en la Tabla 11.

## Qué queda pendiente de brecha 4

Nada — con esto se cierra. Lo único que queda de todo el bloque de validación humana es brecha 1
(persona2), que sigue su curso aparte (ver Parte 2).

# Parte 2 — Brecha 1: auditoría de precisión de `persona2` (en curso, todavía no cerrada)

## Qué es persona2 y de dónde sale

`persona2` es el detector que marca cuándo el DM le narra al jugador su decisión, pensamiento,
emoción o habla en vez de dejar que el jugador la declare — lo que en la tesis se llama
"usurpación de la agencia del jugador" (indicador QN-2). No es un instrumento inventado sin
respaldo: la razón de que exista viene directamente de **Zhu et al. (2023), "FIREBALL: A Dataset
of Dungeons and Dragons Actual-Play with Structured Game State Information"** — el dataset de
~25,000 sesiones reales de D&D jugadas en Discord con el asistente Avrae. En el análisis
cualitativo de FIREBALL, 45 evaluadores humanos identificaron la usurpación de la agencia del
jugador como **el fallo más frecuente** de los sistemas de generación narrativa que evaluaron. Es
decir: no es una preocupación teórica, es el problema que la literatura ya señaló como el más
común, y persona2 se construyó específicamente para medirlo en este corpus.

Dos citas más redondean el fundamento: **Ware et al. (2023, IEEE Transactions on Games)**, que
mostró que un sistema que nunca suprime las acciones del jugador produce una mayor percepción de
agencia (precedente de que gestionar bien esto sí se nota), y **Murray (1997)**, que es quien
define "agencia" en narrativa interactiva como la capacidad del jugador de tomar acciones con
sentido y ver las consecuencias de sus decisiones — la definición teórica que persona2 opera.

## Por qué es importante ahora mismo

persona2 es el único instrumento confirmatorio (condicionado) de toda la calidad narrativa
emergente, y es el que sostiene, él solo, la única hipótesis comparativa que se acepta en toda la
tesis: H1f (agencia del jugador, G1 favorece con r entre −0.98 y −1.00, p < 0.0001). Si esta
auditoría sale mal, H1f deja de tener sustento. Por eso el asesor ya la tiene marcada como
prioridad en las recomendaciones del propio documento.

## Qué se hizo hasta ahora

Primera pasada: etiquetado ciego de los 515 ítems de la sonda, hecho con asistencia de IA (no por
un evaluador humano) porque hacía falta un avance rápido antes del cierre anterior — y está
documentado como tal explícitamente, nunca presentado como si fuera trabajo humano. Contra la
clave del propio detector: precisión 25.6% (IC95% 20.2–31.8%), recall 67.9% (IC95% 57.1–77.1%).

Desglosado por categoría, el detector no rinde igual en todas: `COGNICION` es la más confiable
(56.7% de lo que marca se confirma), mientras que `HABLA` es la más problemática (apenas 4.3% se
confirma) — casi todo lo que marca como "el PJ habla sin declararlo" en realidad resulta ser
diálogo de un PNJ en el mismo turno, que el detector confunde por su vocabulario cerrado.

## Limitaciones que hay que decir de frente

- **La pasada de arriba no es evaluación humana** — es un proxy de IA, transparente pero proxy.
  No cuenta como la auditoría que pide la literatura de validación de instrumentos de codificación
  automática (Nadya González Romero et al., 2021), que exige medir concordancia con juicio humano.
- **Vocabulario cerrado (v2b congelado):** persona2 busca patrones léxicos fijos, no entiende
  paráfrasis — por eso confunde diálogo de PNJ con habla del PJ.
- **Precisión no medida por separado entre G1 y G2:** si los falsos positivos se concentraran más
  en una arquitectura que en otra, el tamaño del efecto de H1f podría estar sesgado. Todavía no se
  ha calculado esto por separado — queda como recomendación pendiente en la propia tesis.
- **La submuestra del 20% (102 ítems) es la verificación que falta**, y es la que de verdad cuenta
  como auditoría humana.

## Qué se está haciendo ahora (esto es lo nuevo)

El plan original preveía un solo evaluador externo para el 20%. Se decidió ampliarlo a **tres**
evaluadores externos al equipo investigador, mismo criterio de juez y parte que ya rigió brecha 4,
y por la misma razón: con un solo evaluador no hay forma de saber si su criterio es confiable, y
con tres se puede calcular kappa de Fleiss entre ellos y detectar si alguno rinde mal (como pasó
con E2 en brecha 4) sin perder toda la validación. Los tres reciben exactamente los mismos 102
ítems (semilla fija), etiquetan a ciegas sin ver el veredicto del detector, y el análisis va a
cruzar tres cosas: acuerdo entre los tres evaluadores, el consenso mayoritario contra el propio
detector (la precisión/recall real, 100% humana), y ese mismo consenso contra la pasada de IA
(para saber si el proxy sirvió o no para los 413 ítems que ningún humano etiquetó). El script que
hace ese análisis (`analizar_persona2.py`) ya está listo y probado, a la espera de que vuelvan los
tres formularios.

## Qué decir si preguntan "¿y si sale mal?"

Que está contemplado en la propia tesis: la aceptación de H1f está explícitamente marcada como
"confirmatorio provisional" hasta que esto cierre, no como un resultado definitivo escondido bajo
la alfombra. Si la auditoría confirma que el detector es razonablemente preciso, H1f queda
consolidada; si no, hay que revisar los criterios antes de sostenerla — cualquiera de los dos
resultados es una respuesta honesta, no un fracaso del diseño.

## Dónde está todo

- Carpeta/zip para el asesor: `Entrega_Asesor_TESIS/` (con el docx de la tesis actualizado y el
  nuevo reporte de brecha 4 en `03_Resultados_y_Analisis/`).
- persona2 (brecha 1): `datos/validacion/etiquetado_persona2_E2/E3/E4.html` (los tres formularios ciegos
  ya armados, listos para mandar), `experimento/scripts/analizar_persona2.py` (el análisis, pendiente de los
  CSV de vuelta), `03_Resultados_y_Analisis/Auditoria_Persona2_IA_Asistida.md` (la pasada de IA).
- Un detalle aparte, no de ninguna de las dos brechas: al regenerar el docx noté que el Resumen y
  el Abstract todavía describen el diseño original (panel de 5 DMs, escala Likert), mientras el
  resto de la tesis ya documenta el cambio a instrumentos deterministas del 14 de setiembre. Vale
  la pena revisarlo antes de la sustentación — quedó anotado en el `00_LEEME.md` de la entrega, no
  lo toqué porque no es parte de ninguno de estos dos cierres.
