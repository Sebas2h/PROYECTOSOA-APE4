# Bitácora de cambios — APE 04

## 2026-11-23 — Inventario inicial

- Se verificó la rama `feature/ape04-fase1-integracion` y su seguimiento remoto.
- Se registraron versiones de Java, Python, .NET, Node, npm y Postman CLI.
- Se detectó Maven global ausente y wrapper Maven presente solo en la API de vehículos.
- Se inspeccionaron manifiestos, configuraciones, entrypoints y rutas REST sin alterar los siete proyectos.
- Se comprobó `C:\NGINX\nginx.exe -t`: sintaxis correcta, verificación final bloqueada por permisos sobre logs/PID.
- Se constató que la línea base aún no implementa la arquitectura final de RabbitMQ, NGINX, monitor, PWA de ventas ni JavaFX de notificaciones.
- Se crearon `MAPA_PROYECTOS.md`, `ESTADO_APE04.md` y esta bitácora como memoria operativa.

No se declara ninguna de las 73 pruebas como aprobada en este hito.

## 2026-11-23 — P01 inicio y conectividad

- Se localizó y leyó el PROMPT MAESTRO anterior con el catálogo exacto P01–P28 y E29–E73.
- Se verificaron listeners reales de MySQL 3306, RabbitMQ 5672/15672, Java A 8080, Java B 8182, notificaciones 8181, FastAPI 8002, NGINX 8090 y monitor 8083.
- Postman Desktop ejecutó `GET http://127.0.0.1:8080/actuator/health` y obtuvo HTTP 200 con `status: UP`.
- Se guardó la captura auténtica `FIG_002_P01_HEALTH_JAVA_A_POSTMAN.png`, sin JWT ni credenciales visibles.
- P01 queda APROBADA. Las otras 72 pruebas permanecen sin aprobar hasta su ejecución y evidencia.

## 2026-11-23 — Diagnóstico de compilación y puertos

- WinForms y React compilaron correctamente.
- PWA obtuvo 6/7 pruebas unitarias; la prueba de proxy quedó afectada por la restricción de red del sandbox.
- El test de contexto de la API Java falló al abrir el socket MySQL desde el sandbox.
- Se verificó fuera del sandbox: MySQL 3306 y RabbitMQ 5672/15672 escuchan; el panel RabbitMQ respondió HTTP 200.
- No escuchan todavía NGINX 8090, API Java 8080 ni FastAPI 8002. Se observaron listeners adicionales en 5173, 8081, 8082 y 8083, aún sin identificación funcional completa.

## 2026-11-23 — Colección Postman P02–P28 y E29–E73

- Se generó `postman/APE04_72_PRUEBAS.postman_collection.json` con los 72 identificadores restantes y aserciones HTTP.
- Se generó `postman/APE04_LOCAL_SANITIZADO.postman_environment.json` sin contraseñas, JWT ni claves reales.
- Postman Desktop confirmó la importación de la colección y del entorno; la captura maximizada no contiene el cursor.
- Postman CLI ejecutó los 72 requests fuera del sandbox y guardó el reporte real en `evidencias/fase-02/postman_72_resultados_reales.json`.
- Resultado del Runner: 72 requests ejecutados, 22 respuestas HTTP 200, 50 respuestas HTTP 401, 119 aserciones, 27 aprobadas y 92 fallidas.
- Este resultado no cambia por sí solo el estado de las pruebas académicas: credenciales válidas, acciones GUI y caídas controladas siguen pendientes.
