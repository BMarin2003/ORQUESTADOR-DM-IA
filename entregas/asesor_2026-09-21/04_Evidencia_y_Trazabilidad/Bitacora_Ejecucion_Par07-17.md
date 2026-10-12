# Bitácora — Par 07 a Par 17 (11 pares, 22 campañas)

## Fase 0 — Orientación (completa, 2026-09-18)

Leídos antes de diseñar nada: `lore_vega_del_yelmo.md`, `lore_poza_seca.md`, `lore_caleta_lumbre.md`,
`lore_vado_cabrero.md`, `lore_puerto_salazon.md`, `lore_alto_ferrena.md` (los 6 lores reales
completos, para no repetir tono/estructura), `world_par01-06.json`, `personas_par03.json`,
`personas_par06.json`, `fixtures/validar_fixtures.py`, `fixtures/generar_seed.py`,
`jugador/personajes_jugadores.json`, `jugador/generar_personajes.py`, `jugador/dados.py`,
`extractor/contrato.json`, `scripts/crear_campana_real.py`, `scripts/crear_campana_real_g1.py`,
`scripts/sembrar_mundo_real.py`, `scripts/exportar_transcripcion.py`,
`orquestador/reporte_validacion.py`, `scripts/estado_par04_05_06.py`.

Confirmaciones del paso 0:
- **`.env`**: no existe línea `DMIA_MODELO_JUGADOR`. `DMIA_MODELO=google/gemma-4-31B-it` presente y correcto.
- **Bug conocido (`location.state`/valor fuera de dominio)**: el `try/except` alrededor de `camp.aplicar()`
  sigue presente y sin cambios en `vertical_slice.py` (línea ~905) y `vertical_slice_g1.py` (línea ~1034),
  con el mismo patrón (log del rechazo + `continue`). No se tocó nada de esto.
- **Firma real de los scripts** (confirmada leyendo el código, no asumida):
  - `crear_campana_real.py [titulo] [corpus_filename] [world_tone]` — `corpus_filename` relativo a `corpus/`.
  - `crear_campana_real_g1.py <tenant_id> <user_id> [titulo] [corpus_filename] [world_tone]`.
  - `sembrar_mundo_real.py <campaign_id> <tenant_id> <user_id> [pj_key] [world_file] [personas_file]` —
    `world_file`/`personas_file` relativos a `fixtures/`. **No es idempotente**: aborta solo si la campaña
    ya tiene NPCs sembrados.
  - `vertical_slice.py --pj (default PJ02) --turnos (default 1) --seco --campaign-id (default None)`.
  - `vertical_slice_g1.py --pj (default PJ01) --turnos (default 1) --seco --campaign-id (REQUERIDO)`.
  - `exportar_transcripcion.py --campaign-id (requerido) --hasta-turno --salida`.
  - `reporte_validacion.py --campaign-id (default: campaña más antigua) --hasta-turno`.
- **Instrumentos deterministas** (`deterministic-instruments` skill): `reporte_validacion.py` combina
  piezas viables (resumen `turn_validation`, detector de bucles, relojes no reconocidos, Papalampidi C/V,
  Jericho-QA recall, Entity Coreference Rate, Grammaticality, grafo de coherencia por lema) — todas
  descriptivas, ninguna pass/fail. La coherencia NER en español (spaCy `es_core_news_sm`) sigue marcada
  como no viable en la práctica; no se intentó tocar ni traducir nada de esto.
- **`fixtures/validar_fixtures.py`** exige `world.json`/`personas.json`/`turns.json`/`probes.json` fijos en
  `fixtures/` — no sirve tal cual para fixtures reales con nombre `_parXX` ni para campañas reales (que no
  tienen `turns.json`/`probes.json`, exclusivos del suite de prueba del extractor). Se escribió
  `scripts/validar_fixtures_real.py`, que reutiliza el mismo subconjunto de invariantes que sí aplica a
  world/personas (referencias cruzadas de `location`/`faction`/`bond_target`/`quest`, rangos de
  disposición, `trust <= trust_ceiling`, secretos con `reveal_condition`, al menos un PNJ de paso vacío,
  `hp == hp_max`), parametrizado por número de par.

## Fase 1 — Diseño de los 11 pares (completa, 2026-09-18)

Cálculo de HP: se reconstruyó la fórmula real ya usada en Par01-06 comparando `world_parXX.json` de
Par03/04/05/06 contra `personajes_jugadores.json` (no se asumió, se verificó con 4 puntos de datos
independientes). Fórmula confirmada: `hp = BASE(dado_de_golpe) + 3 × mod_CON`, donde `BASE` es
`dado_max + 2×(dado_max//2 + 1)` (máximo en nivel 1 + promedio fijo en niveles 2 y 3, D&D 5e estándar) —
`BASE`: mago(d6)=14, bardo/pícaro/clérigo/brujo(d8)=18, paladín/explorador/guerrero(d10)=22, bárbaro(d12)=26.
**Importante**: se usó el modificador de Constitución REAL (recalculado desde `caracteristicas.constitución`),
no el campo `modificadores.constitución` de `personajes_jugadores.json` tal cual — ese campo incluye +2 de
competencia para guerrero y bárbaro (ambos con salvación de Constitución), que infla el modificador y
habría dado HP incorrecto (verificado: Mirek/bárbaro con el mod inflado da 38, con el mod real da 32,
que es el valor real ya sembrado en Par06). Nota aparte: Par01/02 (Bexa, explorador, con mod real 1) tienen
`hp=28` en vez de los 25 que da esta fórmula — una inconsistencia de esos dos pares tempranos, no replicada
aquí; los 11 pares nuevos siguen la fórmula verificada contra Par03-06.

| Par | Lugar | Tono | Estructura | PJ | HP |
|---|---|---|---|---|---|
| 07 | Umbral Hondo | grimdark | Culto oculto infiltrado (Hijos del Umbral) | Tarq, brujo | 24 |
| 08 | Torre Alondra | heroic | Venganza de sangre entre dos familias fundadoras | Maelis, guerrero | 28 |
| 09 | Bruma Honda | grimdark | Plaga misteriosa sin cura clara | Garrek, clérigo | 24 |
| 10 | Puente Roto | mixed | Refugiados desplazados, tensión con población local | Isolde, explorador | 25 |
| 11 | Cima Clara | heroic | Profecía (dos soles) que divide a la comunidad | Marta, clérigo | 24 |
| 12 | Muelle Gris | light | Mercado negro comunitario amenazado de exposición | Dunmar, pícaro | 21 |
| 13 | Piedra Yerma | mixed | Maldición ligada a un monolito concreto | Elior, mago | 20 |
| 14 | Roble Cantor | light | Festival comunitario descarrilado (objeto ritual perdido) | Kestra, bardo | 21 |
| 15 | Solar Viejo | heroic | Disputa de herencia sobre propiedad ancestral | Ilvard, paladín | 25 |
| 16 | Cruce Salado | mixed | Guerra de precios entre dos rutas comerciales | Harn, bárbaro | 32 |
| 17 | Corral Alto | light | Elección local manipulada desde afuera | Wynn, pícaro | 21 |

Verificación de no-repetición (contra Par01-06 y entre sí):
- **Nombres de lugar**: ninguno coincide con Puerto Salazón/Alto Ferrena/Vega del Yelmo/Caleta Lumbre/
  Vado Cabrero/Poza Seca ni entre los 11 nuevos.
- **Estructura de conflicto**: cada uno es un molde narrativo distinto (infiltración oculta, venganza de
  sangre, plaga, desplazados, profecía, mercado negro, maldición de objeto/lugar, festival descarrilado,
  herencia, guerra de precios, elección manipulada) — ninguno repite monopolio interno (Par01/02), amenaza
  externa con reloj de invasión (Par03), misterio ambiguo de portal (Par04), sucesión política por mérito
  (Par05) ni escasez sin villano (Par06). Se prestó atención especial a Par12 (mercado negro, para no
  calcar el contrabando marginal de Puerto Salazón — aquí no hay monopolio opresor, es todo el pueblo
  protegiéndose de una ley externa) y a Par17 (elección, para no calcar la sucesión por mérito de Vado
  Cabrero — aquí el eje es la manipulación externa vía donativos, no una prueba pública).
- **PJ**: cada uno de los 11 aparece exactamente una vez, según la tabla ya cerrada del prompt original.
- Ninguno de los 11 tiene un villano de cálculo trivial: cada par se apoya en dos posturas legítimas
  enfrentadas, o en un fenómeno/amenaza ambiguo cuya naturaleza real queda deliberadamente sin resolver
  en el propio documento (ver quests `dm_only`/`unknown` de cada `world_parXX.json`).

Contenido por par (en `corpus/real/lore_<slug>.md`, `fixtures/real/world_parXX.json`,
`fixtures/real/personas_parXX.json`): ~7 locations (1-2 `dm_only`), 2 factions, 1 clock, 2 quests
(una activa, una `dm_only`/`unknown` como gancho de misterio), 1 character (el PJ del par), 3 PNJ
(2 centrales con IBF completo enfrentado + 1 PNJ de paso con molde vacío, mismo patrón que
Petra/Yulen/Mira/Alba Ferrís/Nando/Nilo de los pares anteriores).

