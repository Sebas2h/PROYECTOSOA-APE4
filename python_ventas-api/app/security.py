"""Valida la identidad con Java y autoriza las operaciones de ventas."""
# Realiza solicitudes HTTP a las APIs Java.
import httpx
# Publica endpoints web y valida solicitudes.
from fastapi import Header
# Importa el componente local correspondiente a esta responsabilidad.
from app.config import JAVA_URL
from app.errors import ApiError


# Resuelve el JWT enviado en Authorization consultando a Java.
def identidad(authorization: str | None = Header(default=None)):
    # Exige un token con prefijo Bearer.
    if not authorization or not authorization.startswith("Bearer "):
        # Responde 401 cuando no hay una autenticación válida.
        raise ApiError(401, "NO_AUTENTICADO", "Enviar access token")
    # Protege la llamada HTTP o la interpretación del JSON.
    try:
        # Solicita a Java el nombre del usuario y su lista de roles.
        r = httpx.get(JAVA_URL + "/api/identidad",
                      # Reenvía el token recibido, sin inventar un JWT nuevo.
                      headers={"Authorization": authorization}, timeout=5)
    # Detecta que Java está desconectado o agotó el tiempo.
    except httpx.RequestError:
        # Devuelve 503 cuando no se puede comprobar la identidad.
        raise ApiError(503, "IDENTIDAD_NO_DISPONIBLE", "Java no responde")
    # Respeta un rechazo 401 o 403 originado por Java.
    if r.status_code in (401, 403):
        # Notifica un error a la capa responsable de gestionarlo.
        raise ApiError(r.status_code, "ACCESO_RECHAZADO", "Token no autorizado")
    # No acepta respuestas inesperadas del servicio de identidad.
    if r.status_code != 200:
        # Devuelve 503 cuando no se puede comprobar la identidad.
        raise ApiError(503, "IDENTIDAD_NO_DISPONIBLE", "No se validó la identidad")
    # El contrato de identidad exige un objeto con usuario y lista de roles.
    # Protege la llamada HTTP o la interpretación del JSON.
    try:
        # Convierte a objeto Python el JSON devuelto por Java.
        data = r.json()
        # Comprueba que se recibió un objeto JSON.
        if not isinstance(data, dict):
            # Notifica un error a la capa responsable de gestionarlo.
            raise ValueError("No es un objeto")
        # Exige un usuario textual en el contrato de identidad.
        if not isinstance(data.get("usuario"), str):
            # Notifica un error a la capa responsable de gestionarlo.
            raise ValueError("Usuario ausente")
        # Exige que roles sea una lista.
        if not isinstance(data.get("roles"), list):
            # Notifica un error a la capa responsable de gestionarlo.
            raise ValueError("Roles ausentes")
    # Captura JSON corrupto o un tipo de dato incorrecto.
    except (ValueError, TypeError):
        # Devuelve 503 cuando no se puede comprobar la identidad.
        raise ApiError(503, "IDENTIDAD_INVALIDA", "Respuesta de Java inválida")
    # Evita insertar usuarios más largos que la columna SQL.
    if len(data["usuario"]) > 100:
        # Notifica un error a la capa responsable de gestionarlo.
        raise ApiError(403, "IDENTIDAD_INVALIDA", "Usuario demasiado largo")
    # Devuelve usuario y roles validados al endpoint.
    return data


# Verifica si puede registrar compradores y ventas.
def vendedor(usuario):
    # Permite solo roles OPERADOR y ADMIN.
    if not {"ROLE_OPERADOR", "ROLE_ADMIN"}.intersection(usuario["roles"]):
        # Notifica un error a la capa responsable de gestionarlo.
        raise ApiError(403, "SIN_PERMISO", "Se requiere OPERADOR o ADMIN")


# Comprueba que pueda acceder a registros de ese usuario.
def propietario(usuario, dueno):
    # Acepta al propietario o a un ADMIN.
    if usuario["usuario"] != dueno and "ROLE_ADMIN" not in usuario["roles"]:
        # Notifica un error a la capa responsable de gestionarlo.
        raise ApiError(403, "SIN_PERMISO", "Recurso de otro usuario")
