from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.categoria.models import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Categoria)

    def get_by_nombre(self, nombre: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Categoria]:
        return list(
            self.session.exec(
                select(Categoria)
                .where(Categoria.deleted_at.is_(None))
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def get_by_parent(self, parent_id: int, offset: int = 0, limit: int = 20) -> list[Categoria]:
        return list(
            self.session.exec(
                select(Categoria)
                .where(Categoria.parent_id == parent_id)
                .where(Categoria.deleted_at.is_(None))
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count(self) -> int:
        return len(
            self.session.exec(
                select(Categoria).where(Categoria.deleted_at.is_(None))
            ).all()
        )
