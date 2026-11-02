# Prompt para Claude Code — Generar Par 07 a Par 17 (11 pares, 22 campañas)

Pega esto tal cual como primer mensaje a Claude Code, parado en `C:\BMARIN2003\DEV\proyecto`.

---

Eres el operador técnico del pipeline de generación de campañas de mi tesis (QuestMasters — comparación de coherencia narrativa MAS vs. Monolítico en D&D). Tienes acceso completo y en vivo a este repo. Tu tarea: diseñar, sembrar y generar 11 pares nuevos (Par 07 a Par 17, 22 campañas en total: G1 multiagente + G2 monolítico por par), llevándolos a 1,400 turnos cada una, sin supervisión constante de mi parte — yo voy a estar trabajando el documento de tesis en paralelo con otra sesión de Claude. Repórtame solo cuando termines una fase completa, cuando necesites una decisión que no puedas tomar sola, o si algo se sale mucho del presupuesto/tiempo esperado.

## 0. Orientación obligatoria antes de tocar nada — no asumas el schema, léelo

No inventes el formato de los fixtures. Antes de escribir cualquier archivo nuevo, lee completos estos archivos de referencia (son la fuente de verdad del formato, no lo que yo te diga aquí):

- `corpus/real/lore_vega_del_yelmo.md` y `corpus/real/lore_poza_seca.md` (dos lores completos, uno de estructura "amenaza externa" y otro de "escasez de recursos" — para el tono de prosa y la longitud esperada)
- `fixtures/real/world_par03.json` y `fixtures/real/world_par06.json` (schema de locations/factions/clocks/quests/character)
- `fixtures/real/personas_par03.json` y `fixtures/real/personas_par06.json` (schema de PNJ, incluyendo el molde de "PNJ de paso" con casi todo vacío)
- `fixtures/validar_fixtures.py` (el validador real — vas a correrlo sobre cada fixture nuevo antes de crear ninguna campaña)
- `fixtures/generar_seed.py`
- `jugador/personajes_jugadores.json` (roster completo de 27 PJ — ya sé cuáles voy a usar, ver tabla abajo, pero confirma que los campos `caracteristicas`/`modificadores`/`deriva` de cada PJ elegido coinciden con lo que vas a referenciar)
- `extractor/contrato.json` (los `mutable_fields` con sus enums reales — MUY IMPORTANTE, ver bug conocido abajo)
- `scripts/crear_campana_real.py`, `scripts/crear_campana_real_g1.py`, `scripts/sembrar_mundo_real.py`, `orquestador/vertical_slice.py`, `orquestador/vertical_slice_g1.py`, `scripts/exportar_transcripcion.py`, `orquestador/reporte_validacion.py` (los scripts que vas a invocar — lee sus `--help`/argparse para confirmar la firma exacta de argumentos, no asumas)
- `scripts/estado_par04_05_06.py` (patrón para hacerte tu propio script de estado de las 22 campañas nuevas — cópialo y adapta los campaign_id)
- El `.env` del proyecto: confirma que **no** existe una línea `DMIA_MODELO_JUGADOR=...` (se sacó a propósito el 2026-09-18 porque pisaba el default correcto, `google/gemma-4-31B-it`). Si la encuentras, bórrala.

## 1. Reglas fijas del proyecto — no son opcionales

