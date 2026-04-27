# app/modules/ingrediente/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.ingrediente.models import Ingrediente
from app.modules.producto.models import ProductoIngrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    """
    Repositorio de Ingredientes.
    Agrega queries específicas del dominio sobre el CRUD base.
    Solo habla con la DB — nunca levanta HTTPException.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de Ingrediente.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, Ingrediente)

    def get_by_nombre(self, nombre: str) -> Ingrediente | None:
        """
        Obtiene un ingrediente por su nombre.

        Args:
            nombre (str): Nombre del ingrediente.

        Returns:
            Ingrediente | None: Instancia encontrada o None si no existe.
        """
        return self.session.exec(
            select(Ingrediente).where(Ingrediente.nombre == nombre)
        ).first()

    def get_all_paged(self, offset: int = 0, limit: int = 20) -> list[Ingrediente]:
        """
        Obtiene ingredientes con paginación.

        Args:
            offset (int): Cantidad de registros a omitir.
            limit (int): Máximo de registros a devolver.

        Returns:
            list[Ingrediente]: Lista de ingredientes.
        """
        return list(
            self.session.exec(
                select(Ingrediente).offset(offset).limit(limit)
            ).all()
        )

    def count(self) -> int:
        """
        Cuenta la cantidad total de ingredientes.

        Returns:
            int: Total de registros en la tabla Ingrediente.
        """
        return len(self.session.exec(select(Ingrediente)).all())


class ProductoIngredienteRepository(BaseRepository[ProductoIngrediente]):
    """
    Repositorio de la tabla intermedia ProductoIngrediente.
    Solo habla con la DB — nunca levanta HTTPException.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de ProductoIngrediente.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, ProductoIngrediente)

    def get_by_producto(self, producto_id: int) -> list[ProductoIngrediente]:
        """
        Obtiene todas las relaciones de un producto con sus ingredientes.

        Args:
            producto_id (int): ID del producto.

        Returns:
            list[ProductoIngrediente]: Lista de relaciones encontradas.
        """
        return list(
            self.session.exec(
                select(ProductoIngrediente).where(
                    ProductoIngrediente.producto_id == producto_id
                )
            ).all()
        )

    def get_by_pk(self, producto_id: int, ingrediente_id: int) -> ProductoIngrediente | None:
        """
        Obtiene una relación específica por su PK compuesta.

        Args:
            producto_id (int): ID del producto.
            ingrediente_id (int): ID del ingrediente.

        Returns:
            ProductoIngrediente | None: Relación encontrada o None.
        """
        return self.session.get(ProductoIngrediente, (producto_id, ingrediente_id))

    def exists(self, producto_id: int, ingrediente_id: int) -> bool:
        """
        Verifica si ya existe la relación entre producto e ingrediente.

        Args:
            producto_id (int): ID del producto.
            ingrediente_id (int): ID del ingrediente.

        Returns:
            bool: True si existe, False si no.
        """
        return self.get_by_pk(producto_id, ingrediente_id) is not None
