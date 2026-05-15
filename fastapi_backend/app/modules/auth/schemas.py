from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=3, max_length=100)


class RegisterRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    apellido: str = Field(min_length=1, max_length=80)
    email: str = Field(max_length=254)
    password: str = Field(min_length=3, max_length=100)
    celular: Optional[str] = Field(default=None, max_length=20)


class UserPublic(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    celular: Optional[str] = None
    roles: List[str] = []


class AuthResponse(BaseModel):
    success: bool = True
    message: str = "Operacion exitosa"
    user: UserPublic


class RolPublic(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
