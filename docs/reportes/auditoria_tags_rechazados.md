# Auditoría de tags de habilidad rechazados (28/09)

Generado por `scripts/reporte_v2/auditoria_tags_rechazados.py`. Cuenta, sobre el texto real de `player_buffer`, cuántas habilidades declaradas entre `{llaves}` `dados.resolver_turno` acepta (tira) vs. rechaza (no tira -- ver `dados.VALIDAS`/`CARACTERISTICAS_NORM`). Mismo código para G1 y G2.

## Resumen por brazo

| brazo | turnos con >=1 tag | tags declarados | tags aceptados | tags rechazados | % rechazados | errores |
|---|---|---|---|---|---|---|
| G1 | 37343 | 38047 | 37853 | 194 | 0.5% | 0 |
| G2 | 37271 | 38599 | 38435 | 164 | 0.4% | 0 |

## Textos rechazados más frecuentes

| texto declarado (rechazado) | veces |
|---|---|
| `Exploración` | 71 |
| `Performance` | 23 |
| `Tecnología` | 14 |
| `Uso de Herramientas de Manos` | 13 |
| `Actuación` | 11 |
| `Herramientas de Ladrón` | 9 |
| `Memoria` | 8 |
| `Combate` | 8 |
| `Agilidad` | 6 |
| `Ingeniería` | 6 |
| `Empatía` | 6 |
| `Búsqueda` | 5 |
| `Ingenio` | 5 |
| `Golpe con arma` | 4 |
| `Invocación divina` | 4 |
| `Informática` | 4 |
| `Percepción e Investigación` | 3 |
| `Determinación` | 3 |
| `Habilidad` | 3 |
| `Destreza con Objetos` | 2 |
| `Oración de Fuerza` | 2 |
| `Valentía` | 2 |
| `Invocación a la Protección Divina` | 2 |
| `Liderazgo` | 2 |
| `Herramientas de ladrón` | 2 |
| `pensamiento` | 2 |
| `Pensamiento rápido` | 2 |
| `Inteligencia Investigación` | 2 |
| `Invocación Divina` | 2 |
| `Defensa` | 2 |
| `Curación` | 2 |
| `Manos ligeras` | 2 |
| `Tiro con Arco` | 2 |
| `Hechizar` | 2 |
| `Desempeño` | 2 |
| `Descarga Sobrenatural` | 2 |
| `Persuación` | 2 |
| `Adiestramiento con Armas` | 1 |
| `Tacto` | 1 |
| `Percepción del callejón` | 1 |

Detalle completo (brazo, par, turno, texto) en `datos_v2/cierre/tags_rechazados.csv`.