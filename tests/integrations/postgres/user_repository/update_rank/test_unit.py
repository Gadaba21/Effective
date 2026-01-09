from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

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
    rank1 = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(rank_id=rank.id)
    stmt = select(count(UserORM.id)).where(
        UserORM.id == user.id,
        UserORM.rank_id == rank1.id,
    )
    assert await fake_session.scalar(stmt) == 0
    await user_repository.update_rank(
        user_id=user.id,
        rank=rank1.id,
    )
    assert await fake_session.scalar(stmt) == 1
