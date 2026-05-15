from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.pedido.models import Pedido, DetallePedido
from app.modules.pedido.schemas import (
    PedidoCreate, PedidoUpdateEstado, PedidoPublic, PedidoDetail, PedidoList,
    DetallePedidoPublic, HistorialEstadoPublic,
)
from app.modules.pedido.unit_of_work import PedidoUnitOfWork
from app.modules.producto.repository import ProductoRepository
from app.modules.estado_pedido.service import validar_transicion


class PedidoService:
    def __init__(self, session: Session):
        self._session = session

    def _build_public(self, pedido: Pedido) -> PedidoPublic:
        return PedidoPublic(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
            estado_codigo=pedido.estado_codigo,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            notas=pedido.notas,
            created_at=pedido.created_at,
            updated_at=pedido.updated_at,
        )

    def _build_detail(self, pedido: Pedido, uow: PedidoUnitOfWork) -> PedidoDetail:
        detalles = uow.detalles.get_by_pedido(pedido.id)
        historial = uow.historial.get_by_pedido(pedido.id)
        return PedidoDetail(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
            estado_codigo=pedido.estado_codigo,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            notas=pedido.notas,
            created_at=pedido.created_at,
            updated_at=pedido.updated_at,
            detalles=[
                DetallePedidoPublic(
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    nombre_snapshot=d.nombre_snapshot,
                    precio_snapshot=d.precio_snapshot,
                    subtotal_snap=d.subtotal_snap,
                    personalizacion=d.personalizacion,
                ) for d in detalles
            ],
            historial=[
                HistorialEstadoPublic(
                    id=h.id,
                    pedido_id=h.pedido_id,
                    estado_desde=h.estado_desde,
                    estado_hacia=h.estado_hacia,
                    motivo=h.motivo,
                    created_at=h.created_at,
                ) for h in historial
            ],
        )

    def create(self, usuario_id: int, data: PedidoCreate) -> PedidoDetail:
        with PedidoUnitOfWork(self._session) as uow:
            producto_repo = ProductoRepository(self._session)

            subtotal = 0.0
            detalles_data = []

            for item in data.items:
                producto = producto_repo.get_by_id(item.producto_id)
                if not producto:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto id={item.producto_id} no encontrado",
                    )

                precio = producto.precio_base
                sub = round(precio * item.cantidad, 2)
                subtotal += sub

                detalles_data.append({
                    "producto_id": producto.id,
                    "cantidad": item.cantidad,
                    "nombre_snapshot": producto.nombre,
                    "precio_snapshot": precio,
                    "subtotal_snap": sub,
                    "personalizacion": item.personalizacion,
                })

            costo_envio = 50.0 if data.direccion_id else 0.0
            total = round(subtotal + costo_envio, 2)

            pedido = Pedido(
                usuario_id=usuario_id,
                direccion_id=data.direccion_id,
                estado_codigo="PENDIENTE",
                subtotal=subtotal,
                descuento=0.0,
                costo_envio=costo_envio,
                total=total,
                notas=data.notas,
            )
            uow.pedidos.add(pedido)

            for dd in detalles_data:
                detalle = DetallePedido(pedido_id=pedido.id, **dd)
                uow.detalles.add(detalle)

            uow.historial.add_entry(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_hacia="PENDIENTE",
                usuario_id=usuario_id,
            )

            result = self._build_detail(pedido, uow)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> PedidoList:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedidos.get_all_paged(offset, limit)
            total = uow.pedidos.count()
            return PedidoList(
                data=[self._build_public(p) for p in pedidos],
                total=total,
            )

    def get_by_user(self, usuario_id: int, offset: int = 0, limit: int = 20) -> PedidoList:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedidos.get_by_usuario(usuario_id, offset, limit)
            total = uow.pedidos.count_by_usuario(usuario_id)
            return PedidoList(
                data=[self._build_public(p) for p in pedidos],
                total=total,
            )

    def get_by_id(self, pedido_id: int) -> PedidoDetail:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
            return self._build_detail(pedido, uow)

    def avanzar_estado(
        self,
        pedido_id: int,
        data: PedidoUpdateEstado,
        usuario_id: int,
        user_roles: list[str],
    ) -> PedidoDetail:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

            if not validar_transicion(pedido.estado_codigo, data.estado_codigo, user_roles):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede transicionar de {pedido.estado_codigo} a {data.estado_codigo}",
                )

            if data.estado_codigo == "CANCELADO" and not data.motivo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se requiere motivo para cancelar un pedido",
                )

            estado_anterior = pedido.estado_codigo
            pedido.estado_codigo = data.estado_codigo
            pedido.updated_at = datetime.now(timezone.utc)
            uow.pedidos.add(pedido)

            uow.historial.add_entry(
                pedido_id=pedido.id,
                estado_desde=estado_anterior,
                estado_hacia=data.estado_codigo,
                usuario_id=usuario_id,
                motivo=data.motivo,
            )

            result = self._build_detail(pedido, uow)
        return result

    def get_historial(self, pedido_id: int) -> list[HistorialEstadoPublic]:
        with PedidoUnitOfWork(self._session) as uow:
            historial = uow.historial.get_by_pedido(pedido_id)
            return [
                HistorialEstadoPublic(
                    id=h.id,
                    pedido_id=h.pedido_id,
                    estado_desde=h.estado_desde,
                    estado_hacia=h.estado_hacia,
                    motivo=h.motivo,
                    created_at=h.created_at,
                ) for h in historial
            ]
