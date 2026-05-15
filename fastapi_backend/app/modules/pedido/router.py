from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.pedido.schemas import (
    PedidoCreate, PedidoUpdateEstado, PedidoPublic, PedidoDetail, PedidoList,
    HistorialEstadoPublic,
)
from app.modules.pedido.service import PedidoService

router = APIRouter(dependencies=[Depends(get_current_user)])

LimitQuery = Annotated[int, Query(ge=1, le=100)]


def get_service(session: Session = Depends(get_session)) -> PedidoService:
    return PedidoService(session)


@router.get("/", response_model=PedidoList)
def list_pedidos(
    offset: int = Query(0, ge=0),
    limit: LimitQuery = 20,
    user: dict = Depends(get_current_user),
    svc: PedidoService = Depends(get_service),
):
    if "ADMIN" in user.get("roles", []) or "PEDIDOS" in user.get("roles", []):
        return svc.get_all(offset, limit)
    return svc.get_by_user(user["id"], offset, limit)


@router.post("/", response_model=PedidoDetail, status_code=status.HTTP_201_CREATED)
def create_pedido(
    data: PedidoCreate,
    user: dict = Depends(get_current_user),
    svc: PedidoService = Depends(get_service),
):
    return svc.create(user["id"], data)


@router.get("/{pedido_id}", response_model=PedidoDetail)
def get_pedido(
    pedido_id: int,
    svc: PedidoService = Depends(get_service),
):
    return svc.get_by_id(pedido_id)


@router.patch("/{pedido_id}/estado", response_model=PedidoDetail)
def avanzar_estado(
    pedido_id: int,
    data: PedidoUpdateEstado,
    user: dict = Depends(get_current_user),
    svc: PedidoService = Depends(get_service),
):
    return svc.avanzar_estado(pedido_id, data, user["id"], user.get("roles", []))


@router.get("/{pedido_id}/historial", response_model=list[HistorialEstadoPublic])
def get_historial(
    pedido_id: int,
    svc: PedidoService = Depends(get_service),
):
    return svc.get_historial(pedido_id)
