from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.achievement_orm import AchievementORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    achievement = await orm_factories[AchievementORM].acreate()
    achievement2 = await orm_factories[AchievementORM].acreate()
    stmt = select(count(AchievementORM.id))
    assert await fake_session.scalar(stmt) == 2
    await user_repository.delete_all_achievement()
    assert await fake_session.scalar(stmt) == 0
