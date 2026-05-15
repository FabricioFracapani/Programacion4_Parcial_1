# app/modules/auth/repository.py
from sqlmodel import Session, select
from app.modules.auth.models import Usuario


class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(Usuario.username == username)
        ).first()

    def create(self, usuario: Usuario) -> Usuario:
        self.session.add(usuario)
        self.session.flush()
        self.session.refresh(usuario)
        return usuario

    def commit(self):
        self.session.commit()
