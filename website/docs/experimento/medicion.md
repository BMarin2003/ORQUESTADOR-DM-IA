---
title: Medición y análisis
---

Toda la medición es **de solo lectura sobre la base** y no llama al modelo, de modo que se puede repetir sin coste ni efectos sobre las campañas.

## Instrumentos

| Instrumento | Mide | Código |
| --- | --- | --- |
| Respuesta a la acción (z) | Cuánto responde la narración a la acción del jugador | [`respuesta_accion.py`](../referencia/scripts/instrumentos/respuesta_accion.md) |
| Anclaje al escenario | Persistencia del lore del escenario en el texto | [`anclaje_escenario.py`](../referencia/scripts/instrumentos/anclaje_escenario.md) |
| persona2 | Usurpación de la agencia del jugador | [`persona2.py`](../referencia/scripts/instrumentos/persona2.md) |
| Validación por campaña | Coherencia, consistencia de atributos, gramaticalidad | [`reporte_validacion.py`](../referencia/orquestador/reporte_validacion.md) |
| Semántico (exploratorio) | Recall con embeddings bge-m3 | `scripts/semantico/` |

Cada instrumento se valida con **pruebas de sensibilidad por perturbación** (`scripts/sensibilidad/`), con expectativas selladas con SHA-256 antes de correr, y, donde interpreta texto, con evaluadores humanos externos (`validacion/`).

## Flujo de análisis

1. `recalcular*.py` produce las mediciones por turno, por detector booleano, por persona2 y por campaña (`datos_v2/`).
2. `page_test.py` evalúa la degradación de G2 (H1a–H1c).
3. `consolidar.py` compara G1 vs G2 con bootstrap (H1d–H1f).
4. `resultados_tesis.py` y `cierre_brechas.py` arman el paquete de resultados por objetivo.

Los comandos exactos están en [Réplica del experimento](replica.md#7-medir-y-analizar-sin-llm-solo-lectura).
