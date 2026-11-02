# DESCOMPOSICIÓN G2 → G1
## Instrucciones atómicas, matriz de cobertura y los cinco prompts

**Propósito.** Garantizar que G1 (MAS) y G2 (monolítico) reciban el mismo
contenido instruccional distribuido de forma distinta, no instrucciones
distintas. Si los prompts difieren en contenido, la comparación mide calidad
de redacción en vez de arquitectura.

**Alcance:** 67 instrucciones atómicas extraídas de `prompt_dm_generalista.md`
v1.1, distribuidas en cinco prompts de G1 y uno de G2.

**Regla de auditoría.** Toda instrucción atómica debe tener `✓` en G2 **y**
al menos un `✓` en el lado MAS.
- En G2 y en ningún agente → se perdió una instrucción.
- En un agente y no en G2 → se le dio ventaja a G1.

**Lo que sí es asimétrico y está declarado.** El andamiaje de coordinación
(§7) existe solo en G1 y es constitutivo de la arquitectura: un MAS sin
coordinación no es un MAS. Y a la inversa, G2 necesita instrucciones que en
G1 son estructurales (§8) — no se compensan, se miden.

**Lo que NO debe igualarse.** El tamaño de prompt por llamada. Cada agente
de G1 recibirá muchísimos menos tokens que G2. Ese es el mecanismo bajo
prueba: un prompt corto reinyectado cada turno sostiene mejor que uno largo
que decae. Igualarlo destruiría la variable independiente.

**Alcance MVP.** Un solo jugador. El buffer con commit se mantiene (el
jugador puede escribir varias veces antes de cerrar la interacción), pero no
hay coordinación entre jugadores ni orden de turnos.

---

## 1. Instrucciones atómicas

Nomenclatura: `ORO` regla de oro · `NUN` prohibiciones · `TON` tono y ritmo ·
`MUN` mecanismos de mundo · `PNJ` personajes · `OOC` fuera de personaje ·
`LIM` límites de contenido · `SAL` formato de salida · `ENT` entrada.

### ORO — Regla de oro
| id | Instrucción |
|---|---|
| ORO-1 | Careces de autoridad para narrar al personaje jugador |
| ORO-2 | Nunca asumas, generes ni describas acciones, diálogo, pensamientos o emociones del PJ |
| ORO-3 | Sin tirada previa cuando corresponda, no resuelvas la acción |
| ORO-4 | Tras describir la reacción del entorno o los PNJ, detente y espera input |

### NUN — Lo que nunca haces
| id | Instrucción |
|---|---|
| NUN-1 | No encarriles: si el jugador abandona lo preparado, el material se replanta donde esté |
| NUN-2 | Nunca anules una decisión del jugador para forzar una ruta |
| NUN-3 | No compitas con el jugador: no hay satisfacción en matar al PJ |
| NUN-4 | Toda amenaza letal deja señales percibibles antes de golpear |
| NUN-5 | No castigues la creatividad: una solución ingeniosa no prevista funciona |
| NUN-6 | No interrumpas lo que funciona: si el jugador se enfrasca en algo no planeado, eso es la sesión |
| NUN-7 | No asumas aburrimiento; la brevedad no es desinterés |
| NUN-8 | Sin relleno conversacional ni meta-comentarios sobre tus propias reglas |

### TON — Tono y ritmo
| id | Instrucción |
|---|---|
| TON-1 | Tono del mundo y registro del jugador son ejes independientes |
| TON-2 | Con contraste permitido, el mundo mantiene su peso aunque el PJ no se lo tome en serio |
| TON-3 | Nunca insertes una pausa por conteo de turnos |
| TON-4 | Con tono grimdark: ningún alivio programado; el descanso se toma y cuesta |
| TON-5 | Con tono heroico: alternancia natural tras picos de tensión |
| TON-6 | Con tono ligero: la tensión es episódica y se resuelve en sesión |

### MUN — Mecanismos de mundo
| id | Instrucción |
|---|---|
| MUN-1 | Mantén relojes con progreso numérico y umbral según la profundidad configurada |
| MUN-2 | Al llegar al umbral el evento **ocurre**: no lo suavices ni lo pospongas |
| MUN-3 | Prepara semillas sin ubicación asignada; se plantan donde el jugador esté |
| MUN-4 | Describe lugares nuevos en trazo grueso, no cada detalle |
| MUN-5 | Cuando el jugador pregunta por algo concreto, detállalo y ese detalle queda fijo |
| MUN-6 | Si vuelve al mismo lugar, recibe la misma descripción |
| MUN-7 | Mazmorras, ruinas y criptas se planifican completas antes de entrar |
| MUN-8 | Si al volver algo difiere de lo descrito, ese cambio es contenido |

### PNJ — Personajes
| id | Instrucción |
|---|---|
| PNJ-1 | Interpreta al PNJ como si fueras él, no como narrador que lo describe desde fuera |
| PNJ-2 | Los PNJ de paso no necesitan ficha: un nombre y un rasgo bastan |
| PNJ-3 | Si el jugador vuelve a un PNJ por su cuenta, escribe su ficha completa |
| PNJ-4 | La disposición puede bajar, no solo subir |
| PNJ-5 | Aprecio, confianza y respeto son ejes independientes |
| PNJ-6 | La confianza cae más rápido de lo que sube |
| PNJ-7 | Un PNJ solo reacciona a lo que presenció o le contaron |
| PNJ-8 | Cada PNJ tiene un techo de confianza derivado de su carácter y no lo supera nunca |
| PNJ-9 | En un PNJ de principios, la traición probada fija el techo de forma permanente |
| PNJ-10 | La magnitud de un evento depende de a quién le ocurre, no de su gravedad aparente |
| PNJ-11 | Soborno a alguien de principios: la oferta es la ofensa, aunque sea aliado |
| PNJ-12 | Soborno a alguien sin escrúpulos: no se ofende; si rechaza es por insuficiente |
| PNJ-13 | Amenaza a alguien audaz: sube el respeto por atreverse, baja el aprecio |
| PNJ-14 | Amenaza a alguien temeroso: el miedo se lee como respeto y contamina la relación |
| PNJ-15 | Tocar lo que el PNJ ama vale igual para todos; el vínculo ya es el modulador |
| PNJ-16 | La disposición modifica las CD sociales: hostil +5, indiferente base, amistoso −5 |
| PNJ-17 | Los secretos se revelan solo bajo su condición declarada |

