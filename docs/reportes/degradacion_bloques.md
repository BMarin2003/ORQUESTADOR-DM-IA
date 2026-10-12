# Prueba de tendencia de Page (1963) para H1a-H1c -- degradacion por bloques de 200 turnos

Generado por `scripts/reporte_v2/page_test.py`. Fuente: `docs/reportes/sensibilidad_a4bc_distribucion_27.csv` (CR-2a por bloque, ya calculado el 2026-09-21), `datos_v2/cierre/bloques.csv` (CL/MATTR/persona2 por bloque) y, cuando ya existe, `datos_v2/cierre/pnj_inactivo_relativizado.csv` (generado por `scripts/reporte_v2/relativizar_pnj_inactivo.py`, que sí necesita acceso a la base de datos -- solo SELECT sobre `npcs`/`state_deltas`, sin LLM). H0 = 'no disminuye/no aumenta' (no arbitraria); H1 = degradacion monotona a lo largo de la campana G2 (7 bloques de 200 turnos, n=27). Prueba de Page unilateral + Wilcoxon exacto bloque1-vs-bloque7 como complemento.

**Autoverificacion antes de correr sobre datos reales**: caso de juguete perfectamente degradante -> p~0; calibracion bajo H0 (3000 simulaciones, n=27 k=7) -> ~5% de p<0.05 (formula y signo confirmados, no solo revisados a ojo).

## Resultado

| Hipotesis / instrumento | direccion H1 | n | Page z | Page p (unilateral) | Wilcoxon p (bloque1 vs 7) | mediana bloque1 -> bloque7 |
|---|---|---|---|---|---|---|
| H1a -- CR-2a(z), confirmatorio | decrece | 27 | 0.50 | 0.3097 | 0.4204 | 2.768 -> 2.742 |
| H1b -- PNJ inactivo mencionado, CRUDO (sin relativizar; confundido, ver Lectura) | crece | 27 | 1.81 | 0.0352 | 0.0127 | 0.000 -> 0.000 |
| H1b -- PNJ inactivo mencionado, RELATIVIZADO (denominador = turnos con >=1 PNJ ya inactivo) | crece | 10 | 0.12 | 0.4505 | 0.5000 | 0.000 -> 0.000 |
| H1c -- MATTR, exploratorio | decrece | 27 | -0.18 | 0.5702 | 0.5252 | 0.828 -> 0.828 |
| H1c -- persona2 primaria, condicionado a auditoria | crece | 27 | 1.35 | 0.0890 | 0.0665 | 0.030 -> 0.035 |

`cl2_lugar_jaccard_similarity` no tiene direccion 'mejor' definida en la ficha (`consolidar.py`: '·', bilateral) -- reportado aparte: p(disminuye)=0.9812, p(aumenta)=0.0196, bilateral=0.0392 (sube significativamente -- lectura ambigua: mas continuidad lexica con la escena anterior, o mas repeticion/estancamiento; la propia ficha ya advierte que este instrumento 'no distingue deriva de evolucion legitima del mundo').

**Holm dentro de H1c** (mattr + persona2_primaria): H1c_mattr p_holm=0.5702, H1c_persona2_primaria p_holm=0.1780

## Lectura

Con los datos reales, **4 de 5 instrumentos NO muestran degradacion significativa** (mas `cl2_lugar_jaccard`, que no tiene direccion definida). El resultado crudo de `cl2_pnj_inactivo_actua` (sin relativizar) es justamente el indicador que la propia propuesta señalaba como el mas expuesto a un confusor: mas PNJ estan muertos/desaparecidos hacia el final de la campana, asi que la tasa de turnos que los narra como activos puede subir solo porque hay mas PNJ inactivos elegibles para el error, no porque el sistema degrade.

**Version relativizada** (resuelve el pendiente #1 de la version anterior de este informe -- ver `scripts/reporte_v2/relativizar_pnj_inactivo.py` y `datos_v2/cierre/pnj_inactivo_relativizado.csv`): denominador = turnos del bloque donde ya habia al menos un PNJ inactivo visible (reconstruido turno a turno desde `npcs`/`state_deltas`, la misma logica que usa el motor para `estados_pnj`), en vez de los 200 turnos del bloque. Resultado: Page z=0.12 p=0.4505 (Wilcoxon bloque1-vs-7 p=0.5000; mediana 0.000 -> 0.000; n=10 campanas completas, 12 excluidas por tener algun bloque sin ningun PNJ inactivo todavia -- tipicamente el bloque 1). La significancia desaparece al relativizar por PNJ ya inactivos: consistente con que el resultado crudo era el confusor sospechado, no degradacion real de la coherencia.

`persona2_primaria` (p=0.0890 sin corregir, p_holm=0.1780) sugiere en el mejor de los casos una tendencia leve, y de todas formas sigue pendiente de una auditoria de precision con un evaluador EXTERNO (no el equipo investigador -- ver correccion en `claude/persona2-auditoria-IA-analisis.md`) para poder tratarse como confirmatorio.

**Conclusion honesta para el asesor**: la redefinicion de H1a-H1c como hipotesis de degradacion es tecnicamente solida (formula verificada, reutiliza instrumentos ya validados, resuelve el problema real del punto medio de Likert que ya estaba documentado en `resultados_tesis.py`), pero los datos, hasta ahora, no confirman de forma robusta la premisa de degradacion que motivo la propuesta. Es un hallazgo legitimo en si mismo (la nula 'no degrada' se sostiene en la mayoria de los instrumentos, con una H0 no arbitraria como pedia el diseño), pero cambia la narrativa: no es 'confirmamos que el sistema monolitico degrada', es 'probamos rigurosamente si degrada y, con esta instrumentacion, la evidencia es limitada'.

## Pendiente antes de escribir el capitulo 6 con esto

1. Version relativizada de `cl2_pnj_inactivo_actua`: **hecho** (ver arriba). Revisar con el asesor si la lectura (confusor confirmado o degradacion real) es la que se reporta en el capitulo 6.
2. Cerrar la auditoria de precision de persona2 con un evaluador EXTERNO al equipo investigador (Brecha 3) antes de tratar `persona2_primaria` como confirmatorio.
3. Decidir con el asesor si `cl2_lugar_jaccard_similarity` entra a H1b con una direccion 'mejor' definida, o se deja fuera del contraste inferencial y solo se describe.
4. Confirmar la regla de decision de la hipotesis general (si H1a-c entran a la misma regla 'solo se sostiene si a,b,c,d,e,f se sostienen' junto con H1d-f, y si Holm debe correr sobre esas 6 juntas en vez de por hipotesis separada, que es como esta hoy).