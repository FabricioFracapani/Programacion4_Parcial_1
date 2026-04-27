# app/modules/ingrediente/router.py
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.ingrediente.schemas import (
    IngredienteCreate, IngredientePublic, IngredienteUpdate, IngredienteList,
    ProductoIngredienteCreate, ProductoIngredientePublic, ProductoIngredienteList
)
from app.modules.ingrediente.service import IngredienteService

router = APIRouter()


def get_ingrediente_service(session: Session = Depends(get_session)) -> IngredienteService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return IngredienteService(session)


# ── Tipos paginación reutilizables con Annotated ──────────────────────────────
OffsetQuery = Annotated[int, Query(ge=0, description="Registros a omitir")]
LimitQuery  = Annotated[int, Query(ge=1, le=100, description="Máximo de resultados")]


# ── Endpoints Ingrediente ─────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=IngredientePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un ingrediente",
)
def create_ingrediente(
    data: IngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)


@router.get(
    "/",
    response_model=IngredienteList,
    summary="Listar ingredientes (paginado)",
)
def list_ingredientes(
    offset: OffsetQuery = 0,
    limit: LimitQuery = 20,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_all(offset=offset, limit=limit)


# IMPORTANTE: rutas específicas ANTES de /{ingrediente_id}
@router.get(
    "/producto/{producto_id}",
    response_model=ProductoIngredienteList,
    summary="Listar ingredientes de un producto",
)
def list_relaciones_por_producto(
    producto_id: Annotated[int, Path(gt=0, description="ID del producto")],
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> ProductoIngredienteList:
    return svc.get_relaciones_por_producto(producto_id)


@router.post(
    "/producto",
    response_model=ProductoIngredientePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Asignar ingrediente a un producto",
)
def create_relacion(
    data: ProductoIngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> ProductoIngredientePublic:
    return svc.create_relacion(data)


@router.delete(
    "/producto/{producto_id}/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar relación producto ↔ ingrediente",
)
def delete_relacion(
    producto_id: Annotated[int, Path(gt=0, description="ID del producto")],
    ingrediente_id: Annotated[int, Path(gt=0, description="ID del ingrediente")],
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> None:
    svc.delete_relacion(producto_id, ingrediente_id)


@router.get(
    "/{ingrediente_id}",
    response_model=IngredientePublic,
    summary="Obtener ingrediente por ID",
)
def get_ingrediente(
    ingrediente_id: Annotated[int, Path(gt=0, description="ID del ingrediente")],
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.get_by_id(ingrediente_id)


@router.patch(
    "/{ingrediente_id}",
    response_model=IngredientePublic,
    summary="Actualización parcial de ingrediente",
)
def update_ingrediente(
    ingrediente_id: Annotated[int, Path(gt=0, description="ID del ingrediente")],
    data: IngredienteUpdate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.update(ingrediente_id, data)


@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ingrediente",
)
def delete_ingrediente(
    ingrediente_id: Annotated[int, Path(gt=0, description="ID del ingrediente")],
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> None:
    svc.soft_delete(ingrediente_id)
