[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [switch]$NoDesktopClients
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root '.runtime'
$StateFile = Join-Path $Runtime 'services.json'
$RabbitLink = 'C:\Users\Sebas2hVR\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\RabbitMQ Server\RabbitMQ Service - start.lnk'
$NginxExe = 'C:\NGINX\nginx.exe'
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null

function Test-Listening([int]$Port) {
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync('127.0.0.1', $Port)
        return $task.Wait(250) -and $client.Connected
    } catch { return $false }
    finally { $client.Dispose() }
}

$Reserved = [Collections.Generic.HashSet[int]]::new()
function Get-FreePort([int]$Start) {
    for ($port = $Start; $port -le 65535; $port++) {
        if ($Reserved.Contains($port) -or (Test-Listening $port)) { continue }
        $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $port)
        try { $listener.Start(); [void]$Reserved.Add($port); return $port }
        catch { continue }
        finally { try { $listener.Stop() } catch {} }
    }
    throw "No existe un puerto libre desde $Start."
}

function Wait-Port([int]$Port, [int]$Seconds = 30) {
    $limit = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $limit) {
        if (Test-Listening $Port) { return }
        Start-Sleep -Milliseconds 400
    }
    throw "El puerto $Port no empezó a escuchar en $Seconds segundos."
}

function Import-EnvFile([string]$Path) {
    if (-not (Test-Path $Path)) { return }
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*([^#=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2], 'Process')
        }
    }
}

function New-Base64Secret([int]$Bytes = 48) {
    $buffer = New-Object byte[] $Bytes
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($buffer) }
    finally { $generator.Dispose() }
    return [Convert]::ToBase64String($buffer)
}

function Start-Managed([string]$Name, [string]$File, [string[]]$Arguments, [string]$WorkingDirectory) {
    $out = Join-Path $Runtime "$Name.out.log"
    $err = Join-Path $Runtime "$Name.err.log"
    $process = Start-Process -FilePath $File -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
    $script:Processes[$Name] = $process.Id
    return $process
}

if (Test-Path $StateFile) {
    try {
        $old = Get-Content -Raw $StateFile | ConvertFrom-Json
        $alive = @($old.processes.PSObject.Properties.Value | Where-Object {
            Get-Process -Id $_ -ErrorAction SilentlyContinue
        })
        if ($alive.Count -gt 0) {
            Write-Host "APE 04 ya tiene $($alive.Count) procesos activos. Estado: $StateFile" -ForegroundColor Yellow
            Write-Host "Use scripts\stop-all.ps1 antes de crear otra instancia."
            return
        }
    } catch {}
}

Import-EnvFile (Join-Path $Root 'python_ventas-api\.env')
$SecretsFile = Join-Path $Runtime 'secrets.env'
if (-not (Test-Path $SecretsFile)) {
    @(
        "JWT_SECRET=$(New-Base64Secret)"
        "OAUTH_CLIENT_ID=vehiculos-client"
        "OAUTH_CLIENT_SECRET=$(New-Base64Secret 32)"
        "VENTAS_SERVICE_KEY=$(New-Base64Secret 40)"
        "NOTIFICACIONES_KEY=$(New-Base64Secret 40)"
    ) | Set-Content -LiteralPath $SecretsFile -Encoding utf8
}
Import-EnvFile $SecretsFile

$Ports = [ordered]@{
    javaA = Get-FreePort 8080
    javaB = Get-FreePort 8081
    ventas = Get-FreePort 8002
    notificaciones = Get-FreePort 8081
    monitor = Get-FreePort 8083
    nginx = Get-FreePort 8090
    react = Get-FreePort 5173
    pwa = Get-FreePort 5174
}
$Processes = [ordered]@{}

# RabbitMQ usa el puerto configurado por el servicio de Windows. Si ya escucha, se reutiliza.
$RabbitPort = if ($env:RABBITMQ_PORT) { [int]$env:RABBITMQ_PORT } else { 5672 }
if (-not (Test-Listening $RabbitPort)) {
    if (-not (Test-Path $RabbitLink)) { throw "No existe el acceso directo de RabbitMQ: $RabbitLink" }
    Start-Process -FilePath $RabbitLink -WindowStyle Hidden | Out-Null
    Wait-Port $RabbitPort 40
}