1. **Nunca relances una corrida con `--turnos 1400` a ciegas.** Si una corrida se corta (crash, saldo, lo que sea), calculá `1400 - current_turn` real (consultado contra Postgres, no contra el log) y usá esa cifra exacta para reanudar.
2. **Cada par nuevo debe ser distinto de TODOS los pares reales anteriores (Par01-Par17 acumulado) en tono, estructura de conflicto y personaje jugador.** La tabla de la sección 2 ya está diseñada para cumplir esto contra Par01-06 — no la cambies sin razón, y verificá que ningún par de la tabla se repita entre sí tampoco.
3. **Verificación por contenido, no por mensaje de éxito.** Cuando escribas un archivo, confirmá con un `Get-Content`/lectura real que el contenido quedó como esperabas — no asumas que "escribió sin error" significa "el contenido es correcto". Esto ha mordido al proyecto varias veces esta semana (con el puente remoto, no debería pasarte a vos que corrés local, pero mantené el hábito).
4. **Las rutas de los scripts de creación/siembra son relativas a `corpus/` y `fixtures/` respectivamente, NO a `corpus/real/`/`fixtures/real/`.** Tenés que pasar el prefijo `real\` explícito en cada argumento de archivo (`real\lore_xxx.md`, `real\world_parXX.json`, `real\personas_parXX.json`). Ya mordió el proyecto dos veces por esto.
5. **Bug conocido y ya parcheado — no lo reintroduzcas ni asumas que no puede volver a pasar de otra forma:** el extractor puede proponer un campo válido (ej. `location.state`) con un valor que en realidad pertenece a OTRO campo del mismo tipo de entidad (ej. `location.detail`). El chequeo de campo (paso 7 del pipeline) valida que el CAMPO esté en la lista blanca, pero no que el VALOR corresponda a ese campo — eso solo lo valida el enum real de Postgres, y si no está protegido, tumba la corrida entera. Ya existe `try/except Exception` alrededor de la llamada `camp.aplicar()` del loop de deltas del extractor en ambos `vertical_slice*.py` — confirmá que sigue ahí (no debería haber cambiado) antes de arrancar. Si en 22 campañas nuevas aparece OTRA clase de excepción no capturada tumbando una corrida, aplicá el mismo patrón (try/except específico, log del rechazo, `continue`) en vez de dejarlo caído, document{alo, y avisame en el reporte final — no relances sin el fix.
6. **No toques Par01-06 (ya cerrados) ni sus archivos.** No toques el `.docx`/documento de tesis — eso lo estoy llevando en paralelo con otra sesión de Claude.
7. **Costo de referencia medido: ~$3.83/par (11 pares ≈ ~$42 total), ~$0.00137/turno.** Si en cualquier momento el costo por turno reportado por los scripts se dispara muy por encima de eso (2-3x sostenido), pausá y avisame antes de seguir gastando — puede ser una señal de un bug nuevo (reintentos de más, modelo equivocado, etc.), no solo variabilidad normal.
8. **Confirmá el modelo del jugador al arrancar cada campaña.** El log de arranque debe imprimir `**jugador:** \`google/gemma-4-31B-it\``. Si ves Hermes, parate y revisá el `.env` antes de seguir gastando turnos.

## 2. Los 11 pares a diseñar — tabla de asignación ya cerrada

No cambies esta asignación (tono/estructura/PJ) salvo que encuentres una razón técnica real (ej. el PJ no tiene stats completas en `personajes_jugadores.json`). El **nombre del lugar/ambientación** para cada uno lo inventás vos, siguiendo el estilo de los lores existentes (nombre evocador de dos palabras, español, sin repetir ningún nombre de lugar ya usado en Par01-06: Puerto Salazón, Alto Ferrena, Vega del Yelmo, Caleta Lumbre, Vado Cabrero, Poza Seca).

| Par | Tono (`world_tone`) | Estructura de conflicto (no repetir con Par01-06 ni entre sí) | PJ (id / nombre / clase) |
| --- | --- | --- | --- |
| 07 | `grimdark` | Culto oculto infiltrado en la comunidad | `pj_pj23` — Tarq, brujo ("Fanático del culto") |
| 08 | `heroic` | Venganza de sangre entre dos familias | `pj_pj04` — Maelis, guerrero ("Caballera caída") |
| 09 | `grimdark` | Plaga/enfermedad misteriosa sin cura clara | `pj_pj17` — Garrek, clérigo ("Médica de guerra") |
| 10 | `mixed` | Refugiados desplazados, tensión con la población local | `pj_pj24` — Isolde, explorador ("Huérfana de la frontera") |
| 11 | `heroic` | Profecía o presagio que divide a la comunidad | `pj_pj26` — Marta, clérigo ("Devota con dudas") |
| 12 | `light` | Contrabando/mercado negro que amenaza con exponer al pueblo | `pj_pj07` — Dunmar, pícaro ("Ladrón con código") |
| 13 | `mixed` | Maldición ligada a un lugar u objeto concreto | `pj_pj21` — Elior, mago ("Nigromante académico") |
| 14 | `light` | Festival o ritual comunitario que sale mal | `pj_pj20` — Kestra, bardo ("Estafador de sonrisa fácil") |
| 15 | `heroic` | Disputa de herencia/propiedad ancestral | `pj_pj01` — Ilvard, paladín ("Paladín de juramento") |
| 16 | `mixed` | Guerra de precios entre dos rutas comerciales rivales | `pj_pj12` — Harn, bárbaro ("Superviviente del camino") |
| 17 | `light` | Elección de liderazgo local manipulada desde afuera | `pj_pj22` — Wynn, pícaro ("Sicario metódico") |

