from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import CreateRankDTO
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_create_rank(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    rank = dto_factories[CreateRankDTO].build()

    stmt = select(count(RankORM.id))
    assert await fake_session.scalar(stmt) == 0
    await user_repository.create_rank(rank=rank)
    assert await fake_session.scalar(stmt) == 1
    achievement_stmt = select(RankORM).where(RankORM.name == rank.name)
    result = await fake_session.execute(achievement_stmt)
    updated_achievement = result.scalars().one()

    assert updated_achievement.name == rank.name
    assert updated_achievement.points_required == rank.points_required
