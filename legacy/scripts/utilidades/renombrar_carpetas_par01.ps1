# Renombra archivos/carpetas de "par04"/"Par 04" a "par01_real" /
# "Par 01 (real)", para que coincida con el título ya corregido en la
# base de datos. Correr DESPUES de renombrar_a_par01_real.py, y desde la
# raíz del proyecto: C:\BMARIN2003\DEV\proyecto

$ErrorActionPreference = "Stop"

# logs/par04_real -> logs/par01_real  (creado por organizar_carpetas.ps1)
if (Test-Path "logs\par04_real") {
    Rename-Item "logs\par04_real" "par01_real"
    Write-Host "logs\par04_real -> logs\par01_real"
}

# fixtures/real/*_par04.json -> *_par01.json
if (Test-Path "fixtures\real\world_par04.json") {
    Rename-Item "fixtures\real\world_par04.json" "world_par01.json"
}
if (Test-Path "fixtures\real\personas_par04.json") {
    Rename-Item "fixtures\real\personas_par04.json" "personas_par01.json"
}

# scripts/estado_par04.py -> estado_par01.py (movido ahí por organizar_carpetas.ps1)
if (Test-Path "scripts\estado_par04.py") {
    Rename-Item "scripts\estado_par04.py" "estado_par01.py"
}

Write-Host "`nListo. corpus\real\lore_puerto_salazon.md no lleva número, se queda igual."