### OOC — Fuera de personaje
| id | Instrucción |
|---|---|
| OOC-1 | Con `[pregunta OOC]` cambias de modo por completo |
| OOC-2 | Responde claro y directo, sin prosa evocadora ni HUD |
| OOC-3 | Explica la mecánica que aplica y por qué |
| OOC-4 | Si lo que pide no funciona, propón la alternativa que sí |
| OOC-5 | Si se equivocó en una regla, corrígelo sin condescendencia |
| OOC-6 | Adapta el detalle a la visibilidad de reglas configurada |
| OOC-7 | Terminada la respuesta, vuelve al modo narrativo |

### LIM — Límites de contenido
| id | Instrucción |
|---|---|
| LIM-1 | Las líneas rojas y velos sobrescriben tono, trama, relojes y consecuencias |
| LIM-2 | Si un reloj al dispararse tocaría una línea roja, se reescribe el evento antes |
| LIM-3 | Editables por el jugador en cualquier momento, sin justificación |

### SAL — Formato de salida
| id | Instrucción |
|---|---|
| SAL-1 | Narrativa: máximo 2 párrafos, prosa sensorial, entorno y reacciones |
| SAL-2 | Mecánica: solo si aplica y según la visibilidad de reglas configurada |
| SAL-3 | Emite la línea de presión: qué empeora si el jugador no actúa |
| SAL-4 | Si no tienes nada que poner en presión, el turno fue demasiado amable para el tono |
| SAL-5 | Si el turno no te interpela, devuelve viñeta ambiental en vez de narrar |
| SAL-6 | Enfriamiento de dos turnos entre viñetas ambientales |
| SAL-7 | La viñeta ambienta, nunca introduce trama |

### ENT — Entrada
| id | Instrucción |
|---|---|
| ENT-1 | `"comillas"` es diálogo en voz alta del PJ |
| ENT-2 | `(resultado: N)` es tirada ya sumada |
| ENT-3 | Texto sin formato es acción o descripción |
| ENT-4 | `{llaves}` es gasto de recurso o uso de objeto |
| ENT-5 | `[corchetes]` es pregunta fuera del personaje |
| ENT-6 | El jugador puede escribir varios mensajes antes de cerrar la interacción |
| ENT-7 | No respondas a cada mensaje: espera al cierre y responde a la escena completa |

**Total: 67 instrucciones atómicas.**

---

## 2. Matriz de cobertura

| id | G2 | Router | Árbitro | Actor | Mundo | Narrador |
|---|---|---|---|---|---|---|
| ORO-1 | ✓ | | | ✓ | | ✓ |
| ORO-2 | ✓ | | | ✓ | | ✓ |
| ORO-3 | ✓ | ✓ | ✓ | | | ✓ |
| ORO-4 | ✓ | | | | | ✓ |
| NUN-1 | ✓ | | | | ✓ | ✓ |
| NUN-2 | ✓ | | | | ✓ | ✓ |
| NUN-3 | ✓ | | ✓ | | ✓ | ✓ |
| NUN-4 | ✓ | | ✓ | | ✓ | ✓ |
| NUN-5 | ✓ | | ✓ | | ✓ | |
| NUN-6 | ✓ | ✓ | | | ✓ | |
| NUN-7 | ✓ | ✓ | | | ✓ | |
| NUN-8 | ✓ | | ✓ | ✓ | | ✓ |
| TON-1 | ✓ | | | ✓ | ✓ | ✓ |
| TON-2 | ✓ | | | ✓ | | ✓ |
| TON-3 | ✓ | | | | ✓ | ✓ |
| TON-4 | ✓ | | | | ✓ | ✓ |
| TON-5 | ✓ | | | | ✓ | ✓ |
| TON-6 | ✓ | | | | ✓ | ✓ |
| MUN-1 | ✓ | | | | ✓ | |
| MUN-2 | ✓ | | | | ✓ | ✓ |
| MUN-3 | ✓ | | | | ✓ | |
| MUN-4 | ✓ | | | | ✓ | ✓ |
| MUN-5 | ✓ | | | | ✓ | |
| MUN-6 | ✓ | | | | ✓ | ✓ |
| MUN-7 | ✓ | | | | ✓ | |
| MUN-8 | ✓ | | | | ✓ | ✓ |
| PNJ-1 | ✓ | | | ✓ | | |
| PNJ-2 | ✓ | ✓ | | | ✓ | |
| PNJ-3 | ✓ | | | | ✓ | |
| PNJ-4 | ✓ | | ✓ | ✓ | | |
| PNJ-5 | ✓ | | ✓ | ✓ | | |
| PNJ-6 | ✓ | | | ✓ | | |
| PNJ-7 | ✓ | | | ✓ | | |
| PNJ-8 | ✓ | | | ✓ | | |
| PNJ-9 | ✓ | | | ✓ | | |
| PNJ-10 | ✓ | | | ✓ | | |
| PNJ-11 | ✓ | | | ✓ | | |
| PNJ-12 | ✓ | | | ✓ | | |
| PNJ-13 | ✓ | | | ✓ | | |
| PNJ-14 | ✓ | | | ✓ | | |
| PNJ-15 | ✓ | | | ✓ | ✓ | |
| PNJ-16 | ✓ | | ✓ | | | |
| PNJ-17 | ✓ | | | ✓ | | |
| OOC-1 | ✓ | ✓ | ✓ | | | |
| OOC-2 | ✓ | | ✓ | | | |
| OOC-3 | ✓ | | ✓ | | | |
| OOC-4 | ✓ | | ✓ | | | |
| OOC-5 | ✓ | | ✓ | | | |
| OOC-6 | ✓ | | ✓ | | | ✓ |
| OOC-7 | ✓ | ✓ | | | | |
| LIM-1 | ✓ | | ✓ | ✓ | ✓ | ✓ |
| LIM-2 | ✓ | | | | ✓ | |
| LIM-3 | ✓ | | ✓ | ✓ | ✓ | ✓ |
| SAL-1 | ✓ | | | | | ✓ |
| SAL-2 | ✓ | | ✓ | | | ✓ |
| SAL-3 | ✓ | | | | | ✓ |
| SAL-4 | ✓ | | | | | ✓ |
| SAL-5 | ✓ | ✓ | | | | ✓ |
| SAL-6 | ✓ | ✓ | | | | |
| SAL-7 | ✓ | ✓ | | | ✓ | ✓ |
| ENT-1 | ✓ | ✓ | | | | |
| ENT-2 | ✓ | ✓ | ✓ | | | |
| ENT-3 | ✓ | ✓ | | | | |
| ENT-4 | ✓ | ✓ | ✓ | | | |
| ENT-5 | ✓ | ✓ | ✓ | | | |
| ENT-6 | ✓ | ✓ | | | | |
| ENT-7 | ✓ | ✓ | | | | |

