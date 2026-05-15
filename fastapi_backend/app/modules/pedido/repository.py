from typing import Sequence
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.pedido.models import Pedido, DetallePedido, HistorialEstadoPedido


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session):
        super().__init__(session, Pedido)

    def get_all_paged(self, offset: int = 0, limit: int = 20) -> Sequence[Pedido]:
        return self.session.exec(
            select(Pedido).where(Pedido.deleted_at.is_(None)).offset(offset).limit(limit)
        ).all()

    def get_by_usuario(self, usuario_id: int, offset: int = 0, limit: int = 20) -> Sequence[Pedido]:
        return self.session.exec(
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .where(Pedido.deleted_at.is_(None))
            .offset(offset)
            .limit(limit)
        ).all()

    def count(self) -> int:
        return len(self.session.exec(
            select(Pedido).where(Pedido.deleted_at.is_(None))
        ).all())

    def count_by_usuario(self, usuario_id: int) -> int:
        return len(self.session.exec(
            select(Pedido).where(Pedido.usuario_id == usuario_id).where(Pedido.deleted_at.is_(None))
        ).all())


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    def __init__(self, session: Session):
        super().__init__(session, DetallePedido)

    def get_by_pedido(self, pedido_id: int) -> Sequence[DetallePedido]:
        return self.session.exec(
            select(DetallePedido).where(DetallePedido.pedido_id == pedido_id)
        ).all()

    def delete_by_pedido(self, pedido_id: int) -> None:
        detalles = self.get_by_pedido(pedido_id)
        for d in detalles:
            self.session.delete(d)
        self.session.flush()


class HistorialEstadoPedidoRepository(BaseRepository[HistorialEstadoPedido]):
    def __init__(self, session: Session):
        super().__init__(session, HistorialEstadoPedido)

    def get_by_pedido(self, pedido_id: int) -> Sequence[HistorialEstadoPedido]:
        return self.session.exec(
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
        ).all()

    def add_entry(
        self,
        pedido_id: int,
        estado_desde: str | None,
        estado_hacia: str,
        usuario_id: int | None = None,
        motivo: str | None = None,
    ) -> HistorialEstadoPedido:
        entry = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_desde=estado_desde,
            estado_hacia=estado_hacia,
            usuario_id=usuario_id,
            motivo=motivo,
        )
        self.session.add(entry)
        self.session.flush()
        return entry
