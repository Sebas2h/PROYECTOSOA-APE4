"""Cliente HTTP de Python para consultar y reservar vehículos en Java."""
# Realiza solicitudes HTTP a las APIs Java.
import httpx
# Importa el componente local correspondiente a esta responsabilidad.
from app.config import JAVA_URL, SERVICE_KEY


# Excepción para identificar errores HTTP del servicio Java.
class FalloRemoto(Exception):

    # Memoriza código HTTP y explicación del fallo remoto.
    def __init__(self, status, detalle):
        # Deja disponibles el estado y el detalle para el Service.
        self.status, self.detalle = status, detalle


# Cliente concentrado en llamadas a los endpoints internos de reservas.
class VehiculosClient:

    # Método reutilizable para enviar cualquier petición de reservas.
    def llamar(self, metodo, ruta, **kwargs):
        # Empieza una sección controlada para recuperar los errores esperados.
        try:
            # Realiza la petición HTTP hacia Java en el puerto configurado.
            r = httpx.request(metodo, JAVA_URL + ruta,
                # Autentica las rutas internas mediante la clave de servicio.
                headers={"X-Service-Key": SERVICE_KEY},
                # Limita los segundos de conexión y lectura para no quedar bloqueado.
                timeout=httpx.Timeout(5, connect=2), **kwargs)
        # Detecta un timeout o un fallo de red; el resultado puede ser incierto.
        except httpx.RequestError:
            # No asegura que Java haya fallado; permite conciliación posterior.
            raise FalloRemoto(503, "Resultado remoto desconocido")
        # Traduce cualquier rechazo HTTP de Java a FalloRemoto.
        if r.status_code >= 400:
            # Conserva el estado del rechazo para distinguir 404/409 de 503.
            raise FalloRemoto(r.status_code, "Operación Java rechazada")
        # Empieza una sección controlada para recuperar los errores esperados.
        try:
            # Devuelve el cuerpo JSON de la respuesta si existe.
            return r.json() if r.content else None
        # Captura un cuerpo remoto que no es JSON válido.
        except ValueError:
            # Notifica un error a la capa responsable de gestionarlo.
            raise FalloRemoto(502, "Respuesta Java ilegible")

    # Busca una reserva ya iniciada por el mismo operacionId.
    def por_operacion(self, op):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return self.llamar("GET", "/api/reservas",
                           # Envía el UUID para evitar crear una segunda reserva.
                           params={"operacionId": op})

    # Reserva un vehículo disponible a través de Java.
    def reservar(self, vehiculo, op):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return self.llamar("POST", f"/api/vehiculos/{vehiculo}/reservas",
                           # Entrega el UUID compartido para conseguir idempotencia entre servicios.
                           json={"operacionId": op})

    # Confirma la reserva; Java cambia el vehículo a VENDIDO.
    def confirmar(self, reserva):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return self.llamar("PUT", f"/api/reservas/{reserva}/confirmacion")
