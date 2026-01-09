from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.integrations.postgres.orms.baseorm import BaseORM


class UserGameStatisticsORM(BaseORM):
    """Хранит статистику игрока по играм."""

    __tablename__ = 'player_game_statistics'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер записи')
    game_name: Mapped[str] = mapped_column(comment='Название игры')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), comment='Номер игрока')
    total_game: Mapped[int] = mapped_column(default=0, comment='Сколько игр сыгранно')
    won_game: Mapped[int] = mapped_column(default=0, comment='Сколько игр выиграно')
