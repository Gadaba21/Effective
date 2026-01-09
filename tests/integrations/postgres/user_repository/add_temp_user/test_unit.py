import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import UserTempCreateDTO, UserTempResponseDTO
from app.integrations.postgres.exceptions import UsernameAlreadyExistsPostgres
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
    await user_repository.add_temp_user(user_temp_data=dto_factories[UserTempCreateDTO].build())
    assert await fake_session.scalar(stmt) == 1


async def test_creation_schema(
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_temp_data = dto_factories[UserTempCreateDTO].build()
    user_temp = await user_repository.add_temp_user(user_temp_data=user_temp_data)
    assert user_temp == UserTempResponseDTO(username=user_temp_data.username)


async def test_db_schema(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_temp_data = dto_factories[UserTempCreateDTO].build()
    await user_repository.add_temp_user(user_temp_data=user_temp_data)
    assert (
        await fake_session.scalar(
            select(count(UserORM.id)).where(
                UserORM.username == user_temp_data.username,
                UserORM.status == user_temp_data.status,
            )
        )
        == 1
    )


async def test_creation_username_already_exists(
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    user_temp_data = dto_factories[UserTempCreateDTO].build()
    await user_repository.add_temp_user(user_temp_data=user_temp_data)
    with pytest.raises(UsernameAlreadyExistsPostgres):
        await user_repository.add_temp_user(user_temp_data=user_temp_data)
