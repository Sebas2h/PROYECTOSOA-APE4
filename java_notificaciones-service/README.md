# Servicio de Notificaciones — Java Spring Boot

**Autor:** Javier Vargas

## 1. Software necesario

- Windows 10 u 11 y Visual Studio Code.
- JDK 17 y Apache Maven instalado.
- Postman para comprobar el servicio.

## 2. Preparar el proyecto

1. Se descarga o clona `soa-notificaciones-java` y se abre la carpeta principal, donde se encuentra `pom.xml`.
2. Se crea o recupera localmente `src/main/resources/application.properties`.
3. Se configura el puerto `8081` y `app.notificacion-key` con la clave privada compartida por los servicios autorizados. Esta clave debe permanecer fuera de Git.
4. Se verifica la instalación:

```powershell
java -version
mvn -version
```

## 3. Compilar

```powershell
mvn clean package -DskipTests
```

El archivo compilado queda en `target`.

## 4. Ejecutar

```powershell
mvn spring-boot:run
```

Se mantiene abierta la terminal con el servicio en `http://127.0.0.1:8081`, si se conserva el puerto configurado.

## 5. Comprobar

1. En Postman se realiza `POST http://127.0.0.1:8081/api/notificaciones`.
2. Se agrega la cabecera `X-Notification-Key` con la clave autorizada y `Content-Type: application/json`.
3. Se envía un JSON válido con `vehiculoId`, `destinatario`, `tipo` y `mensaje`.
4. Se verifica la respuesta HTTP `201` para un registro correcto.
5. Se detiene el servicio con `Ctrl + C`.

> Esta versión recibe notificaciones por HTTP REST. No se debe dar por implementado RabbitMQ únicamente por ejecutar este proyecto.