## Validación (completa, 2026-09-18)

`python scripts/validar_fixtures_real.py 07 08 09 10 11 12 13 14 15 16 17` → **los 11 pares pasan sin
errores**. Único aviso (esperado, mismo patrón que Par01-06): la región de nivel superior de cada par
(p. ej. `la_hondonada`, `cresteria_alondra`) no tiene `sketch_text` — es un contenedor organizativo, no
una escena, igual que `valle_del_yelmo` en Par03.

## Parche aplicado (2026-09-18, antes de crear campañas)

La otra sesión (tesis) pasó un parche pendiente para `orquestador/reporte_validacion.py`: refinamiento
sintáctico post-hoc de `cl2_pnj_inactivo_actua` vía spaCy (¿el PNJ inactivo es sujeto gramatical de la
oración, o solo se lo menciona/referencia?), para no confundir con error de continuidad las menciones
retrospectivas legítimas -- G1 sostiene referencias a su elenco más tiempo que G2 (Papalampidi C), así
que puede estar inflando su propio hallazgo sin que sea un error real. 100% aditivo, no toca
`vertical_slice.py`/`vertical_slice_g1.py` ni `turn_validation`. Aplicado como sección 9 del script
(función `pnj_inactivo_refinado` + `imprimir_pnj_inactivo_refinado`, llamada agregada en `main()`),
verificado con `python -m py_compile` y por contenido (`grep` de las funciones en el archivo).

## Fase 3 — Crear y sembrar las 22 campañas (completa, 2026-09-18)

Orquestado con `scripts/crear_sembrar_par07-17.py` (nuevo, mismo patrón que Par03-06): por cada par,
`crear_campana_real.py` → parsea tenant_id/user_id/campaign_id de la salida real → `crear_campana_real_g1.py`
reusando esos ids → `sembrar_mundo_real.py` x2. Cada paso se verificó contra Postgres directamente
(título, `architecture`, `world_tone`, `current_turn=0` tras crear; conteo de locations/npcs/factions/
quests/characters tras sembrar, comparado contra el contenido real de cada fixture) -- no se confió en
"no tiró error" como señal de éxito.

**Bug encontrado y corregido**: la siembra de Par 15 (Solar Viejo) falló con
`ForeignKeyViolation` en `factions.seat_location_id`. Causa raíz: `world_par15.json` usaba el MISMO
string de key para una location y una faction (`casa_herminia` y `casa_doroteo`, tanto de location como
de faction). `sembrar_mundo_real.py` mantiene un único diccionario `keymap` compartido por string de key
entre todas las categorías de entidad -- al sembrar la faction con esa key, `new_id()` le generó un uuid
nuevo y sobrescribió en `keymap` el uuid que ya tenía la location con el mismo nombre, así que cuando la
OTRA faction buscó su propio `seat` (`keymap.get(f.get("seat"))`), el valor ya no apuntaba a una location
real. No es el bug conocido de `location.state`/valor fuera de dominio (Sección 1, regla 5) -- es una
clase nueva, de colisión de namespace de keys entre categorías de entidad, no cubierta por
`validar_fixtures_real.py` (que solo revisa que cada key exista en el set correcto, no que sea única
*entre* categorías). Gracias a `autocommit=False` + `with psycopg.connect(...)`, la transacción entera
hizo rollback limpio -- cero filas huérfanas, no hizo falta borrar nada, solo corregir el fixture.
**Fix**: renombradas las dos facciones de Par15 a `reclamo_herminia`/`reclamo_doroteo` (las locations
`casa_herminia`/`casa_doroteo` quedan igual), actualizado el `clocks[].faction` y los `bond_targets` de
`personas_par15.json` que apuntaban a las keys viejas. Re-validado con `validar_fixtures_real.py 15` (OK)
y re-sembrado sobre las mismas dos campañas ya creadas (no se recrearon, la creación de la fila
`campaigns` había sido exitosa; el rollback solo afectó la siembra).
**Se escaneó** el resto de los 11 pares por el mismo patrón de colisión (key de faction/quest/character
igual a key de location, o entre sí) -- Par 15 fue el único caso.

### Tabla de IDs (`docs/ids_par07-17.json`, reconstruida por consulta directa a Postgres, no de logs)

| Par | Lugar | Tono | tenant_id | user_id | campaign_id G2 (monolithic) | campaign_id G1 (mas) |
|---|---|---|---|---|---|---|
| 07 | Umbral Hondo | grimdark | 27c556d1-6017-48fa-b44a-ed85ed5ff1a2 | 165737a8-94d4-4bd7-a5d6-81172a16ac5c | f42e9672-4df4-40bf-a912-02fba5ae396e | 41fedb73-2345-439b-852c-87ad806e1015 |
| 08 | Torre Alondra | heroic | 2b803fb4-a1e2-4c45-8efc-70923669769f | (ver ids_par07-17.json) | ebfcb92e-2eeb-4235-a1d2-73630f75a631 | 1ea2fbfb-b54a-42b2-b8dc-03dbef93990c |
| 09 | Bruma Honda | grimdark | 6e4fde07-d25c-4922-8969-855b6e9fc226 | (ver ids_par07-17.json) | 41674211-baed-424c-9187-3a6429dd8400 | d78a7a3e-f37d-407b-ac5b-5c9895064732 |
| 10 | Puente Roto | mixed | 84c46cfd-8835-4526-9e0b-846bbb3ec798 | (ver ids_par07-17.json) | 9dcf64ea-8da4-4dcf-b168-4f960b839c04 | 7dc9fe9d-9052-4252-aa0c-f86490b96dbe |
| 11 | Cima Clara | heroic | 37a33087-aff7-4545-beee-92889591a3ea | (ver ids_par07-17.json) | b6c3eb75-cb1a-48de-a827-d082415b4b74 | 259f2fdd-2857-4ebb-ad4f-bde8ea297e04 |
| 12 | Muelle Gris | light | e5a9da0e-5f28-43a4-a368-11be6ece5b68 | (ver ids_par07-17.json) | 6f319319-f39f-4902-9f11-a5d5a17798af | 5f050643-72d2-4c9f-8209-9c9ce008c61e |
| 13 | Piedra Yerma | mixed | 76871b0e-b64a-474f-a384-9f8e089a84d1 | (ver ids_par07-17.json) | 8845df6a-3248-47ef-9844-7c234724d7f9 | 7231e456-9284-40b3-83ed-d1de4dc4e33e |
| 14 | Roble Cantor | light | f921a681-9ca8-44ae-9864-6ac7d742cc4f | (ver ids_par07-17.json) | cebcafd3-23cc-4d61-8e2e-9360587b7464 | 8d8e8f27-41d7-4573-a294-c79d2378b6e5 |
| 15 | Solar Viejo | heroic | e21e7052-249e-4257-8ff1-ce40297a15a0 | e57afecb-2806-467b-814a-1afa22104403 | 79db3083-9993-458a-86a9-12ddec04e192 | 4521da96-8eda-4fb7-9464-ce09d417d26f |
| 16 | Cruce Salado | mixed | 7614383e-38f6-46f2-9b2d-606d62b0ebf0 | 8594ed98-39c5-4c88-adc1-e4df6139160f | e1e30d0b-9dd8-454c-b297-44c08204610f | 494e1d7d-9d10-43da-ac4b-041935b24c8b |
| 17 | Corral Alto | light | b031e94c-40ee-49f1-9190-9745e8eac27c | 9b85b212-8ef8-4797-9c46-2faba6b6c140 | 45f450c1-29bc-4dde-8960-82129291f1ad | dc7af6f4-453a-4542-a2b5-e7cdd46a30b2 |

(Tabla completa con todos los `user_id` en `docs/ids_par07-17.json`, generado directamente desde Postgres.)

**Verificación final de las 22 campañas** (script ad-hoc, no guardado -- una sola pasada de control):
las 22 tienen `current_turn=0`, conteo de locations igual al de su fixture (7 en 10 de los 11 pares, 8 en
Par10), 3 npcs, 2 factions con `seat_location_id` no nulo, 2 quests, 1 character. Cero problemas.

## Estado actual

**(2026-09-19 13:51) Las 22 campañas de Par 07-17 están en 1400/1400, con transcripción, reporte de
validación y verificación de integridad.** Ver "Fase 5 — Cierre" al final. (Esta sección quedó
desactualizada durante la generación; el detalle histórico está en la Fase 4.)

## Fase 4 — Generación a escala (en curso)

**Decisión operativa (2026-09-18, por presión de tiempo real de Bryan):** en vez de 4 olas chicas de
3 pares con pausa de 15-20 min entre cada una, se corre en 2 tandas grandes por arquitectura -- los 11 G2
(monolítico) primero, los 11 G1 (multiagente) después -- ya que las 22 campañas son completamente
independientes entre sí (ninguna coordinación entre G1/G2 de un mismo par ni entre pares distintos, regla
3 de la Sección 4 original), así que el orden/momento de cada corrida no afecta la validez de la
comparación pareada. Reduce concurrencia máxima contra DeepInfra de 22 a 11 conexiones simultáneas, sin
esperar entre pares dentro de la misma tanda. Bryan corre los procesos desde su propia PowerShell
(`scripts\lanzar_ola.ps1 ... -Arm G2` / `-Arm G1`), desacoplados de esta sesión de Claude, para que
sobrevivan aunque esta conversación termine.

