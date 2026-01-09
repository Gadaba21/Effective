from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import PlayerStatisticDTO
from app.integrations.postgres.orms.player_game_statistics_orm import UserGameStatisticsORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_get_game_statistics(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(rank_id=None)

    game_statistics = await orm_factories[UserGameStatisticsORM].acreate(user_id=user.id)
    assert await fake_session.scalar(select(count(UserGameStatisticsORM.id))) == 1
    received_game_statistics = await lobby_repository.get_game_statistics(user_id=game_statistics.user_id)
    assert received_game_statistics == PlayerStatisticDTO.model_validate(game_statistics)
    assert received_game_statistics.game_name == game_statistics.game_name
    assert received_game_statistics.won_game == game_statistics.won_game
    assert received_game_statistics.total_game == game_statistics.total_game


async def test_game_statistics_is_none(
    lobby_repository: LobbyRepository,
) -> None:
    game_statistics = await lobby_repository.get_game_statistics(user_id=1)
    assert game_statistics is None
