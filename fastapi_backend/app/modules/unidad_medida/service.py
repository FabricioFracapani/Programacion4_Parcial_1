from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.unidad_medida.models import UnidadMedida
from app.modules.unidad_medida.schemas import (
    UnidadMedidaCreate,
    UnidadMedidaUpdate,
    UnidadMedidaPublic,
)
from app.modules.unidad_medida.unit_of_work import UnidadMedidaUnitOfWork


class UnidadMedidaService:
    def __init__(self, session: Session):
        self._session = session

    def list(self, offset: int = 0, limit: int = 20) -> list[UnidadMedidaPublic]:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidades = uow.unidades.get_all(offset, limit)
            return [
                UnidadMedidaPublic(
                    id=u.id, nombre=u.nombre, simbolo=u.simbolo, tipo=u.tipo
                )
                for u in unidades
            ]

    def get_by_id(self, unidad_id: int) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            u = uow.unidades.get_by_id(unidad_id)
            if not u:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad de medida no encontrada")
            return UnidadMedidaPublic(id=u.id, nombre=u.nombre, simbolo=u.simbolo, tipo=u.tipo)

    def create(self, data: UnidadMedidaCreate) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = UnidadMedida(**data.model_dump())
            uow.unidades.add(unidad)
        return UnidadMedidaPublic(id=unidad.id, nombre=unidad.nombre, simbolo=unidad.simbolo, tipo=unidad.tipo)

    def update(self, unidad_id: int, data: UnidadMedidaUpdate) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            u = uow.unidades.get_by_id(unidad_id)
            if not u:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad de medida no encontrada")
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(u, key, value)
            self._session.add(u)
        return UnidadMedidaPublic(id=u.id, nombre=u.nombre, simbolo=u.simbolo, tipo=u.tipo)
