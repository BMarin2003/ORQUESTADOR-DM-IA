# Spec: cl2_recall_semantico_v2 (nulo condicionado por mención)

Fecha: 2026-10-09 · Clasificación: EXPLORATORIO (posterior al contraste de hipótesis; no decide H1e).

## Motivo

La A2 de la v1 falló en SC2: una oración que solo nombra a la entidad encendía el reconocimiento.
Es el sesgo documentado de los sentence transformers: la similitud la dominan los participantes
nominales compartidos (Nikolaev y Padó, EACL 2023). La v1 comparaba la ventana del evento contra
cualquier ventana de la campaña, y la mayoría no nombra a la entidad.

## Cambio (único)

Solo cuentan las oraciones que mencionan a la entidad, en la ventana real y en el nulo. La decisión
pasa a comparar «mención + cambio» contra «solo mención». Todo lo demás es la v1 sin tocar
(`comun.py`): mismos 790 eventos, mismas consultas, ventana [t, t+1], exclusión de ±5 turnos,
percentil 95, búsqueda exacta en pgvector, solo lectura.

- Ventana real sin mención: no reconocido.
- Evento evaluable solo si el nulo condicionado tiene al menos 20 ventanas.
- Regla de alias: palabras del nombre con mayúscula, de 4 letras o más, sin artículos; si no hay
  ninguna, la frase completa. Misiones: título completo. Texto normalizado sin tildes; palabra completa.

## A2 v2 (sellada antes de correr)

Criterio: decisión (reconocido sí/no), McNemar exacta, Holm por familia. El margen no sirve para
juzgar SC2: condicionar el nulo no cambia cuánto sube la similitud real, solo el umbral que debe cruzar.

| Perturbación | Muestra | Esperado |
|---|---|---|
| SQ1 paráfrasis sin lexema | eventos no reconocidos | se_dispara |
| SQ2 ventana ajena | eventos reconocidos | baja |
| SC1 oración neutra | cualquier evento | sin_cambio |
| SC2 nombre sin cambio | cualquier evento | sin_cambio |

n = 40 por perturbación · semilla 20261009 · mismas oraciones de perturbación que la v1.

SHA-256 de expectativas y parámetros: `5af1c4ea8d677ba32a3fdd78f2383c58f4bec7c062e5d70ac72ac5327a828373`

Comparación descriptiva: en SC1 y SC2 se calcula también la decisión de la v1 con la misma inserción.

## Archivos

- `experimento/scripts/semantico/condicionado.py`: alias, SQL condicionado, decisión v2.
- `experimento/scripts/semantico/sensibilidad_semantico_v2.py`: A2 v2.
- Salida: `docs/reportes/semantico/sensibilidad_semantico_v2.{md,csv,json}`.

## Lectura fijada de antemano

- Si las cuatro responden: el nulo condicionado corrige el sesgo de mención; la v2 reemplaza a la v1
  como instrumento exploratorio de CL-2.
- Si SC2 vuelve a fallar: el sesgo no es solo de mención y el instrumento semántico queda descartado
  para estado; la recomendación pasa a NLI multilingüe.
- Si SQ1 no responde: el condicionamiento quitó sensibilidad; se reporta como límite.
