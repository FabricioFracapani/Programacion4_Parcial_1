# app/modules/producto/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.producto.models import Producto, ProductoCategoria, ProductoIngrediente


class ProductoRepository(BaseRepository[Producto]):
    """
    Repositorio de Productos.
    Solo habla con la DB — nunca levanta HTTPException.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def get_all_paged(self, offset: int = 0, limit: int = 20) -> list[Producto]:
        """Obtiene todos los productos con paginación."""
        return list(
            self.session.exec(
                select(Producto).offset(offset).limit(limit)
            ).all()
        )

    def get_by_categoria(self, categoria_id: int, offset: int = 0, limit: int = 20) -> list[Producto]:
        """Obtiene productos que pertenecen a una categoría específica."""
        return list(
            self.session.exec(
                select(Producto)
                .join(ProductoCategoria)
                .where(ProductoCategoria.categoria_id == categoria_id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count(self) -> int:
        """Cuenta la cantidad total de productos."""
        return len(self.session.exec(select(Producto)).all())


class ProductoCategoriaRepository(BaseRepository[ProductoCategoria]):
    """
    Repositorio de la tabla intermedia ProductoCategoria.
    Solo habla con la DB — nunca levanta HTTPException.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session, ProductoCategoria)

    def get_all_relaciones(self) -> list[ProductoCategoria]:
        """Obtiene todas las relaciones producto ↔ categoría."""
        return list(self.session.exec(select(ProductoCategoria)).all())

    def get_by_producto(self, producto_id: int) -> list[ProductoCategoria]:
        """Obtiene todas las categorías asignadas a un producto."""
        return list(
            self.session.exec(
                select(ProductoCategoria).where(
                    ProductoCategoria.producto_id == producto_id
                )
            ).all()
        )

    def get_by_pk(self, producto_id: int, categoria_id: int) -> ProductoCategoria | None:
        """Obtiene una relación específica por su PK compuesta."""
        return self.session.get(ProductoCategoria, (producto_id, categoria_id))

    def exists(self, producto_id: int, categoria_id: int) -> bool:
        """Verifica si ya existe la relación entre producto y categoría."""
        return self.get_by_pk(producto_id, categoria_id) is not None


class ProductoIngredienteRepository(BaseRepository[ProductoIngrediente]):
    """
    Repositorio de la tabla intermedia ProductoIngrediente.
    Solo habla con la DB — nunca levanta HTTPException.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session, ProductoIngrediente)

    def get_all_relaciones(self) -> list[ProductoIngrediente]:
        """Obtiene todas las relaciones producto ↔ ingrediente."""
        return list(self.session.exec(select(ProductoIngrediente)).all())

    def get_by_producto(self, producto_id: int) -> list[ProductoIngrediente]:
        """Obtiene todos los ingredientes asignados a un producto."""
        return list(
            self.session.exec(
                select(ProductoIngrediente).where(
                    ProductoIngrediente.producto_id == producto_id
                )
            ).all()
        )

    def get_by_pk(self, producto_id: int, ingrediente_id: int) -> ProductoIngrediente | None:
        """Obtiene una relación específica por su PK compuesta."""
        return self.session.get(ProductoIngrediente, (producto_id, ingrediente_id))

    def exists(self, producto_id: int, ingrediente_id: int) -> bool:
        """Verifica si ya existe la relación entre producto e ingrediente."""
        return self.get_by_pk(producto_id, ingrediente_id) is not None