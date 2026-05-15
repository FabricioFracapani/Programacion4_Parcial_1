from typing import Sequence
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.direccion.models import DireccionEntrega


class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session):
        super().__init__(session, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int) -> Sequence[DireccionEntrega]:
        return self.session.exec(
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.deleted_at.is_(None))
        ).all()

    def get_principal(self, usuario_id: int) -> DireccionEntrega | None:
        return self.session.exec(
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.es_principal == True)
            .where(DireccionEntrega.deleted_at.is_(None))
        ).first()

    def clear_principal(self, usuario_id: int) -> None:
        direcciones = self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal == True,
            )
        ).all()
        for d in direcciones:
            d.es_principal = False
            self.session.add(d)
        self.session.flush()
