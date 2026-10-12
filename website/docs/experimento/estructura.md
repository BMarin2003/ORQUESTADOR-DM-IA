---
title: Estructura del repositorio
---

| Bloque | Carpeta | Contenido |
| --- | --- | --- |
| **Sistema** | `orquestador/` `dm/` `jugador/` `extractor/` `migrations/` `entorno/` | Motor DM-IA |
| | `docker-compose.yml` `pgadmin-servers.json` `.env.example` | Base local y configuración |
| **Experimento** | `corpus/` | Lore de cada escenario (`pilotos/` y `real/`) |
| | `fixtures/` | Mundo y PNJ de cada escenario, con su validador |
| | `scripts/` | Operación, medición y análisis |
| | `sondeos/` | Pruebas previas del proveedor |
| **Datos** | `logs/` `transcripciones/` `datos_v2/` `validacion/` | Bitácoras, transcripciones, mediciones y validación humana |
| **Resultados** | `docs/` | Resultados, reportes, especificaciones e IDs |
| **Tesis** | `tesis/` `sustentacion/` `entregas/` | Documento, deck y paquetes al asesor |
| **Sitio** | `website/` | Esta documentación (Docusaurus) |
