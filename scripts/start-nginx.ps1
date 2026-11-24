$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$prefijo = Join-Path $raiz 'infraestructura\nginx'
New-Item -ItemType Directory -Force -Path (Join-Path $prefijo 'logs'), (Join-Path $prefijo 'temp') | Out-Null
& 'C:\NGINX\nginx.exe' -t -p "$prefijo\" -c nginx.conf
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& 'C:\NGINX\nginx.exe' -p "$prefijo\" -c nginx.conf

