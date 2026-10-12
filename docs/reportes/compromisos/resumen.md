# Eventos de compromiso reconstruidos desde los logs

Solo lectura. Exploratorio: no decide ninguna hipótesis.

## Auditoría de la reconstrucción

- Eventos de compromiso vistos en los logs (con duplicados de reanudaciones): {'promise_made': 580, 'promise_kept': 2, 'promise_broken': 2}
- Eventos sin delta de afinidad emparejado: {'promise_made': 171, 'promise_kept': 2, 'promise_broken': 2}
- Eventos únicos recuperados en las 54 campañas (turnos 1-1400): 259
- Filas donde el PNJ del log no coincide con el de la base: 0

## Totales por brazo

| Evento | G1 | G2 |
|---|---|---|
| promise_broken | 0 | 0 |
| promise_kept | 0 | 0 |
| promise_made | 103 | 156 |

## promise_made por par

| Par | G1 | G2 |
|---|---|---|
| 01 | 2 | 6 |
| 02 | 3 | 81 |
| 03 | 4 | 20 |
| 04 | 0 | 1 |
| 05 | 2 | 0 |
| 06 | 0 | 0 |
| 07 | 0 | 0 |
| 08 | 0 | 0 |
| 09 | 42 | 8 |
| 10 | 0 | 0 |
| 11 | 2 | 16 |
| 12 | 2 | 0 |
| 13 | 0 | 0 |
| 14 | 4 | 1 |
| 15 | 21 | 17 |
| 16 | 0 | 1 |
| 17 | 1 | 0 |
| 18 | 0 | 1 |
| 19 | 0 | 0 |
| 20 | 1 | 0 |
| 21 | 0 | 1 |
| 22 | 0 | 0 |
| 23 | 0 | 0 |
| 24 | 1 | 3 |
| 25 | 0 | 0 |
| 26 | 18 | 0 |
| 27 | 0 | 0 |

Wilcoxon pareado (promise_made, G1 vs G2): W = 75.5, p = 0.9620. Descriptivo.
