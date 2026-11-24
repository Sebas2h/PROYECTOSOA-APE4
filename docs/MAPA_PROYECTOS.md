# Mapa compacto de proyectos — APE 04

Actualizado: 2026-11-23. Rama de trabajo: `feature/ape04-fase1-integracion`.

| Proyecto | Tecnología | Función observada | Puerto actual/objetivo | Estado inicial |
|---|---|---|---|---|
| `java_venta-vehiculos-api_security` | Java 17, Spring Boot, JPA, JWT | OAuth y API de vehículos | 8080 y futura réplica 8082 | Código original; usa MySQL `venta_vehiculos`; wrapper Maven disponible |
| `python_ventas-api` | Python, FastAPI, SQLAlchemy | Compradores y ventas con idempotencia | 8002 | Código parcial; requiere `.env`; notifica por HTTP, sin RabbitMQ confirmado |
| `java_notificaciones-service` | Java 17, Spring Boot | Recepción HTTP de notificaciones | 8081 | Solo API HTTP en la línea base; sin persistencia/listener RabbitMQ |
| `AplicacionEscritorioWINDOWS_FORMS` | C# / WinForms | Consulta de vehículos | cliente | Código original orientado a consulta; falta alcance APE 04 |
| `AplicacionEscritorioJAVA_FX` | JavaFX | Consulta de vehículos con JWT pegado | cliente | No consulta notificaciones ni actualiza automáticamente |
| `AplicacionWebREACT/react-fetch-vehiculos` | React 19, Vite | Consulta de vehículos | 5173 | Consulta básica mediante proxy directo a Java |
| `AplicacionMovilPWA` | JavaScript, Node | Consulta de vehículos | 5174 objetivo | Actualmente solicita pegar JWT; no autentica ni registra ventas |

## Infraestructura objetivo pendiente de verificar/crear

- NGINX local: instalación aportada en `C:\NGINX`; objetivo `http://localhost:8090`.
- MySQL/MariaDB: XAMPP aportado como activo; objetivo 3306 con esquemas separados.
- RabbitMQ: aportado como activo; objetivos 5672 y panel 15672.
- Monitor: objetivo 8083.
- Todo cliente HTTP deberá pasar por NGINX y la API Java deberá operar en 8080/8082.

## Orden de integración

1. Sanear configuración y secretos; comprobar esquemas MySQL.
2. Construir y arrancar API Java A/B.
3. Completar FastAPI, RabbitMQ y notificaciones persistentes.
4. Incorporar NGINX, health y monitor.
5. Adaptar WinForms, React, PWA y JavaFX a sus responsabilidades.
6. Ejecutar pruebas por servicio, integración y fallos controlados.

