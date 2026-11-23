"""Tratamiento centralizado de errores HTTP y errores del dominio."""
# Registra errores de la aplicación.
import logging
# Genera identificadores únicos.
from uuid import uuid4
# Publica endpoints web y valida solicitudes.
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
# Implementa las excepciones HTTP compatibles con FastAPI.
from starlette.exceptions import HTTPException
# Ofrece ORM, consultas y transacciones SQL.
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


# Excepción propia de negocio con estado HTTP, código interno y detalle.
class ApiError(Exception):

    # Constructor que agrupa los datos que necesita la respuesta de error.
    def __init__(self, status, codigo, detalle):
        # Conserva los valores para convertirlos después a JSON.
        self.status, self.codigo, self.detalle = status, codigo, detalle


# Construye un formato coherente para todos los errores HTTP.
def respuesta(req, status, codigo, detalle):
    # Genera un identificador único para buscar el fallo en registros.
    trace = str(uuid4())
    # Devuelve un JSON con el código HTTP indicado.
    return JSONResponse(status_code=status,
        # Identifica el formato application/problem+json.
        media_type="application/problem+json", content={
            # Incluye la URN que clasifica el tipo de problema.
            "type": "urn:ventas:" + codigo.lower(),
            # Guarda estado, detalle, ruta y código para depurar.
            "title": codigo, "status": status, "detail": detalle,
            # Registra en qué endpoint ocurrió el error.
            "instance": req.url.path, "codigo": codigo, "traceId": trace,
        })


# Registra los manejadores de errores en FastAPI.
def instalar(app):
    # Captura errores expresos de las reglas de negocio.
    @app.exception_handler(ApiError)
    # Registra un controlador de excepción asíncrono.
    async def negocio(req, ex):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return respuesta(req, ex.status, ex.codigo, ex.detalle)
    # Traduce fallos de validación de Pydantic a HTTP 422.
    @app.exception_handler(RequestValidationError)
    # Registra un controlador de excepción asíncrono.
    async def validar(req, ex):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return respuesta(req, 422, "VALIDACION", "; ".join(
            # Define un valor de cadena dentro del conjunto de datos.
            ".".join(map(str, e["loc"])) + ": " + e["msg"]
            # Procesa secuencialmente cada elemento disponible.
            for e in ex.errors()))
    # Normaliza excepciones HTTP propias del framework.
    @app.exception_handler(HTTPException)
    # Registra un controlador de excepción asíncrono.
    async def http(req, ex):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return respuesta(req, ex.status_code, "ERROR_HTTP", str(ex.detail))
    # Traduce claves duplicadas de base de datos a HTTP 409.
    @app.exception_handler(IntegrityError)
    # Registra un controlador de excepción asíncrono.
    async def integridad(req, ex):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return respuesta(req, 409, "CONFLICTO_DATOS", "Registro duplicado")
    # Agrupa errores generales de persistencia para HTTP 503.
    @app.exception_handler(SQLAlchemyError)
    # Registra un controlador de excepción asíncrono.
    async def bd(req, ex):
        # Registra la excepción completa solo en la consola del servidor.
        logging.error("Fallo de persistencia", exc_info=(type(ex), ex, ex.__traceback__))
        # Devuelve el valor indicado a la función que realizó la llamada.
        return respuesta(req, 503, "BD_NO_DISPONIBLE",
                         # Define un valor de cadena dentro del conjunto de datos.
                         "No se pudo acceder a la persistencia")
    # Evita revelar información sensible ante errores no previstos.
    @app.exception_handler(Exception)
    # Registra un controlador de excepción asíncrono.
    async def inesperado(req, ex):
        # Registra la excepción completa solo en la consola del servidor.
        logging.error("Fallo inesperado", exc_info=(type(ex), ex, ex.__traceback__))
        # Devuelve el valor indicado a la función que realizó la llamada.
        return respuesta(req, 500, "ERROR_INTERNO", "Error interno registrado")