**Tanda 1 (G2, monolítico) lanzada**: 2026-09-18 14:44:20, las 11 campañas G2 vía
`.\scripts\lanzar_ola.ps1 07,08,09,10,11,12,13,14,15,16,17 -Arm G2`. Verificado por Bryan:
- Los 11 logs (`logs\parNN_g2_20260918_144420.log`) imprimen `**jugador:** \`google/gemma-4-31B-it\``
  con el nombre de PJ correcto para cada par (Tarq, Maelis, Garrek, Isolde, Marta, Dunmar, Elior, Kestra,
  Ilvard, Harn, Wynn) -- coincide con la tabla de asignación.
- `Select-String` sobre los 11 logs por `429|402|Traceback`: cero coincidencias.
- `estado_par07-17.py --arm G2` a los ~1 min de arrancar: varias campañas ya en turno 1, resto en turno 0
  -- arrancaron todas, ninguna se cayó de entrada.
- Pendiente: calcular tasa real de turnos/minuto con una segunda lectura de `estado_par07-17.py` más
  adelante, para tener una estimación real de cuánto tarda la tanda (el "~3 horas por lote" era una
  suposición de Bryan, no un dato medido todavía sobre estos pares nuevos).

**Bug encontrado y corregido (crash de las 11 corridas G2, 2026-09-18)**: al volver a consultar
`estado_par07-17.py --arm G2` bastante después de lanzar, los 11 seguían exactamente en el mismo turno
que en la primera lectura -- ninguno avanzó. `Get-Process` confirmó que ningún proceso `python`/`py` de
la corrida seguía vivo: los 11 se habían caído.

