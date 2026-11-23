"""Engine, sesiones y Base ORM que usan las tablas Python."""
# Obtiene parámetros del sistema y variables de entorno.
import os
# Ofrece ORM, consultas y transacciones SQL.
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker
# Importa el componente local correspondiente a esta responsabilidad.
from app.config import requerido
# Construye una URL de conexión segura sin concatenar manualmente la contraseña.
url = URL.create(
    # Selecciona el controlador PyMySQL para acceder a XAMPP.
    "mysql+pymysql",
    # Usa el usuario definido en .env.
    username=requerido("DB_USER"), # usuario XAMPP compartido
    # Usa la contraseña de la base, que en un XAMPP local podría estar vacía.
    password=os.getenv("DB_PASSWORD", ""), # XAMPP local puede no tener contraseña
    # Indica el servidor MySQL.
    host=requerido("DB_HOST"),
    # Convierte a entero el puerto MySQL configurado.
    port=int(os.getenv("DB_PORT", "3306")),
    # Selecciona la base venta_vehiculos, compartida con Java.
    database=requerido("DB_NAME"),
    # Pide UTF-8 de cuatro bytes para admitir acentos y otros símbolos.
    query={"charset": "utf8mb4"},
)
# Crea el motor y verifica las conexiones antes de reutilizarlas.
engine = create_engine(url, pool_pre_ping=True,
                       # Usa el nivel de aislamiento READ COMMITTED.
                       isolation_level="READ COMMITTED")
# Define el constructor de sesiones que usarán Router y Service.
SessionLocal = sessionmaker(engine, expire_on_commit=False)


# Clase base para registrar solo las tablas propias de Python.
class Base(DeclarativeBase):
    # No necesita métodos adicionales: SQLAlchemy implementa el ORM.
    pass
