# app/modules/ingrediente/unit_of_work.py
from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.producto.repository import ProductoIngredienteRepository


class IngredienteUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo ingrediente.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
        UnitOfWork específico del dominio Ingrediente.

        Extiende el UnitOfWork base y registra los repositorios necesarios
        para operar dentro de una misma transacción consistente.

        Repositorios expuestos:
            - ingredientes: acceso a operaciones sobre Ingrediente
            - producto_ingredientes: acceso a operaciones sobre ProductoIngrediente
                                     (tabla intermedia producto ↔ ingrediente)

        Args:
            session (Session): Sesión activa de base de datos compartida
                               por todos los repositorios.

        Uso típico:

            with IngredienteUnitOfWork(session) as uow:
                ingrediente = Ingrediente(...)
                uow.ingredientes.add(ingrediente)

            with IngredienteUnitOfWork(session) as uow:
                relacion = ProductoIngrediente(...)
                uow.producto_ingredientes.add(relacion)
        """
        super().__init__(session)
        self.ingredientes = IngredienteRepository(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)