Para cada par, seguí exactamente el molde de contenido de Par03/Par06 (ya leído en el paso 0):

- **Lore (`corpus/real/lore_<slug>.md`):** prosa completa — el lugar/asentamiento, el conflicto central sin villano de cálculo trivial (dos posturas legítimas o una amenaza/fenómeno ambiguo, según corresponda a la estructura), 2-3 personajes centrales con motivación propia, un reloj narrativo si aplica, nota de tono explícita.
- **`fixtures/real/world_parXX.json`:** ~7 locations (incluí 1-2 `dm_only` para un gancho de misterio si la estructura lo permite), 2 factions, 1 clock, 2 quests, 1 character (el PJ asignado, con su `hp` calculado a mano igual que los pares anteriores: dado de golpe de su clase × nivel 3 + mod de Constitución × 3 — sacá el mod de CON real de `personajes_jugadores.json` para ese PJ, no lo inventes).
- **`fixtures/real/personas_parXX.json`:** 3 PNJ — 2 con ideal/vínculo/defecto completos y motivación propia enfrentada entre sí (las "dos posturas legítimas" del conflicto), 1 "PNJ de paso" con el molde vacío ya usado en Par01-06 (mismo patrón que Petra/Yulen/Mira/Alba Ferrís).

**Validación obligatoria antes de crear ninguna campaña:** corré `fixtures/validar_fixtures.py` (o el chequeo cruzado que use — leelo en el paso 0) sobre los 11 pares. Confirmá JSON parseable y que toda `location`/`bond_target`/`seat`/`faction` referenciada resuelve contra una clave real del mismo `world_parXX.json`. No sigas al paso 3 con ningún par que falle esta validación.

## 3. Crear y sembrar las 22 campañas

Mismo patrón que Par03-06 (confirmá la firma exacta de cada script en el paso 0, esto es el patrón esperado):

```
REM Por cada par XX (07..17), con <slug> el nombre de archivo y <Lugar> el nombre bonito del lore:

REM 1) Crear G2 -- imprime tenant_id, user_id, campaign_id
python scripts\crear_campana_real.py "Par XX (real) · G2 (Monolítico) · <Lugar>" real\lore_<slug>.md <tono>

REM 2) Crear G1, reusando el MISMO tenant_id/user_id del paso 1
python scripts\crear_campana_real_g1.py <tenant_id> <user_id> "Par XX (real) · G1 (Multiagente) · <Lugar>" real\lore_<slug>.md <tono>

REM 3) Sembrar G2
python scripts\sembrar_mundo_real.py <campaign_id_G2> <tenant_id> <user_id> pj_pjNN real\world_parXX.json real\personas_parXX.json

REM 4) Sembrar G1 -- mundo independiente, mismo escenario/PJ
python scripts\sembrar_mundo_real.py <campaign_id_G1> <tenant_id> <user_id> pj_pjNN real\world_parXX.json real\personas_parXX.json
```

Llevá un registro (archivo local, ver sección 6) de cada `tenant_id`/`user_id`/`campaign_id` que te devuelva cada comando — los vas a necesitar para los pasos 4 y 5, y para el reporte final.

## 4. Generar a escala completa, en paralelo

```
python orquestador\vertical_slice.py --campaign-id <campaign_id_G2> --pj PJNN --turnos 1400
python orquestador\vertical_slice_g1.py --campaign-id <campaign_id_G1> --pj PJNN --turnos 1400
```

**Estrategia de paralelismo — no lances las 22 de una sola vez sin probar primero:**

