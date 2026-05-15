from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    codigo: str = Field(primary_key=True, max_length=20)
    nombre: str = Field(unique=True, max_length=50)
    descripcion: Optional[str] = Field(default=None)

    usuarios: List["UsuarioRol"] = Relationship(back_populates="rol")


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=80)
    apellido: str = Field(max_length=80)
    email: str = Field(unique=True, max_length=254, index=True)
    celular: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=60)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

    roles: List["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "[UsuarioRol.usuario_id]"},
    )
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="usuario")


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_codigo: str = Field(foreign_key="rol.codigo", primary_key=True, max_length=20)
    asignado_por_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    expires_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    usuario: Usuario = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={"foreign_keys": "[UsuarioRol.usuario_id]"},
    )
    rol: Rol = Relationship(back_populates="usuarios")


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    token_hash: str = Field(unique=True, max_length=64)
    expires_at: datetime = Field()
    revoked_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    usuario: Usuario = Relationship(back_populates="refresh_tokens")
