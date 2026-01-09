from datetime import datetime
from typing import TYPE_CHECKING

from passlib.context import CryptContext
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.integrations.postgres.orms.baseorm import BaseORM

if TYPE_CHECKING:
    from app.integrations.postgres.orms.rank_orm import RankORM

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserORM(BaseORM):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер пользователя')
    username: Mapped[str] = mapped_column(String(50), unique=True, comment='Имя пользователя')
    email: Mapped[str] = mapped_column(String, unique=True, comment='Электронная почта')
    hash_password: Mapped[str | None] = mapped_column(String(120), comment='Хешированный пароль')
    exp: Mapped[int] = mapped_column(default=0, comment='Очки опыта')
    rank_id: Mapped[str | None] = mapped_column(ForeignKey('ranks.id'), comment='Номер ранга')
    status: Mapped[bool] = mapped_column(default=False, comment='Статус пользователя')
    date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), comment='Дата регистрации')
    avatar: Mapped[str | None] = mapped_column(String, comment='Путь к аватару')
    is_vip: Mapped[bool] = mapped_column(default=False, comment='VIP статус')
    its_vip_time: Mapped[datetime | None] = mapped_column(DateTime, comment='Дата получения VIP статуса')
    count_vip_card_reset: Mapped[int] = mapped_column(default=0, comment='Количество сбросов карт VIP')
    dracoins: Mapped[int | None] = mapped_column(default=0, comment='Дракоины пользователя')
    is_active: Mapped[bool] = mapped_column(default=False, comment='Активность пользователя')
    in_room: Mapped[bool] = mapped_column(default=False, comment='Присутствие в комнате')
    nickname_color: Mapped[str] = mapped_column(String(8), default='#00FFFF', comment='Цвет ника')
    rank: Mapped['RankORM'] = relationship(back_populates='users', lazy='raise')
    time_last_game: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(), comment='Время последней игры'
    )
    is_admin: Mapped[bool] = mapped_column(default=False, comment='Является ли пользователь админом')


    def __str__(self) -> str:
        return self.username
