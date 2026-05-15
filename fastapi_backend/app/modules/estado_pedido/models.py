from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.pedido.models import Pedido, HistorialEstadoPedido


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estado_pedido"

    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=80)
    orden: int = Field()
    es_terminal: bool = Field(default=False)

    pedidos: List["Pedido"] = Relationship(back_populates="estado")
    historiales_desde: List["HistorialEstadoPedido"] = Relationship(
        back_populates="estado_desde_rel",
        sa_relationship_kwargs={"foreign_keys": "[HistorialEstadoPedido.estado_desde]"},
    )
    historiales_hacia: List["HistorialEstadoPedido"] = Relationship(
        back_populates="estado_hacia_rel",
        sa_relationship_kwargs={"foreign_keys": "[HistorialEstadoPedido.estado_hacia]"},
    )