$env:DB_HOST = if ($env:DB_HOST) { $env:DB_HOST } else { '127.0.0.1' }
$env:DB_PORT = if ($env:DB_PORT) { $env:DB_PORT } else { '3306' }
$env:DB_USER = if ($null -ne $env:DB_USER) { $env:DB_USER } else { 'root' }
if ($null -eq $env:DB_PASSWORD) { $env:DB_PASSWORD = '' }
$env:VEHICULOS_DB = 'venta_vehiculos'
$env:DB_NAME = 'ventas_service'
$env:NOTIFICACIONES_DB = 'notificaciones_service'
$env:RABBITMQ_HOST = if ($env:RABBITMQ_HOST) { $env:RABBITMQ_HOST } else { '127.0.0.1' }
$env:RABBITMQ_PORT = [string]$RabbitPort
$env:RABBITMQ_USER = if ($env:RABBITMQ_USER) { $env:RABBITMQ_USER } else { 'guest' }
$env:RABBITMQ_PASSWORD = if ($env:RABBITMQ_PASSWORD) { $env:RABBITMQ_PASSWORD } else { 'guest' }
$env:NOTIFICATION_TRANSPORT = 'rabbitmq'

if (-not (Test-Listening ([int]$env:DB_PORT))) {
    throw "MySQL no escucha en $($env:DB_HOST):$($env:DB_PORT). Inicie MySQL desde XAMPP."
}

$schemaCode = "import os,pymysql; c=pymysql.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.getenv('DB_PASSWORD',''),autocommit=True); q=c.cursor(); [q.execute('CREATE DATABASE IF NOT EXISTS '+n+' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci') for n in ('venta_vehiculos','ventas_service','notificaciones_service')]; c.close()"
& python -c $schemaCode
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron preparar los esquemas MySQL.' }

$Maven = Join-Path $Root 'java_venta-vehiculos-api_security\mvnw.cmd'
if (-not $SkipBuild) {
    & $Maven -q -f (Join-Path $Root 'java_venta-vehiculos-api_security\pom.xml') -DskipTests package
    if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación de la API Java.' }
    & $Maven -q -f (Join-Path $Root 'java_notificaciones-service\pom.xml') -DskipTests package
    if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación de notificaciones.' }
    & dotnet build (Join-Path $Root 'AplicacionEscritorioWINDOWS_FORMS\ConsultaVehiculosWinForms.sln') --nologo -v:q
    if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación de WinForms.' }
    Push-Location (Join-Path $Root 'AplicacionMovilPWA'); npm run build; Pop-Location
    Push-Location (Join-Path $Root 'AplicacionWebREACT\react-fetch-vehiculos'); npm run build; Pop-Location
}

Push-Location (Join-Path $Root 'python_ventas-api')
python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { Pop-Location; throw 'Falló la migración de ventas.' }
Pop-Location

$env:NOTIFICACIONES_URL = "http://127.0.0.1:$($Ports.nginx)"
$env:JAVA_URL = "http://127.0.0.1:$($Ports.nginx)"
$env:APE04_BASE_URL = "http://127.0.0.1:$($Ports.nginx)"
$env:API_BASE_URL = $env:APE04_BASE_URL

$JavaJar = (Resolve-Path (Join-Path $Root 'java_venta-vehiculos-api_security\target\venta-vehiculos-api-0.0.1-SNAPSHOT.jar')).Path
foreach ($item in @(@('java-a', $Ports.javaA), @('java-b', $Ports.javaB))) {
    $env:SERVER_PORT = [string]$item[1]
    Start-Managed $item[0] 'java' @('-jar', $JavaJar) (Split-Path $JavaJar) | Out-Null
}

$env:SERVER_PORT = [string]$Ports.notificaciones
$NotifJar = (Resolve-Path (Join-Path $Root 'java_notificaciones-service\target\notificaciones-service-0.0.1-SNAPSHOT.jar')).Path
Start-Managed 'notificaciones' 'java' @('-jar', $NotifJar) (Split-Path $NotifJar) | Out-Null

$PythonDir = Join-Path $Root 'python_ventas-api'
Start-Managed 'ventas' 'python' @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port',[string]$Ports.ventas) $PythonDir | Out-Null
Start-Managed 'ventas-worker' 'python' @('-m','app.worker') $PythonDir | Out-Null

