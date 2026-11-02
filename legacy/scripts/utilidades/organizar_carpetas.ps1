# Organiza corpus/, fixtures/ y logs/ separando pilotos (Par01-03) de
# datos reales (Par04 en adelante). Solo MUEVE archivos, no borra nada.
# Correr desde la raíz del proyecto: C:\BMARIN2003\DEV\proyecto

$ErrorActionPreference = "Stop"

function Ensure-Dir($path) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
        Write-Host "Creada: $path"
    }
}

# --- corpus/ ---
Ensure-Dir "corpus\pilotos"
Move-Item "corpus\lore_par02_vela_honda.md"  "corpus\pilotos\" -Force
Move-Item "corpus\lore_par03_cosecha_dorada.md" "corpus\pilotos\" -Force
Move-Item "corpus\lore_vado_de_ceniza.md"    "corpus\pilotos\" -Force
# corpus\real\lore_puerto_salazon.md ya está bien ubicado

# --- fixtures/ ---
Ensure-Dir "fixtures\pilotos"
Move-Item "fixtures\personas.json"        "fixtures\pilotos\" -Force
Move-Item "fixtures\personas_par02.json"  "fixtures\pilotos\" -Force
Move-Item "fixtures\personas_par03.json"  "fixtures\pilotos\" -Force
Move-Item "fixtures\world.json"           "fixtures\pilotos\" -Force
Move-Item "fixtures\world_par02.json"     "fixtures\pilotos\" -Force
Move-Item "fixtures\world_par03.json"     "fixtures\pilotos\" -Force
Move-Item "fixtures\characters_nuevos.sql" "fixtures\pilotos\" -Force
Move-Item "fixtures\seed.sql"             "fixtures\pilotos\" -Force
Move-Item "fixtures\turns.json"           "fixtures\pilotos\" -Force
Move-Item "fixtures\probes.json"          "fixtures\pilotos\" -Force
# generar_seed.py y validar_fixtures.py se quedan en fixtures\ (son
# herramientas, no datos de una campaña concreta)
# fixtures\real\world_par04.json y personas_par04.json ya están bien ubicados

# --- logs/ ---
Ensure-Dir "logs\pilotos"
Ensure-Dir "logs\par04_real"

$pilotos = @(
    "par01_g1_ef4e900a_frag_turnos_1-200_20260911_102540.md",
    "par01_g1_ef4e900a_frag_turnos_152-261_20260911_154312.md",
    "par01_g1_ef4e900a_frag_turnos_169-223_20260911_160231.md",
    "par01_g1_ef4e900a_frag_turnos_224-250_20260911_193441.md",
    "par01_g1_ef4e900a_frag_turnos_34-215_20260911_124158.md",
    "par01_g1_ef4e900a_frag_turnos_95-259_20260911_142757.md",
    "par01_g1_ef4e900a_hasta-turno250.md",
    "par01_g2_7b7a3cd5_hasta-turno250.md",
    "par01_g2_7b7a3cd5_raw_powershell_hasta-turno535.txt",
    "par02_g1_d750fd38_turnos_1-250_20260914_021726.md",
    "par02_g2_96352852_turnos_1-250_20260914_005526.md",
    "par03_g2_292bb8f6_turnos_1-250_20260914_082409.md",
    "piloto_log.txt",
    "sesion_292bb8f6_turnos_1-250_20260914_082409.md",
    "sesion_96352852_turnos_1-250_20260914_005526.md",
    "sesion_g1_d750fd38_turnos_1-250_20260914_021726.md",
    "sesion_g1_ef4e900a_turnos_1-200_20260911_102540.md",
    "sesion_g1_ef4e900a_turnos_152-261_20260911_154312.md",
    "sesion_g1_ef4e900a_turnos_169-223_20260911_160231.md",
    "sesion_g1_ef4e900a_turnos_224-250_20260911_193441.md",
    "sesion_g1_ef4e900a_turnos_34-215_20260911_124158.md",
    "sesion_g1_ef4e900a_turnos_95-259_20260911_142757.md"
)
foreach ($f in $pilotos) {
    $p = "logs\$f"
    if (Test-Path $p) { Move-Item $p "logs\pilotos\" -Force }
}

$par04 = @(
    "par_04_g1_multiagente_puerto_salazon_g1_68a5896f_turnos_562-1400_20260914_231208.md",
    "par_04_g1_multiagente_puerto_salazon_g1_68a5896f_turnos_69-1468_20260914_181642.md",
    "sesion_e9bef82d_turnos_1-1400_20260914_172455.md",
    "sesion_g1_68a5896f_turnos_1-1400_20260914_172457.md"
)
foreach ($f in $par04) {
    $p = "logs\$f"
    if (Test-Path $p) { Move-Item $p "logs\par04_real\" -Force }
}

# --- raíz: script de diagnóstico suelto -> scripts/ ---
if (Test-Path "estado_par04.py") {
    Move-Item "estado_par04.py" "scripts\estado_par04.py" -Force
}

# --- limpiar bytecode cacheado, por seguridad (punto 26 de la bitácora) ---
Get-ChildItem -Recurse -Directory -Filter "__pycache__" . | Remove-Item -Recurse -Force

Write-Host "`nListo. Estructura final:"
Write-Host "  corpus\pilotos\   corpus\real\"
Write-Host "  fixtures\pilotos\ fixtures\real\"
Write-Host "  logs\pilotos\     logs\par04_real\"
Write-Host "  scripts\estado_par04.py"