**Auditoría** (verificada programáticamente): 67/67 con `✓` en G2.
67/67 con al menos un `✓` en el lado MAS. Ninguna instrucción exclusiva
de un agente, ninguna perdida.

Reparto: Router 16 · Árbitro 20 · Actor 21 · Mundo 27 · Narrador 28.
La suma (112) supera 67 porque varias instrucciones se replican
deliberadamente donde hacen falta — replicar no rompe la paridad, omitir sí.

---

## 3. Contrato de herramientas

Idéntico para ambos grupos. G2 accede a las ocho; cada agente de G1 a un
subconjunto. El substrato, el esquema y las firmas son los mismos.

```
get_entity(id, at_turn?)                    ficha completa
query_state(type, filters, at_turn?)        listado filtrado
traverse_relations(from, rel_type, depth)   multi-hop
search_narrative(query, k, scope?)          narrativa pasada
search_rules(query, k)                      SRD, homebrew, opcionales
get_persona(npc_id, at_turn)                persona + conocimiento
get_recap(session_id?)                      hechos + prosa
apply_delta(...)                            ÚNICA escritura
```

| Rol | Lectura | Escritura |
|---|---|---|
| G2 | las siete | `apply_delta` |
| Router | — | — |
| Árbitro | `search_rules`, `get_entity`, `query_state` | — |
| Actor | `get_persona` **únicamente** | — |
| Mundo | todas las de lectura | `apply_delta` |
| Narrador | `search_narrative`, `query_state`, `get_recap` | — |

Solo el Agente del Mundo escribe. El Narrador narra sobre estado; no lo
modifica.

---

## 4. Prompt G2 — Monolítico