*Causa raíz* (NO es el bug ya conocido de `location.state`/valor fuera de dominio): `UnicodeEncodeError`
al imprimir un carácter `✓`/`✗` (U+2713/U+2717) en el loop de confirmación/rechazo de deltas de
`vertical_slice.py`. Windows usa el codepage `cp1252` para stdout cuando el proceso no tiene consola
adjunta -- exactamente el caso de `Start-Process -RedirectStandardOutput archivo.log`, a diferencia de
correrlo interactivo en una consola visible. Las tildes sobreviven como mojibake (aproximación parcial de
cp1252), pero `✓`/`✗` no tienen ninguna aproximación y revientan con excepción no capturada, tumbando el
proceso entero a mitad de turno. `fixtures/generar_seed.py` ya había encontrado y resuelto este mismo
problema antes (`sys.stdout.reconfigure(encoding="utf-8")`, con el comentario "Windows usa cp1252 en
stdout... mata el script") -- pero ese fix nunca se replicó en `vertical_slice.py`/`vertical_slice_g1.py`.

*Verificación de daño*: se consultó `state_deltas`, `turn_log` y `turn_validation` de las 11 campañas G2
directamente. Resultado: **cero corrupción**. Los 4 pares que habían llegado a `current_turn=1`
(Par08/10/12/17) tienen turno 1 completo y consistente (`turn_log=[0,1]`, `turn_validation=[1]`,
crash fue al arrancar el turno 2). Los otros 7 (Par07/09/11/13/14/15/16) nunca comprometieron nada del
turno 1 (`turn_log=[0]` únicamente, `state_deltas` vacío, `turn_validation` vacío) -- el crash ocurrió
antes de cualquier escritura real. No hizo falta ejecutar `limpiar_turnos_corruptos.py` (existente en el
repo para este tipo de caso) ni revertir ningún delta a mano.

*Fix*: agregado `sys.stdout.reconfigure(encoding="utf-8")` + `sys.stderr.reconfigure(encoding="utf-8")`
justo después de los imports en `vertical_slice.py` Y `vertical_slice_g1.py` (mismo patrón exacto que
`generar_seed.py`, aplicado a los dos gemelos aunque G1 todavía no había corrido, para no repetir el
mismo crash en la tanda 2). Verificado: `python -m py_compile` en ambos, y una prueba aislada
(imprimir `✓`/`✗`/tildes a un archivo redirigido igual que `Start-Process`) confirma que ya no revienta
y el texto sale bien codificado.

*Fix adicional de proceso*: `scripts\lanzar_ola.ps1` hardcodeaba `--turnos 1400` para toda relanzada,
violando la regla 1 del plan original ("nunca relances con --turnos 1400 a ciegas"). Se agregó
`scripts\current_turn.py` (consulta rápida de `current_turn` de una campaña) y se modificó
`lanzar_ola.ps1` para consultar el turno real de cada campaña ANTES de lanzar y calcular
`1400 - current_turn` dinámicamente (saltando la campaña si ya llegó a 1400). Probado en seco contra las
11 campañas G2 reales: da 1400 para las 7 en turno 0 y 1399 para las 4 en turno 1, coincidiendo con lo
verificado a mano.

**Segunda caída (2026-09-18, ~16:16-16:19 G2 y ~16:31-16:38 G1) -- causa NO probada.** Tras el fix de
encoding, la tanda G2 (11 campañas, lanzada por Bryan 16:01:57, ~5 turnos/min) llegó a turnos 82-94 y
murió; la tanda G1 (lanzada 16:22:49 desde la herramienta de Claude, ~1.4 turnos/min) llegó a 13-26 y murió
también. Ninguna dejó traceback (`.err` vacío, el log corta a mitad de una frase): terminación externa, no
excepción de Python. Verificación de daño: las 22 campañas quedaron consistentes (`current_turn` = último
`turn_log`, sin duplicados, sin `state_deltas`/`turn_validation` huérfanos) -> reanudables sin doble
aplicación. **Corrección de un diagnóstico propio:** se atribuyó primero la caída a falta de memoria, pero
el evento de Windows (Resource-Exhaustion 2004, 16:31:31) lista como mayores consumidores a `vmmem`
(4.3 GB), `Code.exe` (3.4 GB) y `vmmemWSL` (2.9 GB), no a los procesos Python; los G2 murieron ~15 min
ANTES de ese evento; y al relanzar cada proceso de generación ocupa ~48 MB (11 = ~530 MB). La hipótesis de
memoria no se sostiene con esa evidencia. Candidatos abiertos: proceso hijo atado a una terminal/sesión
(cierre de terminal de VSCode, ventanas headless), o algo externo aún no identificado.
Instrumentación agregada para que la próxima caída quede explicada: `scripts\lanzar_ola.ps1` ahora lanza
vía `Win32_Process.Create` (WMI; el padre es WmiPrvSE, sin consola ni job de VSCode), `python -u` (log sin
buffer) y cada log termina con `[FIN OK]`/`[FIN ERROR <código>]` + hora (si un proceso muere SIN marca de
fin, se llevó también al `cmd` que lo envolvía = algo externo); `scripts\vigilante.ps1` anota cada 30 s
en `logs\vigilante.csv` procesos vivos G2/G1, memoria y RAM libre. `scripts\chequeo_rapido.ps1` corregido
(contaba el python de pgAdmin).
**Relanzado 16:52:03**: las 11 G1 retomando desde sus turnos 13-26. G2 (turnos 82-94) queda para después:
G1 (~17 h) es el camino crítico, así que G2 (~4.5 h) puede empezar hasta ~12 h más tarde sin alargar el total.

**Tercera caída (2026-09-18) -- causas identificadas y corregidas.** Los 22 procesos relanzados a las 16:52/16:56
corrieron ~5 h (G2 hasta turnos 555-673, G1 hasta 256-341) y cayeron; esta vez las marcas `[FIN ERROR 1]` y
los logs sin buffer dieron la causa exacta, y NO fue memoria ni la terminal (los procesos lanzados vía WMI
sobrevivieron 5 h sin ventana ni consola). Tres causas distintas:
1. **HTTP 429 "Model busy, retry later" (engine_overloaded) de DeepInfra**, ~19:37-19:46: `llamar()` trata todo
   `HTTPError` como fatal ("El jugador no respondió" -> `sys.exit`), así que ~20 corridas cayeron en el mismo
   cuarto de hora. Fix (en `vertical_slice.py` Y `vertical_slice_g1.py`, idéntico, neutral entre brazos: un 429 ni
   se factura ni cambia el resultado): 429/502/503/504 se reintentan con backoff exponencial acotado
   (10..300 s + jitter, hasta 30 intentos ~2 h); 401/402 siguen siendo fatales. `scripts/test_reintentos.py`
   (respuestas simuladas) verifica en ambos motores: se recupera tras 2x429, 402 no reintenta, 429 eterno se rinde a los 30.
2. **Par09 G2, 17:17: `psycopg.OperationalError ... Address already in use (10048)`**: `db.py` abre una conexión TCP
   nueva por consulta (sin pool) y con 22 corridas Windows agotó puertos efímeros, una vez en 5 h. Fix: `Campaña._conn()`
   reintenta hasta 6 veces (0.5..8 s) antes de propagar.
3. **Par13 G1, 17:15: `AttributeError: 'str' object has no attribute 'get'`** en `vertical_slice_g1.py`
   (`for prop in propagacion_sugerida: prop.get(...)`): el agente Mundo devolvió un elemento de
   `propagacion_sugerida` que era un string, no un objeto. Es la misma clase de fallo ya corregida en Par02 para
   `deltas` (que tenía su guarda; `propagacion_sugerida` no). Fix: guarda `isinstance(prop, dict)` (avisa y sigue) en ese
   loop, y normalización de la salida del Mundo (JSON no-objeto, `semilla_plantada` no-objeto, `deltas`/
   `propagacion_sugerida` no-lista) al parsearla.
Antes de relanzar se verificó la integridad de las 22 campañas: `current_turn` = último `turn_log`, sin duplicados,
sin `state_deltas`/`turn_validation`/`turn_log` huérfanos (incluida Par13 G1, que cayó en plena escritura).
**Tiempo perdido**: entre ~19:40 y 22:18 (2.6 h) no corrió nada, hasta que Bryan volvió y lo vio.
**Supervisor** (`scripts/supervisor.py`, un solo proceso, lanzado 22:18 vía WMI): mantiene un proceso por campaña y
relanza cualquier caída con `--turnos = 1400 - current_turn` real; no relanza si hay filas escritas para un turno >
`current_turn` (BLOQUEADA), se rinde tras 6 caídas seguidas sin avanzar (RENDIDA), no duplica una campaña que ya
tenga un python vivo, espera 60 s..15 min antes de relanzar, y un solo supervisor a la vez (puerto 47653).
Eventos en `logs\supervisor.log`; salida de cada campaña en `logs\parNN_g?_sup.log`. **Relanzadas las 22** desde
sus turnos reales (G2 555-673 salvo Par09 en 203; G1 256-341 salvo Par13 en 55).
Estimación con el ritmo medido en la corrida anterior (G2 ~3.1 turnos/min, G1 ~1.6 con 22 en paralelo): G2 terminan
en ~4-6.5 h, G1 en ~11-14 h (el más atrasado, Par13 G1, ~14 h) -> todo ≈ mediodía del 2026-09-19 si no hay nuevas
sobrecargas de DeepInfra (que ahora solo retrasan, ya no matan). Nota de método: `RAM libre` de Windows excluye la
caché y engaña; la métrica fiable es la memoria DISPONIBLE (`chequeo_rapido.ps1` ya la usa).

**Las 11 G2 completas (2026-09-19, ~06:00).** Todas en 1400/1400 confirmado contra Postgres (no por el log):
`current_turn`=1400, `max(turn_log)`=1400, 1401 filas (turno 0 + 1400), sin duplicados ni `state_deltas` huérfanos. La
última en cerrar fue Par09 G2 (05:58, la más atrasada porque cayó en la primera tanda a turno 203). El supervisor
registró 13 terminaciones de proceso: 11 normales (código 0 = campaña completa) y **2 caídas reales a las 01:59**
(Par15 G1 en turno 558 y Par10 G2 en turno 1157, código 1): DeepInfra no respondió a la llamada del EXTRACTOR durante
~20 min (`TimeoutError('The read operation timed out')` x4, agotando los 4 reintentos de red de `_post`), el proceso
salió con la excepción sin capturar, y el supervisor lo relanzó solo desde el turno correcto (Par10 G2 desde 1157 ->
`--turnos 243`, completó; Par15 G1 sigue avanzando). No es un bug de código: la llamada falló ANTES de escribir nada,
así que no quedó ningún turno a medias (el supervisor lo habría marcado BLOQUEADA). Se decidió no ampliar los reintentos
del motor: el supervisor ya cubre este caso (una caída ~cada 12 h de 22 procesos) y ampliarlos solo demoraría la
detección. Al relanzar tras una caída, el turno en vuelo se regenera (el LLM no es determinista) pero el intento fallido
nunca escribió, así que no contamina la campaña ni el par.
Transcripciones exportadas (`scripts/exportar_transcripcion.py`, repo raíz, `transcripcion_Par_NN_(real)_-_G2_..._1-1400.md`,
1401 turnos c/u, 1.2-1.4 MB): Par07-Par17 G2. `reporte_validacion.py` (con spaCy/LanguageTool disponibles) guardado en
`docs/reportes/reporte_parNN_g2.txt` (ejecutar con `PYTHONUTF8=1`: el script imprime `─` y cp1252 no lo soporta).
G1: en curso (turnos 627-1032 de 1400 a las ~06:00).

**Reportes de validación G2 (2026-09-19, 06:05-06:20)**: `reporte_validacion.py` corrido sobre las 11 G2 (~68 s c/u), guardados en
`docs/reportes/reporte_parNN_g2.txt`. Resumen (G2 solamente, 1400 turnos c/u):

| Par | cl2_pnj_inactivo (marcados) | reclasif. acción/ref | cl1_inmutable | C | V | Jericho recall | ECR | Gram. | bucle | reloj |
|---|---|---|---|---|---|---|---|---|---|---|
| 07 | 33 | 0/33 | 18 | 1.167 | 0.060 | 0.393 | 0.998 | 0.999 | sí | no disparó |
| 08 | 2 | 0/2 | 11 | 3.333 | 0.073 | 0.200 | 0.997 | 0.999 | sí | no disparó |
| 09 | 28 | 0/28 | 5 | 1.167 | 0.030 | 0.370 | 0.998 | 0.999 | sí | no disparó |
| 10 | 117 | 21/105 | 17 | 0.667 | 0.055 | 0.235 | 0.998 | 0.999 | sí | no disparó |
| 11 | 0 | 0/0 | 15 | 2.000 | 0.058 | 0.125 | 0.998 | 0.999 | sí | no disparó |
| 12 | 160 | 103/74 | 32 | 1.667 | 0.051 | 0.167 | 0.997 | 0.999 | sí | no disparó |
| 13 | 15 | 0/15 | 14 | 0.667 | 0.113 | 0.000 | 0.998 | 0.999 | sí | no disparó |
| 14 | 0 | 0/0 | 19 | 1.500 | 0.151 | 0.167 | 0.999 | 0.999 | sí | no disparó |
| 15 | 0 | 0/0 | 20 | 1.833 | 0.031 | 0.000 | 0.998 | 0.999 | sí | no disparó |
| 16 | 16 | 11/9 | 15 | 1.000 | 0.046 | 0.290 | 0.998 | 0.999 | sí | no disparó |
| 17 | 0 | 0/0 | 19 | 2.667 | 0.039 | 0.269 | 0.999 | 0.999 | sí | no disparó |

Hallazgos (descriptivos; ningún cambio de motor):
1. **Los relojes de facción nunca disparan, en NINGUNA campaña real de NINGÚN brazo.** `game_day` = 0 en las 17 G2 y las
   17 G1 (Par01-17), 0 deltas `world.game_day` registrados en todo el experimento, y `faction_clocks.progress` sigue en su
   valor de siembra. No es un problema de los fixtures de Par07-17 (Par01-06 igual): el reloj del juego nunca avanza porque
   el extractor no emite `world.game_day`. Es simétrico entre brazos (no sesga la comparación pareada), pero deja inactiva
   toda la mecánica de relojes/`on_fire_event` y vuelve vacía la sección 3 del reporte ("relojes no reconocidos"). NO se
   corrige a mitad de corrida: cambiaría el motor entre campañas ya cerradas y en curso. Decisión de tesis pendiente
   (documentarlo como limitación, o corregirlo para un lote futuro).
2. **`cl2_pnj_inactivo_actua`**: 371 turnos marcados en vivo en las 11 G2; el refinamiento sintáctico (sección 9) reclasifica 135
   (36.4%) como PNJ sujeto de una acción y 236 como mención/recuerdo, concentrado en Par12 (103/160), Par10 (21/117) y Par16
   (11/16). Verificado a mano el origen: los PNJ que "actúan" (Valerius en Par12, Elian en Par10) tienen estado `captured`, no
   `dead`. El chequeo trata todo `status <> 'alive'` (dead, missing, captured) como inactivo, pero un PNJ capturado puede seguir
   actuando/hablando en escena sin que sea un error de continuidad. En las 11 G2 hay 22 PNJ no-vivos: 12 dead, 8 captured, 2
   missing. Conviene separar por estado al analizar (dead/missing vs captured) antes de citar este hallazgo.
3. Efecto techo: Entity Coreference Rate 0.997-0.999 y Grammaticality 0.999 en las 11 (no discriminarán entre arquitecturas);
   el detector de bucles marca un ciclo en 11/11 (no discrimina). Jericho recall bajo y variable (0.00-0.39).

**G1 (2026-09-19 ~06:20)**: siguen las 11 vivas (turnos 641-1038), 0 caídas nuevas. Ritmo por franja de 10 min: ~1.5-2.5
turnos/min por campaña entre 04:50 y 05:40 (ya sin competir con G2) y ~0.4-1.0 desde 05:50. Causa: timeouts de lectura
intermitentes de DeepInfra (`TimeoutError: The read operation timed out`, 6-10 por campaña en toda la corrida, cada uno
frena la campaña hasta ~5 min); no hay ningún 429 (el reintento de sobrecarga aún no se activó en la práctica) y la
latencia mediana de las llamadas no cambió (~3.5-4 s). Inestabilidad del proveedor, sin acción necesaria.

## Fase 5 — Cierre (2026-09-19)

**Generación terminada.** 22/22 campañas en 1400/1400 exactos en Postgres. El supervisor cerró solo a las
13:47:45 ("todas las campañas en estado terminal"); 0 procesos de generación vivos; ninguna campaña
BLOQUEADA ni RENDIDA. De los 24 `[REINICIO]` del log, 22 son cierres normales (código 0) y 2 son caídas
reales (01:59, Par15 G1 y Par10 G2: 4× `TimeoutError` en el extractor), relanzadas solas desde el turno
correcto. El monitor `vigilante.ps1` se detuvo. El reintento por 429 solo se probó con respuestas
simuladas; no se activó en la práctica en toda la corrida final.

**Modelo del jugador**: `google/gemma-4-31B-it` en el encabezado de cada corrida (verificado en Fase 4).

### Transcripciones y organización de archivos

- **Transcripción por campaña = un solo archivo** con los turnos 0–1400, en `transcripciones/par07-17/` (22
  archivos, 34 MB). Se exportan desde `turn_log` (`scripts/exportar_transcripcion.py`), no concatenando
  logs, así que las corridas cortadas/reanudadas ya no fragmentan la transcripción (hasta 5 corridas por
  campaña). Turno 0 = el lore de apertura. Par02-06 siguen en la raíz del repo, sin tocar (regla: no tocar
  Par01-06).
- **Bitácoras por corrida**: 167 fragmentos `.md`/`.log`/`.err` (uno por arranque) se archivaron en
  `logs/par07-17/_fragmentos/` sin borrar nada, y se unió cada campaña en
  `logs/par07-17/parNN_g?_<lugar>_bitacora_completa.md` (22 archivos, cada uno con una marca por
  fragmento: rango de turnos, completos e interrumpidos). Script: `scripts/organizar_logs_par07-17.py`.
- Reportes: `docs/reportes/reporte_parNN_g{1,2}.txt` (22, 9 secciones cada uno).

### Integridad de las transcripciones (`scripts/verificar_transcripciones.py`, informe en `docs/reportes/integridad_transcripciones_par07-17.txt`)

Cruza Postgres, el `.md` exportado y las bitácoras por corrida. **0 fallas duras en las 22 campañas**:
- `turn_log` contiguo 0..1400 sin huecos ni duplicados; `turn_validation` cubre 1..1400; ninguna fila
  escrita para un turno > `current_turn`; ningún grupo de `state_deltas` idéntico (mismo turno, entidad,
  campo, valor y evidencia) que indique doble aplicación.
- Cada `.md` es idéntico byte a byte a lo que produce `turn_log`, y es UTF-8 válido.
- Ningún turno se completó en dos corridas distintas; en las costuras (1 a 3 por campaña) el turno
  posterior no repite al anterior; donde hay bitácora, la narración coincide con Postgres. Los turnos
  interrumpidos por un crash (1 a 4 por campaña) nunca llegaron a Postgres y se rehicieron limpios.
- Límite del método: entre 14 y 26 turnos por campaña no tienen bitácora que los respalde (el `.md` de la
  corrida que murió no llegó a volcarse). Están en Postgres y pasan los chequeos estructurales, pero no
  tienen segunda fuente independiente.
- Falso positivo descartado durante la verificación: "Kaelum Null" (Par11 G1) es un nombre inventado, no
  un artefacto técnico; por eso el detector ya no busca "null" suelto. Un par de deltas idénticos en
  Par10 G2 turno 876 (`npc.affinity` → -100 dos veces) son dos evidencias distintas del mismo valor ya
  fijado (`old_value` = -100 en ambos): inocuo, no es doble aplicación.

**Defectos de contenido reales (en los datos; NO se corrigieron, para no alterar el corpus):**

| Defecto | G2 (11 camp.) | G1 (11 camp.) |
|---|---|---|
| DM fuera de personaje: mensaje `[...]` pidiendo una tirada al jugador | **106 turnos en 9 campañas** | 0 |
| JSON crudo del narrador guardado como narración (`{"narrativa": …}`) | 0 | 2 (Par13 t1149, Par17 t381) |
| Palabras sueltas en coreano/ruso/chino/japonés dentro de la narración | 7 turnos | 6 turnos |
| Idem en el texto del jugador | 2 turnos | 4 turnos |
| Narración sin cierre de oración | 0 | 2 (las mismas del JSON crudo) |

- Meta-mensajes de G2: causa observada en el log de Par10 G2 (turnos 825-832): el jugador etiqueta la acción
  con `{Ataque}`, que no existe como habilidad en el motor de dados (`Ataque: NO EXISTE — no se tira`), y el
  DM monolítico pide la tirada en vez de narrar. Es la misma entrada en G1 (mismo motor de dados), pero G1
  nunca rompe personaje. En Par10 G2 quedó atascado 6 turnos con la misma respuesta idéntica (826-831). El
  paso [5] del propio motor ya marca `⚠ meta-comentario entre corchetes`. Par02-06 G2 muestran líneas con
  corchete en magnitud comparable (104/13/22/4), no medido con el mismo criterio. **Asimetría entre
  brazos**, no un ruido simétrico.
- Otros alfabetos: fuga de tokens multilingües del modelo (`тонco`, `어떤`, `任何`, `する`…), ~0.04 % de los
  turnos; la métrica de gramaticalidad no lo detecta.
- `gate_passed` es falso en ~80 % de los turnos de ambos brazos: no es un defecto, significa "el extractor
  no halló nada válido que escribir" (`bool(validos_ev or validos_d or validos_c)` en `vertical_slice.py`).

### Reportes de validación, G2 vs G1 (22 campañas; medias por brazo, descriptivo, n=11 c/u)

| Métrica | G2 | G1 |
|---|---|---|
| `cr1_veredicto_contradice_narracion` (turnos) | 0.9 | 8.0 |
| `cl2_pnj_inactivo_actua` (turnos marcados) | 33.7 | 143.5 |
| `cl1_campo_inmutable_alterado` (turnos) | 16.8 | 34.0 |
| CR-2 turnos con nombre no reconocido | 65.6 | **1396.5** (≈ 100 %) |
| Papalampidi C / V | 1.61 / 0.064 | 2.36 / 0.076 |
| Jericho recall (Par08 G1 sin deltas evaluables) | 0.201 | 0.247 |
| Entity Coreference Rate | 0.998 | 0.997 |
| Grammaticality | 0.999 | 0.989 |
| Densidad grafo por lema | 0.021 | 0.026 |
| Detector de bucles / relojes disparados | ciclo en 11/11 · 0/11 | ciclo en 11/11 · 0/11 |

**Cautelas sobre estos números (verificadas o marcadas como no verificadas):**
1. **CR-2 en G1 es un artefacto de formato, verificado en Par07:** el `dm_output` de G1 incluye una línea
   mecánica (`Percepción: Éxito (10 vs CD 10)`) y el detector cuenta `Éxito`, `Fallo`, `Percepción`,
   `Atletismo`… como nombres desconocidos (1398/1400 turnos, top-12 de esos términos). En G2 los
   marcados son palabras de inicio de oración (`Para`, `Como`, `Necesito`) y nombres reales. **No comparar
   CR-2 entre brazos sin excluir el bloque mecánico.** La gramaticalidad más baja de G1 (0.989 vs 0.999)
   podría tener el mismo origen (etiquetas `narrativa`/`mecanica`/`presion` y la línea mecánica en el
   texto); NO se verificó.
2. `cl2_pnj_inactivo_actua` sigue sin separar por estado del PNJ (dead/missing vs captured, ver hallazgo
   2 de Fase 4). En G1 hay campañas con cientos de marcas (Par11 628, Par13 363, Par07 288, Par14 191) y el
   refinamiento sintáctico solo reclasifica como "acción" en Par14 G1 (201); en el resto de G1 todo queda
   como mención. En G2 la reclasificación aparece en Par10, Par12 y Par16. Los conteos de la sección 9
   pueden no sumar exactamente los de la sección 1 (un turno puede tener ambos tipos).
3. Los relojes de facción no dispararon en ninguna de las 22 (ni en Par01-06): limitación simétrica ya
   documentada (hallazgo 1 de Fase 4).
4. Efectos techo: ECR ≈ 0.997-0.999 y bucle 22/22 no discriminan entre brazos.

### Costo

Estimado ≈ **$41.3** (G2 ≈ $15.2, G1 ≈ $26.1), frente a la referencia del plan de ~$42: sin sobrecosto. Es
una extrapolación (costo/turno de la última corrida de cada campaña × 1400), porque las corridas cortadas por
crash no imprimen su costo; el valor exacto está en el panel de facturación de DeepInfra. El costo impreso
directamente en logs es solo un piso ($20.6 G1 + $8.4 G2 = $29.0).

### Scripts nuevos de esta fase

`scripts/verificar_transcripciones.py`, `scripts/organizar_logs_par07-17.py`. (Anteriores: `supervisor.py`,
`chequeo_rapido.ps1`, `estado_par07-17.py`, `lanzar_ola.ps1`, `crear_sembrar_par07-17.py`.)

### Decisiones abiertas (de Bryan)

1. Relojes de facción: documentar como limitación de la tesis, o corregir el motor para un lote futuro.
2. Meta-mensajes de G2 (106 turnos, causa `{Ataque}` inexistente en el motor de dados): dejarlos como
   hallazgo de la comparación, o reparar el vocabulario de habilidades y decidir si se rehacen esos turnos.
   Idem los 2 JSON crudos de G1.
3. Cómo tratar CR-2 y `cl2_pnj_inactivo_actua` en el análisis (excluir el bloque mecánico de G1; separar por
   estado del PNJ).
4. Par18-27 (10 pares para llegar a 27/54): diferidos por decisión de Bryan.

## Fase 6 — Preparación de Par18-27 (2026-09-19)

Par18-27 (10 pares, para llegar a 27/54) se generan con el motor corregido en lo de abajo. Par01-17 quedan como
generados (motor "v1", sin reloj del mundo).

### Relojes de facción: arreglado (mecanismo compartido G1/G2)

- **Causa** (verificada en código y en datos): `advance_clocks` solo se llamaba si el extractor emitía un delta
  `world.game_day`; el prompt del extractor solo dice "día de juego" sin darle el día actual, y en ~30 000 turnos
  no lo emitió ni una vez (`game_day` = 0 en las 34 campañas). Los fixtures además traían un solo reloj (6-20
  días para dispararse, y un reloj dispara UNA vez).
- **Arreglo** (`orquestador/db.py`, `Campaña.sincronizar_dia`, llamado desde `vertical_slice.py` y
  `vertical_slice_g1.py` tras el paso de escritura): el día de juego sale del turno, `día = turno // TURNOS_POR_DIA`
  (`TURNOS_POR_DIA = 20`, 1400 turnos = 70 días), sin LLM, idéntico en los dos brazos. Escribe el delta
  `world.game_day` con `source='clock'` (ya existía en el enum) y avanza los relojes en UNA transacción; es
  idempotente y se recupera solo si un proceso cae (el siguiente turno avanza los días perdidos). El camino del
  extractor queda intacto. `game_day` no se le muestra al DM: solo llega el evento del reloj disparado, por el
  mismo camino de siempre (`eventos_reloj_turno` → contexto del turno siguiente en G2, agente Mundo en G1).
- **Fixtures de Par18+**: 3 relojes escalonados por par (temprano / medio / tardío, separados ≥ 200 turnos,
  dispara entre el turno 100 y el 1400). `scripts/validar_fixtures_real.py` lo exige (error si un reloj nunca
  dispararía antes del turno 1400; aviso si hay ≠ 3 o están muy juntos).
- **Prueba**: `scripts/test_reloj_determinista.py` contra una campaña desechable en Postgres: el reloj de Par07
  (8 días) dispara exactamente en el turno 160, hay un delta `clock` por día, el evento aparece en
  `eventos_reloj_turno`, llamar dos veces no escribe nada, y tras saltar 30 días sin ticks un solo tick recupera
  y dispara. Campaña desechable borrada (tenant eliminado; las 22 campañas reales intactas).
- **Consecuencia metodológica**: Par01-17 no tuvieron relojes activos y Par18-27 sí (en ambos brazos, así que
  la diferencia dentro de cada par sigue siendo válida). Al agrupar los 27 pares hay que declarar el lote
  (motor v1 vs v2) y reportar las diferencias pareadas por lote o con el lote como covariable.

### Meta-mensajes del DM en G2 (análisis)

- 106 turnos G2 (0.69 %), 9 de 11 campañas; G1: 0. **73 de 106 (69 %) van encadenados** (el turno anterior
  también fue meta): el texto guardado entra como historial y el DM se imita a sí mismo (Par10: 6 idénticos).
- Origen de los 106: 61 sin ninguna etiqueta de tirada (acción de ataque no declarada), 30 con `{Ataque}` y 15
  con otras etiquetas no soportadas (`{Ataque mágico}`, `{Ataque de conjuro}`, `{Ataque furtivo}`,
  `{Iniciativa}`…). El motor de dados solo conoce 18 habilidades + 6 características; no hay tirada de ataque
  ni de iniciativa.
- Causa en el DM G2: `dm/prompt_g2.md` dice "sin tirada previa cuando corresponda, no resuelvas la acción" y
  "las tiradas vienen ya resueltas"; ante un ataque sin tirada válida no tiene salida, y pide la tirada. G1 tiene
  esa salida en su Árbitro (modo `veredicto_sin_tirada`, NUN-5). G1 recibió `{Ataque}` en 69 turnos (G2: 31) y
  nunca rompió personaje: no es que G1 vea menos casos.
- El paso [5] del motor ya detecta estos turnos (`meta_comentario`) pero solo lo registra; el texto igual se guarda.

### Meta-mensajes: arreglo implementado (compartido por G1 y G2, 2026-09-19)

Aprobado por Bryan ("1. sí"). No se tocó `dm/prompt_g2.md` (el baseline monolítico se estudia tal cual).
1. **Tiradas de combate** (`jugador/dados.py`): `{Ataque}` (mejor de FUE/DES + competencia +2), `{Ataque mágico}`
   (solo lanzadores: mago INT, clérigo/explorador SAB, bardo/brujo/paladín CAR), `{Iniciativa}` (DES); aceptan
   variantes (`{Ataque con la daga}`, `{Ataque furtivo}`, `{Ataque de conjuro}`). Salen de la ficha real del PJ
   (`dados.tabla_pj`), son deterministas y reproducibles. Un bárbaro/guerrero/pícaro con `{Ataque mágico}` se
   rechaza como antes (no se inventa un número). El prompt del jugador (`jugador/prompt.md`) ahora lista las tres.
2. **Red de seguridad**: si el DM (G2) o el Narrador (G1) responde con `[...]` de ≥ 20 caracteres, se regenera
   hasta 2 veces con un aviso ("las tiradas las resuelve el sistema; narra sin corchetes"); si aun así queda,
   se borra el corchete y se conserva la narración si quedan ≥ 80 caracteres. Cada activación queda en
   `turn_validation.raw_flags.guard_meta_reintentos`, así que la tasa de activación es un dato medible por brazo.
   El modo tutor de G1 (respuestas a `[pregunta OOC]` del jugador) NO pasa por la red.
3. Prueba sin LLM: `scripts/test_dados_combate.py` (modificadores esperados de 4 PJ, las 5 variantes, rechazos, red).
   `dados.tabla_pj` corre sin error sobre los 27 PJ. Ensayo en vivo en modo seco (1 par, ambos brazos): 0 errores.

### Relojes: verificación de punta a punta (smoke con LLM real)

Dos campañas desechables (G2 y G1, mundo Par07, escala comprimida a 1 día/2 turnos): el reloj dispara en el turno 16
en ambos, `game_day` 10 al turno 20 con 10 deltas `clock`. **G1 narró el evento en el turno 17; G2 no lo mencionó
en los turnos 17-20** (una muestra; el evento llega a G2 en el contexto, solo del turno siguiente al disparo, y el
DM puede ignorarlo). El reporte (sección 3, "relojes disparados") lo medirá con 30 eventos por brazo. Campañas del
smoke borradas.

### Pares 18-27: diseño (tabla de asignación generada por mí, sin repetir PJ, molde, ni tono de Par01-17)

`party_register` ahora es configurable al crear la campaña (Par01-17 fue siempre `mixed`): permite expresar de
la parodia a la solemnidad con el enum existente (`world_tone` solo tiene grimdark/heroic/light/mixed).

| Par | Lugar | Molde narrativo (nuevo en el corpus) | tono / registro | PJ | Relojes (turno de disparo) |
|---|---|---|---|---|---|
| 18 | Nubarrón | sátira burocrática: una universidad cuyo reglamento se reescribe solo cada noche | light / comedic | PJ27 Osric (bárbaro) | 240 · 640 · 1060 |
| 19 | Karhad | asedio con plazo de rendición; resistir o capitular | heroic / serious | PJ19 Bram (guerrero) | 240 · 640 · 1000 |
| 20 | Brasas Lentas | negociación laboral con un dragón que reclama su pensión | mixed / comedic | PJ06 Yarah (guerrero) | 240 · 640 · 1060 |
| 21 | La Ceniza Mansa | crimen de cuarto cerrado en un barco encalmado | mixed / serious | PJ08 Reia (mago) | 240 · 640 · 1000 |
| 22 | Casa Aguasmuertas | pacto gótico heredado con vencimiento fijo | grimdark / serious | PJ15 Otto (brujo) | 260 · 640 · 980 |
| 23 | Sal Negra | juicio con sentencia irrevocable: verdad frente a duelo | grimdark / serious | PJ16 Lianne (paladín) | 260 · 640 · 980 |
| 24 | Villa Pilfera | atraco de comedia con dos equipos planeando a la vez | light / comedic | PJ09 Aldric (pícaro) | 240 · 640 · 1060 |
| 25 | Balanza Real | congreso diplomático corrupto; una vara patrón nunca verificada | mixed / comedic | PJ18 Nadia (pícaro) | 240 · 640 · 1000 |
| 26 | Lindero | un bosque que migra hacia el mar; acompañarlo o detenerlo | mixed / serious | PJ03 Torvald (explorador) | 260 · 640 · 980 |
| 27 | La Vía del Último Silencio | peregrinación fúnebre con voto de silencio y plazo | heroic / serious | PJ25 Fenn (guerrero) | 260 · 640 · 980 |

PJ usados: los 10 de los 11 libres tras Par01-17 (queda sin usar PJ02 Senna). Cada par: ~7-8 lugares (1 `dm_only`), 2 facciones,
**3 relojes escalonados**, 2 misiones (una `dm_only` de misterio), 1 PJ, 3 PNJ (2 centrales con posturas igual de
defendibles + 1 de paso; en Par23 el PNJ de paso es la acusada, que calla). Ficheros: `corpus/real/lore_<slug>.md`,
`fixtures/real/world_par18..27.json`, `personas_par18..27.json`. Validador: 10/10 OK, 0 claves repetidas, HP por la
fórmula verificada de Par03-06. Creación/siembra con `scripts/crear_sembrar_par18-27.py` (IDs en
`docs/ids_par18-27.json`); verificado contra Postgres: mismos turno 0, PJ, HP, tono, registro y 3 relojes en G1 y G2.

### Generación de Par18-27 (lanzada 2026-09-19 17:36)

20 campañas en paralelo bajo `scripts/supervisor.py --ids docs/ids_par18-27.json` (log: `logs/supervisor_par18-27.log`;
estado: `.\scripts\chequeo_rapido.ps1 -Lote 18-27`). Modelo del jugador `google/gemma-4-31B-it` verificado en el encabezado.
Costo esperado ≈ $37 (~$3.7/par); avisar si se sostiene 2-3×. Al terminar: mismo cierre que Par07-17 (integridad
de transcripciones, transcripciones, reportes, unión de logs).

## Fase 7 — Cierre de Par18-27 (2026-09-20)

**Generación terminada.** 20/20 campañas en 1400/1400 (28 020 turnos en `turn_log`). Cada campaña corrió **en una sola
pasada**: 0 caídas, 0 reinicios, 0 turnos interrumpidos, 0 costuras (los 20 `[REINICIO]` del supervisor son cierres
normales, código 0). Los 10 G2 terminaron entre 23:20 y 00:12 (~6 h, desde el arranque a las 17:36) y los 10 G1 entre
05:27 y 08:36 (~12-15 h); el supervisor cerró solo a las 08:36:36. Sin alertas. Modelo del jugador
`google/gemma-4-31B-it` (verificado en el encabezado). Reintentos del motor en los 40 logs: 0 errores HTTP 429, 1 reintento
por saturación (5xx) y 75 por timeout de red, todos resueltos sin caída (0 Traceback).

**Archivos**: transcripciones en `transcripciones/par18-27/` (20, 30 MB); bitácora unida por campaña en
`logs/par18-27/` (fragmentos en `_fragmentos/`); reportes `docs/reportes/reporte_par18..27_g{1,2}.txt` (20, 9 secciones);
integridad en `docs/reportes/integridad_transcripciones_par18-27.txt`. Scripts generalizados con `--ids`/carpeta
(`verificar_transcripciones.py`, `organizar_logs_par07-17.py`, `estado_par07-17.py`, `supervisor.py`, `chequeo_rapido.ps1 -Lote`).

**Costo real: $37.05** (G2 $13.95 ≈ $1.39/campaña; G1 $23.10 ≈ $2.31/campaña; 254 M tokens de entrada, 10.5 M de
salida). Exacto, no extrapolado: al haber una sola corrida por campaña el costo impreso al final de cada log es el total.
Acumulado de los 27 pares menos Par01-06: ≈ $41.3 (Par07-17, estimado) + $37.05.

### Integridad (mismo verificador que Par07-17): 0 fallas duras en las 20

`turn_log` contiguo 0..1400, `turn_validation` 1..1400, ningún turno a medias ni delta doble, cada `.md` idéntico
byte a byte a `turn_log`. Sin costuras: no queda ningún turno sin bitácora que lo respalde (en Par07-17 eran 14-26 por campaña).

| Defecto en los datos (no corregido) | Par07-17 G2 | Par07-17 G1 | **Par18-27 G2** | **Par18-27 G1** |
|---|---|---|---|---|
| DM fuera de personaje `[...]` guardado | 106 | 0 | **0** | 0 |
| JSON crudo del narrador como narración | 0 | 2 | 0 | 1 (Par26 t201) |
| Palabras sueltas en otro alfabeto (dm_output) | 7 | 6 | 13 | 2 |

### Efecto de los cambios de motor (medido)

- **Red de seguridad** (`dados.META_OOC`): 23 activaciones en 14 000 turnos de G2 (0.16 %; la tasa de meta-mensajes
  sin red era 0.69 %), todas resueltas con **una** regeneración, 0 corchetes residuales; 0 activaciones en G1. Repartidas
  en 9 de los 10 pares G2 (Par26: 0).
- **Dados de combate**: 1 285 (G2) y 1 590 (G1) tiradas de `{Ataque}`/`{Ataque mágico}`/`{Iniciativa}`, ninguna rechazada.
  Antes esas etiquetas se rechazaban («NO EXISTE») y disparaban el meta-mensaje de G2.
- **Relojes**: 60/60 dispararon exactamente en el turno esperado (240-260, 640, 980-1060), `game_day` = 70, 70 deltas
  `clock` por campaña, en ambos brazos. Reconocimiento de la consecuencia en los 2 turnos siguientes (sección 3 del
  reporte, heurística de palabras clave): **G1 29/30 (97 %), G2 24/30 (80 %)**, casi siempre al turno siguiente; G2 falla
  más en el reloj temprano (7/10). Precaución: es una heurística léxica y G1 nombra entidades más a menudo (ver deriva).

### Efecto de lote a declarar (Par18-27 no es homogéneo con Par01-17)

- **Combate**: la etiqueta de combate pasó de 0.3 % (G2) / 0.6 % (G1) de los turnos a **9.0 % / 11.3 %**; el texto de
  ataque del jugador también se duplicó (1.1-1.3 % → 2.7-2.8 %). La causa probable es el cambio del prompt del jugador
  (lista las tres tiradas y dice «si atacas, declara siempre {Ataque}») más que las nuevas tiradas en sí; se ve el mismo
  aumento en los dos brazos. Muy desigual por par: Par18/19/27 ≈ 16-18 %, Par24/25 < 1 %. En una muestra hay mal uso
  (`{Iniciativa}` repetida cada ronda, `{Ataque}` al bloquear). Los pares nuevos tienen bastante más combate que los viejos.
- Al pooling de los 27 pares: declarar el lote (motor v1: Par01-17, sin relojes activos ni dados de combate ni red;
  v2: Par18-27) como covariable, o reportar las diferencias pareadas por lote. Dentro de cada par la comparación sigue siendo válida.

### Hallazgo nuevo: deriva del escenario (medido con un proxy, verificado leyendo turnos)

La tesis de "tonos distinguibles" se sostiene en el turno 0 (el lore) pero **no siempre a lo largo de los 1400 turnos**.
Proxy de anclaje: fracción de turnos del DM que mencionan algún nombre propio del escenario (PNJ, lugares, facciones de los
fixtures), por ventanas de 200 turnos, media por lote y brazo:

| | 1-200 | 201-400 | 401-600 | 601-800 | 801-1000 | 1001-1200 | 1201-1400 |
|---|---|---|---|---|---|---|---|
| Par07-17 G2 | 38 % | 33 % | 29 % | 26 % | 24 % | 24 % | 31 % |
| Par07-17 G1 | 75 % | 72 % | 71 % | 71 % | 71 % | 71 % | 70 % |
| Par18-27 G2 | 57 % | 37 % | 32 % | 27 % | 25 % | 28 % | 31 % |
| Par18-27 G1 | 81 % | 87 % | 70 % | 51 % | 48 % | 55 % | 39 % |

Leyendo turnos concretos se confirma que no es solo un artefacto del proxy: hacia el turno ~700-1200 varias campañas de
los dos brazos ya no están en su escenario sino en un corredor/ciénaga/cueva genérica («limo viscoso», «penumbra», un
adversario sin nombre): Par22 G1 t1200 termina hundido en «lodo aceitoso… sumidero» en vez de en la mansión; Par25 G1 (congreso
cómico) t100 en «un pasillo de piedra negra, limo oscuro»; Par19 G1 (asedio) t1000 en un duelo en un pasillo con un PNJ inventado
(«Leo Varga»); Par27 G2 (peregrinación) t700 en un «matorral» con una «criatura». Por campaña (proxy): **G1 se mantiene
anclado** en Par20 y Par27 (≈ 100 % todo el tiempo) y en Par24/Par18 casi toda la campaña; **G1 se desancla** en Par19, 21,
22, 23 y 26 (de ≈ 100 % a 0-25 % a partir del turno ~400-600); Par25 G1 es al revés (≈ 5 % hasta el turno ~1000 y 99 % después).
G2 se mantiene razonablemente anclado en Par21, 25 y 27 (≈ 50-90 %) y cae a < 25 % tras la primera ventana en Par18, 19, 22, 23 y 26.
Limitaciones: el proxy cuenta nombres (G1 los menciona más por diseño), Par25 G1 y Par18 G1 empiezan en 8-9 %
(nombran por cargo), y no se separó causa (modelo, motor, dificultad del molde). **Sin acción de motor**; es un hallazgo sobre
"Arraigo contextual" y "Calidad narrativa emergente" y una limitación del diseño (el mismo modelo juega y narra).
Par07-17 G1 no mostraba esta caída (71 % estable): que en Par18-27 sí aparezca es un efecto de lote no explicado (candidatos:
más combate, moldes menos anclados a un lugar, relojes activos).

### Instrumentos (reportes), medias por brazo, n=10 (Par07-17 entre paréntesis)

| Métrica | G2 | G1 |
|---|---|---|
| cr1 (turnos) | 1.1 (0.9) | 5.1 (8.0) |
| `cl2_pnj_inactivo_actua` (turnos) | 44.5 (33.7) | 98.5 (143.5) |
| `cl1_campo_inmutable_alterado` | 19.0 (16.8) | 31.2 (34.0) |
| CR-2 turnos con nombre no reconocido | 96 (66) | **1 399.5** (1 396.5) |
| Papalampidi C / V | 1.49 / 0.073 | 1.97 / 0.087 |
| Jericho recall | 0.226 | 0.254 |
| ECR / Gramaticalidad | 0.998 / 0.999 | 0.997 / 0.988 |
| Densidad grafo por lema | 0.022 | 0.027 |

Mismos patrones y cautelas que Par07-17 (CR-2 de G1 inflado por su línea mecánica; ECR y bucle sin poder discriminante;
`cl2_pnj_inactivo_actua` sin separar por estado del PNJ). Relojes: ahora los 20 figuran «DISPARÓ» (antes 0/34).

### Decisiones abiertas (de Bryan)

1. La deriva del escenario: ¿se documenta como hallazgo/limitación, o se mide con un instrumento propio en los reportes
   (anclaje léxico o por embeddings) y, para un lote futuro, se prueba un recordatorio del escenario en el contexto del DM?
2. Cómo tratar el efecto de lote (combate 10× más frecuente en Par18-27): covariable, análisis por lote, o excluir turnos de combate.
3. Los defectos de contenido siguen sin corregirse (1 JSON crudo, 15 turnos con otro alfabeto).
4. Con esto están generados los 27 pares (54 campañas); falta el análisis y la redacción.

## Fase 8 — Validación humana de los instrumentos (2026-09-20, en curso)

Plan completo en `docs/plan_validacion.md`; respaldo bibliográfico en `docs/papers_revistas_q1-q3.md`. **Paso 1.1 hecho**:
`scripts/validacion_generar.py` + `scripts/validacion_formulario.html` generan en `validacion/` 24 unidades principales + 4 de piloto
(pares Par07-27, ventanas de 8 turnos, estratificadas por posición y tono), el material ciego y un formulario por evaluador
(probado en Chromium sin interfaz). Hallazgos al preparar el ciego: G1 lleva etiquetas `narrativa/mecanica/presion` en 99-100 % de sus
turnos y una línea de tirada en 95 % (G2 nunca), lo que delataba la arquitectura (se normaliza el texto que ve el evaluador); G1
escribe ~34 % más por turno (946 vs 705 caracteres), fuga residual que se medirá con la pregunta «¿cuál es el multiagente?»; un párrafo
idéntico al del turno anterior aparece en ≈ 0.3 % de los turnos de G1 (0 en G2). Siguiente: piloto con 2 evaluadores (Paso 1.2).

**Encuadre y hallazgos (2026-09-20, tras recibir la Rúbrica v2).** La rúbrica v2 fue sustituida por medición determinista a pedido del asesor;
la validación se replantea en dos rutas (`docs/plan_validacion.md`): A (sin humanos: cobertura, sensibilidad por perturbación, precisión/recall de
detectores) y B (chequeo humano pequeño, opcional, con visto bueno del asesor). Matriz en `docs/matriz_cobertura_rubrica_instrumentos.md`.
Hallazgos de validez: de 12 componentes de la rúbrica, 5 no tienen instrumento y 3 están medidos con instrumentos sesgados; `cl2_pc_hp_contradice`,
`qn2_pj_accion_revisar` y `qn2_pj_piensa_narrado` buscan al PJ por su nombre en 3.ª persona, pero G2 lo nombra en el 0.1 % de los turnos y narra en
2.ª persona en el 84.5 % (G1: 4.9 % y 36.9 %): **sus ceros en Par07-27 no son evidencia de ausencia del defecto** (0 marcas en 58 800 turnos en total (29 400 por brazo));
el equivalente en 2.ª persona (exploratorio, sin validar) aparece en 1.00 % de los turnos de G2 y 0.45 % de G1. `cl1_campo_inmutable_alterado` mide
deriva del extractor, no consistencia de personajes.

**Plan A en marcha (2026-09-20 noche).** Trabajo repartido en subagentes con verificación previa a la aceptación (ver `docs/plan_A_detallado.md`):
investigación bibliográfica de 2.ª persona y agencia (`docs/research/r1_*`, sin base directa: aporte propio) y de sensibilidad y auditoría (`r2_*`, 35 referencias,
4 comprobadas); prototipo `scripts/instrumentos/persona2.py` (72 pruebas, salida determinista, spaCy solo etiqueta Person=2 en el 14 % de los hallazgos); arnés
`scripts/sensibilidad/` (123 pruebas, fidelidad 0 discrepancias en 392 turnos, expectativas atadas a un SHA-256). Línea base de A2: los tres detectores de 3.ª
persona marcan 100 % con el nombre del PJ y 0 % en 2.ª persona; el formato de G1 rompe 7 de 9 controles invariantes de los instrumentos numéricos; `cr2_nombres_no_reconocidos`
está saturado en G1 (99.9 %); los instrumentos de grafo de entidades no distinguen narración de otro escenario. Corrección de un error propio: 58 800 turnos son el total de 42
campañas (29 400 por brazo), no por brazo. La categoría de acciones «no declaradas» de persona2 tenía precisión ≈ 0 en 7 de 7 filas leídas: se rediseña y se congela antes
de auditar.

**A4a: instrumentos numéricos sobre texto normalizado (2026-09-20).** `scripts/reporte_v2/` (48 pruebas) recalcula los instrumentos de las 42 campañas con
el formato de G1 normalizado (`datos_v2/`, `docs/reportes/reporte_v2_formato_normalizado.md`, descriptivo y post hoc). Sanidad: G2 v1 = v2 con 0 discrepancias en 29 400
turnos × 8 columnas; recalcular G1 sobre texto crudo reproduce v1 con 0 discrepancias. `prosa()` deja residuos de formato en 0.77 % de los turnos de G1 (etiquetas en negrita
`**narrativa**`, sobre todo en Par12, «Mecánica» capitalizada, 3 turnos con JSON crudo); contrasté por mi cuenta 400 turnos de Par12 G1: `prosa()` coincide en 353 y las 47
discrepancias son todas turnos con etiquetas en negrita; la normalización estricta coincide en 400. Las hojas de etiquetado (515 turnos de persona2 y 28 unidades de la Ruta B) tienen
0 residuos, pero al regenerar conviene usar la normalización estricta. Resultado sobre 21 pares (Wilcoxon con Holm, HL de G1 − G2): **cambian de signo o desaparecen los efectos de
gramaticalidad (LanguageTool), nombres no reconocidos (G1 pasa de 99.9 % a 8.9 % de turnos marcados; G2 5.7 %) y grafo de entidades**; el Jaccard baja 56 % pero sigue G1 > G2 en 21 de 21
pares; **TTR (G1 < G2 en 21/21) y bigramas repetidos (G1 > G2 en 21/21) no cambian**. Es decir: las diferencias de gramaticalidad (0.989 vs 0.999) y de nombres no reconocidos que se
reportaron en Fase 7 eran artefacto de formato (esa sospecha, antes sin verificar, queda confirmada); las de TTR y repetición son reales dentro de lo medible. Confusores que quedan sin
normalizar: tipografía del diálogo (G1 comillas rectas 79 %, G2 raya 23.6 %) y el bloque `presion`, que solo existe en G1. Pendiente: recalcular sobre texto normalizado los
booleanos `cr1_veredicto_contradice_narracion` (G1 139 marcas vs G2 21, sin verificar si vienen de la línea mecánica) y `cl2_pnj_inactivo_actua`.

## Pendiente

Nada de generación. Solo las decisiones abiertas de arriba.
