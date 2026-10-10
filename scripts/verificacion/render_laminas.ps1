# Exporta láminas del deck a PNG con PowerPoint (solo lectura del .pptx).
# Uso: powershell -File render_laminas.ps1 <ruta.pptx> <carpeta_salida> 17 28 31 32 33
param([string]$Pptx, [string]$Salida, [Parameter(ValueFromRemainingArguments = $true)][int[]]$Laminas)
New-Item -ItemType Directory -Force $Salida | Out-Null
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open((Resolve-Path $Pptx).Path, $true, $false, $false)
    foreach ($n in $Laminas) {
        $destino = Join-Path (Resolve-Path $Salida).Path ("lamina_{0:D2}.png" -f $n)
        $pres.Slides.Item($n).Export($destino, "PNG", 1280, 720)
        Write-Output "exportada $destino"
    }
    $pres.Close()
} finally {
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
}
