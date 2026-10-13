<#
.SYNOPSIS
  Chequeo de una sola pasada: turnos reales (Postgres), procesos vivos, RAM y
  estado del supervisor (reinicios, campanias bloqueadas/rendidas).

.PARAMETER Lote
  "07-17" (por defecto) o "18-27": que lote de pares se mira.

.EXAMPLE
  .\experimento\scripts\chequeo_rapido.ps1
  .\experimento\scripts\chequeo_rapido.ps1 -Lote 18-27
#>
param([string]$Lote = "07-17")
$raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $raiz

$idsRel = "docs/ids_par$Lote.json"
$supLog = if ($Lote -eq "07-17") { "datos\logs\supervisor.log" } else { "datos\logs\supervisor_par$Lote.log" }
$pares  = @(Get-Content $idsRel -Raw -Encoding utf8 | ConvertFrom-Json).Count

Write-Host "=== 1) TURNOS REALES (Postgres) -- lote Par $Lote ===" -ForegroundColor Cyan
py experimento\scripts\estado_par07-17.py --ids $idsRel

Write-Host ""
Write-Host "=== 2) PROCESOS VIVOS ===" -ForegroundColor Cyan
$gen = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'vertical_slice' })
$g1 = @($gen | Where-Object { $_.CommandLine -match 'vertical_slice_g1' }).Count
Write-Host "procesos de generacion vivos: G2=$($gen.Count - $g1)  G1=$g1   (esperado mientras haya campanias sin terminar: $pares y $pares)"
$sup = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'supervisor' })
if ($sup.Count -ge 1) { Write-Host "supervisor: VIVO (PID $($sup[0].ProcessId))" -ForegroundColor Green }
else { Write-Host "supervisor: NO ESTA CORRIENDO -- nadie relanza las campanias que se caigan" -ForegroundColor Red }
$mem = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
Write-Host ("Memoria DISPONIBLE: {0:N1} GB (libre + cache reutilizable; 'libre' a secas engana en Windows)   procesos de generacion: {1:N0} MB" -f ($mem.AvailableMBytes/1024), (($gen | Measure-Object WorkingSetSize -Sum).Sum/1MB))

Write-Host ""
Write-Host "=== 3) SUPERVISOR: eventos ===" -ForegroundColor Cyan
if (Test-Path $supLog) {
    $ev = Get-Content $supLog -Encoding utf8
    $reinicios = @($ev | Select-String "\[REINICIO\]").Count
    $alertas   = @($ev | Select-String "\[BLOQUEADA\]|\[RENDIDA\]|\[AVISO\]|\[DB\]")
    $completas = @($ev | Select-String "\[COMPLETA\]").Count
    Write-Host "reinicios acumulados: $reinicios    campanias completas: $completas de $($pares * 2)"
    if ($alertas.Count -gt 0) {
        Write-Host "ALERTAS (revisar):" -ForegroundColor Red
        $alertas | Select-Object -Last 8 | ForEach-Object { Write-Host "  $($_.Line)" }
    } else { Write-Host "sin alertas (ninguna campania bloqueada ni rendida)" -ForegroundColor Green }
    Write-Host "ultimos eventos:"
    $ev | Select-Object -Last 5 | ForEach-Object { Write-Host "  $_" }
} else { Write-Host "todavia no existe $supLog" }

Write-Host ""
Write-Host "Como leerlo: corre esto de nuevo en 10 min. Los TURNOS deben subir; el supervisor" -ForegroundColor Yellow
Write-Host "relanza solo cualquier caida (ves [REINICIO]). Solo actuar si hay ALERTAS o si el" -ForegroundColor Yellow
Write-Host "supervisor figura NO ESTA CORRIENDO." -ForegroundColor Yellow
