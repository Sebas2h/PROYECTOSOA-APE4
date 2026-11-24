"""Parámetros de integración obtenidos del archivo .env de ventas-api."""
# Obtiene parámetros del sistema y variables de entorno.
import os
# Maneja rutas de archivos de forma portable.
from pathlib import Path
# Carga variables de configuración desde .env.
from dotenv import load_dotenv
# Cargar siempre el .env junto a requirements.txt, incluso desde otra carpeta.
# Carga el archivo .env desde la raíz del proyecto, aunque se ejecute desde otra ruta.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


# Define una función que obliga a configurar cada parámetro indispensable.
def requerido(nombre):
    # Lee el valor de la variable indicada desde el entorno.
    valor = os.environ.get(nombre, "")
    # Comprueba que la variable no esté vacía.
    if not valor:
        # Detiene el arranque con un error claro cuando falta configuración.
        raise RuntimeError(f"Falta configurar {nombre}")
    # Entrega la configuración que pasó la comprobación.
    return valor
# Guarda la dirección base de Spring Boot y quita la barra final.
JAVA_URL = requerido("JAVA_URL").rstrip("/")
# Toma la clave privada que Java verifica en X-Service-Key.
SERVICE_KEY = requerido("VENTAS_SERVICE_KEY")
# Define la URL del receptor Java de notificaciones.
NOTIF_URL = requerido("NOTIFICACIONES_URL").rstrip("/")
# Lee la clave de autenticación del receptor de avisos.
NOTIF_KEY = requerido("NOTIFICACIONES_KEY")
NOTIFICATION_TRANSPORT = os.getenv("NOTIFICATION_TRANSPORT", "rabbitmq").lower()
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "127.0.0.1")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "ventas.events")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "venta.completada")
# Valida que ambas claves de integración tengan 32 caracteres o más.
if min(len(SERVICE_KEY), len(NOTIF_KEY)) < 32:
    # Detiene el arranque con un error claro cuando falta configuración.
    raise RuntimeError("Claves de servicio de al menos 32 caracteres")

# Comprueba que el docente reemplazó los textos de ejemplo por claves reales.
if SERVICE_KEY.startswith("COLOCA_") or NOTIF_KEY.startswith("COLOCA_"):
    # Impide continuar si faltan credenciales de integración.
    raise RuntimeError("Reemplaza las claves de ejemplo en el archivo .env")
