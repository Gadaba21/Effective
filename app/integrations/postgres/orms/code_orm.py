from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.integrations.postgres.orms.baseorm import BaseORM


class CodeORM(BaseORM):
    __tablename__ = 'codes'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Номер записи')
    code: Mapped[str] = mapped_column(String(6), comment='Код верификации')
    email: Mapped[str] = mapped_column(String, comment='Электронная почта пользователя')

    def __str__(self) -> str:
        return self.email
