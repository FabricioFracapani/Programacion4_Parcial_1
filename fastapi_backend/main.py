import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from sqlmodel import SQLModel
from app.core.database import create_db_and_tables, engine, DATABASE_URL


from app.modules.producto.router import router as producto_router
from app.modules.categoria.router import router as categoria_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.auth.router import router as auth_router
from app.modules.unidad_medida.router import router as unidad_medida_router
from app.modules.estado_pedido.router import router as estado_pedido_router
from app.modules.direccion.router import router as direccion_router
from app.modules.pedido.router import router as pedido_router


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def create_app() -> FastAPI:
    app = FastAPI(
        title="TP4 - Food Store API",
        description="API REST para gestion de catalogo de productos, pedidos y trazabilidad.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        SQLModel.metadata.drop_all(engine)
        create_db_and_tables()
        from app.db.seed import seed_all
        seed_all()

    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(
        unidad_medida_router,
        prefix="/unidades-medida",
        tags=["Unidades de Medida"],
    )
    app.include_router(
        estado_pedido_router,
        prefix="/estados-pedido",
        tags=["Estados de Pedido"],
    )
    app.include_router(
        direccion_router,
        prefix="/direcciones",
        tags=["Direcciones"],
    )
    app.include_router(
        pedido_router,
        prefix="/pedidos",
        tags=["Pedidos"],
    )
    app.include_router(
        producto_router,
        prefix="/productos",
        tags=["Productos"],
    )
    app.include_router(
        categoria_router,
        prefix="/categorias",
        tags=["Categorias"],
    )
    app.include_router(
        ingrediente_router,
        prefix="/ingredientes",
        tags=["Ingredientes"],
    )

    @app.get("/")
    def root():
        return {"message": "Food Store API funcionando"}

    return app


app = create_app()
