---
slug: /
sidebar_position: 1
title: Introducción
---

# DM-IA · Coherencia narrativa: sistema multiagente vs. monolítico

Tesis de Ingeniería de Sistemas e Inteligencia Artificial (UPAO, 2026).
Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David. Asesor: Dr. Cueva Chávez, Walter Manuel.

**Pregunta.** ¿Es superior la coherencia narrativa de las campañas de Dungeons & Dragons generadas por un sistema multiagente (G1) frente a uno monolítico (G2)?

**Diseño.** Experimental de medidas repetidas con pares emparejados: 27 escenarios, cada uno con G1 y G2, de 1,400 turnos por campaña (54 campañas, 75,600 turnos). Ambos brazos usan el mismo modelo (`google/gemma-4-31B-it`, DeepInfra) y la misma memoria estructurada en PostgreSQL.

**Resultado.** La hipótesis general no se sostiene. La única ventaja de G1 está en el respeto a la agencia del jugador: 0.17 % frente a 3.47 % de turnos con usurpación.

## Dónde seguir

- [Arquitectura](sistema/arquitectura.md): ciclo del turno, G1 y G2, memoria estructurada.
- [Réplica del experimento](experimento/replica.md): comandos paso a paso.
- [Medición](experimento/medicion.md): instrumentos y flujo de análisis.
- [Referencia de código](/referencia): generada desde los docstrings.
