import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    stmt = select(count(UserORM.id)).where(UserORM.is_active == True)
    user = await orm_factories[UserORM].acreate(
        email='test@example.com',
        is_active=False,
        rank_id=rank.id,
    )
    assert await fake_session.scalar(stmt) == 0
    await user_repository.activate_user(email=user.email)
    assert await fake_session.scalar(stmt) == 1


async def test_nonexistent_user(
    user_repository: UserRepository,
) -> None:
    with pytest.raises(UserNotFoundPostgres):
        await user_repository.activate_user(email='test@example.com')
