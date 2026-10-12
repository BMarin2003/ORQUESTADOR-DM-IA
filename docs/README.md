# docs

| Carpeta o archivo | Contenido |
| --- | --- |
| [`resultados/`](resultados/) | Resultados finales por campaña y por par (`por_campana_largo.csv`, `por_pareja_ancho.csv`) y `resultados_tesis.md` |
| [`reportes/`](reportes/) | Salidas de la medición y del análisis (ver su [README](reportes/README.md)) |
| `cierre_brechas.md` | Matriz de cierre de brechas por objetivo (la genera `scripts/reporte_v2/cierre_brechas.py`) |
| `avance_resultados.json` | Contador de avance que lee `scripts/reporte_v2/consolidar.py` |
| `ids_par01-06.json`, `ids_par07-17.json`, `ids_par18-27.json` | `campaign_id` de cada par y brazo; los usan los scripts de operación y de análisis |
| [`especificaciones/`](especificaciones/) | Descomposición de prompts G1↔G2, matriz rúbrica↔instrumentos y especificaciones de instrumentos |
| [`planificacion/`](planificacion/) | Plan de validación y plan A |
| [`bitacoras/`](bitacoras/) | Bitácora de operación de los pares 07–17 |
| [`literatura/`](literatura/) | Listas de papers y revistas |
| [`research/`](research/) | Notas de investigación para el diseño de instrumentos (segunda persona y agencia, sensibilidad y auditoría, respuesta a la acción) |
| [`guias/`](guias/) | Configuración del proveedor (DeepInfra) |
| [`sql/`](sql/) | Consultas de inspección y de humo |
| [`archivo/`](archivo/) | Prompts de DM descartados |

Los archivos sueltos de esta carpeta los leen o escriben scripts del pipeline en esta ruta, por eso no se mueven.
