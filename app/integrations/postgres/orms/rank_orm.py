from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.integrations.postgres.orms.baseorm import BaseORM

if TYPE_CHECKING:
    from app.integrations.postgres.orms.user_orm import UserORM


class RankORM(BaseORM):
    __tablename__ = 'ranks'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер ранга')
    name: Mapped[str] = mapped_column(String(20), comment='Название ранга')
    points_required: Mapped[int] = mapped_column(comment='Количество очков для ранга')

    users: Mapped[list['UserORM']] = relationship(back_populates='rank', lazy='raise')

    def __str__(self) -> str:
        return self.name