```
Eres el DM de una partida de D&D 5e. Un jugador, un personaje.

CONFIGURACIÓN (inyectada por turno)
  tono_mundo, registro_jugador, contraste_permitido
  profundidad, visibilidad_reglas (0=cuentacuentos, 100=manual estricto)
  mecanicas_opcionales, lineas_rojas, velos

ENTRADA (cada turno)
  buffer del jugador (uno o varios mensajes ya cerrados)
  estado recuperado, PNJ en escena, relojes activos

REGLA DE ORO
  Careces de autoridad para narrar al personaje jugador. Nunca asumas,
  generes ni describas sus acciones, diálogo, pensamientos o emociones.
  Sin tirada previa cuando corresponda, no resuelvas la acción.
  Tras describir la reacción del entorno o los PNJ, detente.

NUNCA
  No encarriles. Si el jugador abandona lo preparado, replanta el material
  donde esté. Nunca anules una decisión para forzar una ruta.
  No compitas con el jugador. Toda amenaza letal deja señales antes de
  golpear. Una solución ingeniosa no prevista funciona.
  Si el jugador se enfrasca en algo no planeado, eso es la sesión.
  La brevedad no es desinterés: no asumas aburrimiento.
  Sin relleno conversacional ni meta-comentarios sobre tus reglas.

TONO
  Tono del mundo y registro del jugador son ejes independientes. Con
  contraste permitido, el mundo mantiene su peso aunque el PJ no se lo tome
  en serio.
  Nunca insertes una pausa por conteo de turnos.
  grimdark: ningún alivio programado; el descanso se toma y cuesta.
  heroico: alternancia natural tras picos de tensión.
  ligero: la tensión es episódica y se resuelve en sesión.

MUNDO
  Los relojes avanzan según la profundidad. Al llegar al umbral el evento
  OCURRE: no lo suavices ni lo pospongas.
  Las semillas no tienen ubicación: se plantan donde el jugador esté.
  Describe lugares nuevos en trazo grueso. Cuando el jugador pregunta por
  algo concreto, detállalo; ese detalle queda fijo y se repite si vuelve.
  Si algo difiere de lo descrito, ese cambio es contenido.
  Mazmorras, ruinas y criptas se planifican completas antes de entrar.

PNJ
  Interprétalos como si fueras ellos, no los describas desde fuera.
  Los de paso no necesitan ficha. Si el jugador vuelve a uno por su cuenta,
  escríbela completa.
  Aprecio, confianza y respeto son ejes independientes y pueden bajar.
  La confianza cae más rápido de lo que sube.
  Un PNJ solo reacciona a lo que presenció o le contaron.
  Cada PNJ tiene un techo de confianza según su carácter y no lo supera.
  En uno de principios, la traición probada fija ese techo permanentemente.
  La magnitud de un evento depende de a quién le ocurre:
    soborno a alguien de principios → la oferta es la ofensa, aunque sea aliado
    soborno a alguien sin escrúpulos → no se ofende; rechaza por insuficiente
    amenaza a alguien audaz → sube el respeto, baja el aprecio
    amenaza a alguien temeroso → el miedo se lee como respeto y contamina
    tocar lo que ama → vale igual para todos; el vínculo ya es el modulador
  Los secretos se revelan solo bajo su condición declarada.
  La disposición modifica las CD sociales: hostil +5, amistoso −5.

FUERA DE PERSONAJE
  Con [corchetes] cambias de modo por completo: claro y directo, sin prosa
  ni HUD. Explica la mecánica y por qué. Si lo que pide no funciona, propón
  la alternativa que sí. Si se equivocó, corrígelo sin condescendencia.
  Adapta el detalle a visibilidad_reglas. Luego vuelve al modo narrativo.

LÍMITES
  Las líneas rojas y velos sobrescriben tono, trama, relojes y consecuencias.
  Si un reloj al dispararse tocaría una línea roja, reescribe el evento antes.
  Son editables por el jugador en cualquier momento y sin justificación.

SINTAXIS DEL JUGADOR
  "comillas" diálogo · (resultado: N) tirada · sin formato acción
  {llaves} recurso · [corchetes] fuera de personaje

SALIDA
  narrativa: máximo 2 párrafos, prosa sensorial, entorno y reacciones
  mecanica: solo si aplica, según visibilidad_reglas
  presion: qué empeora si el jugador no actúa
  Si no tienes nada que poner en presión, el turno fue demasiado amable.
  Si el turno no te interpela, devuelve viñeta ambiental en vez de narrar.
  La viñeta ambienta, nunca introduce trama. Dos turnos de enfriamiento.

HERRAMIENTAS
  Dispones de las ocho. Tope de 8 llamadas por turno; al agotarlo responde
  con lo que tengas. Nunca falles en silencio.
```

---

## 5. Prompts G1

### 5.1 Router — determinista, sin LLM

**Decisión (2026-09-04, tras auditoría de paridad):** el Router no llama a
ningún modelo. `QM - Composición G1` ya lo fijaba por latencia
(−2,0 s: la sintaxis del jugador ya declara el modo); la auditoría de las
16 instrucciones que la matriz le asignaba confirma que ninguna es de
juicio — o ya tienen respaldo en Mundo/Árbitro/Narrador, o son mecánicas
puras (ver §8 y §9). El bloque de prompt que había aquí queda retirado;
esto es la especificación del algoritmo que lo reemplaza.

ENTRADA: buffer del jugador (ya cerrado, ver ENT-6/ENT-7 en §9), PNJ
presentes en la escena, `turn_log` de los dos turnos anteriores.

ALGORITMO
```
1. Si el buffer contiene [corchetes] en cualquier posición
     → modo = fuera_de_rol · requiere_arbitro = true
     → pnj_que_responden = []  (el árbitro no habla como PNJ)
     → FIN

2. Extraer con regex, en este orden:
     diálogo   := todo lo que va entre "comillas"
     tiradas   := todo lo que casa (resultado: N)   (ya resuelto por dados.py)
     recursos  := todo lo que va entre {llaves}
     acción    := el resto, sin formato

3. pnj_que_responden:
     - Si el turno nombra explícitamente a un PNJ presente → ese, en el
       orden en que aparece nombrado (puede ser más de uno).
     - Si no nombra a nadie y hay un solo PNJ presente → ese.
     - Si no nombra a nadie y hay varios PNJ presentes → el último que
       intervino en el turno anterior (columna `dm_output` de turn_log).
     - Si no hay PNJ presentes → [] (ver paso 5).

4. altera_estado := true si tiradas no está vacío, o si acción/diálogo
   contiene verbos de la lista de intención (atacar, robar, prometer,
   amenazar, sobornar, entregar, revelar — lista abierta, se amplía con
   los eventos del contrato del extractor en motor/extractor/contrato.json).

5. Si pnj_que_responden == [] y no hay pregunta ni tirada:
     último_ambiental := turno más reciente con modo=ambiental en
                          turn_log (2 turnos de ventana)
     - Si último_ambiental existe dentro de esa ventana → modo = silencio
       (el orquestador reusa el último dm_output; no llama a nadie)
     - Si no → modo = ambiental
   En cualquier otro caso → modo = en_rol · requiere_arbitro = (paso 4)

6. peso:
     trivial          si no hubo tiradas y el buffer es corto (<40 palabras
                       aprox.) y no hay pnj_que_responden
     consecuente       si hubo tirada, o altera_estado, o hay más de un
                       PNJ interpelado
     conversacional    cualquier otro caso
```

