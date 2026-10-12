# Brecha B: prueba de sensibilidad A2 para Jericho recall y relojes

**Estado: script escrito y listo para correr, NO EJECUTADO todavía.** Esta sesión no tiene acceso a la base de datos (Postgres) de la máquina de Bryan, así que no pude correrlo yo mismo. Necesita una corrida (`--rapido` primero, como humo) desde donde sí hay acceso — su máquina, o el proceso que corre Claude Code localmente.

## Qué pide la brecha

`docs/cierre_brechas.md` (fila CL-2) y `docs/triage-brechas-cierre-2026-09-21.md` marcan dos instrumentos de coherencia longitudinal sin prueba de sensibilidad (A2): **Jericho recall** y **relojes reconocidos**. Sin esa prueba, H1e queda indeterminada. `docs/plan_A_detallado.md` ya documenta el patrón general para cerrar este tipo de brecha (registrar expectativas con hash antes de correr, nunca tocar `sensibilidad_baseline.*`, informe en archivo aparte) — dos veces usado ya (persona2, Szigriszt-Pazos/MTLD/MATTR).

## Lo que encontré (no estaba documentado en ningún doc del proyecto)

`jericho_qa_recall()` y `relojes_no_reconocidos()` (`orquestador/reporte_validacion.py`) **no** son instrumentos de texto-por-turno como los de `scripts/sensibilidad/instrumentos_texto.py`. Son heurísticas de solapamiento léxico sobre **eventos estructurados reales**:

- **Jericho recall**: por cada delta narrable (`Campaña.deltas_narrables()` — cambios de `npc.status`, `npc.affinity` con cruce de banda, `quest.status`), busca si alguna palabra de una tabla de lexemas fija (`_KEYWORDS_NPC_STATUS`, `_KEYWORDS_QUEST_STATUS`, `_KEYWORDS_AFINIDAD_BANDA`) aparece como subcadena en el texto narrado del turno del delta + 1 turno siguiente (`ventana=1`). `recall_global` = fracción de deltas "reconocidos".
- **Relojes reconocidos**: por cada reloj de facción disparado (`Campaña.relojes_disparados()`), busca si el nombre de la facción o una palabra (≥4 letras) de su agenda aparece (con `\bpalabra\b`) en los 2 turnos siguientes al disparo (`ventana=2`).

Esto significa que la unidad de perturbación correcta **no es un turno muestreado al azar** (como el resto del arnés en `scripts/sensibilidad/`), sino **un evento real con su ventana de evidencia**: hay que insertar o quitar texto exactamente en el turno donde el instrumento mira, usando el lexema exacto que el instrumento busca.

## Diseño de la prueba (`scripts/sensibilidad/correr_jericho_relojes.py`)

Cuatro perturbaciones, cada una con dirección pre-especificada (fijada y con hash SHA-256 ANTES de correr, igual que el resto del arnés):

| Perturbación | Sobre | Acción | Esperado |
|---|---|---|---|
| JQ1 | delta narrable hoy NO reconocido | inserta una oración con el lexema exacto del estado nuevo, en el turno de evidencia | reconocido False→True (`se_dispara`) |
| JQ2 | delta narrable hoy reconocido | quita del turno de evidencia real la(s) oración(es) con el lexema que lo reconoce | reconocido True→False (`se_apaga`) |
| RJ1 | reloj disparado hoy NO reconocido | inserta una oración con la facción/palabra de agenda, en el primer turno de evidencia | reconocido False→True (`se_dispara`) |
| RJ2 | reloj disparado hoy reconocido | quita del turno de evidencia real la oración con la palabra que lo reconoce | reconocido True→False (`se_apaga`) |

Las 12 oraciones de refuerzo (una por cada estado npc.status/quest.status/banda de afinidad) se verifiqué programáticamente que contienen el lexema exacto de la tabla real del instrumento antes de escribir este documento (script de verificación en el propio `correr_jericho_relojes.py`, función `_assert_oraciones_contienen_lexema()`, que se corre automáticamente al inicio — si alguna oración no calza, el script se detiene ahí y no perturba nada).

La inserción reutiliza `perturbaciones._insertar_al_inicio_de_parrafo` (misma función que usan P1-P5, respeta la zona «narrativa» de G1). La supresión de oraciones reutiliza el mismo criterio de partición de oraciones que P6 (`_partir_zona` + split por `[.!?]`).

## Límite pre-registrado

Los relojes de facción **solo existen en Par18-27** (Par01-17 se generó con el motor sin avance de reloj — nota ya presente en `docs/cierre_brechas.md`). La muestra de RJ1/RJ2 sale solo de esas 10 parejas / 20 campañas, así que es más chica que la de JQ1/JQ2 (que puede usar las 27 parejas). Esto ya estaba anotado como limitación conocida en el proyecto; aquí solo se hereda, no se inventa.

## Qué falta para que el resultado sea válido

1. **Correr el humo primero**: `PYTHONUTF8=1 py scripts/sensibilidad/correr_jericho_relojes.py --rapido` (3+3 Jericho, 2+2 relojes). Revisar a mano 2-3 filas del CSV de salida — confirmar que la oración insertada/quitada es la que se esperaba y que el campo `resultado` tiene sentido.
2. Si el humo se ve bien, correr la muestra completa (por defecto: 40 deltas Jericho por dirección, 16 relojes por dirección — ajustable con `--n-jericho`/`--n-relojes` según cuántos candidatos reales existan; el propio script imprime cuántos candidatos encontró antes de perturbar).
3. Leer `docs/reportes/sensibilidad_jericho_relojes.md` (tasa de confirmatorias por perturbación) y decidir si Jericho recall / relojes reconocidos pasan a tener celda A2 en `docs/cierre_brechas.md` y `scripts/reporte_v2/consolidar.py` (hoy: `"heurística léxica; sin prueba de sensibilidad"` / `"proxy de solapamiento léxico; sin prueba A2"` — habría que actualizar esa nota una vez haya un resultado real, no antes).

No toqué `docs/cierre_brechas.md` ni ningún archivo generado (`datos_v2/`, `docs/reportes/`) porque el script no se ha corrido: actualizar esos documentos antes de tener un resultado real sería exactamente el tipo de cosa que este mismo proyecto evita (expectativas fijadas ANTES de correr, nunca al revés).

## Archivos entregados

- `scripts/sensibilidad/correr_jericho_relojes.py` — el script completo, comentado en el mismo estilo que el resto de `scripts/sensibilidad/`, listo para correr. Importa las tablas de lexemas y las funciones reales de `reporte_validacion.py` (`_KEYWORDS_NPC_STATUS`, `_KEYWORDS_QUEST_STATUS`, `_KEYWORDS_AFINIDAD_BANDA`, `_banda_afinidad`, `_texto_reloj`) en vez de duplicarlas, para que la oración inyectada nunca pueda divergir de lo que el instrumento real busca.
