# docs/reportes

Salidas de la medición y del análisis. Los archivos sueltos de esta carpeta los **escriben o leen los scripts del pipeline** en esta ruta exacta, así que no se mueven. Abajo, cada uno con el script que lo produce.

## Carpetas

| Carpeta | Contenido |
| --- | --- |
| [`brechas/`](brechas/) | Cierres de brecha por objetivo: auditoría de nombres (OE-1), descomposición de CR-2 (OE-4), costo por arquitectura, sonda de persona2, pares 01–06 |
| [`compromisos/`](compromisos/) | Promesas registradas como cambios de estado (`eventos_compromiso.csv`) |
| [`degradacion/`](degradacion/) | Análisis exploratorio del último bloque (turnos 1,301–1,400) y mecanismo por bloque |
| [`semantico/`](semantico/) | Instrumento semántico exploratorio (bge-m3), v1 y v2 |
| [`validacion_humana/`](validacion_humana/) | Acuerdo de los evaluadores externos sobre persona2 |
| [`validacion_por_campana/`](validacion_por_campana/) | Salida de `orquestador/reporte_validacion.py` para cada campaña de los pares 07–27 |
| [`integridad_transcripciones/`](integridad_transcripciones/) | Cruce de integridad de las transcripciones (pares 07–17 y 18–27) |
| [`verificacion_dados/`](verificacion_dados/) | Coincidencia de tiradas entre brazos (`scripts/verificacion/verificar_dados_pareados.py`) |

## Archivos del pipeline (en la raíz de esta carpeta)

| Grupo | Archivos | Script |
| --- | --- | --- |
| **Consolidado G1 vs G2** | `consolidado_v2.csv`, `consolidado_v2.md` | `scripts/reporte_v2/consolidar.py` |
| | `reporte_v2_formato_normalizado.md`, `reporte_v2_booleanos.md` | `scripts/reporte_v2/consolidar.py`, `recalcular_booleanos.py` |
| | `auditoria_tags_rechazados.md` | `scripts/reporte_v2/auditoria_tags_rechazados.py` |
| **Degradación (H1a–H1c)** | `degradacion_bloques.md` | `scripts/reporte_v2/page_test.py` |
| **Supervivencia** | `kaplan_meier_pnj.csv`, `.md`, `.png` | `scripts/reporte_v2/kaplan_meier_pnj.py` |
| **persona2** | `persona2_equivalencia.md` | `scripts/sensibilidad/correr_persona2.py` |
| **Sensibilidad por perturbación** | `sensibilidad_baseline.csv`, `.md` | `scripts/sensibilidad/perturbaciones.py` |
| | `sensibilidad_a4bc*.csv`, `.md` | `scripts/instrumentos/correr_a4bc.py`, `matriz_a4bc_v2.py` |
| | `sensibilidad_a4bc_distribucion_27.csv` (respuesta a la acción por bloque) | `scripts/instrumentos/distribucion_a4bc_27.py` |
| | `sensibilidad_ext_sz_mtld*` | `scripts/sensibilidad/correr_extension_sz_mtld.py` |
| | `sensibilidad_jericho_relojes*` | `scripts/sensibilidad/correr_jericho_relojes.py`, `diagnostico_jericho_relojes.py` |

Los `*_expectativas.json` son las expectativas selladas (SHA-256) antes de correr cada prueba de sensibilidad.
