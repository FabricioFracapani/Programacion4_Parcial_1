# app/modules/categoria/service.py
from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone

from app.modules.categoria.models import Categoria
from app.modules.categoria.schemas import CategoriaCreate, CategoriaPublic, CategoriaUpdate, CategoriaList
from app.modules.categoria.unit_of_work import CategoriaUnitOfWork

def _now() -> datetime:
    return datetime.now(timezone.utc)


class CategoriaService:
    """
    Capa de lógica de negocio para Categorias.

    Responsabilidades:
    - Validaciones de dominio (nombre único, parent válido, etc.)
    - Coordinar repositorios a través del UoW
    - Levantar HTTPException cuando corresponde
    - NUNCA acceder directamente a la Session

    REGLA IMPORTANTE — objetos ORM y commit():
    Después de que el UoW hace commit(), SQLAlchemy expira los atributos
    del objeto ORM. Toda serialización (model_dump / model_validate)
    debe ocurrir DENTRO del bloque `with uow:`, antes de que __exit__
    dispare el commit.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            session (Session): Sesión activa que será utilizada por el UnitOfWork.

        Nota:
            El servicio no maneja directamente la transacción; delega en CategoriaUnitOfWork.
        """
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: CategoriaUnitOfWork, categoria_id: int) -> Categoria:
        """
        Obtiene una categoría por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (CategoriaUnitOfWork): Unidad de trabajo activa.
            categoria_id (int): ID de la categoría.

        Returns:
            Categoria: Instancia encontrada.

        Raises:
            HTTPException: 404 si la categoría no existe.
        """
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )
        return categoria

    def _assert_nombre_unique(self, uow: CategoriaUnitOfWork, nombre: str) -> None:
        """
        Valida que el nombre no esté en uso.

        Args:
            uow (CategoriaUnitOfWork): Unidad de trabajo activa.
            nombre (str): Nombre a validar.

        Raises:
            HTTPException: 409 si el nombre ya existe.

        Nota:
            Esta validación es a nivel aplicación, no reemplaza un UNIQUE en DB.
        """
        if uow.categorias.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso",
            )

    def _assert_parent_exists(self, uow: CategoriaUnitOfWork, parent_id: int) -> None:
        """
        Valida que la categoría padre exista.

        Args:
            uow (CategoriaUnitOfWork): Unidad de trabajo activa.
            parent_id (int): ID de la categoría padre.

        Raises:
            HTTPException: 404 si la categoría padre no existe.
        """
        parent = uow.categorias.get_by_id(parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria padre con id={parent_id} no encontrada",
            )

    # ── Casos de uso ─────────────────────────────────────────────────────────

    def create(self, data: CategoriaCreate) -> CategoriaPublic:
        """
        Crea una nueva categoría.

        Flujo:
        - Valida unicidad de nombre
        - Valida que el parent exista (si se envía)
        - Construye entidad desde DTO
        - Persiste usando repositorio
        - Serializa antes de cerrar la transacción

        Args:
            data (CategoriaCreate): Datos de entrada.

        Returns:
            CategoriaPublic: DTO de salida.
        """
        with CategoriaUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)

            if data.parent_id is not None:
                self._assert_parent_exists(uow, data.parent_id)

            categoria = Categoria.model_validate(data)
            uow.categorias.add(categoria)

            result = CategoriaPublic.model_validate(categoria)

        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> CategoriaList:
        """
        Obtiene lista paginada de categorías activas.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            CategoriaList: DTO con lista de categorías y total.
        """
        with CategoriaUnitOfWork(self._session) as uow:
            categorias = uow.categorias.get_active(offset=offset, limit=limit)
            total = uow.categorias.count()

            result = CategoriaList(
                data=[CategoriaPublic.model_validate(c) for c in categorias],
                total=total,
            )

        return result

    def get_by_id(self, categoria_id: int) -> CategoriaPublic:
        """
        Obtiene una categoría por ID.

        Args:
            categoria_id (int): ID de la categoría.

        Returns:
            CategoriaPublic: DTO de la categoría.

        Raises:
            HTTPException: 404 si no existe.
        """
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            result = CategoriaPublic.model_validate(categoria)

        return result

    def get_by_parent(self, parent_id: int, offset: int = 0, limit: int = 20) -> CategoriaList:
        """
        Obtiene subcategorías de una categoría padre.

        Args:
            parent_id (int): ID de la categoría padre.
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            CategoriaList: DTO con lista de subcategorías y total.

        Raises:
            HTTPException: 404 si el padre no existe.
        """
        with CategoriaUnitOfWork(self._session) as uow:
            self._assert_parent_exists(uow, parent_id)
            categorias = uow.categorias.get_by_parent(parent_id, offset=offset, limit=limit)

            result = CategoriaList(
                data=[CategoriaPublic.model_validate(c) for c in categorias],
                total=len(categorias),
            )

        return result

    def update(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaPublic:
        """
        Actualiza una categoría existente de forma parcial (PATCH).

        Flujo:
        - Obtiene entidad
        - Valida nombre si cambia
        - Valida parent si cambia
        - Aplica cambios dinámicamente
        - Persiste cambios

        Args:
            categoria_id (int): ID de la categoría.
            data (CategoriaUpdate): Datos parciales.

        Returns:
            CategoriaPublic: DTO actualizado.
        """
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)

            if data.nombre and data.nombre != categoria.nombre:
                self._assert_nombre_unique(uow, data.nombre)

            if data.parent_id and data.parent_id != categoria.parent_id:
                self._assert_parent_exists(uow, data.parent_id)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(categoria, field, value)

            categoria.updated_at = _now()
            uow.categorias.add(categoria)
            result = CategoriaPublic.model_validate(categoria)

        return result

    def soft_delete(self, categoria_id: int) -> None:
        """
        Realiza un borrado lógico de la categoría.

        Flujo:
        - Obtiene entidad
        - Marca como inactiva y registra deleted_at
        - Persiste cambio

        Args:
            categoria_id (int): ID de la categoría.

        Nota:
            No elimina físicamente el registro de la base de datos.
        """
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            categoria.activo = False
            categoria.deleted_at = _now()
            categoria.updated_at = _now()
            uow.categorias.add(categoria)
