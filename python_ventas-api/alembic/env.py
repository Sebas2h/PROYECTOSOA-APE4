"""Migraciones restringidas a las tablas de la API Python."""
# Gestiona migraciones controladas del esquema.
from alembic import context
# Importa el componente local correspondiente a esta responsabilidad.
from app.db import Base, engine
# Obtiene parámetros del sistema y variables de entorno.
from app import models  # Importar modelos para poblar Base.metadata.
# Lista blanca de tablas que puede manejar Python, sin tocar las Java.
TABLAS_PYTHON = {"compradores", "ventas"}
# Referencia las definiciones de entidades SQLAlchemy.
target_metadata = Base.metadata


# Filtra por nombre las tablas visibles durante autogeneración.
def incluir_nombre(nombre, tipo, nombres_padre):
    # No reflejar ni comparar tablas que administra Spring Boot.
    # Solo aplica la comparación a objetos tipo tabla.
    if tipo == "table":
        # Impide incluir tablas ajenas a compradores/ventas.
        return nombre in TABLAS_PYTHON
    # Devuelve el valor indicado a la función que realizó la llamada.
    return True


# Añade una segunda barrera para limitar las tablas administradas.
def incluir_objeto(objeto, nombre, tipo, reflejado, comparar):
    # Defensa adicional para autogeneración posterior (NO requerida ahora).
    # Solo aplica la comparación a objetos tipo tabla.
    if tipo == "table":
        # Impide incluir tablas ajenas a compradores/ventas.
        return nombre in TABLAS_PYTHON
    # Devuelve el valor indicado a la función que realizó la llamada.
    return True


# Define cómo generar SQL sin conectarse a la base.
def run_migrations_offline():
    # Configura conexión, metadatos y filtros de Alembic.
    context.configure(
        # Usa la conexión de SQLAlchemy creada con datos de .env.
        url=str(engine.url),
        # Suministra el modelo ORM como referencia.
        target_metadata=target_metadata,
        # Excluye de comparación las tablas de la API Java.
        include_name=incluir_nombre,
        # Protege la revisión de objetos no administrados por Python.
        include_object=incluir_objeto,
        # Permite detectar diferencias de tipos de columna.
        compare_type=True,
        # En modo offline escribe literales SQL directamente.
        literal_binds=True,
    )
    # Abre el bloque transaccional de migración.
    with context.begin_transaction():
        # Ejecuta las revisiones pendientes.
        context.run_migrations()


# Define cómo aplicar cambios con conexión real de MySQL.
def run_migrations_online():
    # Abre conexión real para las migraciones.
    with engine.connect() as connection:
        # Configura conexión, metadatos y filtros de Alembic.
        context.configure(
            # Reutiliza la conexión a MySQL.
            connection=connection,
            # Suministra el modelo ORM como referencia.
            target_metadata=target_metadata,
            # Excluye de comparación las tablas de la API Java.
            include_name=incluir_nombre,
            # Protege la revisión de objetos no administrados por Python.
            include_object=incluir_objeto,
            # Permite detectar diferencias de tipos de columna.
            compare_type=True,
        )
        # Abre el bloque transaccional de migración.
        with context.begin_transaction():
            # Ejecuta las revisiones pendientes.
            context.run_migrations()
# Distingue generación SQL de aplicación directa.
if context.is_offline_mode():
    # Procesa migraciones offline.
    run_migrations_offline()
# Ejecuta la rama alternativa cuando la condición anterior es falsa.
else:
    # Procesa migraciones conectadas a MySQL.
    run_migrations_online()
