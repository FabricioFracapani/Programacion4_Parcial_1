from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CategoriaCreate(BaseModel):
    parent_id: Optional[int] = None
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None


class CategoriaUpdate(BaseModel):
    parent_id: Optional[int] = None
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None


class CategoriaPublic(BaseModel):
    id: int
    parent_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CategoriaList(BaseModel):
    data: List[CategoriaPublic]
    total: int
