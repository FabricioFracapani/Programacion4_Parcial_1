from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone

from app.modules.ingrediente.models import Ingrediente
from app.modules.producto.models import ProductoIngrediente
from app.modules.ingrediente.schemas import (
    IngredienteCreate, IngredientePublic, IngredienteUpdate, IngredienteList,
    ProductoIngredienteCreate, ProductoIngredientePublic, ProductoIngredienteList
)
from app.modules.ingrediente.unit_of_work import IngredienteUnitOfWork


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IngredienteService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )
        return ingrediente

    def _assert_nombre_unique(self, uow: IngredienteUnitOfWork, nombre: str) -> None:
        if uow.ingredientes.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya esta en uso",
            )

    def _assert_relacion_not_exists(self, uow: IngredienteUnitOfWork, producto_id: int, ingrediente_id: int) -> None:
        if uow.producto_ingredientes.exists(producto_id, ingrediente_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El ingrediente id={ingrediente_id} ya esta asignado al producto id={producto_id}",
            )

    def _get_relacion_or_404(self, uow: IngredienteUnitOfWork, producto_id: int, ingrediente_id: int) -> ProductoIngrediente:
        relacion = uow.producto_ingredientes.get_by_pk(producto_id, ingrediente_id)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relacion entre producto id={producto_id} e ingrediente id={ingrediente_id} no encontrada",
            )
        return relacion

    def create(self, data: IngredienteCreate) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)
            ingrediente = Ingrediente.model_validate(data)
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> IngredienteList:
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_all_paged(offset=offset, limit=limit)
            total = uow.ingredientes.count()
            result = IngredienteList(
                data=[IngredientePublic.model_validate(i) for i in ingredientes],
                total=total,
            )
        return result

    def get_by_id(self, ingrediente_id: int) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            if data.nombre and data.nombre != ingrediente.nombre:
                self._assert_nombre_unique(uow, data.nombre)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(ingrediente, field, value)
            ingrediente.updated_at = _now()
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def hard_delete(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            uow.ingredientes.delete(ingrediente)

    def create_relacion(self, data: ProductoIngredienteCreate) -> ProductoIngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            self._assert_relacion_not_exists(uow, data.producto_id, data.ingrediente_id)
            relacion = ProductoIngrediente.model_validate(data)
            uow.producto_ingredientes.add(relacion)
            result = ProductoIngredientePublic.model_validate(relacion)
        return result

    def get_relaciones_por_producto(self, producto_id: int) -> ProductoIngredienteList:
        with IngredienteUnitOfWork(self._session) as uow:
            relaciones = uow.producto_ingredientes.get_by_producto(producto_id)
            result = ProductoIngredienteList(
                data=[ProductoIngredientePublic.model_validate(r) for r in relaciones],
                total=len(relaciones),
            )
        return result

    def delete_relacion(self, producto_id: int, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            relacion = self._get_relacion_or_404(uow, producto_id, ingrediente_id)
            uow.producto_ingredientes.delete(relacion)
