# Prueba A2 de CL-2 recall semántico

SHA-256 de las expectativas (fijadas antes de correr): `d74ec82fc0a5a3874d62353d9f27fe904354899ad99db4546eec87ddaf2e8a45`  ·  semilla 20261008  ·  n por perturbación 40

| Perturbación | Esperado | n | Mdn Δ margen [IC 95 %] | δ Cliff pareado | p signos | p Holm | Observado | Veredicto | 0→1 | 1→0 |
|---|---|---|---|---|---|---|---|---|---|---|
| SQ1 parafrasis sin lexema | sube | 40 | +0.2006 [+0.1649, +0.2160] | +1.00 | 1.819e-12 | 3.638e-12 | sube | **responde** | 39 | 0 |
| SQ2 texto ajeno | baja | 40 | -0.1348 [-0.1517, -0.1117] | -1.00 | 1.819e-12 | 3.638e-12 | baja | **responde** | 0 | 38 |
| SC1 oracion neutra | sin_cambio | 40 | +0.0000 [+0.0000, +0.0000] | +0.00 | 1 | 1 | sin_cambio | **responde** | 0 | 0 |
| SC2 nombre sin cambio | sin_cambio | 40 | +0.0155 [+0.0000, +0.0276] | +0.62 | 5.96e-08 | 1.192e-07 | sube | **cambio inesperado** | 8 | 0 |

Jericho-QA con la misma paráfrasis de SQ1: cambia su veredicto en 0 de 40 eventos (por construcción la paráfrasis no contiene sus lexemas).

**Lectura:** al menos una perturbación no respondió como se esperaba (ver tabla): el instrumento no es informativo en ese aspecto y se reporta como tal.

Clasificación en esta tesis: EXPLORATORIO en cualquier caso (la clasificación de instrumentos se fijó antes del contraste de hipótesis). El resultado de esta prueba orienta la recomendación para un estudio futuro.
