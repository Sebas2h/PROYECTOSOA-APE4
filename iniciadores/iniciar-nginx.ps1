$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$NginxExe = 'C:\NGINX\nginx.exe'
$Prefix = Join-Path $Root 'infraestructura\nginx'

if (-not (Test-Path $NginxExe)) { throw "No existe $NginxExe" }

$listener = Get-NetTCPConnection -State Listen -LocalPort 8090 -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host 'NGINX ya está activo en http://localhost:8090' -ForegroundColor Yellow
    Read-Host 'Presione Enter para cerrar esta consola'
    return
}

New-Item -ItemType Directory -Force -Path (Join-Path $Prefix 'logs'), (Join-Path $Prefix 'temp') | Out-Null
& $NginxExe -t -p "$Prefix\" -c nginx.conf
if ($LASTEXITCODE -ne 0) { throw 'La configuración de NGINX no es válida.' }
& $NginxExe -p "$Prefix\" -c nginx.conf
Start-Sleep -Milliseconds 600

$respuesta = Invoke-WebRequest 'http://127.0.0.1:8090/nginx-ping' -UseBasicParsing -TimeoutSec 5
Write-Host "NGINX iniciado: HTTP $($respuesta.StatusCode) en http://localhost:8090" -ForegroundColor Green
Write-Host "Logs: $Prefix\logs"
Read-Host 'Presione Enter para cerrar esta consola'

