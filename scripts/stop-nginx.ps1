$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$prefijo = Join-Path $raiz 'infraestructura\nginx'
& 'C:\NGINX\nginx.exe' -p "$prefijo\" -c nginx.conf -s quit

