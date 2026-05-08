# app/modules/ingrediente/service.py
from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone

from app.modules.ingrediente.models import Ingrediente
from app.modules.producto.models import ProductoIngrediente
from app.modules.ingrediente.schemas import (
    IngredienteCreate, IngredientePublic, IngredienteUpdate, IngredienteList,
    ProductoIngredienteCreate, ProductoIngredientePublic, ProductoIngredienteList
)
from app.modules.ingrediente.unit_of_work import IngredienteUnitOfWork


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IngredienteService:
    """
    Capa de lógica de negocio para Ingredientes y ProductoIngrediente.

    Responsabilidades:
    - Validaciones de dominio (nombre único, relación duplicada, etc.)
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
        """
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        """
        Obtiene un ingrediente por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (IngredienteUnitOfWork): Unidad de trabajo activa.
            ingrediente_id (int): ID del ingrediente.

        Returns:
            Ingrediente: Instancia encontrada.

        Raises:
            HTTPException: 404 si el ingrediente no existe.
        """
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )
        return ingrediente

    def _assert_nombre_unique(self, uow: IngredienteUnitOfWork, nombre: str) -> None:
        """
        Valida que el nombre no esté en uso.

        Args:
            uow (IngredienteUnitOfWork): Unidad de trabajo activa.
            nombre (str): Nombre a validar.

        Raises:
            HTTPException: 409 si el nombre ya existe.
        """
        if uow.ingredientes.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso",
            )

    def _assert_relacion_not_exists(self, uow: IngredienteUnitOfWork, producto_id: int, ingrediente_id: int) -> None:
        """
        Valida que la relación producto ↔ ingrediente no exista ya.

        Args:
            uow (IngredienteUnitOfWork): Unidad de trabajo activa.
            producto_id (int): ID del producto.
            ingrediente_id (int): ID del ingrediente.

        Raises:
            HTTPException: 409 si la relación ya existe.
        """
        if uow.producto_ingredientes.exists(producto_id, ingrediente_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El ingrediente id={ingrediente_id} ya está asignado al producto id={producto_id}",
            )

    def _get_relacion_or_404(self, uow: IngredienteUnitOfWork, producto_id: int, ingrediente_id: int) -> ProductoIngrediente:
        """
        Obtiene una relación por PK compuesta o lanza 404.

        Args:
            uow (IngredienteUnitOfWork): Unidad de trabajo activa.
            producto_id (int): ID del producto.
            ingrediente_id (int): ID del ingrediente.

        Returns:
            ProductoIngrediente: Relación encontrada.

        Raises:
            HTTPException: 404 si no existe.
        """
        relacion = uow.producto_ingredientes.get_by_pk(producto_id, ingrediente_id)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relación entre producto id={producto_id} e ingrediente id={ingrediente_id} no encontrada",
            )
        return relacion

    # ── Casos de uso: Ingrediente ─────────────────────────────────────────────

    def create(self, data: IngredienteCreate) -> IngredientePublic:
        """
        Crea un nuevo ingrediente.

        Flujo:
        - Valida unicidad de nombre
        - Construye entidad desde DTO
        - Persiste usando repositorio
        - Serializa antes de cerrar la transacción

        Args:
            data (IngredienteCreate): Datos de entrada.

        Returns:
            IngredientePublic: DTO de salida.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)
            ingrediente = Ingrediente.model_validate(data)
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)

        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> IngredienteList:
        """
        Obtiene lista paginada de ingredientes.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            IngredienteList: DTO con lista de ingredientes y total.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_all_paged(offset=offset, limit=limit)
            total = uow.ingredientes.count()

            result = IngredienteList(
                data=[IngredientePublic.model_validate(i) for i in ingredientes],
                total=total,
            )

        return result

    def get_by_id(self, ingrediente_id: int) -> IngredientePublic:
        """
        Obtiene un ingrediente por ID.

        Args:
            ingrediente_id (int): ID del ingrediente.

        Returns:
            IngredientePublic: DTO del ingrediente.

        Raises:
            HTTPException: 404 si no existe.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            result = IngredientePublic.model_validate(ingrediente)

        return result

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredientePublic:
        """
        Actualiza un ingrediente existente de forma parcial (PATCH).

        Flujo:
        - Obtiene entidad
        - Valida nombre si cambia
        - Aplica cambios dinámicamente
        - Persiste cambios

        Args:
            ingrediente_id (int): ID del ingrediente.
            data (IngredienteUpdate): Datos parciales.

        Returns:
            IngredientePublic: DTO actualizado.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)

            if data.nombre and data.nombre != ingrediente.nombre:
                self._assert_nombre_unique(uow, data.nombre)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(ingrediente, field, value)

            ingrediente.updated_at = _now()
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)

        return result

    def soft_delete(self, ingrediente_id: int) -> None:
        """
        Realiza un borrado lógico del ingrediente.

        Args:
            ingrediente_id (int): ID del ingrediente.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            ingrediente.activo = False
            ingrediente.deleted_at = _now()
            ingrediente.updated_at = _now()
            uow.ingredientes.add(ingrediente)

    # ── Casos de uso: ProductoIngrediente ────────────────────────────────────

    def create_relacion(self, data: ProductoIngredienteCreate) -> ProductoIngredientePublic:
        """
        Asigna un ingrediente a un producto.

        Flujo:
        - Valida que la relación no exista ya
        - Construye entidad desde DTO
        - Persiste usando repositorio

        Args:
            data (ProductoIngredienteCreate): Datos de la relación.

        Returns:
            ProductoIngredientePublic: DTO de la relación creada.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            self._assert_relacion_not_exists(uow, data.producto_id, data.ingrediente_id)
            relacion = ProductoIngrediente.model_validate(data)
            uow.producto_ingredientes.add(relacion)
            result = ProductoIngredientePublic.model_validate(relacion)

        return result

    def get_relaciones_por_producto(self, producto_id: int) -> ProductoIngredienteList:
        """
        Obtiene todos los ingredientes asignados a un producto.

        Args:
            producto_id (int): ID del producto.

        Returns:
            ProductoIngredienteList: DTO con lista de relaciones y total.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            relaciones = uow.producto_ingredientes.get_by_producto(producto_id)
            result = ProductoIngredienteList(
                data=[ProductoIngredientePublic.model_validate(r) for r in relaciones],
                total=len(relaciones),
            )

        return result

    def delete_relacion(self, producto_id: int, ingrediente_id: int) -> None:
        """
        Elimina la relación entre un producto y un ingrediente.

        Args:
            producto_id (int): ID del producto.
            ingrediente_id (int): ID del ingrediente.

        Raises:
            HTTPException: 404 si la relación no existe.
        """
        with IngredienteUnitOfWork(self._session) as uow:
            relacion = self._get_relacion_or_404(uow, producto_id, ingrediente_id)
            uow.producto_ingredientes.delete(relacion)
