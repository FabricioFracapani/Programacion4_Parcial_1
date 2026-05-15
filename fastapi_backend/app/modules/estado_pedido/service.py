from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.estado_pedido.models import EstadoPedido
from app.modules.estado_pedido.schemas import EstadoPedidoCreate, EstadoPedidoPublic
from app.modules.estado_pedido.unit_of_work import EstadoPedidoUnitOfWork


ESTADOS_SEED = [
    {"codigo": "PENDIENTE", "descripcion": "Pedido creado, pendiente de confirmacion", "orden": 1, "es_terminal": False},
    {"codigo": "CONFIRMADO", "descripcion": "Pago confirmado, en espera de preparacion", "orden": 2, "es_terminal": False},
    {"codigo": "EN_PREP", "descripcion": "En preparacion", "orden": 3, "es_terminal": False},
    {"codigo": "EN_CAMINO", "descripcion": "En camino al destino", "orden": 4, "es_terminal": False},
    {"codigo": "ENTREGADO", "descripcion": "Entregado al cliente", "orden": 5, "es_terminal": True},
    {"codigo": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
]

FSM_TRANSICIONES = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["EN_CAMINO", "CANCELADO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}

FSM_RESTRICCIONES = {
    ("EN_PREP", "CANCELADO"): ["ADMIN", "PEDIDOS"],
}


def validar_transicion(estado_actual: str, estado_nuevo: str, roles: list[str] | None = None) -> bool:
    destinos = FSM_TRANSICIONES.get(estado_actual, [])
    if estado_nuevo not in destinos:
        return False
    restriccion = FSM_RESTRICCIONES.get((estado_actual, estado_nuevo))
    if restriccion and roles:
        if not any(r in roles for r in restriccion):
            return False
    return True


class EstadoPedidoService:
    def __init__(self, session: Session):
        self._session = session

    def list(self) -> list[EstadoPedidoPublic]:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            estados = uow.estados.get_all(0, 100)
            return [
                EstadoPedidoPublic(codigo=e.codigo, descripcion=e.descripcion, orden=e.orden, es_terminal=e.es_terminal)
                for e in estados
            ]

    def create(self, data: EstadoPedidoCreate) -> EstadoPedidoPublic:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            e = EstadoPedido(**data.model_dump())
            uow.estados.add(e)
        return EstadoPedidoPublic(codigo=e.codigo, descripcion=e.descripcion, orden=e.orden, es_terminal=e.es_terminal)
