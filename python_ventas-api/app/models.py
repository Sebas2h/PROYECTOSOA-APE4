"""Entidades Comprador y Venta; no redefine la tabla vehiculos de Java."""
# Controla la pausa entre reintentos.
from datetime import datetime, timezone
# Evita errores de redondeo en importes.
from decimal import Decimal
# Ofrece ORM, consultas y transacciones SQL.
from sqlalchemy import String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
# Importa el componente local correspondiente a esta responsabilidad.
from app.db import Base


# Define la entidad SQLAlchemy que representa a un comprador.
class Comprador(Base):
    # Especifica el nombre físico de la tabla MySQL.
    __tablename__ = "compradores"
    # Declara restricciones de integridad adicionales.
    __table_args__ = (
        # Impide duplicados de la combinación de campos indicada.
        UniqueConstraint("usuario", "documento",
                         # Asigna o configura el valor de esta instrucción.
                         name="uq_comprador_usuario_documento"),
    )
    # Identificador autogenerado de la fila.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Usuario dueño del registro, obtenido del JWT validado por Java.
    usuario: Mapped[str] = mapped_column(String(100))
    # Número de identificación del comprador, guardado como texto.
    documento: Mapped[str] = mapped_column(String(30))
    # Nombre completo del comprador.
    nombre: Mapped[str] = mapped_column(String(120))
    # Correo donde se referencia la notificación de venta.
    correo: Mapped[str] = mapped_column(String(200))
    # Relación ORM para navegar de un comprador a sus ventas.
    ventas: Mapped[list["Venta"]] = relationship(
        # Asigna o configura el valor de esta instrucción.
        back_populates="comprador")


# Define una venta en Python; el vehículo pertenece al servicio Java.
class Venta(Base):
    # Especifica el nombre físico de la tabla MySQL.
    __tablename__ = "ventas"
    # Declara restricciones de integridad adicionales.
    __table_args__ = (
        # Impide duplicados de la combinación de campos indicada.
        UniqueConstraint("usuario", "idempotency_key",
                         # Asigna o configura el valor de esta instrucción.
                         name="uq_venta_usuario_clave"),
    )
    # Identificador autogenerado de la fila.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Identificador UUID para reconocer la misma operación en Java.
    operacion_id: Mapped[str] = mapped_column(String(36), unique=True)
    # Usuario dueño del registro, obtenido del JWT validado por Java.
    usuario: Mapped[str] = mapped_column(String(100))
    # Columna que referencia mediante una clave foránea al comprador.
    comprador_id: Mapped[int] = mapped_column(
        # Crea la referencia a compradores.id dentro de las tablas Python.
        ForeignKey("compradores.id"))
    # Conserva únicamente el ID remoto del vehículo administrado por Java.
    vehiculo_id: Mapped[int]
    # Clave aportada por el cliente para evitar ventas duplicadas.
    idempotency_key: Mapped[str] = mapped_column(String(100))
    # Huella SHA-256 para detectar reutilización de la clave con otro JSON.
    request_hash: Mapped[str] = mapped_column(String(64))
    # Estado local de la operación: PENDIENTE, EN_REVISION, COMPLETADA o FALLIDA.
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    # UUID de la reserva que creó Java; puede no existir todavía.
    reserva_id: Mapped[str | None] = mapped_column(String(36))
    # Importe confirmado por Java, no enviado libremente por el cliente.
    precio_acordado: Mapped[Decimal | None] = mapped_column(Numeric(12,2))
    # Moneda comunicada por el servicio de reservas.
    moneda: Mapped[str | None] = mapped_column(String(3))
    # Código HTTP de un rechazo definitivo, si existe.
    error_status: Mapped[int | None]
    # Detalle comprensible del último error de la venta.
    error_detalle: Mapped[str | None] = mapped_column(String(250))
    # Estado del aviso: PENDIENTE o ENVIADA.
    notificacion: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    # Registra en UTC el instante de creación de la venta.
    fecha: Mapped[datetime] = mapped_column(
        # Genera la fecha actual, guardada sin zona para MySQL.
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    # Relación ORM desde la venta hasta su comprador.
    comprador: Mapped[Comprador] = relationship(back_populates="ventas")
