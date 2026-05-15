from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.direccion.models import DireccionEntrega
from app.modules.direccion.schemas import (
    DireccionCreate, DireccionUpdate, DireccionPublic,
)
from app.modules.direccion.unit_of_work import DireccionUnitOfWork


def _now():
    return datetime.now(timezone.utc)


class DireccionService:
    def __init__(self, session: Session):
        self._session = session

    def _get_or_404(self, uow: DireccionUnitOfWork, direccion_id: int) -> DireccionEntrega:
        d = uow.direcciones.get_by_id(direccion_id)
        if not d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Direccion no encontrada")
        return d

    def list_by_user(self, usuario_id: int) -> list[DireccionPublic]:
        with DireccionUnitOfWork(self._session) as uow:
            direcciones = uow.direcciones.get_by_usuario(usuario_id)
            return [DireccionPublic.model_validate(d) for d in direcciones]

    def create(self, usuario_id: int, data: DireccionCreate) -> DireccionPublic:
        with DireccionUnitOfWork(self._session) as uow:
            if data.es_principal:
                uow.direcciones.clear_principal(usuario_id)
            direccion = DireccionEntrega(usuario_id=usuario_id, **data.model_dump())
            uow.direcciones.add(direccion)
            result = DireccionPublic.model_validate(direccion)
        return result

    def update(self, usuario_id: int, direccion_id: int, data: DireccionUpdate) -> DireccionPublic:
        with DireccionUnitOfWork(self._session) as uow:
            d = self._get_or_404(uow, direccion_id)
            if d.usuario_id != usuario_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
            if data.es_principal:
                uow.direcciones.clear_principal(usuario_id)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(d, field, value)
            d.updated_at = _now()
            uow.direcciones.add(d)
            result = DireccionPublic.model_validate(d)
        return result

    def delete(self, usuario_id: int, direccion_id: int) -> None:
        with DireccionUnitOfWork(self._session) as uow:
            d = self._get_or_404(uow, direccion_id)
            if d.usuario_id != usuario_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
            d.deleted_at = _now()
            uow.direcciones.add(d)
