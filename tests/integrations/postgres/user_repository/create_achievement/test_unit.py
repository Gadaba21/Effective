from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.game_bj_dto import AchievementCreateBJDTO
from app.integrations.postgres.orms.achievement_orm import AchievementORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_create_achievement(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    achievement = dto_factories[AchievementCreateBJDTO].build()

    stmt = select(count(AchievementORM.id))
    assert await fake_session.scalar(stmt) == 0
    await user_repository.create_achievement(achievement=achievement)
    assert await fake_session.scalar(stmt) == 1
    achievement_stmt = select(AchievementORM).where(AchievementORM.name == achievement.name)
    result = await fake_session.execute(achievement_stmt)
    updated_achievement = result.scalars().one()

    assert updated_achievement.name == achievement.name
    assert updated_achievement.desc == achievement.desc
