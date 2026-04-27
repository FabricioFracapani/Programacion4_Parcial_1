# app/modules/producto/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo producto.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime


# ── Entrada Producto ──────────────────────────────────────────────────────────

class ProductoCreate(SQLModel):
    """Body para POST /productos/"""
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: Optional[str] = None
    precio_base: float = Field(gt=0)
    imagen_url: List[str] = Field(default_factory=list)
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = True


class ProductoUpdate(SQLModel):
    """Body para PATCH /productos/{id} — todos los campos opcionales."""
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Optional[float] = Field(default=None, gt=0)
    imagen_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    disponible: Optional[bool] = None


# ── Salida Producto ───────────────────────────────────────────────────────────

class ProductoPublic(SQLModel):
    """Response model: campos que se exponen al cliente."""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagen_url: List[str]
    stock_cantidad: int
    disponible: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class ProductoList(SQLModel):
    """Response model paginado para GET /productos/"""
    data: List[ProductoPublic]
    total: int


# ── Entrada ProductoCategoria ─────────────────────────────────────────────────

class ProductoCategoriaCreate(SQLModel):
    """Body para POST /productos/categorias"""
    producto_id: int = Field(gt=0)
    categoria_id: int = Field(gt=0)
    es_principal: bool = False


# ── Salida ProductoCategoria ──────────────────────────────────────────────────

class ProductoCategoriaPublic(SQLModel):
    """Response model para la relación producto ↔ categoría."""
    producto_id: int
    categoria_id: int
    es_principal: bool
    created_at: datetime


class ProductoCategoriaList(SQLModel):
    """Response model para GET /productos/categorias"""
    data: List[ProductoCategoriaPublic]
    total: int


class ProductoIngredienteCreate(SQLModel):
    """Body para POST /productos/ingredientes"""
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
    """Response model para GET /productos/ingredientes"""
    data: List[ProductoIngredientePublic]
    total: int