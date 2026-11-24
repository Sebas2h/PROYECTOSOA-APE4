# Bitácora de errores — APE 04

## 2026-11-23 — Ruta health a través de NGINX

- Error observado: `GET http://127.0.0.1:8090/actuator/health` devolvió HTTP 404.
- Causa comprobada: la configuración NGINX no publica esa ruta general; enruta las rutas de API configuradas y mantiene `/nginx-ping` como comprobación propia.
- Corrección: pendiente de decidir por contrato; no se modificó NGINX para ocultar el hallazgo.
- Reintento: pendiente dentro de P26/E68 y las rutas reales del proxy.
- Estado: abierto.

## 2026-11-23 — Postman CLI sin acceso a localhost dentro del sandbox

- Error observado: los 72 requests devolvieron `connect EACCES 127.0.0.1:8090` en el primer intento.
- Causa comprobada: restricción de sockets del sandbox; los mismos servicios respondían fuera de ese entorno.
- Corrección: repetir el mismo Runner con autorización fuera del sandbox.
- Reintento: 72 requests llegaron a NGINX; se obtuvieron 22 HTTP 200 y 50 HTTP 401.
- Estado: corregido para conectividad; permanecen pendientes las credenciales y precondiciones funcionales.
