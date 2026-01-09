from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.integrations.postgres.orms.baseorm import BaseORM

if TYPE_CHECKING:
    from app.integrations.postgres.orms.room_orm import RoomORM


class PlayerORM(BaseORM):
    """Представляет игрока в игре."""

    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер игрока')
    name: Mapped[str] = mapped_column(comment='Ник игрока')
    user_id: Mapped[int | None] = mapped_column(comment='Номер пользователя')
    is_disconnect: Mapped[bool] = mapped_column(default=False, comment='Разрыв соединения')
    nickname_color: Mapped[str] = mapped_column(String(8), default='#00FFFF', comment='Цвет ника')
    avatar: Mapped[str | None] = mapped_column(comment='Путь к аватару')
    is_vip: Mapped[bool] = mapped_column(default=False, comment='VIP статус')
    is_host: Mapped[bool] = mapped_column(default=False, comment='Хост')
    room_id: Mapped[int] = mapped_column(
        ForeignKey('rooms.id', ondelete='CASCADE'), comment='ID комнаты, в которой находится игрок'
    )
    room: Mapped['RoomORM'] = relationship('RoomORM', back_populates='players', lazy='raise')