1. Arrancá con **3 pares (6 campañas) en paralelo** como primera oleada — cada una en su propio proceso en segundo plano (`Start-Process` de PowerShell o equivalente), no bloqueante.
2. Dejalas correr ~15-20 minutos y revisá que las 6 avancen sin errores de rate-limit (HTTP 429) ni de saldo (402) de DeepInfra. Si todo va bien, sumá la siguiente oleada de 3 pares, y así hasta cubrir los 11. Si ves 429 sostenidos, bajá la concurrencia y espaciá el arranque de las siguientes oleadas.
3. Cada campaña corre independiente — no hay coordinación entre G1 y G2 de un mismo par ni entre pares distintos, así que el paralelismo es seguro en términos de datos (cada una escribe solo en su propio `campaign_id`).

## 5. Protocolo ante un crash

Si cualquier corrida se corta (traceback no capturado, corte de red, timeout):

1. NO la relances de inmediato. Primero consultá `current_turn` real contra Postgres (adaptá `scripts/estado_par04_05_06.py` con los 22 `campaign_id` nuevos, o corré una consulta directa).
2. Si el traceback es una excepción NO capturada por el `try/except` ya existente (es decir, una clase de bug nueva, no la ya conocida de `location.state`/Mundo), aplicá el mismo patrón de fix (try/except específico alrededor de la llamada que falló, log del rechazo, seguir) — documentalo en el archivo de bitácora de la sección 6 con la causa raíz exacta, igual que se hizo con los bugs anteriores del proyecto (no lo arregles con un parche genérico sin entender la causa).
3. Reanudá con `--turnos = 1400 - current_turn` calculado en el momento, nunca un número fijo.

## 6. Bitácora y cierre — dejame algo para retomar

Yo NO tengo acceso a tu sesión ni a tu terminal en vivo — solo veo lo que Bryan me pegue de vuelta en el chat, o lo que escribas a un archivo del repo. Así que:

- Llevá un archivo `docs/bitacora_par07-17.md` (creálo si no existe) donde vayas anotando, por par: nombre/tono/estructura elegidos, los 3 `campaign_id`/`tenant_id`/`user_id`, cualquier bug encontrado y su fix exacto (causa raíz + parche), turno final de cada campaña, y costo aproximado si podés inferirlo del log de cada corrida (el desglose por modelo que imprime `vertical_slice*.py` al terminar).
- Cuando una campaña llegue a 1400 turnos exactos (confirmado contra Postgres, no solo por el log), corré:
  ```
  python scripts\exportar_transcripcion.py --campaign-id <id>
  python orquestador\reporte_validacion.py --campaign-id <id>
  ```
- Cuando las 11 pares estén cerrados (22 campañas a 1400/1400, transcripciones exportadas, `reporte_validacion.py` corrido sobre las 22), armá un resumen final en la misma bitácora: tabla de los 11 pares con su estado, cualquier hallazgo cualitativo o cuantitativo que te llame la atención (igual que se hizo con Par03: colisión de identidades, drift de personajes, etc.), y el costo total real de este lote de 11 pares.
- Avisame (a mí, Bryan, en el chat de donde salió este prompt) cuando: (a) termine la fase de diseño de los 11 fixtures y estén validados, antes de crear ninguna campaña — quiero un vistazo rápido; (b) termine toda la generación; o (c) necesites una decisión que no puedas tomar sola (presupuesto fuera de rango, una ambigüedad real en el diseño, un bug que no sabés cómo resolver con el patrón ya establecido).

## 7. Qué NO hacer

- No toques `TESIS-Comparación...docx.md` ni nada relacionado a redacción de la tesis — eso lo llevo en paralelo con otra sesión de Claude.
- No regeneres ni modifiques Par01-06 (ya cerrados).
- No cambies la asignación de tono/estructura/PJ de la tabla sin avisar primero.
- No relances ninguna corrida con `--turnos 1400` fijo tras un corte — siempre `1400 - current_turn`.
- No gastes muy por encima del presupuesto de referencia (~$42 para el lote completo) sin pausar y avisar.

---

Arrancá por la sección 0 (orientación) y no saltes directo al diseño sin haber leído los archivos de referencia reales.
