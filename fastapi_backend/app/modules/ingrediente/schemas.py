# app/modules/ingrediente/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo ingrediente.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime


# ── Entrada Ingrediente ───────────────────────────────────────────────────────

class IngredienteCreate(SQLModel):
    """Body para POST /ingredientes/"""
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class IngredienteUpdate(SQLModel):
    """Body para PATCH /ingredientes/{id} — todos los campos opcionales."""
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None


# ── Salida Ingrediente ────────────────────────────────────────────────────────

class IngredientePublic(SQLModel):
    """Response model: campos que se exponen al cliente."""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool
    created_at: datetime
    updated_at: datetime


class IngredienteList(SQLModel):
    """Response model paginado para GET /ingredientes/"""
    data: List[IngredientePublic]
    total: int


# ── Entrada ProductoIngrediente ───────────────────────────────────────────────

class ProductoIngredienteCreate(SQLModel):
    """Body para POST /ingredientes/producto"""
    producto_id: int = Field(gt=0)
    ingrediente_id: int = Field(gt=0)
    es_removible: bool = False


# ── Salida ProductoIngrediente ────────────────────────────────────────────────

class ProductoIngredientePublic(SQLModel):
    """Response model para la relación producto ↔ ingrediente."""
    producto_id: int
    ingrediente_id: int
    es_removible: bool


class ProductoIngredienteList(SQLModel):
    """Response model paginado para GET /ingredientes/producto/{producto_id}"""
    data: List[ProductoIngredientePublic]
    total: int
