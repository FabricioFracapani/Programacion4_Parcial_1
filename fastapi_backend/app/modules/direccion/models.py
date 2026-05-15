from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.auth.models import Usuario


class DireccionEntrega(SQLModel, table=True):
    __tablename__ = "direccion_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    alias: Optional[str] = Field(default=None, max_length=50)
    linea1: str = Field(max_length=500)
    linea2: Optional[str] = Field(default=None, max_length=500)
    ciudad: str = Field(max_length=100)
    provincia: Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    latitud: Optional[float] = Field(default=None)
    longitud: Optional[float] = Field(default=None)
    es_principal: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)
