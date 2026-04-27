# app/modules/categorias/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo categorias.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime


# ── Entrada ───────────────────────────────────────────────────────────────────

class CategoriaCreate(SQLModel):
    """Body para POST /categorias/"""
    parent_id: Optional[int] = None
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    es_principal: bool = True


class CategoriaUpdate(SQLModel):
    """Body para PATCH /categorias/{id} — todos los campos opcionales."""
    parent_id: Optional[int] = None
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None
    es_principal: Optional[bool] = None


# ── Salida ────────────────────────────────────────────────────────────────────
class CategoriaPublic(SQLModel):
    """Response model: campos que se exponen al cliente."""
    id: int
    parent_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    es_principal: bool = True
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CategoriaList(SQLModel):
    """Response model paginado para GET /categorias/"""
    data: List[CategoriaPublic]
    total: int
