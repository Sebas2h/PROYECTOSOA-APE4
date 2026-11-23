"""Caso de uso de creación, conciliación y notificación de ventas."""
# Calcula hashes SHA-256.
import hashlib
# Interpreta o genera cuerpos JSON.
import json
# Genera identificadores únicos.
from uuid import uuid4
# Evita errores de redondeo en importes.
from decimal import Decimal
# Realiza solicitudes HTTP a las APIs Java.
import httpx
# Ofrece ORM, consultas y transacciones SQL.
from sqlalchemy.exc import IntegrityError
# Importa el componente local correspondiente a esta responsabilidad.
from app.db import SessionLocal
from app.models import Venta, Comprador
# Importa las consultas SQL de ventas desde la capa Repository.
from app.repositories.venta_repository import VentaRepository
from app.clients.vehiculos_client import VehiculosClient, FalloRemoto
# Importa el componente local correspondiente a esta responsabilidad.
from app.config import NOTIF_URL, NOTIF_KEY
from app.errors import ApiError
from app.security import propietario
# Prepara el cliente HTTP de reservas de Java.
remote = VehiculosClient()


# Convierte el objeto de base de datos a una respuesta pública sin secretos.
def salida(v):
    # Construye el JSON con identificadores y datos de la operación.
    return {"id": v.id, "operacionId": v.operacion_id,
            # Agrega IDs de vehículo y comprador referenciados.
            "vehiculoId": v.vehiculo_id, "compradorId": v.comprador_id,
            # Usa el precio establecido por Java; no por el cliente.
            "precioAcordado": str(v.precio_acordado)
                # Si Java aún no respondió, devuelve null para el precio.
                if v.precio_acordado is not None else None,
            # Incluye moneda y estado de la venta.
            "moneda": v.moneda, "estado": v.estado,
            # Indica si el receptor procesó la notificación.
            "notificacion": v.notificacion,
            # Presenta la fecha en formato ISO-8601 UTC.
            "fechaUTC": v.fecha.isoformat() + "Z"}


# Comienza el caso de uso de venta con JSON, clave y usuario.
def crear(datos, clave, usuario):
    # Serializa el cuerpo con un orden estable de claves.
    cuerpo = json.dumps(datos.model_dump(), sort_keys=True,
                        # Elimina diferencias irrelevantes de espacios en el JSON.
                        separators=(",", ":"))
    # Calcula SHA-256 del cuerpo para detectar cambios en un reintento.
    huella = hashlib.sha256(cuerpo.encode()).hexdigest()
    # Asume que es una repetición hasta comprobar lo contrario.
    nueva = False
    # Abre una sesión SQLAlchemy y la cierra al salir del bloque.
    with SessionLocal() as db:
        # Crea el repositorio encargado de buscar operaciones previas.
        repo = VentaRepository(db)
        # Comprueba si esta clave ya corresponde a una venta.
        v = repo.por_clave(usuario["usuario"], clave)
        # Si no existe, preparará una nueva operación.
        if v is None:
            # Busca el comprador antes de guardar la venta.
            comprador = db.get(Comprador, datos.compradorId)
            # Impide vender a un comprador inexistente.
            if comprador is None:
                # Responde con HTTP 404 para el comprador no registrado.
                raise ApiError(404, "COMPRADOR_NO_EXISTE", "Comprador inexistente")
            # Impide usar un comprador ajeno, salvo que sea ADMIN.
            propietario(usuario, comprador.usuario)
            # Construye la venta PENDIENTE, con UUID de operación único.
            v = Venta(operacion_id=str(uuid4()), usuario=usuario["usuario"],
                      # Asocia IDs y deja el precio pendiente de Java.
                      vehiculo_id=datos.vehiculoId, comprador_id=datos.compradorId,
                      # Asocia la clave de petición y su huella para reintentos seguros.
                      idempotency_key=clave, request_hash=huella)
            # Prepara el INSERT de la nueva venta.
            db.add(v)
            # Empieza una sección controlada para recuperar los errores esperados.
            try:
                # Confirma primero la venta PENDIENTE antes de llamar al otro servicio.
                db.commit()  # La operación existe antes de llamar a Java.
                # Registra que esta solicitud acaba de crear una operación.
                nueva = True
            # Gestiona una carrera donde otra petición guardó antes la misma clave.
            except IntegrityError:
                # Deshace el intento conflictivo para poder consultar de nuevo.
                db.rollback()
                # Comprueba si esta clave ya corresponde a una venta.
                v = repo.por_clave(usuario["usuario"], clave)
                # Si no existe, preparará una nueva operación.
                if v is None:
                    # Vuelve a lanzar la excepción original si tampoco existe tras el conflicto.
                    raise
        # Rechaza reutilizar una clave idempotente con distinto contenido.
        if v.request_hash != huella:
            # Devuelve 409 cuando la misma clave ya representa otra solicitud.
            raise ApiError(409, "CLAVE_REUTILIZADA",
                           # Explica al cliente por qué se rechazó reutilizar la clave.
                           "La misma clave requiere el mismo cuerpo")
        # Conserva el ID antes de cerrar la sesión.
        id = v.id
    # Solicita a Java reservar o confirmar la operación de forma recuperable.
    procesar(id)
    # Envía aviso solo si la venta terminó COMPLETADA.
    notificar(id)
    # Abre una sesión SQLAlchemy y la cierra al salir del bloque.
    with SessionLocal() as db:
        # Recarga la venta para devolver su estado actualizado.
        v = db.get(Venta, id)
        # Distingue un rechazo definitivo de una operación pendiente.
        if v.estado == "FALLIDA":
            # Entrega a Postman el rechazo procedente de la regla Java.
            raise ApiError(v.error_status or 409, "VENTA_RECHAZADA",
                           # Continúa la operación indicada en la línea de código.
                           v.error_detalle or "La venta fue rechazada")
        # Devuelve 201 nueva, 200 repetida o 202 pendiente de conciliación.
        status = (201 if nueva else 200) if v.estado == "COMPLETADA" else 202
        # Regresa el contenido de la venta y su código HTTP.
        return salida(v), status


