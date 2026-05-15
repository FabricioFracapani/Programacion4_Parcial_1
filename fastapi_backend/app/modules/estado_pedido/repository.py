from sqlmodel import Session
from app.core.repository import BaseRepository
from app.modules.estado_pedido.models import EstadoPedido


class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    def __init__(self, session: Session):
        super().__init__(session, EstadoPedido)
