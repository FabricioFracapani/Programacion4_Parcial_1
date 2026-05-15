from typing import Optional, Sequence
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.auth.models import Usuario, Rol, UsuarioRol, RefreshToken


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session):
        super().__init__(session, Usuario)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        return self.session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()


class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session):
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Optional[Rol]:
        return self.session.get(Rol, codigo)


class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, session: Session):
        super().__init__(session, UsuarioRol)

    def get_roles_for_user(self, usuario_id: int) -> Sequence[str]:
        rows = self.session.exec(
            select(UsuarioRol.rol_codigo).where(UsuarioRol.usuario_id == usuario_id)
        ).all()
        return rows

    def assign_role(
        self, usuario_id: int, rol_codigo: str, asignado_por_id: Optional[int] = None
    ) -> UsuarioRol:
        existing = self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_codigo == rol_codigo,
            )
        ).first()
        if existing:
            return existing
        ur = UsuarioRol(
            usuario_id=usuario_id,
            rol_codigo=rol_codigo,
            asignado_por_id=asignado_por_id,
        )
        self.session.add(ur)
        self.session.flush()
        return ur


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: Session):
        super().__init__(session, RefreshToken)

    def get_valid_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        now = datetime.now(timezone.utc)
        return self.session.exec(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        ).first()

    def revoke_by_hash(self, token_hash: str) -> None:
        rt = self.session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()
        if rt:
            rt.revoked_at = datetime.now(timezone.utc)
            self.session.add(rt)
            self.session.flush()

    def revoke_all_for_user(self, usuario_id: int) -> None:
        tokens = self.session.exec(
            select(RefreshToken).where(
                RefreshToken.usuario_id == usuario_id,
                RefreshToken.revoked_at.is_(None),
            )
        ).all()
        for rt in tokens:
            rt.revoked_at = datetime.now(timezone.utc)
            self.session.add(rt)
        self.session.flush()
