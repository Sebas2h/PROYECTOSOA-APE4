$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$NotifProject = Join-Path $Root 'java_notificaciones-service'
$NotifPom = Join-Path $NotifProject 'pom.xml'
$Maven = Join-Path $Root 'java_venta-vehiculos-api_security\mvnw.cmd'
$RabbitLink = 'C:\Users\Sebas2hVR\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\RabbitMQ Server\RabbitMQ Service - start.lnk'
$SecretsFile = Join-Path $Root '.runtime\secrets.env'
New-Item -ItemType Directory -Force -Path (Split-Path $SecretsFile) | Out-Null

function Test-Port([int]$Port) {
    $client = New-Object Net.Sockets.TcpClient
    try { $task = $client.ConnectAsync('127.0.0.1', $Port); return $task.Wait(300) -and $client.Connected }
    catch { return $false } finally { $client.Dispose() }
}
function Wait-Port([int]$Port, [int]$Seconds) {
    $limit = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $limit) { if (Test-Port $Port) { return }; Start-Sleep -Milliseconds 400 }
    throw "El puerto $Port no empezó a escuchar."
}
function New-Secret([int]$Bytes) {
    $buffer = New-Object byte[] $Bytes
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($buffer) } finally { $generator.Dispose() }
    [Convert]::ToBase64String($buffer)
}

if (-not (Test-Port 5672)) {
    if (-not (Test-Path $RabbitLink)) { throw "No existe el iniciador de RabbitMQ: $RabbitLink" }
    Start-Process -FilePath $RabbitLink -WindowStyle Hidden | Out-Null
    Wait-Port 5672 40
    Write-Host 'RabbitMQ iniciado en 5672.' -ForegroundColor Green
} else { Write-Host 'RabbitMQ ya está activo en 5672.' -ForegroundColor Yellow }

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

if (Test-Port 8181) {
    Write-Host 'Notificaciones ya está activo en 8181; no se inicia otra copia.' -ForegroundColor Yellow
    return
}

$env:SERVER_PORT = '8181'
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '3306'
$env:DB_USER = 'root'
$env:DB_PASSWORD = ''
$env:NOTIFICACIONES_DB = 'notificaciones_service'
$env:RABBITMQ_HOST = '127.0.0.1'
$env:RABBITMQ_PORT = '5672'
$env:RABBITMQ_USER = 'guest'
$env:RABBITMQ_PASSWORD = 'guest'

$escapedProject = $NotifProject.Replace("'", "''")
$escapedMaven = $Maven.Replace("'", "''")
$escapedPom = $NotifPom.Replace("'", "''")
$command = "Set-Location -LiteralPath '$escapedProject'; `$host.UI.RawUI.WindowTitle='APE04 Notificaciones + RabbitMQ'; & '$escapedMaven' -f '$escapedPom' spring-boot:run"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
$process = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList @('-NoExit','-NoProfile','-EncodedCommand',$encoded) -PassThru
Write-Host "Consola de notificaciones abierta en 8181, PID $($process.Id)" -ForegroundColor Green
Write-Host 'La consola permanecerá abierta y mostrará los logs de Maven/Spring Boot.'
