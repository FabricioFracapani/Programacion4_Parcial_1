from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.dependencies import get_current_user
from app.modules.direccion.schemas import DireccionCreate, DireccionUpdate, DireccionPublic
from app.modules.direccion.service import DireccionService

router = APIRouter(dependencies=[Depends(get_current_user)])


def get_service(session: Session = Depends(get_session)) -> DireccionService:
    return DireccionService(session)


@router.get("/", response_model=list[DireccionPublic])
def list_direcciones(
    user: dict = Depends(get_current_user),
    svc: DireccionService = Depends(get_service),
):
    return svc.list_by_user(user["id"])


@router.post("/", response_model=DireccionPublic, status_code=status.HTTP_201_CREATED)
def create_direccion(
    data: DireccionCreate,
    user: dict = Depends(get_current_user),
    svc: DireccionService = Depends(get_service),
):
    return svc.create(user["id"], data)


@router.patch("/{direccion_id}", response_model=DireccionPublic)
def update_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    user: dict = Depends(get_current_user),
    svc: DireccionService = Depends(get_service),
):
    return svc.update(user["id"], direccion_id, data)


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_direccion(
    direccion_id: int,
    user: dict = Depends(get_current_user),
    svc: DireccionService = Depends(get_service),
):
    svc.delete(user["id"], direccion_id)
