# Cliente Web — React + Vite

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11 y Visual Studio Code.
- Node.js 24 LTS con npm.
- API Java Spring Boot en `http://127.0.0.1:8080`.
- JWT válido para consultar el catálogo.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-react` y se abre la carpeta que contiene `package.json`.
2. Se verifica Node.js y npm:

```powershell
node -v
npm -v
```

3. Se instalan las dependencias declaradas:

```powershell
npm ci
```

## 3. Compilar

```powershell
npm run build
```

Los archivos listos para publicación quedan en `dist`.

## 4. Ejecutar en desarrollo

```powershell
npm run dev
```

Se abre `http://localhost:5173` en el navegador. Vite reenvía `/api` hacia Java en el puerto `8080`.

## 5. Comprobar

1. Se obtiene un JWT válido desde el servicio Java.
2. Se pega el token en la pantalla y se presiona **Consultar vehículos**.
3. Se comprueba el listado, el filtro por marca y el detalle al seleccionar un vehículo.
4. Para ver la compilación local se ejecuta `npm run preview` y se abre `http://localhost:4173`.
5. Se detiene el servidor con `Ctrl + C`.

> El proxy configurado por Vite corresponde a ejecución local; el despliegue en otro servidor requiere configurar el enrutamiento de `/api`.
