"""Migración inicial de las dos tablas administradas por Python."""
# Gestiona migraciones controladas del esquema.
from alembic import op
# Ofrece ORM, consultas y transacciones SQL.
import sqlalchemy as sa
# Identificador de la migración inicial.
revision = "0001"
# Es la primera migración: no existe versión anterior.
down_revision = None
# No necesita etiquetas de rama.
branch_labels = None
# No depende de otras revisiones.
depends_on = None


# Crea solamente las dos tablas propias de la API Python.
def upgrade():
    # Define la tabla de compradores.
    op.create_table("compradores",
        # Columna ID y clave primaria de cada tabla.
        sa.Column("id", sa.Integer, primary_key=True),
        # Dueño del registro con NOT NULL.
        sa.Column("usuario", sa.String(100), nullable=False),
        # Documento de identificación.
        sa.Column("documento", sa.String(30), nullable=False),
        # Nombre del comprador.
        sa.Column("nombre", sa.String(120), nullable=False),
        # Correo del comprador.
        sa.Column("correo", sa.String(200), nullable=False),
        # Define unicidad para evitar compradores u operaciones duplicados.
        sa.UniqueConstraint("usuario", "documento",
                            # Asigna o configura el valor de esta instrucción.
                            name="uq_comprador_usuario_documento"))
    # Define la tabla de ventas, sin modificar vehiculos.
    op.create_table("ventas",
        # Columna ID y clave primaria de cada tabla.
        sa.Column("id", sa.Integer, primary_key=True),
        # UUID que identifica la operación en Java.
        sa.Column("operacion_id", sa.String(36), nullable=False, unique=True),
        # Dueño del registro con NOT NULL.
        sa.Column("usuario", sa.String(100), nullable=False),
        # Clave foránea hacia compradores.id.
        sa.Column("comprador_id", sa.Integer,
                  # Asigna o configura el valor de esta instrucción.
                  sa.ForeignKey("compradores.id"), nullable=False),
        # ID de vehículo de Java, almacenado sin FK local.
        sa.Column("vehiculo_id", sa.Integer, nullable=False),
        # Clave que impide duplicar intentos.
        sa.Column("idempotency_key", sa.String(100), nullable=False),
        # Hash que valida que un reintento no cambió el cuerpo.
        sa.Column("request_hash", sa.String(64), nullable=False),
        # Estado actual de la venta.
        sa.Column("estado", sa.String(20), nullable=False),
        # ID de reserva opcional generado por Java.
        sa.Column("reserva_id", sa.String(36)),
        # Precio establecido por el servicio de vehículos.
        sa.Column("precio_acordado", sa.Numeric(12,2)),
        # Moneda de la transacción.
        sa.Column("moneda", sa.String(3)),
        # Código HTTP de error, cuando exista.
        sa.Column("error_status", sa.Integer),
        # Descripción del fallo o estado pendiente.
        sa.Column("error_detalle", sa.String(250)),
        # Estado del intento de notificación.
        sa.Column("notificacion", sa.String(20), nullable=False),
        # Fecha de creación UTC.
        sa.Column("fecha", sa.DateTime, nullable=False),
        # Define unicidad para evitar compradores u operaciones duplicados.
        sa.UniqueConstraint("usuario", "idempotency_key",
                            # Asigna o configura el valor de esta instrucción.
                            name="uq_venta_usuario_clave"))


# Deshabilita revertir automáticamente evitando DROP TABLE.
def downgrade():
    # Impide borrar tablas y perder datos durante el taller.
    raise RuntimeError("Reversión con borrado de tablas deshabilitada")
