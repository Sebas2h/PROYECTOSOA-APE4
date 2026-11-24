$raiz = Split-Path -Parent $PSScriptRoot
python (Join-Path $raiz 'infraestructura\monitor\monitor.py')