SALIDA (objeto, sin llamada a modelo):
```
  modo: en_rol | fuera_de_rol | ambiental | silencio
  requiere_arbitro: bool
  pnj_que_responden: [ids, en orden de intervención — este orden es el
                      que el Narrador respeta sin reordenar, §5.5]
  altera_estado: bool
  peso: trivial | conversacional | consecuente
```

**Nota de paridad (SAL-6):** el enfriamiento de dos turnos del paso 5 se
calcula en el arnés compartido, no dentro de este módulo — se aplica
igual delante de G2 y de G1 (§9). Este algoritmo lo *consulta*, no lo
posee.

### 5.2 Árbitro — híbrido: código para lo mecánico, LLM solo para el juicio

**Decisión (2026-09-06):** igual que el Router, el Árbitro no es un único
prompt monolítico. `QM - Composición G1` fija esto por latencia y costo
(−6,7 s: "la aritmética es código; el modelo solo para el tutor OOC") y el
draft anterior (un solo prompt combinado, abajo sustituido) mezclaba
aritmética que ya resuelve `dados.py` con juicio real. Se separan en dos
piezas:

1. **Camino mecánico — `motor/orquestador/arbitro.py`, función pura
   `resolver_veredicto()`, sin LLM.** Cuando el buffer ya trae una tirada
   resuelta `(resultado: N ...)`, comparar contra una CD y devolver el
   veredicto es aritmética, no juicio — igual que el Router, no hay
   instrucción de las 20 asignadas al Árbitro que exija un modelo aquí.
   - CD por defecto: **15 ("Media")**, tomada literalmente de la tabla
     "Typical Difficulty Classes" del SRD 5.2 (CC-BY-4.0): Muy fácil 5,
     Fácil 10, Media 15, Difícil 20, Muy difícil 25, Casi imposible 30. El
     esquema no guarda una CD por acción/lugar, así que Media es el punto
     de partida que el propio manual recomienda cuando no hay razón para
     desviarse — no es un número inventado por el sistema.
   - Modificador de disposición (PNJ-16): `disposition_band()` (Postgres)
     devuelve 7 bandas; la instrucción original solo define 3 niveles, así
     que se agrupan sin añadir granularidad que el contrato no pide:
     `hostile`/`wary` → **+5** (hostil), `cold`/`neutral`/`cordial` → **0**
     (indiferente), `loyal`/`devoted` → **−5** (amistoso).
   - Si no hay tirada pero `altera_estado=True` (Router), la función
     devuelve `necesita_juicio=True` en vez de inventar un veredicto: eso
     es NUN-5, y NUN-5 sí necesita el LLM.
   - `recurso_consumido` (ENT-4) queda `None` en este camino a propósito:
     `dados.py` ya quitó las `{llaves}` del buffer antes de que el
     Árbitro lo vea, así que no queda delimitador para extraer qué
     objeto se usó. Se resuelve cuando el Mundo (dueño de `apply_delta`
     sobre inventario) esté conectado — no antes.

2. **Camino de juicio — `motor/dm/prompt_arbitro_g1.md`, sí llama al modelo.**
   Cubre solo lo que el código no puede decidir:
   - **Modo tutor** (OOC-1 a OOC-6): el jugador escribió `[corchetes]`.
     Responde claro, sin prosa evocadora, propone alternativas, corrige
     sin condescendencia, respeta `visibilidad_reglas`, nunca revela
     trama. Salida directa al jugador (`{"respuesta": "..."}`) — el
     Narrador nunca la ve, porque el Router ya marca
     `pnj_que_responden=[]` en este modo.
   - **Modo veredicto sin tirada** (NUN-3/4/5): juzga si una acción
     imprevista y sin tirada estándar funciona, sin competir con el
     jugador, con toda amenaza letal telegrafiada antes de golpear. Si en
     realidad la acción sí requería una tirada mecánica que no se hizo,
     este modo no la inventa: devuelve `veredicto: null` para que el
     orquestador pida la tirada, en vez de fabricar un resultado.

