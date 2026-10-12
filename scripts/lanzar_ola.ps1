<#
.SYNOPSIS
  Lanza la generacion G2/G1 de pares Par07-17 como procesos DESACOPLADOS de
  cualquier terminal (Win32_Process.Create via WMI: el padre es WmiPrvSE, no
  la consola ni VSCode), usando los campaign_id de docs/ids_par07-17.json.

.DESCRIPTION
  - --turnos NUNCA se hardcodea: se consulta current_turn real en Postgres
    (scripts\current_turn.py) y se usa 1400 - current_turn; si una campania
    ya esta en 1400 se salta.
  - python -u (sin buffer): el log siempre esta al dia, se puede mirar en
    vivo con  Get-Content logs\parNN_g1_*.log -Wait -Tail 20
  - Cada log termina con una marca "[FIN OK]" o "[FIN ERROR <codigo>]" con
    fecha/hora. Si un proceso muere y NO hay marca de fin, lo mato algo
    externo que se llevo tambien al cmd que lo envolvia.
  - Al lanzar, muestra el PID de cada proceso.

.EXAMPLE
  .\scripts\lanzar_ola.ps1 07,08,09,10,11,12,13,14,15,16,17 -Arm G1
  .\scripts\lanzar_ola.ps1 07,08 -Arm G2
#>
param(
    [Parameter(Mandatory=$true)]
    [string[]]$Pares,

    [ValidateSet("Ambos", "G2", "G1")]
    [string]$Arm = "Ambos"
)

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz
$py = (py -c "import sys; print(sys.executable)").Trim()

# par -> id numerico de personajes_jugadores.json (PJ01..PJ27)
$PJ_POR_PAR = @{
    "07" = "PJ23"; "08" = "PJ04"; "09" = "PJ17"; "10" = "PJ24"; "11" = "PJ26";
    "12" = "PJ07"; "13" = "PJ21"; "14" = "PJ20"; "15" = "PJ01"; "16" = "PJ12";
    "17" = "PJ22";
}

$ids = Get-Content "docs\ids_par07-17.json" -Raw | ConvertFrom-Json
$idsPorPar = @{}
foreach ($e in $ids) { $idsPorPar[$e.par] = $e }

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
$OBJETIVO = 1400

function Iniciar-Desacoplado($script, $campaignId, $pj, $restantes, $log) {
    # /v:on para que !time!/!errorlevel! se expandan al FINAL, no al parsear.
    $cmd = "cmd.exe /v:on /c $py -u $script --campaign-id $campaignId --pj $pj --turnos $restantes > $log 2>&1 " +
           "&& echo [FIN OK] !date! !time! >> $log || echo [FIN ERROR !errorlevel!] !date! !time! >> $log"
    $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create `
            -Arguments @{ CommandLine = $cmd; CurrentDirectory = $raiz }
    if ($r.ReturnValue -ne 0) { throw "Win32_Process.Create fallo (ReturnValue=$($r.ReturnValue))" }
    return $r.ProcessId
}

foreach ($par in $Pares) {
    $par = $par.PadLeft(2, "0")
    if (-not $idsPorPar.ContainsKey($par)) { Write-Warning "Par $par no esta en docs\ids_par07-17.json -- saltado"; continue }
    $entry = $idsPorPar[$par]
    $pj = $PJ_POR_PAR[$par]
    if (-not $pj) { Write-Warning "Par $par sin PJ mapeado -- saltado"; continue }

    Write-Host "=== Par $par ($($entry.lugar)) -- PJ $pj -- brazo(s): $Arm ===" -ForegroundColor Cyan

    foreach ($brazo in @("G2", "G1")) {
        if (-not ($Arm -eq "Ambos" -or $Arm -eq $brazo)) { continue }
        $cid    = if ($brazo -eq "G2") { $entry.campaign_g2 } else { $entry.campaign_g1 }
        $script = if ($brazo -eq "G2") { "orquestador\vertical_slice.py" } else { "orquestador\vertical_slice_g1.py" }
        $turnoActual = [int](py scripts\current_turn.py $cid)
        $restantes = $OBJETIVO - $turnoActual
        if ($restantes -le 0) { Write-Host "  $brazo ya esta en $turnoActual/$OBJETIVO -- no se relanza"; continue }
        $log = "logs\par${par}_$($brazo.ToLower())_${timestamp}.log"
        $procId = Iniciar-Desacoplado $script $cid $pj $restantes $log
        Write-Host "  ${brazo}: $cid en turno $turnoActual -> --turnos $restantes  (cmd PID $procId)  -> $log"
    }
}

Write-Host ""
Write-Host "Lanzado (desacoplado). Ver un log en vivo:  Get-Content logs\par07_g1_*.log -Wait -Tail 20" -ForegroundColor Yellow
Write-Host "Chequeo general:  .\scripts\chequeo_rapido.ps1" -ForegroundColor Yellow
