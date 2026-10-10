# Prueba A2 de cl2_recall_semantico_v2 (nulo condicionado por mención)

SHA-256 de expectativas y parámetros (fijados antes de correr): `5af1c4ea8d677ba32a3fdd78f2383c58f4bec7c062e5d70ac72ac5327a828373`  ·  semilla 20261009  ·  n por perturbación 40  ·  eventos evaluables por la v2: 631

Criterio: decisión (reconocido sí/no), McNemar exacta sobre pares discordantes, Holm por familia.

| Perturbación | Esperado | n | 0→1 | 1→0 | p | p Holm | Observado | Veredicto | Mdn Δ margen (secundario) |
|---|---|---|---|---|---|---|---|---|---|
| SQ1 parafrasis sin lexema | se_dispara | 40 | 38 | 0 | 7.276e-12 | 7.276e-12 | se_dispara | **responde** | +0.1739 (n=33) |
| SQ2 texto ajeno | baja | 40 | 0 | 40 | 1.819e-12 | 3.638e-12 | baja | **responde** | -0.1995 (n=4) |
| SC1 oracion neutra | sin_cambio | 40 | 0 | 0 | 1 | 1 | sin_cambio | **responde** | +0.0000 (n=35) |
| SC2 nombre sin cambio | sin_cambio | 40 | 4 | 0 | 0.125 | 0.25 | sin_cambio | **responde** | +0.0060 (n=35) |

## La misma inserción, decidida por la v1 (sin condicionar)

| Control | n | 0→1 | 1→0 | p | Observado v1 |
|---|---|---|---|---|---|
| SC1 | 40 | 0 | 0 | 1 | sin_cambio |
| SC2 | 40 | 7 | 0 | 0.01562 | se_dispara |

**Lectura:** las cuatro perturbaciones responden como se esperaba.

Clasificación: EXPLORATORIO en cualquier caso (instrumento posterior al contraste de hipótesis).
