# app/modules/producto/unit_of_work.py
from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.producto.repository import (
    ProductoRepository,
    ProductoCategoriaRepository,
    ProductoIngredienteRepository,
)


class ProductoUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo producto.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
        UnitOfWork específico del dominio Producto.

        Repositorios expuestos:
            - productos: acceso a operaciones sobre Producto
            - producto_categorias: acceso a la tabla intermedia producto ↔ categoría
            - producto_ingredientes: acceso a la tabla intermedia producto ↔ ingrediente

        Args:
            session (Session): Sesión activa compartida por todos los repositorios.

        Uso típico:

            with ProductoUnitOfWork(session) as uow:
                uow.productos.add(producto)

            with ProductoUnitOfWork(session) as uow:
                uow.producto_categorias.add(relacion)

            with ProductoUnitOfWork(session) as uow:
                uow.producto_ingredientes.add(relacion)
        """
        super().__init__(session)
        self.productos             = ProductoRepository(session)
        self.producto_categorias   = ProductoCategoriaRepository(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)