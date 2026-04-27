from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORTS SEGUROS (solo lo que seguro existe)
from app.core.database import create_db_and_tables

# Routers (asegurate que estos módulos existan)
from app.modules.producto.router import router as producto_router
from app.modules.categoria.router import router as categoria_router
from app.modules.ingrediente.router import router as ingrediente_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="TP4 - Catálogo de Productos",
        description="API REST para gestión de productos, categorías e ingredientes.",
        version="1.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ⚠️ en producción cambiar esto
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Evento de inicio
    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()

    # Routers
    app.include_router(producto_router, prefix="/productos", tags=["Productos"])
    app.include_router(categoria_router, prefix="/categorias", tags=["Categorias"])
    app.include_router(ingrediente_router, prefix="/ingredientes", tags=["Ingredientes"])

    # Ruta base (para test rápido)
    @app.get("/")
    def root():
        return {"message": "API funcionando 🚀"}

    return app


app = create_app()