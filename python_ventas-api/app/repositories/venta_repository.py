"""Consultas SQLAlchemy para el seguimiento e idempotencia de ventas."""
# Ofrece ORM, consultas y transacciones SQL.
from sqlalchemy import select, or_
# Importa el componente local correspondiente a esta responsabilidad.
from app.models import Venta


# Aísla las consultas SQLAlchemy del resto de la aplicación.
class VentaRepository:

    # Recibe la sesión de base de datos creada por otra capa.
    def __init__(self, db):
        # Almacena la sesión para realizar las consultas.
        self.db = db

    # Busca una venta previa perteneciente al usuario y clave indicados.
    def por_clave(self, usuario, clave):
        # Lee una sola venta que cumple la condición.
        return self.db.scalar(select(Venta).where(
            # Filtra por propietario y clave idempotente al mismo tiempo.
            Venta.usuario == usuario, Venta.idempotency_key == clave))

    # Bloquea la fila para evitar que dos operaciones la procesen simultáneamente.
    def bloquear(self, id):
        # Lee una sola venta que cumple la condición.
        return self.db.scalar(select(Venta).where(Venta.id == id)
                              # Solicita bloqueo de fila en MySQL hasta terminar la transacción.
                              .with_for_update())

    # Consulta ventas sin completar y avisos aún no enviados.
    def pendientes(self):
        # Devuelve el valor indicado a la función que realizó la llamada.
        return self.db.scalars(select(Venta.id).where(or_(
            # Incluye ventas PENDIENTE o EN_REVISION.
            Venta.estado.in_(["PENDIENTE", "EN_REVISION"]),
            # Incluye las COMPLETADAS que todavía requieren notificación.
            (Venta.estado == "COMPLETADA") &
            # Asigna o configura el valor de esta instrucción.
            (Venta.notificacion != "ENVIADA")))
            # Ordena por ID y procesa como máximo 100 por iteración.
            .order_by(Venta.id).limit(100)).all()
