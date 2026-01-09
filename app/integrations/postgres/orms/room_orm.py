from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.integrations.postgres.orms.baseorm import BaseORM
from app.integrations.postgres.orms.blacklis_orm import BlackListORM
from app.integrations.postgres.orms.player_orm import PlayerORM


class RoomORM(AsyncAttrs, BaseORM):
    __tablename__: str = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, comment='Название комнаты')
    is_private: Mapped[bool] = mapped_column(default=False, comment='Приватная')
    password: Mapped[str | None] = mapped_column(String(50), default=None, nullable=True, comment='Пароль')
    game_name: Mapped[str] = mapped_column(default='Идет выбор', comment='Название игры')
    max_players: Mapped[int] = mapped_column(default=12, comment='Максимальное количество игроков')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment='Время создания лобби'
    )
    afk_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment='Время простоя лобби'
    )
    started: Mapped[bool] = mapped_column(default=False, comment='Игра началась')
    players: Mapped[list['PlayerORM']] = relationship(
        back_populates='room', lazy='raise', cascade='all, delete', passive_deletes=True
    )
    blacklisted_players: Mapped[list['BlackListORM']] = relationship(
        back_populates='room', cascade='all, delete', passive_deletes=True, lazy='raise'
    )

    @property
    def chat_id(self) -> str:
        return str(self.id)