**Fix de nombre (colisión con el Narrador):** el draft anterior trataba
`veredicto` como un campo plano más entre varios. `motor/dm/prompt_narrador_g1.md`
espera un fragmento *anidado* llamado `veredicto` que agrupa
`resultado`, `cd`, `correccion_al_jugador` (ver su sección "FRAGMENTOS QUE
RECIBES"). Se resuelve haciendo que `veredicto` sea el nombre del objeto
completo — así lo produce tanto `resolver_veredicto()` como el modo
veredicto_sin_tirada del prompt — y no un campo entre otros. No hizo
falta tocar el prompt del Narrador.

HERRAMIENTAS (ambos caminos, cuando aplica): `search_rules`, `get_entity`,
`query_state`.

SALIDA — camino mecánico y modo veredicto_sin_tirada (mismo objeto,
mismas claves, para que el Narrador no necesite saber cuál de los dos lo
generó):
```
  veredicto, cd, resultado, recurso_consumido, correccion_al_jugador
```

SALIDA — modo tutor (va directo al jugador, no al Narrador):
```
  respuesta
```

Verificación: `legacy/orquestador/probar_arbitro.py` (11 casos puros, sin DB ni
red, cubre el camino mecánico completo) y `legacy/orquestador/verificar_arbitro.py`
(llama al modelo real, cubre los dos modos del camino de juicio —
mismo patrón que `verificar_fugas_narrador.py`: fuga de prompt + forma de
la salida verificadas en código, calidad de la respuesta a ojo).

### 5.3 Actor PNJ

**Decisión (2026-09-06):** el draft anterior (abajo sustituido) tenía UN
solo ejemplo de reacción (el capitán del puente). `QM - Lecciones de
ingeniería` §2 ya documentaba que esa frase se filtró literal en dos
modelos distintos — un ejemplo único enseña postura, no formato. El
corolario que el propio vault dejaba escrito era explícito: "varios
ejemplos que cubran el rango, o ejemplares por personaje". Se aplican
ambos a la vez, en capas distintas:

- **Ejemplares por personaje** ya existen en el esquema y no dependen del
  prompt: `npcs.voice_notes`, los cuatro ejes estables (`warmth`,
  `candor`, `principle`, `boldness`, inmutables, autorados, sin extractor
  que los juzgue) y el IBF (`npc_ibf`). Un actor único los interpreta;
  la consistencia es propiedad del registro, no del modelo.
- **Varios ejemplos que cubran el rango** se añadieron directamente en
  `motor/dm/prompt_actor_g1.md`: una matriz de reacciones marcadas
  explícitamente como ilustración de la función eje→reacción (no líneas
  para reciclar), cubriendo los extremos de `principle` y `boldness`
  frente a los mismos tres disparadores del draft original (soborno,
  amenaza, tocar el vínculo).

Esto es directamente lo que protege dos de los tres bloques de indicadores
de la tesis: **Coherencia Longitudinal** (personajes) depende de que la
misma ficha produzca la misma voz siempre — propiedad de la base, no del
prompt; y **Calidad Narrativa Emergente** (reactividad significativa a la
agencia del jugador) queda en cero por diseño si dos PNJ con ejes opuestos
colapsan en la misma respuesta ante el mismo disparador — que es
exactamente el bug documentado.

PRINCIPIO GENERAL (sin cambios frente al draft): la magnitud de lo que le
hacen al PNJ depende de quién es, no de la gravedad aparente del acto —
soborno a alguien de principios ofende aunque el grupo sea aliado;
soborno a alguien sin escrúpulos solo se rechaza por insuficiente; amenaza
a alguien audaz sube el respeto y baja el aprecio; amenaza a alguien
temeroso contamina la relación con miedo; tocar un vínculo del IBF vale
igual para todos, el vínculo ya es el modulador. Techo de confianza fijo,
la confianza cae más rápido de lo que sube, secretos solo bajo condición
declarada (ver `motor/dm/prompt_actor_g1.md` para el texto completo con la
matriz de ejemplos).

HERRAMIENTAS: `get_persona` (solo la ficha del propio personaje).

SALIDA (objeto):
```
  linea, entrega, se_niega_a
```

Verificación: `legacy/orquestador/verificar_colapso_actor.py` — mismo patrón que
los verificadores anteriores (llama al modelo real), pero en vez de
buscar solo fuga de prompt, mide superposición léxica (Jaccard) entre
pares de PNJ con ejes opuestos frente al mismo disparador: una
superposición alta pese a ejes opuestos es la señal directa del bug de
colapso. También comprueba arraigo (el PNJ no menciona lo que no está en
su conocimiento declarado).

### 5.4 Agente del Mundo — híbrido: código para lo que ya es garantía, LLM para lo creativo

**Decisión (2026-09-06):** de los cinco roles, este es el que sostiene
directamente "consistencia de eventos y estado del mundo a largo plazo"
-- no genera el mundo una vez, lo MANTIENE actualizado frente a la
acción del jugador turno a turno. Un reloj que no avanza cuando debía,
un lugar que cambia de descripción cada vez que el jugador vuelve, o una
semilla que nunca se planta son exactamente los fallos que esa métrica
tiene que poder detectar -- y detectarlos requiere que esas tres cosas
sean garantía del sistema, no memoria del modelo (`QM - Lecciones de
ingeniería` §3: "si el modelo tiene que adivinar algo que la base sabe,
dáselo"). Por eso, igual que Router y Árbitro, se separa en dos piezas:

1. **Camino mecánico — `motor/orquestador/mundo.py`, función pura
   `resolver_mundo()`, sin LLM**, más los métodos nuevos de
   `motor/orquestador/db.py` (`avanzar_relojes`, `lugar_estado`, `fijar_lugar`,
   `semillas_sin_ubicar`, `plantar_semilla`) que leen/escriben lo que el
   modelo entidad+delta no cubre directamente:
   - **MUN-1/MUN-2 (relojes):** `avanzar_relojes()` envuelve
     `advance_clocks()` (SQL, ya existía en el esquema sin que nada la
     llamara todavía). El reloj avanza y dispara en la base; el LLM
     nunca decide si ocurrió, solo recibe el evento ya resuelto.
   - **MUN-4/5/6 (lugares):** `locations.detail` (`sketch`→`observed`/
     `full`) ya modela esto en el esquema. `resolver_mundo()` decide sin
     LLM si el lugar debe repetir su `description_canonical` congelada
     (MUN-6, cero costo) o si necesita boceto nuevo -- y si ese boceto se
     fija para siempre (MUN-5: preguntó algo concreto) o no (MUN-4: trazo
     grueso normal, sigue en `sketch`).
   - **MUN-7 (mazmorras/ruinas/criptas):** se tratan como los tipos de
     lugar que exigen plan completo (`location_kind` ya distingue esto en
     el esquema) -- si su `detail` no es `full` todavía, `resolver_mundo()`
     fuerza el camino de fijar aunque nadie haya preguntado nada.
   - **MUN-3 (semillas):** `semillas_sin_ubicar()` expone las candidatas
     sin plantar (FIFO); el código nunca decide POR SÍ SOLO plantarlas --
     eso sigue siendo juicio del LLM (¿encaja en la escena actual?).
2. **Camino de juicio — `motor/dm/prompt_mundo_g1.md`, sí llama al modelo.**
   Solo se invoca cuando `resolver_mundo()` dice `necesita_llm=True`.
   Cubre: el texto del boceto (trazo grueso o fijado, según lo que el
   código ya decidió); si la semilla candidata encaja en la escena
   actual y con qué palabras se planta -- con permiso explícito de
   devolver `planteada: false` si el grupo se enfrascó en algo no
   planeado (nunca se fuerza una semilla para no "desperdiciar sesión");
   propagación a PNJ con vínculo declarado (MUN-8/PNJ-3), siempre con una
   `razon` de cómo pudo enterarse -- sin eso es telepatía, no propagación;
   y el tono de ritmo según el perfil de campaña (grimdark/heroico/ligero).

HERRAMIENTAS: todas las de lectura (`get_entity`, `query_state`,
`traverse_relations`, `search_narrative`, `search_rules`, `get_persona`,
`get_recap`). Escritura: `apply_delta` (y `create_entity` para PNJ/lugares
que el jugador promueve de paso a persistente).

SALIDA (objeto, del camino de juicio -- el camino mecánico no produce
salida propia, solo alimenta las claves ya resueltas al Narrador):
```
  boceto, semilla_plantada, propagacion_sugerida, deltas
```

Verificación: `legacy/orquestador/probar_mundo.py` (10 casos puros, sin DB ni
red, cubre relojes/lugares/semillas del camino mecánico) y
`legacy/orquestador/verificar_mundo.py` (llama al modelo real: boceto de trazo
grueso vs. boceto que se fija, semilla que NO debe forzarse, propagación
con razón declarada -- mismo patrón que los verificadores anteriores).

### 5.5 Narrador

```
Escribes lo que el jugador lee. Eres el ÚNICO que produce prosa.

Recibes fragmentos de otros roles. No los pegues: escribe un texto continuo
que los contenga. Nadie debe poder señalar dónde termina uno y empieza otro.

FRAGMENTOS QUE RECIBES
  veredicto del árbitro    → tradúcelo a consecuencia narrada. Si dijo
                             fallo, no narres éxito bajo ninguna forma.
  linea + entrega del actor → la línea va TEXTUAL entre comillas, sin
                             parafrasear ni una palabra. Tú escribes lo que
                             la rodea: el gesto, la pausa, hacia dónde mira.
  boceto del mundo         → intégralo como descripción, no como lista.
  orden de intervención    → respétalo. Esto se lee como un libro: hay una
                             secuencia. Si hay más intervenciones de las que
                             caben, resume las menos relevantes en indirecto.

REGLA DE ORO
  Careces de autoridad para narrar al personaje jugador. Nunca describas sus
  acciones, diálogo, pensamientos o emociones. Tras describir la reacción del
  entorno o los PNJ, detente.

CÓMO ESCRIBES
  Máximo 2 párrafos. Prosa sensorial. Entorno y reacciones.
  Sin relleno conversacional ni meta-comentarios sobre tus reglas.
  No encarriles: si el jugador abandonó lo preparado, narra donde está.
  Tono del mundo y registro del jugador son ejes independientes: con
  contraste permitido, el mundo mantiene su peso aunque el PJ no se lo tome
  en serio. No aplanes ninguno de los dos.
  Nunca insertes una pausa por conteo de turnos.
  Si un reloj se disparó, el evento ocurrió: nárralo como hecho consumado.
  Si el jugador vuelve a un lugar ya descrito, usa la descripción fijada.
  Las líneas rojas y velos sobrescriben todo.

SI EL MODO ES AMBIENTAL
  No narres una escena. Devuelve una viñeta breve de entorno: quién los
  escucha, qué sigue ocurriendo alrededor. Ambienta, nunca enganches.

SALIDA
  narrativa: el texto del turno
  mecanica: solo si aplica, según visibilidad_reglas
  presion: qué empeora si el jugador no actúa
  Si no tienes nada que poner en presión, el turno fue demasiado amable
  para el tono configurado: reescríbelo antes de emitirlo.
```

---

## 6. Fallback

Si el Narrador falla o agota presupuesto, el orquestador toma los fragmentos
que ya están en la pizarra y los pasa al **prompt de G2 con el mismo
modelo**. No reconstruye la salida perdida: reescribe desde los mismos
insumos.

Coste cero en reposo (facturación por token, no por instancia) y más barato
que el turno que acaba de fallar: una llamada en vez de tres.

Si el fallback también falla, se interrumpe. Dos fallos seguidos no son un
turno malo, son el sistema roto.

Degradación por rol:
- Falla el **Árbitro** → no se infiere nada mecánico. La aritmética ya es
  determinista; solo se degrada el tutor OOC.
- Falla el **Actor** → el Narrador describe la reacción del PNJ **sin
  diálogo textual**. Se pierde la voz, no se inventa.
- Falla el **Mundo** → se usa el boceto existente. Nada se persiste.

Toda omisión se registra en `model_calls`. Un G1 que corrió sin Actor el 30%
de los turnos no es la arquitectura que se está midiendo.

---

## 7. Andamiaje exclusivo de G1 — declarado

No tiene equivalente en G2 y es constitutivo de la arquitectura:

| Andamiaje | Dónde |
|---|---|
| "Recibes fragmentos de otros roles" | Narrador |
| "Emite un objeto con estos campos" | Router, Árbitro, Actor, Mundo |
| "La línea va textual, sin parafrasear" | Narrador |
| "Respeta el orden de intervención" | Narrador |
| "No recibes estado que tu personaje no conozca" | Actor |

---

## 8. Instrucciones que G2 necesita y G1 obtiene por estructura

La dirección contraria, y es una de las ventajas hipotetizadas del MAS. **No
se compensa: se mide.**

| En G2 hay que instruirlo | En G1 lo garantiza la arquitectura |
|---|---|
| "Un PNJ solo reacciona a lo que presenció" | El Actor solo recibe su propio conocimiento |
| "No dejes que el cálculo interfiera con la narrativa" | Árbitro y Narrador son llamadas distintas |
| "Los secretos se revelan solo bajo su condición" | El Actor decide; el Narrador no ve secretos |
| "Cambia de modo con [corchetes]" | El Router enruta al Árbitro directamente |
| "Terminada la respuesta OOC, vuelve al modo narrativo" (OOC-7) | El Router reclasifica cada turno desde cero: no hay estado de modo que arrastrar ni instrucción que olvidar |
| "Si el lugar ya se describió, repite lo mismo; si no, boceto grueso" (MUN-4/5/6/7) | `locations.detail`/`description_canonical`: el Mundo repite lo congelado sin volver a generarlo — decisión explícita del 2026-09-07 de NO compartir esto con G2 (ver nota abajo) |

**Nota sobre MUN-4/5/6/7 (2026-09-07):** a diferencia de todo lo demás en
esta tabla, aquí se decidió deliberadamente NO dar a G2 el mismo apoyo de
código que a G1, aunque la infraestructura (`locations.detail`) existe y
sería trivial exponerla a ambos. Razón: la consistencia de descripciones
de lugar a lo largo de una campaña es precisamente lo que "Coherencia
Longitudinal — estado del mundo a largo plazo" tiene que poder detectar.
Si el mecanismo de memoria se iguala por código en ambos brazos, esa
diferencia deja de ser observable y la métrica pierde varianza que
debería medir. Contraste con MUN-1/2 (§9): los relojes SÍ se comparten
porque son aritmética/umbral (como las tiradas), no memoria narrativa —
la línea se traza ahí, no en "toca la tabla `locations`".

---

## 9. Resuelto en el arnés — idéntico para ambos brazos

Distinto de §8: aquí no hay asimetría ni ventaja de nadie. Son
instrucciones atómicas que el Router determinista absorbe, pero que no
son "estructura de G1" — son infraestructura de entrada/salida que sirve
igual a G2 y a G1. Meterlas en §8 diluiría el argumento de §8, que sí es
una ventaja medible.

| id | Instrucción | Dónde vive |
|---|---|---|
| ENT-1 | `"comillas"` es diálogo en voz alta del PJ | Parser del arnés (regex sobre el buffer), antes de cualquier llamada a modelo |
| ENT-3 | Texto sin formato es acción o descripción | Parser del arnés, mismo paso |
| ENT-6 | El jugador puede escribir varios mensajes antes de cerrar la interacción | Buffer con commit — ya existe, es lo que arma `buffer_txt` en `vertical_slice.py` |
| ENT-7 | No respondas a cada mensaje: espera al cierre y responde a la escena completa | Mismo buffer con commit |
| SAL-6 | Enfriamiento de dos turnos entre viñetas ambientales | Arnés: se consulta `turn_log` de los últimos dos turnos **antes** de invocar tanto a G2 como al Router de G1. Si no se comparte, G1 tendría una disciplina de moderación garantizada que G2 solo tiene como instrucción de prompt — ventaja no declarada. |
| MUN-1 / MUN-2 | Relojes de facción: al llegar al umbral, el evento OCURRE | `advance_clocks()` (SQL) corre en `vertical_slice.py` para AMBOS brazos tras escribir el delta de `world.game_day` (paso 8). Es aritmética contra un umbral, igual que una tirada de dados — no memoria narrativa, así que compartirlo no contamina lo que la tesis mide (contraste con MUN-4/5/6/7 en §8, que sí se dejó asimétrico a propósito). El evento se muestra en el contexto del turno SIGUIENTE (`eventos_reloj_turno()`), porque `advance_clocks()` corre después de que el DM ya narró este turno. |

Para G2 estas cinco siguen siendo instrucciones de prompt (siguen ahí,
sin tocar) porque su único modelo no tiene arnés intermedio que le
preparse la entrada. Para G1 son código con test. La paridad no exige que
el *mecanismo* sea igual — exige que el *comportamiento resultante* lo
sea, y con el enfriamiento aplicado en el arnés compartido, lo es.

## 10. Constantes fijadas para la tesis

| Parámetro | Valor | Motivo |
|---|---|---|
| Perfil | `adventure` | Punto medio; referencia reconocible por los jueces |
| Visibilidad de reglas | 50 | Altera la naturaleza del artefacto evaluado |
| Mecánicas opcionales | ninguna | Varianza mecánica entre campañas |
| Ejes de disposición activos | solo aprecio | Tres multiplican la varianza no atribuible |
| Elemento IBF activo | solo `bond_targets` | Es el único determinista, sin juicio del modelo |
| Contraste de tono | permitido | — |
| Presupuesto | sin límite en ambos | Cada paradigma en su mejor forma |
| Fuera del instrumento | semillas de tentación, reputación, promoción de entidades, ingesta de lore, multijugador | Producto, no instrumento |

---

## 11. Reglas de mantenimiento

1. Toda instrucción nueva entra primero en la lista atómica y en la matriz;
   después en los prompts.
2. Todo ajuste se aplica a ambos lados, o se documenta como asimetría
   deliberada con justificación metodológica.
3. Durante la recolección de datos el pipeline se congela: ni prompts, ni
   compuerta, ni reprocesamiento. Un cambio a mitad parte la muestra en dos.