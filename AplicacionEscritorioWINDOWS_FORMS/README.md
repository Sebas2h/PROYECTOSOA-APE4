# Cliente de Escritorio — Windows Forms

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11.
- Visual Studio con la carga **Desarrollo de escritorio de .NET**, o Visual Studio Code con SDK de .NET 8.
- API Java de vehículos disponible en `http://127.0.0.1:8080`.
- JWT válido para consultar vehículos.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-windows-forms`.
2. Se abre `ConsultaVehiculosWinForms.sln` en Visual Studio o la carpeta del repositorio en Visual Studio Code.
3. Se comprueba el SDK desde la terminal:

```powershell
dotnet --version
```

## 3. Restaurar y compilar

En la carpeta que contiene la solución:

```powershell
dotnet restore .\ConsultaVehiculosWinForms.sln
dotnet build .\ConsultaVehiculosWinForms.sln -c Release
```

## 4. Ejecutar

Desde la terminal:

```powershell
dotnet run --project .\ConsultaVehiculosWinForms\ConsultaVehiculosWinForms.csproj
```

Como alternativa, se ejecuta desde Visual Studio mediante `F5`.

## 5. Comprobar

1. Se inicia primero la API Java y se obtiene un JWT válido.
2. En la ventana se pega el token en el campo correspondiente.
3. Se presiona **Consultar** y se verifica el listado de vehículos y el contador.
4. Se cierra la ventana para finalizar.

> La aplicación incluida realiza la consulta de vehículos; otras operaciones requieren ampliación del cliente.
