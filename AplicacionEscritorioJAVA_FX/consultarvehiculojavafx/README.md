# Cliente de Escritorio — JavaFX

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11 y Visual Studio Code.
- JDK 17 y Apache Maven instalado.
- Extensión **Extension Pack for Java** (recomendada).
- API Java de vehículos en `http://127.0.0.1:8080` y JWT válido.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-javafx` y se abre su carpeta principal, que contiene `pom.xml`.
2. Se verifica el JDK y Maven:

```powershell
java -version
javac -version
mvn -version
```

3. Se comprueba que Maven utilice Java 17. No se requiere instalar JavaFX SDK por separado; Maven obtiene las dependencias.

## 3. Compilar

```powershell
mvn clean compile
```

## 4. Ejecutar

```powershell
mvn javafx:run
```

## 5. Comprobar

1. Se inicia la API Java y se obtiene un JWT autorizado.
2. Se pega el JWT en la ventana JavaFX.
3. Se presiona **Consultar**.
4. Se verifica la tabla de vehículos, el contador y el mensaje HTTP.
5. Se cierra la ventana para finalizar.

> La versión incluida consulta vehículos. La recepción de notificaciones de ventas corresponde a una ampliación posterior.
