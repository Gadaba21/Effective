import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.dtos.user_dto import UserUpdatePartialDTO
from app.integrations.postgres.exceptions import (
    EmailAlreadyExistsPostgres,
    UsernameAlreadyExistsPostgres,
    UserNotFoundPostgres,
)
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    user_update = dto_factories[UserUpdatePartialDTO].build(
        username='test',
        email='test@example.com',
        nickname_color='#FFFFFF',
    )
    user = await orm_factories[UserORM].acreate(
        email='user@example.com',
        rank_id=None,
    )
    await user_repository.update(
        user_id=user.id,
        user_update=user_update,
    )
    updated_user = await fake_session.scalar(select(UserORM).where(UserORM.id == user.id))
    assert updated_user
    assert updated_user.email == user_update.email
    assert updated_user.username == user_update.username
    assert updated_user.nickname_color == user_update.nickname_color


async def test_nonexistent_user(
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    with pytest.raises(UserNotFoundPostgres):
        await user_repository.update(
            user_id=1,
            user_update=dto_factories[UserUpdatePartialDTO].build(
                username='test',
                email='test@example.com',
            ),
        )


async def test_username_already_exists_update(
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    user_1 = await orm_factories[UserORM].acreate(
        email='test@example.com',
        rank_id=None,
    )
    user_2 = await orm_factories[UserORM].acreate(
        email='user@example.com',
        rank_id=None,
    )
    user_update = dto_factories[UserUpdatePartialDTO].build(username=user_1.username)
    with pytest.raises(UsernameAlreadyExistsPostgres):
        await user_repository.update(
            user_id=user_2.id,
            user_update=user_update,
        )


async def test_email_already_exists_update(
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    user_1 = await orm_factories[UserORM].acreate(
        email='test@example.com',
        rank_id=None,
    )
    user_2 = await orm_factories[UserORM].acreate(
        email='user@example.com',
        rank_id=None,
    )
    user_update = dto_factories[UserUpdatePartialDTO].build(email=user_1.email)
    with pytest.raises(EmailAlreadyExistsPostgres):
        await user_repository.update(
            user_id=user_2.id,
            user_update=user_update,
        )
