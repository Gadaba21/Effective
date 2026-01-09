from typing import Any, TypeVar, cast

from polyfactory.factories.base import BuildContext
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.field_meta import FieldMeta, Null
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.orms.baseorm import BaseORM

T = TypeVar('T')


class BaseORMFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __set_relationships__ = False
    __set_association_proxy__ = False
    __check_model__ = False
    async_session: AsyncSession

    @classmethod
    async def acreate(cls, **kwargs: Any) -> T:
        instance = cls.build(
            **kwargs,
        )
        cls.async_session.add(instance)
        await cls.async_session.flush()
        await cls.async_session.refresh(instance)
        return instance


class ORMFactoryDict:
    def __init__(self, session: AsyncSession) -> None:
        self._dict: dict[type[BaseORM], type[BaseORMFactory[BaseORM]]] = {}
        self._session = session

    def __getitem__(self, orm_class: type[T]) -> type[BaseORMFactory[T]]:
        if not self._dict.get(orm_class):
            self._dict[orm_class] = self._get_factory_from_orm(orm_class)
        return cast(type[BaseORMFactory[T]], self._dict[orm_class])

    def _get_factory_from_orm(self, orm_class: type[T]) -> type[BaseORMFactory[T]]:
        factory = cast(type[BaseORMFactory[orm_class]], BaseORMFactory.create_factory(orm_class))  # type: ignore[valid-type]
        factory.async_session = self._session
        return factory


class BaseDTOFactory(ModelFactory[T]):
    __is_base_factory__ = True
    __check_model__ = False

    @classmethod
    def get_field_value(
        cls,
        field_meta: FieldMeta,
        field_build_parameters: Any | None = None,
        build_context: BuildContext | None = None,
    ) -> Any:
        if field_meta.default is not Null:
            return field_meta.default
        return super().get_field_value(
            field_meta=field_meta,
            field_build_parameters=field_build_parameters,
            build_context=build_context,
        )


class DTOFactoryDict:
    def __init__(self) -> None:
        self._dict: dict[type[BaseModel], type[BaseDTOFactory[BaseModel]]] = {}

    def __getitem__(self, dto_class: type[T]) -> type[BaseDTOFactory[T]]:
        if not self._dict.get(dto_class):
            self._dict[dto_class] = self._get_factory_from_dto(dto_class)
        return cast(type[BaseDTOFactory[T]], self._dict[dto_class])

    def _get_factory_from_dto(self, dto_class: type[T]) -> type[BaseDTOFactory[T]]:
        return cast(
            type[BaseDTOFactory[dto_class]],  # type: ignore[valid-type]
            BaseDTOFactory.create_factory(dto_class),
        )
