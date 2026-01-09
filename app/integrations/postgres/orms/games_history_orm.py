from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.integrations.postgres.orms.baseorm import BaseORM


class GameHistoryORM(BaseORM):
    """Хранит историю игроков в играх."""

    __tablename__ = 'game_history'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер истории игроков')
    players: Mapped[JSON] = mapped_column(JSON, comment='Игроки')
    game_name: Mapped[str] = mapped_column(comment='Название игры')
    game_id: Mapped[int] = mapped_column(comment='Номер игры')
