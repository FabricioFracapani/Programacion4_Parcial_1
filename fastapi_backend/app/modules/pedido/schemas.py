from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ItemPedidoRequest(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(default=1, ge=1)
    personalizacion: Optional[List[int]] = None


class PedidoCreate(BaseModel):
    direccion_id: Optional[int] = None
    items: List[ItemPedidoRequest] = Field(min_length=1)
    notas: Optional[str] = None


class PedidoUpdateEstado(BaseModel):
    estado_codigo: str = Field(max_length=20)
    motivo: Optional[str] = None


class DetallePedidoPublic(BaseModel):
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: float
    subtotal_snap: float
    personalizacion: Optional[List[int]] = None


class HistorialEstadoPublic(BaseModel):
    id: int
    pedido_id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    motivo: Optional[str] = None
    created_at: datetime


class PedidoPublic(BaseModel):
    id: int
    usuario_id: int
    direccion_id: Optional[int] = None
    estado_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PedidoDetail(PedidoPublic):
    detalles: List[DetallePedidoPublic] = []
    historial: List[HistorialEstadoPublic] = []


class PedidoList(BaseModel):
    data: List[PedidoPublic]
    total: int
