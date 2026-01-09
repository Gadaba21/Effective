import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import UserCreateDTO, UserDTO
from app.integrations.postgres.exceptions import EmailAlreadyExistsPostgres, UsernameAlreadyExistsPostgres
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict


async def test_creation_fact(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    stmt = select(count(UserORM.id))
    assert await fake_session.scalar(stmt) == 0
    await user_repository.add_one(user_data=dto_factories[UserCreateDTO].build())
    assert await fake_session.scalar(stmt) == 1


async def test_creation_schema(
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_data = dto_factories[UserCreateDTO].build()
    user = await user_repository.add_one(user_data=user_data)
    assert user == UserDTO(email=user_data.email)


async def test_db_schema(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_data = dto_factories[UserCreateDTO].build()
    await user_repository.add_one(user_data=user_data)
    assert (
        await fake_session.scalar(
            select(count(UserORM.id)).where(
                UserORM.email == user_data.email,
                UserORM.username == user_data.username,
                UserORM.status == user_data.status,
            )
        )
        == 1
    )


async def test_creation_username_already_exists(
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_data_1 = dto_factories[UserCreateDTO].build()
    user_data_2 = dto_factories[UserCreateDTO].build(username=user_data_1.username)
    await user_repository.add_one(user_data=user_data_1)
    with pytest.raises(UsernameAlreadyExistsPostgres):
        await user_repository.add_one(user_data=user_data_2)


async def test_creation_email_already_exists(
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_data = dto_factories[UserCreateDTO].build()
    await user_repository.add_one(user_data=user_data)
    with pytest.raises(EmailAlreadyExistsPostgres):
        await user_repository.add_one(user_data=user_data)
