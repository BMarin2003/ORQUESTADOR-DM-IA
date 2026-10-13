# legacy

Material que **no hace falta para reproducir** el experimento ni sus resultados (corpus y resultados cerrados). Se conserva por trazabilidad. La estructura interna replica la de la raíz.

| Carpeta | Qué contiene | Por qué es legacy |
| --- | --- | --- |
| `corpus/pilotos`, `fixtures/pilotos`, `logs/pilotos` | Escenarios y bitácoras de los pilotos (pares 01–03) | Reemplazados por `corpus/real` y `fixtures/real` |
| `sondeos/` | Pruebas previas del proveedor (concurrencia, sesión) | Anteriores al experimento |
| `orquestador/probar_*`, `verificar_*` | Verificaciones de roles de G1 | Una sola vez; sus resultados están en `docs/especificaciones/` |
| `scripts/estado_par01/02/04_05_06`, `listar_par01`, `verificar_sesion1` | Estado de los pilotos | Pares ya cerrados |
| `scripts/barrer_stubs`, `diagnosticar_*`, `limpiar_*`, `fusionar_personaje_duplicado` | Reparación de siembras fallidas | Incidencias resueltas |
| `scripts/utilidades/` | Búsquedas y renombrados puntuales | Una sola vez |
| `scripts/verificacion/` (decks) | `actualizar_deck*`, `volcar_deck`, `render_laminas`, `ver_parrafos` | Decks anteriores |
| `scripts/semantico/recall_semantico_v2_previo.py` | Versión previa del recall semántico | Superada por `recall_semantico_v2.py` |
| `docs/archivo/` | Prompts de DM descartados | Reemplazados por `dm/` |
| `tesis/versiones/` | Versiones anteriores de la tesis | Vigente: `tesis/TESIS2.docx.md` |
| `sustentacion/propuestas/`, `sustentacion/generador/deck*.js` | Decks v1–v4 y sus generadores | Vigente: `Sustentacion_UPAO.pptx` |
| `entregas/` | Paquetes entregados al asesor | Entregados el 2026-09-21 |

Los scripts movidos ya tienen corregida la ruta a la raíz del repositorio, pero no se mantienen: ejecútalos desde la raíz y bajo tu responsabilidad.
