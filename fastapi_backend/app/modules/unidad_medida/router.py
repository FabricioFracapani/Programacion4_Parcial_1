from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.unidad_medida.schemas import (
    UnidadMedidaCreate,
    UnidadMedidaUpdate,
    UnidadMedidaPublic,
)
from app.modules.unidad_medida.service import UnidadMedidaService

router = APIRouter(dependencies=[Depends(get_current_user)])

LimitQuery = Annotated[int, Query(ge=1, le=100, description="Maximo de resultados")]


def get_service(session: Session = Depends(get_session)) -> UnidadMedidaService:
    return UnidadMedidaService(session)


@router.get("/", response_model=list[UnidadMedidaPublic])
def list_unidades(
    offset: int = Query(0, ge=0),
    limit: LimitQuery = 20,
    svc: UnidadMedidaService = Depends(get_service),
):
    return svc.list(offset, limit)


@router.get("/{unidad_id}", response_model=UnidadMedidaPublic)
def get_unidad(unidad_id: int, svc: UnidadMedidaService = Depends(get_service)):
    return svc.get_by_id(unidad_id)


@router.post(
    "/",
    response_model=UnidadMedidaPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_unidad(
    data: UnidadMedidaCreate,
    svc: UnidadMedidaService = Depends(get_service),
    _user: dict = Depends(require_role("ADMIN")),
):
    return svc.create(data)


@router.patch("/{unidad_id}", response_model=UnidadMedidaPublic)
def update_unidad(
    unidad_id: int,
    data: UnidadMedidaUpdate,
    svc: UnidadMedidaService = Depends(get_service),
    _user: dict = Depends(require_role("ADMIN")),
):
    return svc.update(unidad_id, data)
