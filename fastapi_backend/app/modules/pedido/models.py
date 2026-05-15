from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ARRAY, Integer, DateTime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.estado_pedido.models import EstadoPedido
    from app.modules.producto.models import Producto


class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    direccion_id: Optional[int] = Field(default=None, foreign_key="direccion_entrega.id")
    estado_codigo: str = Field(foreign_key="estado_pedido.codigo", default="PENDIENTE", max_length=20)

    subtotal: float = Field(default=0.0)
    descuento: float = Field(default=0.0)
    costo_envio: float = Field(default=50.0)
    total: float = Field(default=0.0)

    notas: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))
    deleted_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))

    estado: Optional["EstadoPedido"] = Relationship(back_populates="pedidos")
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial: List["HistorialEstadoPedido"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={"foreign_keys": "[HistorialEstadoPedido.pedido_id]"},
    )


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    pedido_id: int = Field(foreign_key="pedido.id", primary_key=True)
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)

    cantidad: int = Field(default=1, ge=1)
    nombre_snapshot: str = Field(max_length=200)
    precio_snapshot: float = Field(ge=0)
    subtotal_snap: float = Field(ge=0)
    personalizacion: Optional[List[int]] = Field(default=None, sa_type=ARRAY(Integer()))

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))

    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_desde: Optional[str] = Field(default=None, foreign_key="estado_pedido.codigo", max_length=20)
    estado_hacia: str = Field(foreign_key="estado_pedido.codigo", max_length=20)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    motivo: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))

    pedido: Optional["Pedido"] = Relationship(
        back_populates="historial",
        sa_relationship_kwargs={"foreign_keys": "[HistorialEstadoPedido.pedido_id]"},
    )
    estado_desde_rel: Optional["EstadoPedido"] = Relationship(
        back_populates="historiales_desde",
        sa_relationship_kwargs={"foreign_keys": "[HistorialEstadoPedido.estado_desde]"},
    )
    estado_hacia_rel: Optional["EstadoPedido"] = Relationship(
        back_populates="historiales_hacia",
        sa_relationship_kwargs={"foreign_keys": "[HistorialEstadoPedido.estado_hacia]"},
    )
