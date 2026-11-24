$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
$StateFile = Join-Path $Root '.runtime\services.json'
if (-not (Test-Path $StateFile)) { Write-Host 'No existe estado de ejecución.'; return }
$state = Get-Content -Raw $StateFile | ConvertFrom-Json
foreach ($entry in $state.processes.PSObject.Properties) {
    $process = Get-Process -Id $entry.Value -ErrorAction SilentlyContinue
    if ($process) { Stop-Process -Id $process.Id; Write-Host "Detenido $($entry.Name) ($($process.Id))" }
}
$nginxRuntime = Join-Path $Root '.runtime\nginx'
if (Test-Path (Join-Path $nginxRuntime 'logs\nginx.pid')) {
    & 'C:\NGINX\nginx.exe' -p "$nginxRuntime\" -c nginx.conf -s quit
}
Remove-Item -LiteralPath $StateFile -ErrorAction SilentlyContinue
Write-Host 'Procesos APE 04 detenidos. RabbitMQ y MySQL permanecen activos.'
