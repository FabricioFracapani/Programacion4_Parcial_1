import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

load_dotenv()

from app.modules.producto.models import Producto, ProductoCategoria, ProductoIngrediente
from app.modules.categoria.models import Categoria
from app.modules.ingrediente.models import Ingrediente
from app.modules.auth.models import Usuario, Rol, UsuarioRol, RefreshToken
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.estado_pedido.models import EstadoPedido
from app.modules.direccion.models import DireccionEntrega
from app.modules.pedido.models import Pedido, DetallePedido, HistorialEstadoPedido

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:191700faB@localhost:5432/gestor_productos_tp4"
)

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
