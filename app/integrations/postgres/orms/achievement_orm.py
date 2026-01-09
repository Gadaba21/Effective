from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.integrations.postgres.orms.baseorm import BaseORM


class AchievementORM(BaseORM):
    __tablename__ = 'achievements'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер достижения')
    name: Mapped[str] = mapped_column(String(50), comment='Название достижения')
    desc: Mapped[str] = mapped_column(String(250), comment='Описание достижения')

    def __str__(self) -> str:
        return self.name
