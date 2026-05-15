from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class IngredienteCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None


class IngredientePublic(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool
    created_at: datetime
    updated_at: datetime


class IngredienteList(BaseModel):
    data: List[IngredientePublic]
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
