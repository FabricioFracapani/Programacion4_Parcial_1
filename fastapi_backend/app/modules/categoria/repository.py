# app/modules/categorias/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.categoria.models import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    """
    Repositorio de Categorias.
    Agrega queries específicas del dominio sobre el CRUD base.
    Solo habla con la DB — nunca levanta HTTPException.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de Categoria.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, Categoria)

    def get_by_nombre(self, nombre: str) -> Categoria | None:
        """
        Obtiene una categoría por su nombre.

        Args:
            nombre (str): Nombre de la categoría.

        Returns:
            Categoria | None: Instancia encontrada o None si no existe.

        Nota:
            Se asume que 'nombre' es único a nivel de base de datos.
        """
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Categoria]:
        """
        Obtiene categorías activas con paginación.

        Args:
            offset (int): Cantidad de registros a omitir.
            limit (int): Máximo de registros a devolver.

        Returns:
            list[Categoria]: Lista de categorías activas.
        """
        return list(
            self.session.exec(
                select(Categoria)
                .where(Categoria.activo == True)  # noqa: E712
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def get_by_parent(self, parent_id: int, offset: int = 0, limit: int = 20) -> list[Categoria]:
        """
        Obtiene todas las subcategorías de una categoría padre.

        Args:
            parent_id (int): ID de la categoría padre.
            offset (int): Cantidad de registros a omitir.
            limit (int): Máximo de registros a devolver.

        Returns:
            list[Categoria]: Lista de categorías hijas.
        """
        return list(
            self.session.exec(
                select(Categoria)
                .where(Categoria.parent_id == parent_id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count(self) -> int:
        """
        Cuenta la cantidad total de categorías activas.

        Returns:
            int: Total de registros activos en la tabla Categoria.
        """
        return len(
            self.session.exec(
                select(Categoria).where(Categoria.activo == True)  # noqa: E712
            ).all()
        )
