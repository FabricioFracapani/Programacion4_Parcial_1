import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

load_dotenv()

# Imporpip install -r requirements.txttar todos los modelos para que SQLModel los registre y cree las tablas
from app.modules.producto.models import Producto, ProductoCategoria, ProductoIngrediente
from app.modules.categoria.models import Categoria
from app.modules.ingrediente.models import Ingrediente

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:191700faB@localhost:5432/gestor_productos_tp4"
)

engine = create_engine("postgresql://postgres:191700faB@localhost:5432/gestor_productos_tp4", echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session