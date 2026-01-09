from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.achievement_orm import AchievementORM
from app.integrations.postgres.orms.games_achievements_orm import GameAchievementsORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_create_game_achievement(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    achievement = await orm_factories[AchievementORM].acreate()
    rank = await orm_factories[RankORM].acreate()
    user = await orm_factories[UserORM].acreate(rank_id=rank.id)
    stmt = select(count(GameAchievementsORM.id))
    assert await fake_session.scalar(stmt) == 0
    await lobby_repository.create_game_achievement(
        user_id=user.id, achievement_id=achievement.id, game_name='Black Jokes'
    )
    assert await fake_session.scalar(stmt) == 1
    game_achievement_stmt = select(GameAchievementsORM).where(GameAchievementsORM.user_id == user.id)
    result = await fake_session.execute(game_achievement_stmt)
    updated_game_achievement = result.scalars().one()

    assert updated_game_achievement.game_name == 'Black Jokes'
    assert updated_game_achievement.achievement_id == achievement.id
