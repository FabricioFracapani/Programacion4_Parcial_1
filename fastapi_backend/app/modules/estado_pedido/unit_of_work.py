from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.estado_pedido.repository import EstadoPedidoRepository


class EstadoPedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session):
        super().__init__(session)
        self.estados = EstadoPedidoRepository(session)
