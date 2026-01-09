from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.integrations.postgres.orms.baseorm import BaseORM

if TYPE_CHECKING:
    from app.integrations.postgres.orms.room_orm import RoomORM


class BlackListORM(BaseORM):
    """Черный список"""

    __tablename__ = 'blacklist'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Id записи')
    user_id: Mapped[int] = mapped_column(comment='Номер пользователя')
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id', ondelete='CASCADE'), comment='Номер комнаты')
    room: Mapped['RoomORM'] = relationship(back_populates='blacklisted_players', lazy='raise')
