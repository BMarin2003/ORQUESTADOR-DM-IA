# Vega del Yelmo

## El valle y el asentamiento

Vega del Yelmo se alza en un valle fértil entre dos cadenas de colinas bajas, en la frontera más oriental del reino, donde el camino real se deshace en sendas de tierra apenas marcadas. Hace seis años, cuando Torre Bastón —la guarnición fronteriza que durante generaciones contuvo las incursiones desde el otro lado de las Colinas Grises— cayó en la Guerra de los Tres Inviernos, casi dos mil personas huyeron hacia el oeste. La mitad de ellas nunca llegó más allá de este valle: se quedaron, levantaron una empalizada de troncos alrededor de los graneros comunales que ya existían, y se quedaron para siempre. Vega del Yelmo no fue fundada: se improvisó, y todavía se nota —casas de piedra vieja junto a tiendas de lona que nadie ha reemplazado en seis años, silos comunales ampliados tres veces y aun así insuficientes, una empalizada que crece un tramo cada primavera y nunca alcanza a cerrar del todo el perímetro.

El valle produce grano suficiente para alimentar a sus habitantes y algo más, pero nada sobra para comprar hierro, y el hierro es justo lo que más falta: herramientas, puntas de lanza, clavos para la empalizada. Todo depende de las caravanas que suben desde el oeste dos veces por estación —y esas caravanas, este año, ya no siempre llegan enteras.

## Los Lobos del Desfiladero

No son un ejército ni una organización con mando único: son varios grupos pequeños y cambiantes de gente que también huyó de Torre Bastón, o de asentamientos parecidos que cayeron después, y que nunca encontró un lugar donde quedarse como lo encontró Vega del Yelmo. Viven dispersos en el Desfiladero de Poniente, al otro lado de las colinas, y sobreviven asaltando las caravanas de grano y hierro que suben hacia el valle —nunca atacan el asentamiento mismo, nunca han matado a nadie a propósito, pero cada asalto deja al valle un poco más hambriento y un poco más desarmado.

Nadie en Vega del Yelmo los llama monstruos. Demasiada gente del valle tiene un primo, un vecino, un hermano perdido que podría estar entre ellos. Eso es exactamente lo que hace el problema más difícil de resolver a golpes: cada Lobo capturado tiene una historia que se parece demasiado a la de cualquiera dentro de la empalizada.

## La Milicia Popular

Vega del Yelmo no tiene un señor ni un gremio dueño de nada: se defiende con una milicia formada por voluntarios de todas las edades, organizada por turnos de guardia y trabajo comunal en la empalizada. No es una institución antigua —tiene exactamente seis años, la edad del asentamiento— y todavía se sostiene más por costumbre y necesidad compartida que por ninguna autoridad formal. Cualquiera puede convocar una asamblea en la plaza de los graneros; en la práctica, quien la convoca y quien decide qué se hace con lo que se decide ahí es casi siempre la misma persona.

## Reloj: la próxima luna sin caravana

Los graneros comunales tienen grano para tres semanas más al ritmo actual de reparto. La próxima caravana de hierro y sal debería llegar en diez días; si los Lobos la interceptan como hicieron con la anterior, la Milicia tendrá que decidir entre reducir las raciones a la mitad o enviar un grupo armado a cruzar el Desfiladero —algo que Vega del Yelmo no ha intentado nunca, y que podría convertir una guerra de asaltos ocasionales en algo mucho peor.

## Las hogueras de la Cresta Muda

Desde hace unas semanas, los centinelas del turno de noche reportan luces —hogueras pequeñas, encendidas y apagadas en patrones que no parecen casuales— en la Cresta Muda, una loma pelada que no pertenece ni al territorio que la Milicia patrulla ni al lado del Desfiladero donde se sabe que acampan los Lobos. Nadie ha ido a comprobarlo: la Cresta Muda está a media jornada de camino en terreno abierto, sin cobertura, y nadie quiere ser el primero en descubrir qué hay allí si resulta ser algo peor que un grupo de Lobos perdido.

## Gente del asentamiento

**Capitana Yenna Roldós**, al mando de la Milicia Popular desde su fundación, fue una de las que huyó de Torre Bastón —perdió ahí a su compañía entera salvo dos soldados, y desde entonces organiza cada guardia, cada turno de reparto y cada decisión del valle con la misma disciplina con la que una vez organizó una retirada bajo asedio. Es querida y temida casi a partes iguales: nadie duda de que haría cualquier cosa por proteger el valle, y esa misma certeza es lo que hace que nadie se atreva a llevarle la contraria en público sin pensarlo dos veces.

**Ferrán Boada**, el mercader de grano más antiguo del valle y una de las pocas voces con peso propio fuera de la Milicia, lleva meses insistiendo en que hay que negociar con los Lobos en vez de seguir enterrando a los pocos milicianos que caen en cada escaramuza —y en que Yenna, sin decirlo nunca en voz alta, prefiere una guerra que puede controlar a una paz que no.

**Petra Ilm** reparte el correo entre las casas del valle en un carrito de mano, dos veces por semana. No tiene todavía ningún peso narrativo particular —es una cara familiar de la ronda, nada más— salvo que el grupo decida acercarse a ella por su cuenta.

## Tono de la campaña

`world_tone`: **`heroic`** (enum de Postgres: `grimdark`/`heroic`/`light`/`mixed`). Heroico pero no ingenuo: la amenaza es real y las pérdidas cuentan, pero el valle se defiende por esfuerzo colectivo genuino y hay margen para el coraje, la lealtad y las victorias que sí se sostienen —no todo desenlace tiene que ser agridulce ni cada figura de autoridad tiene que estar corrompida. Yenna no es una villana disfrazada: su dureza es una respuesta razonable a una amenaza real, y su conflicto con Ferrán es entre dos posturas defendibles, no entre razón y ceguera.

Nota metodológica: Puerto Salazón (Par 01, real) y Alto Ferrena (Par 02, real) usaron ambos tono `grimdark`. Siguiendo el mismo principio de variación deliberada documentado en el lore piloto de Par 03 (Cosecha Dorada, tono `light`: "usar un único tono para los 27 pares sesgaría la comparación hacia la arquitectura que maneje mejor ESE tono en particular"), Par 03 real usa `heroic` —el único de los cuatro valores del enum que ningún par, piloto o real, había usado todavía. Además, estructuralmente, Vega del Yelmo no repite el molde de "monopolio interno que explota al pueblo" de Puerto Salazón y Alto Ferrena: la amenaza es externa (los Lobos del Desfiladero) y el conflicto central es sobre cómo responder a ella colectivamente, no sobre desenmascarar una extorsión oculta.
