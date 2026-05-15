from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.auth.repository import (
    UsuarioRepository,
    RolRepository,
    UsuarioRolRepository,
    RefreshTokenRepository,
)


class AuthUnitOfWork(UnitOfWork):
    def __init__(self, session: Session):
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.roles = RolRepository(session)
        self.usuarios_roles = UsuarioRolRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
