$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $Root 'java_venta-vehiculos-api_security'
$Maven = Join-Path $Project 'mvnw.cmd'
$SecretsFile = Join-Path $Root '.runtime\secrets.env'
New-Item -ItemType Directory -Force -Path (Split-Path $SecretsFile) | Out-Null

function New-Secret([int]$Bytes) {
    $buffer = New-Object byte[] $Bytes
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($buffer) } finally { $generator.Dispose() }
    [Convert]::ToBase64String($buffer)
}

if (-not (Test-Path $SecretsFile)) {
    @(
        "JWT_SECRET=$(New-Secret 48)"
        'OAUTH_CLIENT_ID=vehiculos-client'
        "OAUTH_CLIENT_SECRET=$(New-Secret 32)"
        "VENTAS_SERVICE_KEY=$(New-Secret 40)"
        "NOTIFICACIONES_KEY=$(New-Secret 40)"
    ) | Set-Content -LiteralPath $SecretsFile -Encoding utf8
}
foreach ($line in Get-Content $SecretsFile) {
    if ($line -match '^([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') }
}

$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '3306'
$env:DB_USER = 'root'
$env:DB_PASSWORD = ''
$env:VEHICULOS_DB = 'venta_vehiculos'
$env:NOTIFICACIONES_URL = 'http://127.0.0.1:8090'

foreach ($port in 8080, 8182) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) {
        Write-Host "Java ya está escuchando en $port; no se inicia otra copia." -ForegroundColor Yellow
        continue
    }
    $env:SERVER_PORT = [string]$port
    $escapedProject = $Project.Replace("'", "''")
    $escapedMaven = $Maven.Replace("'", "''")
    $command = "Set-Location -LiteralPath '$escapedProject'; `$host.UI.RawUI.WindowTitle='APE04 Java $port'; & '$escapedMaven' spring-boot:run"
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $process = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @('-NoExit','-NoProfile','-EncodedCommand',$encoded) -PassThru
    Write-Host "Consola Java abierta: puerto $port, PID $($process.Id)" -ForegroundColor Green
}
Write-Host 'Las consolas Java permanecerán abiertas. Ciérrelas para detener cada instancia.'

