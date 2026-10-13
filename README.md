# DM-IA · Coherencia narrativa: sistema multiagente vs. monolítico

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)
![Modelo](https://img.shields.io/badge/modelo-gemma--4--31B--it-8E75B2)
![Corpus](https://img.shields.io/badge/corpus-75%2C600%20turnos-0F8B8D)
![Estado](https://img.shields.io/badge/estado-corpus%20y%20resultados%20cerrados-success)

Tesis de Ingeniería de Sistemas e Inteligencia Artificial (UPAO, 2026).
Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David. Asesor: Dr. Cueva Chávez, Walter Manuel.

**Pregunta:** ¿es superior la coherencia narrativa de las campañas de Dungeons & Dragons generadas por un sistema multiagente (G1) frente a uno monolítico (G2)?

**Diseño:** experimental de medidas repetidas con pares emparejados. Son 27 escenarios, cada uno generado con G1 y con G2, de 1,400 turnos por campaña: 54 campañas y 75,600 turnos. Ambos brazos usan el mismo modelo (`google/gemma-4-31B-it`, DeepInfra) y la misma memoria estructurada en PostgreSQL.

**Resultado:** la hipótesis general no se sostiene. La única ventaja de G1 está en el respeto a la agencia del jugador: 0.17 % frente a 3.47 % de turnos con usurpación.

---

## Arquitectura

```mermaid
flowchart LR
    DB[(PostgreSQL 16<br/>estado del mundo)] --> CTX[Contexto de la escena<br/>consultas SQL exactas<br/>+ última escena]
    CTX --> J[Agente jugador<br/>acción + habilidad]
    J --> D[Dados deterministas<br/>d20 + modificador]
    D --> G1
    D --> G2
    subgraph G1 [G1 · multiagente]
        R[Enrutador<br/>código] --> A[Árbitro<br/>código + modelo] --> P[Actor de PNJ<br/>modelo] --> M[Mundo<br/>código + modelo] --> N[Narrador<br/>modelo]
    end
    subgraph G2 [G2 · monolítico]
        DM[Director de juego<br/>una sola llamada]
    end
    N --> V[Verificación<br/>de la narración]
    DM --> V
    V --> X[Extractor de cambios<br/>lista cerrada + cita literal]
    X -->|apply_delta valida y escribe| DB
```

- **Ciclo del turno común:** estado → contexto → jugador → dados → narración → verificación → extractor → estado. Lo único que cambia entre brazos es quién produce la narración.
- **Memoria estructurada común:** el mundo vive en la base, no en el modelo. Ningún LLM escribe en ella: el extractor propone cambios con una cita literal del turno y `apply_delta()` los valida contra una lista blanca de 19 campos. Las magnitudes las fija una tabla según la personalidad del PNJ.
- **Medición:** instrumentos deterministas (solo `SELECT`, sin LLM), validados con pruebas de perturbación y, donde interpretan texto, con evaluadores humanos externos. pgvector (bge-m3) se usó solo después, como capa de medición exploratoria; no interviene en la generación.

| Componente | Dónde |
| --- | --- |
| Turno G2 (monolítico) | [`motor/orquestador/vertical_slice.py`](motor/orquestador/vertical_slice.py) |
| Turno G1 (multiagente) | [`motor/orquestador/vertical_slice_g1.py`](motor/orquestador/vertical_slice_g1.py) con [`router.py`](motor/orquestador/router.py), [`arbitro.py`](motor/orquestador/arbitro.py) y [`mundo.py`](motor/orquestador/mundo.py) |
| Acceso al estado y escritura validada | [`motor/orquestador/db.py`](motor/orquestador/db.py) y [`motor/migrations/001_schema.sql`](motor/migrations/001_schema.sql) |
| Prompts del DM y de los roles de G1 | [`motor/dm/`](motor/dm/) |
| Agente jugador, dados y 27 personajes | [`motor/jugador/`](motor/jugador/) |
| Extractor (contrato y prompts) | [`motor/extractor/`](motor/extractor/) |
| Huella del modelo | [`motor/entorno/`](motor/entorno/) |
| Reporte de validación por campaña | [`motor/orquestador/reporte_validacion.py`](motor/orquestador/reporte_validacion.py) |

## Estructura del repositorio

| Carpeta | Contenido |
| --- | --- |
| [`motor/`](motor/) | Sistema DM-IA: `orquestador/`, `dm/`, `jugador/`, `extractor/`, `migrations/` y `entorno/` (tabla de arriba) |
| [`experimento/`](experimento/) | `corpus/` (lore de cada escenario), `fixtures/` (mundo y PNJ, con su validador) y `scripts/` (operación, medición y análisis; ver [`experimento/scripts/README.md`](experimento/scripts/README.md)) |
| [`datos/`](datos/) | `logs/` (bitácoras por par y del supervisor), `transcripciones/` (pares 02–06, 07–17 y 18–27), `datos_v2/` (mediciones por turno, bloque y campaña) y `validacion/` (validación humana externa) |
| [`docs/`](docs/) | Resultados, reportes, especificaciones e IDs (ver [`docs/README.md`](docs/README.md)) |
| [`tesis/`](tesis/) | Documento vigente (`TESIS2.docx.md`), figuras, audio de asesoría y `sustentacion/` (deck oficial UPAO, generador y guiones) |
| [`website/`](website/) | Documentación en Docusaurus; la referencia de código se genera desde los docstrings |
| [`legacy/`](legacy/) | Material que ya no se usa para reproducir: pilotos, sondeos, entregas, decks y scripts de operación de pares cerrados (ver su [README](legacy/README.md)) |

En la raíz quedan `docker-compose.yml`, `pgadmin-servers.json` y `.env.example` (base de datos local y configuración).

## Documentación

El código está documentado con docstrings en español (estilo Google) en el motor (`motor/orquestador/`, `motor/jugador/`, `motor/entorno/`, `experimento/fixtures/`) y en la medición (`experimento/scripts/instrumentos`, `reporte_v2`, `sensibilidad`, `semantico`, `brechas`). El sitio con arquitectura, réplica y referencia de módulos está en [`website/`](website/):

```powershell
cd website
npm install
npm start        # http://localhost:3000/ORQUESTADOR-DM-IA/
```

La referencia de API se regenera sola con `py experimento/scripts/documentacion/generar_referencia_api.py`.

---

## Replicar el experimento

Todos los comandos se ejecutan **desde la raíz del repositorio**: las rutas de los scripts son relativas a ella. En Windows, conviene fijar `$env:PYTHONUTF8="1"` en la sesión.

### 1. Requisitos

- Docker (PostgreSQL 16 con pgvector y pgAdmin).
- Python 3.12 o superior.
- Java 8 o superior, solo para la gramaticalidad con LanguageTool (CR-1); sin Java, esa sección se omite sola.
- Una clave de [DeepInfra](https://deepinfra.com) (ver [`docs/guias/SETUP_DEEPINFRA.md`](docs/guias/SETUP_DEEPINFRA.md)).

### 2. Configurar y levantar la base

```powershell
copy .env.example .env          # completar DEEPINFRA_API_KEY, DMIA_MODELO, POSTGRES_PASSWORD, DATABASE_URL
docker compose up -d            # dmia_db (puerto 5432) y dmia_pgadmin (http://localhost:5050)
```

Al crearse el volumen por primera vez, PostgreSQL aplica [`motor/migrations/`](motor/migrations/) (esquema completo y tabla de medición semántica).

### 3. Dependencias de Python

```powershell
py -m pip install -r motor/orquestador/requisitos.txt numpy scipy pytest
py -m spacy download es_core_news_sm
py -m pip install sentence-transformers huggingface_hub   # solo para el instrumento semántico exploratorio
```

### 4. Verificar el modelo (antes de cada tanda)

```powershell
py motor/entorno/verificar_modelo.py --modelo $env:DMIA_MODELO --comparar motor/entorno/manifiesto_2026-08-28.json
```

Compara la huella de tres prompts fijos a temperatura 0 y sale con código 2 si el proveedor cambió el artefacto. El experimento usa un solo proveedor y ningún enrutador.

### 5. Crear y sembrar las campañas

```powershell
py experimento/scripts/validar_fixtures_real.py 18 19 20                 # valida mundo y PNJ de cada par
py experimento/scripts/crear_sembrar_par18-27.py 18 19 20                # crea G2 y G1 sobre el mismo tenant y siembra ambos mundos
```

Los `campaign_id` se guardan en `docs/ids_par18-27.json` (los pares 07–17 usan `crear_sembrar_par07-17.py` y `docs/ids_par07-17.json`).

### 6. Generar los 1,400 turnos

```powershell
py -u experimento/scripts/supervisor.py --arm ambos --pares 18,19,20 --ids docs/ids_par18-27.json --log datos/logs/supervisor_par18-27.log
```

El supervisor mantiene un proceso por campaña y relanza los caídos con `1400 − current_turn`. También se puede generar una campaña a mano:

```powershell
py motor/orquestador/vertical_slice.py    --campaign-id <UUID-G2> --pj PJ27 --turnos 1400
py motor/orquestador/vertical_slice_g1.py --campaign-id <UUID-G1> --pj PJ27 --turnos 1400
```

Con `--seco`, el turno se ejecuta sin escribir en la base.

### 7. Medir y analizar (sin LLM, solo lectura)

```powershell
py motor/orquestador/reporte_validacion.py --campaign-id <UUID>         # reporte de validación de una campaña
py experimento/scripts/reporte_v2/recalcular.py                                # instrumentos por turno     -> datos/datos_v2/par*_G?.csv
py experimento/scripts/reporte_v2/recalcular_booleanos.py                      # detectores con tiradas     -> datos/datos_v2/booleanos/
py experimento/scripts/reporte_v2/recalcular_persona2.py                       # usurpación de la agencia   -> datos/datos_v2/persona2/
py experimento/scripts/reporte_v2/recalcular_campana.py                        # instrumentos por campaña   -> datos/datos_v2/campana/
py experimento/scripts/instrumentos/distribucion_a4bc_27.py                    # respuesta a la acción (z) por bloque
py experimento/scripts/reporte_v2/medidas_cierre.py                            # medidas por bloque         -> datos/datos_v2/cierre/
py experimento/scripts/reporte_v2/page_test.py                                 # degradación de G2 (H1a–H1c)
py experimento/scripts/reporte_v2/consolidar.py --B 10000                      # comparación G1 vs G2 (H1d–H1f)
py experimento/scripts/reporte_v2/resultados_tesis.py                          # paquete de resultados por objetivo
py experimento/scripts/reporte_v2/cierre_brechas.py                            # docs/cierre_brechas.md
```

Las salidas quedan en [`docs/resultados/`](docs/resultados/) y [`docs/reportes/`](docs/reportes/). Las pruebas de sensibilidad de cada instrumento están en [`experimento/scripts/sensibilidad/`](experimento/scripts/sensibilidad/), con sus expectativas selladas con SHA-256.

> **Nota sobre la réplica.** Los dados son deterministas, pero las llamadas al modelo no llevan semilla: una nueva corrida reproduce el procedimiento y la medición, no el mismo texto. Los análisis de este repositorio se reproducen exactamente sobre la base y los datos del corpus original.
