# Arranque completo APE 04

Desde PowerShell, en la raíz del repositorio:

```powershell
.\scripts\start-all.ps1
```

El script busca el primer puerto libre desde el puerto base; si está ocupado,
prueba el siguiente de forma consecutiva. Levanta RabbitMQ mediante el acceso
directo instalado, prepara MySQL, compila, inicia APIs, worker, NGINX, monitor,
React, PWA, WinForms y JavaFX. Las URLs y puertos reales quedan en
`.runtime/services.json`; los secretos locales generados quedan en
`.runtime/secrets.env`. Ambos archivos están ignorados por Git.

Opciones:

```powershell
.\scripts\start-all.ps1 -SkipBuild
.\scripts\start-all.ps1 -NoDesktopClients
.\scripts\stop-all.ps1
```

`stop-all.ps1` detiene únicamente los procesos registrados por el script y deja
MySQL/RabbitMQ activos.
