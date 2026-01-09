from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.player_game_statistics_orm import UserGameStatisticsORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_update_game_statistic(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(rank_id=None)
    game_statistic = await orm_factories[UserGameStatisticsORM].acreate(won_game=2, total_game=5, user_id=user.id)
    assert await fake_session.scalar(select(count(UserGameStatisticsORM.id))) == 1

    await lobby_repository.update_game_statistic(win_game=3, total_game=11, statistic_id=game_statistic.id)
    game_statistic_orm = await fake_session.scalar(
        select(UserGameStatisticsORM).where(UserGameStatisticsORM.id == game_statistic.id)
    )
    await fake_session.refresh(game_statistic)

    assert game_statistic.won_game == game_statistic_orm.won_game
    assert game_statistic.total_game == game_statistic_orm.total_game
