from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import UserAchievementsDTO
from app.integrations.postgres.orms.achievement_orm import AchievementORM
from app.integrations.postgres.orms.games_achievements_orm import GameAchievementsORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_get_user_achievements(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    stmt = select(count(GameAchievementsORM.user_id))

    achievement = await orm_factories[AchievementORM].acreate()
    user = await orm_factories[UserORM].acreate(
        rank_id=None,
    )
    assert await fake_session.scalar(stmt) == 0
    user_achievement = await orm_factories[GameAchievementsORM].acreate(
        game_name='test',
        user_id=user.id,
        achievement_id=achievement.id,
    )
    assert await fake_session.scalar(stmt) == 1
    assert await user_repository.get_user_achievements(user_id=user.id) == [
        UserAchievementsDTO.model_validate(user_achievement)
    ]


async def test_nonexistent_user(
    user_repository: UserRepository,
) -> None:
    assert await user_repository.get_user_achievements(user_id=1) == []


async def test_nonexistent_achievements(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    assert await fake_session.scalar(select(count(GameAchievementsORM.id))) == 0
    user = await orm_factories[UserORM].acreate(
        rank_id=None,
    )
    assert await user_repository.get_user_achievements(user_id=user.id) == []
