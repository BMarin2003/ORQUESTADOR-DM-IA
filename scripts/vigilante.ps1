<#
.SYNOPSIS
  Anota cada 30 s en logs\vigilante.csv: cuantos procesos de generacion (G2/G1)
  siguen vivos, su memoria (working set) y la RAM libre del sistema. Sirve para
  correlacionar el momento exacto en que caen procesos con la memoria/eventos.
  Corre en bucle hasta que lo mates (Stop-Process -Name powershell -Id <pid>).
#>
$raiz = Split-Path -Parent $PSScriptRoot
$out = Join-Path $raiz "logs\vigilante.csv"
if (-not (Test-Path $out)) {
    "hora,g2_vivos,g1_vivos,ws_total_mb,ws_max_mb,ram_libre_gb,virt_libre_gb" | Out-File $out -Encoding ascii
}
while ($true) {
    $p  = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'vertical_slice' })
    $g1 = @($p | Where-Object { $_.CommandLine -match 'vertical_slice_g1' }).Count
    $g2 = $p.Count - $g1
    $ws = @($p | ForEach-Object { [math]::Round($_.WorkingSetSize / 1MB, 0) })
    $tot = if ($ws.Count) { ($ws | Measure-Object -Sum).Sum } else { 0 }
    $max = if ($ws.Count) { ($ws | Measure-Object -Maximum).Maximum } else { 0 }
    $os = Get-CimInstance Win32_OperatingSystem
    $linea = "{0},{1},{2},{3},{4},{5:N1},{6:N1}" -f (Get-Date -Format "HH:mm:ss"), $g2, $g1, $tot, $max,
             ($os.FreePhysicalMemory / 1MB), ($os.FreeVirtualMemory / 1MB)
    Add-Content -Path $out -Value $linea -Encoding ascii
    Start-Sleep -Seconds 30
}
