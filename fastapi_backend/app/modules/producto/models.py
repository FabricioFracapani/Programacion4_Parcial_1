# app/modules/producto/models.py
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import String, ARRAY, DateTime
from datetime import datetime

if TYPE_CHECKING:
    from app.modules.categoria.models import Categoria
    from app.modules.ingrediente.models import Ingrediente


class Producto(SQLModel, table=True):
    """Tabla producto en la base de datos."""

    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    descripcion: Optional[str] = Field(default=None)
    precio_base: float = Field(gt=0)
    imagen_url: List[str] = Field(default_factory=list, sa_type=ARRAY(String()))
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)

    # Auditoría
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=True)
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True)
    )

    # Relationships
    # Un Producto puede estar en muchas filas de ProductoCategoria
    producto_categorias: List["ProductoCategoria"] = Relationship(
        back_populates="producto"
    )
    # Un Producto puede estar en muchas filas de ProductoIngrediente
    producto_ingredientes: List["ProductoIngrediente"] = Relationship(
        back_populates="producto"
    )


class ProductoCategoria(SQLModel, table=True):
    """Tabla intermedia producto ↔ categoría (Link Table)."""

    __tablename__ = "producto_categoria"

    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    categoria_id: int = Field(foreign_key="categoria.id", primary_key=True)
    es_principal: bool = Field(default=False)

    # Auditoría
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=True)
    )

    # Relationships — los dos lados del puente
    producto: Optional["Producto"] = Relationship(back_populates="producto_categorias")
    categoria: Optional["Categoria"] = Relationship(back_populates="producto_categorias")


class ProductoIngrediente(SQLModel, table=True):
    """Tabla intermedia producto ↔ ingrediente (Link Table)."""

    __tablename__ = "producto_ingrediente"

    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingrediente.id", primary_key=True)
    es_removible: bool = Field(default=False)

    # Relationships — los dos lados del puente
    producto: Optional["Producto"] = Relationship(back_populates="producto_ingredientes")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_ingredientes")