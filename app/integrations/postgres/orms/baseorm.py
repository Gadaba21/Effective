from sqlalchemy.orm import DeclarativeBase


class BaseORM(DeclarativeBase):
    """Базовый класс для всех моделей."""

    __abstract__ = True
