---
title: Réplica del experimento
---

Todos los comandos se ejecutan **desde la raíz del repositorio**: las rutas de los scripts son relativas a ella. En Windows, conviene fijar `$env:PYTHONUTF8="1"` en la sesión.

### 1. Requisitos

- Docker (PostgreSQL 16 con pgvector y pgAdmin).
- Python 3.12 o superior.
- Java 8 o superior, solo para la gramaticalidad con LanguageTool (CR-1); sin Java, esa sección se omite sola.
- Una clave de [DeepInfra](https://deepinfra.com) (ver [`docs/guias/SETUP_DEEPINFRA.md`](https://github.com/BMarin2003/ORQUESTADOR-DM-IA/blob/main/docs/guias/SETUP_DEEPINFRA.md)).

### 2. Configurar y levantar la base

```powershell
copy .env.example .env          # completar DEEPINFRA_API_KEY, DMIA_MODELO, POSTGRES_PASSWORD, DATABASE_URL
docker compose up -d            # dmia_db (puerto 5432) y dmia_pgadmin (http://localhost:5050)
```

Al crearse el volumen por primera vez, PostgreSQL aplica [`migrations/`](https://github.com/BMarin2003/ORQUESTADOR-DM-IA/tree/main/migrations/) (esquema completo y tabla de medición semántica).

### 3. Dependencias de Python

```powershell
py -m pip install -r orquestador/requisitos.txt numpy scipy pytest
py -m spacy download es_core_news_sm
py -m pip install sentence-transformers huggingface_hub   # solo para el instrumento semántico exploratorio
```

### 4. Verificar el modelo (antes de cada tanda)

```powershell
py entorno/verificar_modelo.py --modelo $env:DMIA_MODELO --comparar entorno/manifiesto_2026-08-28.json
```

Compara la huella de tres prompts fijos a temperatura 0 y sale con código 2 si el proveedor cambió el artefacto. El experimento usa un solo proveedor y ningún enrutador.

### 5. Crear y sembrar las campañas

```powershell
py scripts/validar_fixtures_real.py 18 19 20                 # valida mundo y PNJ de cada par
py scripts/crear_sembrar_par18-27.py 18 19 20                # crea G2 y G1 sobre el mismo tenant y siembra ambos mundos
```

Los `campaign_id` se guardan en `docs/ids_par18-27.json` (los pares 07–17 usan `crear_sembrar_par07-17.py` y `docs/ids_par07-17.json`).

### 6. Generar los 1,400 turnos

```powershell
py -u scripts/supervisor.py --arm ambos --pares 18,19,20 --ids docs/ids_par18-27.json --log logs/supervisor_par18-27.log
```

El supervisor mantiene un proceso por campaña y relanza los caídos con `1400 − current_turn`. También se puede generar una campaña a mano:

```powershell
py orquestador/vertical_slice.py    --campaign-id <UUID-G2> --pj PJ27 --turnos 1400
py orquestador/vertical_slice_g1.py --campaign-id <UUID-G1> --pj PJ27 --turnos 1400
```

Con `--seco`, el turno se ejecuta sin escribir en la base.

### 7. Medir y analizar (sin LLM, solo lectura)

```powershell
py orquestador/reporte_validacion.py --campaign-id <UUID>         # reporte de validación de una campaña
py scripts/reporte_v2/recalcular.py                                # instrumentos por turno     -> datos_v2/par*_G?.csv
py scripts/reporte_v2/recalcular_booleanos.py                      # detectores con tiradas     -> datos_v2/booleanos/
py scripts/reporte_v2/recalcular_persona2.py                       # usurpación de la agencia   -> datos_v2/persona2/
py scripts/reporte_v2/recalcular_campana.py                        # instrumentos por campaña   -> datos_v2/campana/
py scripts/instrumentos/distribucion_a4bc_27.py                    # respuesta a la acción (z) por bloque
py scripts/reporte_v2/medidas_cierre.py                            # medidas por bloque         -> datos_v2/cierre/
py scripts/reporte_v2/page_test.py                                 # degradación de G2 (H1a–H1c)
py scripts/reporte_v2/consolidar.py --B 10000                      # comparación G1 vs G2 (H1d–H1f)
py scripts/reporte_v2/resultados_tesis.py                          # paquete de resultados por objetivo
py scripts/reporte_v2/cierre_brechas.py                            # docs/cierre_brechas.md
```

Las salidas quedan en [`docs/resultados/`](https://github.com/BMarin2003/ORQUESTADOR-DM-IA/tree/main/docs/resultados/) y [`docs/reportes/`](https://github.com/BMarin2003/ORQUESTADOR-DM-IA/tree/main/docs/reportes/). Las pruebas de sensibilidad de cada instrumento están en [`scripts/sensibilidad/`](https://github.com/BMarin2003/ORQUESTADOR-DM-IA/tree/main/scripts/sensibilidad/), con sus expectativas selladas con SHA-256.

> **Nota sobre la réplica.** Los dados son deterministas, pero las llamadas al modelo no llevan semilla: una nueva corrida reproduce el procedimiento y la medición, no el mismo texto. Los análisis de este repositorio se reproducen exactamente sobre la base y los datos del corpus original.
