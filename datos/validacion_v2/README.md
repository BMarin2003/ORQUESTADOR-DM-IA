# Validación humana v2 de los instrumentos

Etiquetado ciego por 5 directores de juego (en la tesis: E1–E5 = códigos de formulario E5–E9) de 982 ítems en cuatro preguntas: A, persona2; B, PNJ inactivo; C, Jericho-QA; D, respuesta a la acción.

## Dónde está cada cosa

| Qué | Archivos |
|---|---|
| **Protocolo** (congelado antes del etiquetado) | `libro_de_codigos_v2.md`, `congelamiento_v2.sha256`, `Consentimiento_informado_evaluadores.docx` (modelo) |
| **Muestra y controles** | `generar_muestra.py`, `pool_pnj.py`, `ampliar_cd.py`, `ajustar_cd.py`, `candidatos_control*.py/.md/.json`, `fijar_controles*.py`, `clave.csv`, `clave_cd.csv`, `controles_clave.csv`, `items*.json`, `poblaciones.py/.json` |
| **Formularios** | `plantilla_formulario.html`, `construir_formulario.py` → `formulario_v2.html` (ronda 1). Ronda A2 (pregunta A con práctica guiada): `plantilla_A2.html`, `construir_formulario_A2.py` → `formulario_A2.html`, `formulario_A2.sha256` |
| **Respuestas válidas** | `respuestas/etiquetas_v2_E5…E9.csv` (el archivo de E6 se rotuló «E3» al enviarse), `respuestas/auditoria_afinidad_respuestas.csv` |
| **Respuestas descartadas** (evidencia de integridad) | `respuestas/descartados/` (ver su `LEEME.md`) |
| **Análisis** | `consolidar_validacion.py` → `resultados_validacion_v2.md/.json`, `anexo_respuestas_v2.csv`. Auditoría de afinidad: `auditoria_afinidad.py/.html`, `auditoria_afinidad_clave.csv` |
| **persona2 v3b** | `tablas_qn2_v3b.py`, `tabla_OE3-9_v3b.csv`, `tabla_OE6-4_5_v3b.csv`. Detector: `../../experimento/scripts/reporte_v2/recalcular_persona2_v3b.py`, datos en `../datos_v2/persona2_v3b/` |
| **Pregunta A: desarrollo y prueba** | `particion_persona2.csv/.sha256` (congelada en el commit b0bba84, antes de cualquier ajuste), `candidatos_control_A2.*` |
| **Textos para el documento** | `entregables_documento/QN2_v3b_para_documento.md`, `entregables_documento/cambios_documento_validacion_v2.md`, `entregables_documento/prompt_correcciones_tesis.md` |
| **Privado (no se publica)** | `privado_no_publicar/` contiene los consentimientos firmados con nombre, documento de identidad y correo. Está excluido de git. |
| **Trabajo intermedio** | `_trabajo/`: verificaciones y bitácoras que no forman parte del resultado |

## Cómo reproducir

```
PYTHONUTF8=1 py datos/validacion_v2/consolidar_validacion.py
PYTHONUTF8=1 py datos/validacion_v2/tablas_qn2_v3b.py
```

**Scripts congelados y reorganización del repositorio.** Esta carpeta estaba en `validacion_v2/` (raíz) y se movió a `datos/validacion_v2/`. Los archivos listados en `congelamiento_v2.sha256` se dejaron **sin modificar** para no invalidar sus hashes, así que conservan las rutas del layout anterior (`scripts/`, `datos_v2/`, `orquestador/`). Para volver a ejecutar la cadena de muestra y formularios (`generar_muestra.py`, `pool_pnj.py`, `ampliar_cd.py`, `poblaciones.py --c`, `auditoria_afinidad.py`, `candidatos_control*.py`; requieren la base `dmia_db`), usar el commit `b7ac5b1`, el último antes de la reorganización:

```
git worktree add ../dmia-b7ac5b1 b7ac5b1
cd ../dmia-b7ac5b1 && PYTHONUTF8=1 py validacion_v2/poblaciones.py --c
```

Las rutas de `congelamiento_v2.sha256` también son las del layout anterior: `validacion_v2/` → `datos/validacion_v2/`, `scripts/` → `experimento/scripts/`, `orquestador/` → `motor/orquestador/`. Algunos archivos de `experimento/scripts/` y `motor/` listados al final del manifiesto sí cambiaron después del congelamiento (solo docstrings y rutas, sin cambios de lógica): ver [`../validacion/congelados_cambios_posteriores.md`](../validacion/congelados_cambios_posteriores.md).
