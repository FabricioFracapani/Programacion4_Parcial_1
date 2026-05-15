from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ProductoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: Optional[str] = None
    precio_base: float = Field(gt=0)
    imagenes_url: List[str] = Field(default_factory=list)
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = True
    unidad_venta_id: Optional[int] = None


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Optional[float] = Field(default=None, gt=0)
    imagenes_url: Optional[List[str]] = None
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    disponible: Optional[bool] = None
    unidad_venta_id: Optional[int] = None


class ProductoPublic(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagenes_url: List[str]
    stock_cantidad: int
    disponible: bool
    unidad_venta_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class ProductoList(BaseModel):
    data: List[ProductoPublic]
    total: int


class ProductoCategoriaCreate(BaseModel):
    producto_id: int = Field(gt=0)
    categoria_id: int = Field(gt=0)
    es_principal: bool = False


class ProductoCategoriaPublic(BaseModel):
    producto_id: int
    categoria_id: int
    es_principal: bool
    created_at: datetime


class ProductoCategoriaList(BaseModel):
    data: List[ProductoCategoriaPublic]
    total: int


class ProductoIngredienteCreate(BaseModel):
    producto_id: int = Field(gt=0)
    ingrediente_id: int = Field(gt=0)
    cantidad: float = Field(default=1.0, gt=0)
    unidad_medida_id: Optional[int] = None
    es_removible: bool = False


class ProductoIngredientePublic(BaseModel):
    producto_id: int
    ingrediente_id: int
    cantidad: float
    unidad_medida_id: Optional[int] = None
    es_removible: bool


class ProductoIngredienteList(BaseModel):
    data: List[ProductoIngredientePublic]
    total: int