# Concilia una venta local con las reservas del servicio Java.
def procesar(id):
    # Bloqueo por venta: solicitudes y trabajador no la procesan a la vez.
    # Abre transacción que hace commit automático si no hay excepción.
    with SessionLocal.begin() as db:
        # Obtiene la venta con bloqueo SQL para evitar procesamiento concurrente.
        v = VentaRepository(db).bloquear(id)
        # Si no existe, preparará una nueva operación.
        if v is None or v.estado in ("COMPLETADA", "FALLIDA"):
            # Finaliza inmediatamente porque ya no hay trabajo pendiente.
            return
        # Empieza una sección controlada para recuperar los errores esperados.
        try:
            # Empieza una sección controlada para recuperar los errores esperados.
            try:
                # Pregunta si Java ya conoce el UUID de operación.
                r = remote.por_operacion(v.operacion_id)
            # Distingue ausencia de reserva de fallos de red/servidor.
            except FalloRemoto as ex:
                # Solo crea una nueva reserva cuando Java confirmó que no existe.
                if ex.status != 404:
                    # Vuelve a lanzar la excepción original si tampoco existe tras el conflicto.
                    raise
                # Empieza una sección controlada para recuperar los errores esperados.
                try:
                    # Solicita reserva de un vehículo DISPONIBLE.
                    r = remote.reservar(v.vehiculo_id, v.operacion_id)
                # Analiza el rechazo que pudo devolver Java.
                except FalloRemoto as rechazo:
                    # Estos códigos significan fracaso de negocio confirmado.
                    if rechazo.status in (404, 409, 422):
                        # Marca la operación local como rechazada definitivamente.
                        v.estado = "FALLIDA"
                        # Guarda el código de estado para la respuesta HTTP.
                        v.error_status = rechazo.status
                        # Describe la causa del rechazo sin filtrar errores internos.
                        v.error_detalle = "Vehículo inexistente o no disponible"
                        # Continúa la operación indicada en la línea de código.
                        return
                    # Vuelve a lanzar la excepción original si tampoco existe tras el conflicto.
                    raise
            # Guarda el UUID de la reserva confirmable.
            v.reserva_id = r["id"]
            # Copia el precio oficial comunicado por Java.
            v.precio_acordado = Decimal(str(r["precio"]))
            # Almacena la moneda indicada por el otro servicio.
            v.moneda = r["moneda"]
            # Impide confirmar una reserva que ya fue cancelada.
            if r["estado"] == "LIBERADA":
                # Marca la operación local como rechazada definitivamente.
                v.estado = "FALLIDA"; v.error_status = 409
                # Guarda la explicación de la liberación.
                v.error_detalle = "Reserva liberada"
                # Continúa la operación indicada en la línea de código.
                return
            # Una reserva válida necesita confirmación en Java.
            if r["estado"] == "RESERVADA":
                # Confirma la reserva: Java actualiza vehículo a VENDIDO.
                r = remote.confirmar(r["id"])
            # Exige una respuesta coherente antes de finalizar la venta.
            if r["estado"] != "CONFIRMADA":
                # Trata el estado inesperado como un problema de integración.
                raise FalloRemoto(502, "Estado de reserva inesperado")
            # Solo se completa después de obtener CONFIRMADA de Java.
            v.estado = "COMPLETADA"
            # Guarda el código de estado para la respuesta HTTP.
            v.error_status = None; v.error_detalle = None
        # Un timeout o cuerpo inválido necesita investigación, no duplicar venta.
        except (FalloRemoto, ValueError, KeyError) as ex:
            # Permite que el worker vuelva a consultar a Java más tarde.
            v.estado = "EN_REVISION"
            # Describe por qué la operación no terminó.
            v.error_detalle = "Pendiente de consultar y conciliar con Java"


# Publica un aviso de venta exitosa al servicio Java receptor.
def notificar(id):
    # Abre transacción que hace commit automático si no hay excepción.
    with SessionLocal.begin() as db:
        # Obtiene la venta con bloqueo SQL para evitar procesamiento concurrente.
        v = VentaRepository(db).bloquear(id)
        # Si no existe, preparará una nueva operación.
        if v is None or v.estado != "COMPLETADA" or v.notificacion == "ENVIADA":
            # Finaliza inmediatamente porque ya no hay trabajo pendiente.
            return
        # Empieza una sección controlada para recuperar los errores esperados.
        try:
            # Hace un POST HTTP al receptor de notificaciones.
            r = httpx.post(NOTIF_URL + "/api/notificaciones", timeout=3,
                # Envía la clave compartida; debe coincidir con el filtro Java.
                headers={"X-Notification-Key": NOTIF_KEY}, json={
                    # Agrega IDs de vehículo y comprador referenciados.
                    "vehiculoId": v.vehiculo_id, "tipo": "VENTA",
                    # Usa el correo del comprador de esta venta.
                    "destinatario": v.comprador.correo,
                    # Construye un mensaje rastreable por ID y UUID.
                    "mensaje": f"Venta {v.id} operación {v.operacion_id} completada",
                })
            # Marca como ENVIADA solo ante HTTP exitoso 2xx.
            v.notificacion = "ENVIADA" if 200 <= r.status_code < 300 else "PENDIENTE"
        # Si hay un problema de red, conserva la notificación pendiente.
        except httpx.RequestError:
            # Permite reintento posterior del worker.
            v.notificacion = "PENDIENTE"
