# API de Ventas y Compradores — Python FastAPI

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11 y Visual Studio Code.
- Python 3.13 con `pip` y `venv`.
- MySQL o XAMPP con la base `venta_vehiculos` disponible.
- API Java de vehículos en `http://127.0.0.1:8080`.
- Servicio Java de notificaciones en `http://127.0.0.1:8081` para comprobar avisos.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-ventas-python` y se abre la carpeta que contiene `requirements.txt` y `alembic.ini`.
2. Se abre PowerShell y se crea el entorno virtual:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Se copia y configura el archivo local de variables:

```powershell
Copy-Item .env.example .env
notepad .env
```

4. En `.env` se ajustan los datos de MySQL, las direcciones de Java y notificaciones, `VENTAS_SERVICE_KEY` y `NOTIFICACIONES_KEY`. Los valores deben coincidir con la configuración privada de los servicios Java.
5. Con MySQL en funcionamiento, se aplican las migraciones incluidas:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## 3. Comprobar el código

```powershell
.\.venv\Scripts\python.exe -m compileall app alembic
```

## 4. Ejecutar la API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

Se comprueba `http://127.0.0.1:8002/health` y se revisan los endpoints en `http://127.0.0.1:8002/docs`.

## 5. Ejecutar el proceso de recuperación (cuando corresponda)

En otra terminal, desde la misma carpeta:

```powershell
.\.venv\Scripts\python.exe -m app.worker
```

Se detienen los procesos con `Ctrl + C`. El archivo `.env` no se publica en Git.

> Para la integración de avisos se comprueba que el receptor Java acepte la cabecera `X-Notification-Key`, tal como la envía esta API.
