from sqlmodel import Session, select
from app.core.database import engine
from app.core.security import hash_password
from app.modules.auth.models import Rol, Usuario, UsuarioRol
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.estado_pedido.models import EstadoPedido


ROLES_SEED = [
    {"codigo": "ADMIN", "nombre": "Administrador", "descripcion": "Acceso total sin restricciones"},
    {"codigo": "STOCK", "nombre": "Gestion de Stock", "descripcion": "Actualiza stock y disponibilidad de productos"},
    {"codigo": "PEDIDOS", "nombre": "Gestion de Pedidos", "descripcion": "Avanza estados CONFIRMADO a ENTREGADO"},
    {"codigo": "CLIENT", "nombre": "Cliente", "descripcion": "Opera solo sus propios datos"},
]

UNIDADES_SEED = [
    {"nombre": "Kilogramo", "simbolo": "kg", "tipo": "masa"},
    {"nombre": "Gramo", "simbolo": "g", "tipo": "masa"},
    {"nombre": "Litro", "simbolo": "L", "tipo": "volumen"},
    {"nombre": "Mililitro", "simbolo": "mL", "tipo": "volumen"},
    {"nombre": "Unidad", "simbolo": "u", "tipo": "unidad"},
    {"nombre": "Docena", "simbolo": "doc", "tipo": "unidad"},
    {"nombre": "Metro cuadrado", "simbolo": "m2", "tipo": "area"},
]

ESTADOS_SEED = [
    {"codigo": "PENDIENTE", "descripcion": "Pedido creado, pendiente de confirmacion", "orden": 1, "es_terminal": False},
    {"codigo": "CONFIRMADO", "descripcion": "Pago confirmado, en espera de preparacion", "orden": 2, "es_terminal": False},
    {"codigo": "EN_PREP", "descripcion": "En preparacion", "orden": 3, "es_terminal": False},
    {"codigo": "EN_CAMINO", "descripcion": "En camino al destino", "orden": 4, "es_terminal": False},
    {"codigo": "ENTREGADO", "descripcion": "Entregado al cliente", "orden": 5, "es_terminal": True},
    {"codigo": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
]


def seed_roles(session: Session):
    for rol_data in ROLES_SEED:
        existing = session.get(Rol, rol_data["codigo"])
        if not existing:
            session.add(Rol(**rol_data))
    session.flush()


def seed_admin(session: Session):
    existing = session.exec(
        select(Usuario).where(Usuario.email == "admin@foodstore.com")
    ).first()
    if not existing:
        admin = Usuario(
            nombre="Admin",
            apellido="Sistema",
            email="admin@foodstore.com",
            password_hash=hash_password("admin123"),
        )
        session.add(admin)
        session.flush()
        ur = UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN")
        session.add(ur)
        session.flush()


def seed_unidades(session: Session):
    for udata in UNIDADES_SEED:
        existing = session.exec(
            select(UnidadMedida).where(UnidadMedida.simbolo == udata["simbolo"])
        ).first()
        if not existing:
            session.add(UnidadMedida(**udata))
    session.flush()


def seed_estados(session: Session):
    for edata in ESTADOS_SEED:
        existing = session.get(EstadoPedido, edata["codigo"])
        if not existing:
            session.add(EstadoPedido(**edata))
    session.flush()


def seed_all():
    with Session(engine) as session:
        seed_roles(session)
        seed_admin(session)
        seed_unidades(session)
        seed_estados(session)
        session.commit()
