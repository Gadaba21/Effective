from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.integrations.postgres.orms.baseorm import BaseORM

if TYPE_CHECKING:
    from app.integrations.postgres.orms.achievement_orm import AchievementORM


class GameAchievementsORM(BaseORM):
    """Хранит достижения игроков в играх."""

    __tablename__ = 'game_achievements'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер достижения игрока')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), comment='Номер игрока')
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey('achievements.id', ondelete='CASCADE'), comment='Номер достижения'
    )
    game_name: Mapped[str] = mapped_column(comment='Название игры')
    receiving_cond: Mapped[datetime] = mapped_column(server_default=func.now(), comment='Время получения')
    achievement: Mapped['AchievementORM'] = relationship(lazy='raise')
