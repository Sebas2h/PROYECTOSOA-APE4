# Estado APE 04

Actualizado: 2026-11-23.

## Control de versiones

- Rama activa y remota: `feature/ape04-fase1-integracion`.
- Árbol de trabajo inicialmente limpio.
- `main`, `develop` y la rama feature parten del commit `8421b59` (`Proyectos iniciales sin modificaciones`).
- No se ha creado commit ni push de integración en esta sesión.

## Herramientas observadas

- Java: 17.0.19.
- Maven global: no disponible; la API Java de vehículos incluye `mvnw.cmd`.
- Python: 3.14.4.
- .NET SDK: 10.0.401.
- Node: 22.22.2; npm: 10.9.7.
- Postman CLI: 1.74.0.
- NGINX: `nginx.conf` sintácticamente aceptado, pero `nginx -t` no pudo abrir `C:\NGINX\logs\error.log` ni `nginx.pid` por acceso denegado desde esta sesión.

## Pruebas

- Aprobadas con evidencia completa: 1/73 (P01).
- Fallidas: 0/73.
- Bloqueadas/no ejecutadas: 72/73.
- Se localizó el `PROMPT MAESTRO — SOA APE 04` en los adjuntos anteriores. Este define P01 como inicio/conectividad y conserva el catálogo P01–P28 y E29–E73.
- P01 se ejecutó en Postman Desktop contra `GET http://127.0.0.1:8080/actuator/health`: HTTP 200 y `status: UP`. Evidencia: `evidencias/fase-01/FIG_002_P01_HEALTH_JAVA_A_POSTMAN.png`.

## Hallazgos prioritarios

1. Confirmados el 2026-11-23: MySQL 3306, RabbitMQ 5672/15672, Java A 8080, Java B 8182, notificaciones 8181, FastAPI 8002, NGINX 8090 y monitor 8083. React 5173 y PWA 5174 no escuchaban durante esta verificación.
2. La PWA y JavaFX requieren pegar un JWT, contrario al contrato objetivo.
3. El servicio de notificaciones no contiene aún el listener/persistencia RabbitMQ requeridos.
4. No existe infraestructura NGINX/SQL/monitor versionada.
5. `application.properties` contiene claves y contraseñas didácticas versionadas; deben sustituirse por variables de entorno y ejemplos sanitizados.

## Siguiente hito

Diagnóstico reproducible de compilación y arranque de cada proyecto, comprobación real de MySQL/RabbitMQ y externalización segura de configuración antes de integrar contratos.

## Diagnóstico de construcción inicial

- WinForms: compilación correcta, 0 errores y 2 advertencias de nulabilidad.
- React: `npm run build` correcto.
- PWA: 6/7 pruebas correctas; prueba de proxy falló bajo restricción de red del sandbox.
- API Java: test de contexto llegó a MySQL, pero falló bajo restricción de socket del sandbox; requiere repetir fuera del sandbox.
- Python: ejecución de `pytest` quedó bloqueada y fue interrumpida; requiere aislar el caso que cuelga.

