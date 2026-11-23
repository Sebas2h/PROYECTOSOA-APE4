# Aplicación Móvil PWA — Consulta de Vehículos

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11 y Visual Studio Code.
- Node.js 20 o superior, con npm.
- Chrome o navegador compatible.
- API Java Spring Boot activa en `http://127.0.0.1:8080` y JWT autorizado.
- Para probar desde Android por USB: Android Platform Tools (`adb`), opcional.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-pwa-movil` y se abre la carpeta que contiene `package.json` y `server.mjs`.
2. Se comprueba Node.js y npm:

```powershell
node -v
npm -v
```

Esta aplicación no declara dependencias externas que deban instalarse con `npm install`.

## 3. Ejecutar en Visual Studio Code

```powershell
npm run dev
```

Se abre `http://localhost:5173`. El servidor reenvía `GET /api/vehiculos` a Java en el puerto `8080`.

## 4. Compilar y comprobar la versión generada

Se detiene la ejecución anterior con `Ctrl + C` y se ejecuta:

```powershell
npm run build
npm run preview
```

Se abre `http://localhost:4173`. La compilación queda en la carpeta `dist`.

## 5. Probar en Android (opcional)

1. Se conecta el teléfono por USB con la depuración USB habilitada.
2. Con `npm run preview` activo y `adb` instalado, se ejecuta en otra terminal:

```powershell
adb devices
adb reverse tcp:4173 tcp:4173
```

3. Se abre `http://localhost:4173` en Chrome del teléfono.
4. Se introduce el JWT y se presiona **Consultar vehículos**.
5. Cuando el navegador lo permita, se utiliza la opción **Instalar aplicación** o **Añadir a pantalla de inicio**.

> La versión incluida solo lista vehículos con JWT; no implementa inicio de sesión ni registro de ventas.
