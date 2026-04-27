from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Respuesta estandarizada para todos los endpoints de la API"""
    success: bool = True
    message: str = "Operación exitosa"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(APIResponse[T]):
    """Respuesta exitosa con datos opcionales"""
    def __init__(self, data: Optional[T] = None, message: str = "Operación exitosa", **kwargs):
        super().__init__(success=True, message=message, data=data, **kwargs)


class ErrorResponse(APIResponse):
    """Respuesta de error"""
    def __init__(self, message: str = "Error en la operación", data: Optional[Any] = None, **kwargs):
        super().__init__(success=False, message=message, data=data, **kwargs)


class ListResponse(BaseModel):
    """Respuesta para listados con paginación"""
    success: bool = True
    message: str = "Listado obtenido exitosamente"
    data: list = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 10
    timestamp: datetime = Field(default_factory=datetime.utcnow)
