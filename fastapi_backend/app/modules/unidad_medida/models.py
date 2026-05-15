from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, max_length=50)
    simbolo: str = Field(unique=True, max_length=10)
    tipo: str = Field(max_length=20)

    created_at: datetime = Field(default_factory=datetime.utcnow)
