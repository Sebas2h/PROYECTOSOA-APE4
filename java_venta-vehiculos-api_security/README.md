# API de Vehículos — Java Spring Boot

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11 y Visual Studio Code (o IntelliJ IDEA).
- JDK 17 y conexión a Internet para descargar dependencias Maven.
- MySQL o XAMPP con la base `venta_vehiculos` y sus tablas existentes.
- Postman para comprobar los endpoints.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-vehiculos-java` y se abre su carpeta principal, donde se encuentran `pom.xml` y `mvnw.cmd`.
2. Se inicia MySQL y se verifica la base `venta_vehiculos`.
3. Se crea o recupera localmente `src/main/resources/application.properties`. Se configuran la conexión MySQL, el puerto `8080`, los valores JWT, el usuario inicial y las claves de integración que exige el proyecto. El archivo no se publica en Git.
4. Se comprueba la instalación:

```powershell
java -version
.\mvnw.cmd -version
```

## 3. Compilar

En la terminal de la carpeta principal:

```powershell
.\mvnw.cmd clean package -DskipTests
```

El archivo compilado queda en la carpeta `target`.

## 4. Ejecutar

```powershell
.\mvnw.cmd spring-boot:run
```

Se mantiene abierta la terminal. La API utilizará `http://127.0.0.1:8080` cuando se conserve el puerto configurado.

## 5. Comprobar

1. En Postman se obtiene un JWT mediante `POST http://127.0.0.1:8080/oauth/token`, con las credenciales autorizadas por la configuración local.
2. Se realiza `GET http://127.0.0.1:8080/api/vehiculos` con la cabecera `Authorization: Bearer <JWT>`.
3. Se verifica el código HTTP y la respuesta JSON.
4. Se detiene el servidor con `Ctrl + C`.

> Los archivos de configuración con secretos permanecen fuera del repositorio.
