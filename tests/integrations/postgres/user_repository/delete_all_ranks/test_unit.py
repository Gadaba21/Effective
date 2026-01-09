from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate()
    rank2 = await orm_factories[RankORM].acreate()
    stmt = select(count(RankORM.id))
    assert await fake_session.scalar(stmt) == 2
    await user_repository.delete_all_ranks()
    assert await fake_session.scalar(stmt) == 0
