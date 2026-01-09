import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import RecoveryPasswordDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    new_hash_password = 'test123'
    stmt = select(count(UserORM.id)).where(UserORM.hash_password == new_hash_password)
    user = await orm_factories[UserORM].acreate(
        email='test@example.com',
        hash_password='qwe123',
        rank_id=None,
    )

    assert await fake_session.scalar(stmt) == 0
    await user_repository.recovery_password(
        recovery_password_data=dto_factories[RecoveryPasswordDTO].build(
            email=user.email,
            hash_password=new_hash_password,
        )
    )
    assert await fake_session.scalar(stmt) == 1


async def test_nonexistent_user(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    with pytest.raises(UserNotFoundPostgres):
        await user_repository.recovery_password(
            recovery_password_data=dto_factories[RecoveryPasswordDTO].build(),
        )
