# scripts

Se ejecutan desde la raíz del repositorio (`py scripts/...`). Los scripts de la raíz de esta carpeta se llaman entre sí por ruta, así que se mantienen donde están; aquí se agrupan por función.

## Carpetas

| Carpeta | Función |
| --- | --- |
| [`instrumentos/`](instrumentos/) | Instrumentos de medición: respuesta a la acción (z), anclaje al escenario, persona2 y sus pruebas |
| [`sensibilidad/`](sensibilidad/) | Pruebas de sensibilidad por perturbaciones (expectativas selladas, δ de Cliff, Holm) |
| [`reporte_v2/`](reporte_v2/) | Recalcular instrumentos, consolidar G1 vs G2, prueba de Page, Kaplan-Meier, resultados de la tesis y cierre de brechas |
| [`semantico/`](semantico/) | Instrumento semántico exploratorio (embeber corpus con bge-m3, recall y sensibilidad) |
| [`brechas/`](brechas/) | Cierres de brecha por objetivo (OE-1 a OE-6), costo por arquitectura y pares 01–06 |
| [`degradacion/`](degradacion/) | Último bloque y mecanismo por bloque |
| [`compromisos/`](compromisos/) | Reconstrucción de promesas registradas |
| [`verificacion/`](verificacion/) | Verificaciones de soporte: dados pareados, modelo del jugador, auditoría del docx y utilidades de los decks anteriores |
| [`utilidades/`](utilidades/) | Scripts de una sola vez (búsquedas puntuales y renombrado de carpetas) |

## Scripts sueltos, por función

| Función | Scripts |
| --- | --- |
| **Crear y sembrar campañas** | `crear_campana_real.py` (G2), `crear_campana_real_g1.py` (G1), `sembrar_mundo_real.py`, `crear_sembrar_par07-17.py`, `crear_sembrar_par18-27.py`, `validar_fixtures_real.py` |
| **Generar y supervisar** | `supervisor.py` (relanza con `1400 − current_turn`), `lanzar_ola.ps1` (procesos desacoplados), `current_turn.py`, `vigilante.ps1`, `chequeo_rapido.ps1` |
| **Estado y reparación de campañas** | `estado_par01.py`, `estado_par02.py`, `estado_par04_05_06.py`, `estado_par07-17.py`, `listar_par01.py`, `barrer_stubs.py`, `diagnosticar_npc_duplicado.py`, `diagnosticar_siembra_doble.py`, `limpiar_siembra_doble.py`, `limpiar_turnos_corruptos.py`, `fusionar_personaje_duplicado.py`, `verificar_sesion1.py` |
| **Transcripciones y bitácoras** | `exportar_transcripcion.py`, `exportar_transcripcion_md.py`, `organizar_logs_par07-17.py`, `verificar_transcripciones.py` |
| **Validación humana externa** | `etiquetado_persona2.py`, `validacion_generar.py`, `validacion_brecha4_generar.py` (con sus formularios `.html`), `analizar_persona2.py`, `analizar_brecha4.py` |
| **Pruebas** | `test_analizar_persona2.py`, `test_dados_combate.py`, `test_reintentos.py`, `test_reloj_determinista.py` |
| **Otros** | `transcribir.py` (audio de reuniones con Whisper, en DeepInfra) |
