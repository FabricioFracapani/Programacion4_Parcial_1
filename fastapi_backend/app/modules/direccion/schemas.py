from typing import Optional
from pydantic import BaseModel, Field


class DireccionCreate(BaseModel):
    alias: Optional[str] = Field(default=None, max_length=50)
    linea1: str = Field(min_length=1, max_length=500)
    linea2: Optional[str] = Field(default=None, max_length=500)
    ciudad: str = Field(min_length=1, max_length=100)
    provincia: Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_principal: bool = False


class DireccionUpdate(BaseModel):
    alias: Optional[str] = Field(default=None, max_length=50)
    linea1: Optional[str] = Field(default=None, max_length=500)
    linea2: Optional[str] = Field(default=None, max_length=500)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    provincia: Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_principal: Optional[bool] = None


class DireccionPublic(BaseModel):
    id: int
    usuario_id: int
    alias: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_principal: bool
