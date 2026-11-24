"""Endpoints REST de compradores y ventas."""
# Carga tipos y funciones que se utilizarán más abajo.
from typing import Annotated
# Publica endpoints web y valida solicitudes.
from fastapi import APIRouter, Depends, Header, Response
# Importa el componente local correspondiente a esta responsabilidad.
from app.db import SessionLocal
from app.models import Venta, Comprador
from app.schemas import CrearVenta, CrearComprador
from app.security import identidad, vendedor, propietario
from app.errors import ApiError
from app.services import venta_service as service
from sqlalchemy import select
# Crea el agrupador de rutas HTTP con prefijo /api.
router = APIRouter(prefix="/api")


# Expone POST /api/compradores; cuando crea devuelve HTTP 201.
@router.post("/compradores", status_code=201)
# Recibe JSON validado y usuario autenticado por Java.
def crear_comprador(d: CrearComprador, u=Depends(identidad)):
    # Comprueba permisos de OPERADOR o ADMIN.
    vendedor(u)
    # Abre una transacción que confirma automáticamente al concluir.
    with SessionLocal.begin() as db:
        # Crea el comprador y guarda el propietario real autenticado.
        c = Comprador(usuario=u["usuario"], **d.model_dump())
        # Registra la entidad y ejecuta el INSERT para obtener el ID.
        db.add(c); db.flush()
        # Envía al cliente el nuevo comprador sin exponer campos internos.
        return {"id": c.id, "nombre": c.nombre, "correo": c.correo}


@router.get("/compradores")
def listar_compradores(u=Depends(identidad)):
    with SessionLocal() as db:
        consulta = select(Comprador)
        if "ROLE_ADMIN" not in u["roles"]:
            consulta = consulta.where(Comprador.usuario == u["usuario"])
        return [{"id": c.id, "documento": c.documento,
                 "nombre": c.nombre, "correo": c.correo}
                for c in db.scalars(consulta.order_by(Comprador.id)).all()]


# Expone POST /api/ventas; requiere JWT y Idempotency-Key.
@router.post("/ventas")
# Acepta el cuerpo validado, la respuesta y la clave idempotente.
def crear(d: CrearVenta, response: Response,
          # Declara cabecera HTTP obligatoria Idempotency-Key.
          idempotency_key: Annotated[str, Header(
              # Limita longitud y caracteres admitidos en la clave.
              min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")],
          # Pide a FastAPI validar la identidad antes de entrar al endpoint.
          u=Depends(identidad)):
    # Comprueba permisos de OPERADOR o ADMIN.
    vendedor(u)
    # Delegación: las reglas y comunicación Java viven en el Service.
    resultado, codigo = service.crear(d, idempotency_key, u)
    # Asigna 201, 200 o 202 según el resultado.
    response.status_code = codigo
    # Informa la URL REST donde puede consultarse esta venta.
    response.headers["Location"] = f"/api/ventas/{resultado['id']}"
    # Entrega el JSON generado por el servicio.
    return resultado


# Expone GET /api/ventas/{id} para consultar la operación.
@router.get("/ventas/{id}")
# Obtiene un identificador y usuario autenticado.
def obtener(id: int, u=Depends(identidad)):
    # Gestiona automáticamente la apertura y cierre del recurso.
    with SessionLocal() as db:
        # Busca la venta mediante clave primaria.
        v = db.get(Venta, id)
        # Comprueba si la venta solicitada no existe.
        if v is None:
            # Responde 404 en vez de un error genérico.
            raise ApiError(404, "VENTA_NO_EXISTE", "Venta inexistente")
        # Restringe la consulta al dueño o administrador.
        propietario(u, v.usuario)
        # Devuelve el mismo formato JSON que POST.
        return service.salida(v)


@router.get("/ventas")
def listar_ventas(u=Depends(identidad)):
    with SessionLocal() as db:
        consulta = select(Venta)
        if "ROLE_ADMIN" not in u["roles"]:
            consulta = consulta.where(Venta.usuario == u["usuario"])
        return [service.salida(v) for v in db.scalars(
            consulta.order_by(Venta.id.desc())).all()]