foreach ($port in @($Ports.javaA, $Ports.javaB, $Ports.notificaciones, $Ports.ventas)) { Wait-Port $port 45 }

$NginxRuntime = Join-Path $Runtime 'nginx'
New-Item -ItemType Directory -Force -Path $NginxRuntime, (Join-Path $NginxRuntime 'logs'), (Join-Path $NginxRuntime 'temp') | Out-Null
$config = Get-Content -Raw (Join-Path $Root 'infraestructura\nginx\nginx.conf.template')
$config = $config.Replace('{{JAVA_A}}',[string]$Ports.javaA).Replace('{{JAVA_B}}',[string]$Ports.javaB)
$config = $config.Replace('{{VENTAS}}',[string]$Ports.ventas).Replace('{{NOTIF}}',[string]$Ports.notificaciones)
$config = $config.Replace('{{NGINX}}',[string]$Ports.nginx)
$config | Set-Content -LiteralPath (Join-Path $NginxRuntime 'nginx.conf') -Encoding utf8
& $NginxExe -t -p "$NginxRuntime\" -c nginx.conf
if ($LASTEXITCODE -ne 0) { throw 'La configuración dinámica de NGINX no es válida.' }
& $NginxExe -p "$NginxRuntime\" -c nginx.conf
Wait-Port $Ports.nginx 20

$env:MONITOR_PORT = [string]$Ports.monitor
$env:MONITOR_NGINX_URL = "http://127.0.0.1:$($Ports.nginx)/nginx-ping"
$env:MONITOR_JAVA_A_URL = "http://127.0.0.1:$($Ports.javaA)/actuator/health"
$env:MONITOR_JAVA_B_URL = "http://127.0.0.1:$($Ports.javaB)/actuator/health"
$env:MONITOR_VENTAS_URL = "http://127.0.0.1:$($Ports.ventas)/health"
$env:MONITOR_NOTIF_URL = "http://127.0.0.1:$($Ports.notificaciones)/actuator/health"
Start-Managed 'monitor' 'python' @((Join-Path $Root 'infraestructura\monitor\monitor.py')) $Root | Out-Null

Start-Managed 'pwa' 'npm.cmd' @('start','--',"--port=$($Ports.pwa)") (Join-Path $Root 'AplicacionMovilPWA') | Out-Null
Start-Managed 'react' 'npm.cmd' @('run','dev','--','--host','127.0.0.1','--port',[string]$Ports.react) (Join-Path $Root 'AplicacionWebREACT\react-fetch-vehiculos') | Out-Null

if (-not $NoDesktopClients) {
    $WinForms = Join-Path $Root 'AplicacionEscritorioWINDOWS_FORMS\ConsultaVehiculosWinForms\bin\Debug\net8.0-windows\ConsultaVehiculosWinForms.exe'
    if (Test-Path $WinForms) { $Processes['winforms'] = (Start-Process $WinForms -WorkingDirectory (Split-Path $WinForms) -PassThru).Id }
    Start-Managed 'javafx-launcher' $Maven @('-q','-f',(Join-Path $Root 'AplicacionEscritorioJAVA_FX\consultarvehiculojavafx\pom.xml'),'javafx:run') (Join-Path $Root 'AplicacionEscritorioJAVA_FX\consultarvehiculojavafx') | Out-Null
}

foreach ($port in @($Ports.monitor, $Ports.pwa, $Ports.react)) { Wait-Port $port 30 }

$state = [ordered]@{
    startedAt = (Get-Date).ToString('o')
    ports = $Ports
    processes = $Processes
    urls = [ordered]@{
        gateway = "http://localhost:$($Ports.nginx)"
        monitor = "http://localhost:$($Ports.monitor)/health"
        react = "http://localhost:$($Ports.react)"
        pwa = "http://localhost:$($Ports.pwa)"
        rabbit = 'http://localhost:15672'
    }
}
$state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $StateFile -Encoding utf8

Write-Host ''
Write-Host 'APE 04 iniciado correctamente' -ForegroundColor Green
$state.urls.GetEnumerator() | ForEach-Object { Write-Host ("{0,-10} {1}" -f $_.Key, $_.Value) }
Write-Host "Puertos: $StateFile"
Write-Host "Secretos locales (ignorado por Git): $SecretsFile"

