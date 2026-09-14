# Rocabella y la Calabaza Colosal — Lore de campaña (Par 03)

## Nota de tono

Este es el tercer par del corpus experimental. Par 01 (Vado de Ceniza) usó
un tono mixto/aventura; Par 02 (Vela Honda) fue deliberadamente lúgubre y
gótico. Par 03 va al extremo opuesto a propósito: **ligero, cómico, de
apuestas bajas** — nadie va a morir por esto, el "desastre" es social y
absurdo, no existencial. Esta variación es metodológica, no estética: el
instrumento de medición mide únicamente coherencia narrativa, y debe
funcionar igual de bien sobre una comedia de pueblo que sobre una tragedia
gótica. Usar un único tono para los 27 pares sesgaría la comparación hacia
la arquitectura que maneje mejor ESE tono en particular — ver bitácora QM,
punto 27.

`world_tone` para esta campaña: **`light`** (enum válido de Postgres:
`grimdark`/`heroic`/`light`/`mixed`).

## El Valle de las Campanas Doradas

Una región agrícola próspera y sin sobresaltos, conocida en tres condados
a la redonda por un único evento: el Festival de la Cosecha Dorada, que
Rocabella celebra cada año desde hace generaciones. El valle no tiene
ejércitos, ni ruinas malditas, ni sectas — tiene gremios rivales que se
sabotean con guisantes podridos y un comité de festival que se toma su
trabajo con una seriedad completamente desproporcionada al tamaño real del
problema.

## Rocabella

Un pueblo mercado de calles empedradas y toldos de colores, con una plaza
central que se llena de puestos, listones y jueces con monóculo cada
otoño. Todo el pueblo — panaderos, granjeros, el propio comité del
festival — vive en una tensión amistosa pero muy real por el premio mayor:
la Cinta Dorada, que este año iba a coronar a la hortaliza más grande
jamás cultivada en el valle.

Hasta que, la noche antes del juicio, la Calabaza Colosal desapareció del
huerto donde llevaba meses creciendo bajo vigilancia.

## El Gremio de Panaderos de Rocabella

La facción organizadora del festival, y también la más sospechosa de
todas: llevan tres años sin ganar la Cinta Dorada frente a los granjeros
independientes, y este año tenían un pastel de calabaza ya anunciado que
dependía enteramente de que la Calabaza Colosal — la ganadora cantada —
NO llegara a la mesa de jueces intacta. Nadie en el pueblo lo dice en voz
alta, pero todos lo piensan.

## Reloj: el Comité del Festival se impacienta

Si la Calabaza Colosal no aparece antes del amanecer del día del juicio,
el Comité cancela el Festival por primera vez en generaciones. El pueblo
entero se lo tomará personal — habrá acusaciones cruzadas, un boicot al
Gremio de Panaderos, y probablemente una pelea de tartas en la plaza que
nadie podrá parar. Nada de esto pone a nadie en peligro real: es puro
caos social, vecinos enfadados entre sí durante meses.

## El huerto y la plaza

El huerto donde creció la calabaza — vallado, vigilado por turnos, y sin
embargo vacío esa mañana — es la escena del "crimen". La plaza del
festival, con su tarima de jueces ya montada, es donde todo tendrá que
resolverse antes del amanecer del día señalado.

## Personajes centrales

**Capitán Bramble Woth**, jefe de la guardia del pueblo, cree genuinamente
que un formulario en triplicado puede resolver cualquier crisis y se
interpone constantemente entre el grupo y cualquier pista con
procedimientos inventados sobre la marcha.

**Mireia Tossel**, granjera y dueña legítima de la Calabaza Colosal,
acusa a gritos al Gremio de Panaderos de todo el pueblo cada cinco
minutos — y no está del todo equivocada, aunque tampoco tiene ni idea de
lo que realmente pasó.

**Ferro "el Cabrero"**, un pastor de cabras que ya dejó de que le importe
la política del pueblo hace años, y que probablemente vio algo esa noche
mientras cuidaba su rebaño — se lo cuenta a cualquiera que se moleste en
sentarse a escucharlo, porque francamente le da igual quién gane la Cinta
Dorada.

## Sobre el uso de este corpus en el protocolo de medición

Igual que en los pares anteriores, este documento se inserta como turno 0
(texto narrativo puro) de AMBAS campañas del par — G1 (multiagente) y G2
(monolítico) — junto con el mismo `fixtures/world_par03.json` y
`fixtures/personas_par03.json`, de modo que ambos brazos arrancan de
exactamente las mismas condiciones iniciales. La variación de tono entre
pares es deliberada; la variación de condiciones DENTRO de un par no lo
es — eso seguiría siendo una ventaja injusta de una arquitectura sobre
la otra.
