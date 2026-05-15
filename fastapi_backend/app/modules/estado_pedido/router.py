from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.estado_pedido.schemas import EstadoPedidoCreate, EstadoPedidoPublic
from app.modules.estado_pedido.service import EstadoPedidoService

router = APIRouter(tags=["Estados de Pedido"])


def get_service(session: Session = Depends(get_session)) -> EstadoPedidoService:
    return EstadoPedidoService(session)


@router.get("/", response_model=list[EstadoPedidoPublic])
def list_estados(svc: EstadoPedidoService = Depends(get_service)):
    return svc.list()


@router.post(
    "/",
    response_model=EstadoPedidoPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def create_estado(
    data: EstadoPedidoCreate,
    svc: EstadoPedidoService = Depends(get_service),
):
    return svc.create(data)
