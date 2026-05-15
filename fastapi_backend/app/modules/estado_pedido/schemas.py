from typing import Optional
from pydantic import BaseModel, Field


class EstadoPedidoCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=20)
    descripcion: str = Field(min_length=1, max_length=80)
    orden: int
    es_terminal: bool = False


class EstadoPedidoPublic(BaseModel):
    codigo: str
    descripcion: str
    orden: int
    es_terminal: bool
