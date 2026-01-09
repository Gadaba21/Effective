from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import PlayerStatisticDTO
from app.integrations.postgres.orms.player_game_statistics_orm import UserGameStatisticsORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_create_game_statistics(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(rank_id=None)
    stmt = select(count(UserGameStatisticsORM.id))
    assert await fake_session.scalar(stmt) == 0

    game_statistics = await lobby_repository.create_game_statistics(user_id=user.id, game_name='Black Jokes')
    assert await fake_session.scalar(stmt) == 1
    game_statistics_stmt = select(UserGameStatisticsORM).where(UserGameStatisticsORM.user_id == user.id)
    result = await fake_session.execute(game_statistics_stmt)
    updated_game_statistics = result.scalars().one()

    assert updated_game_statistics.game_name == game_statistics.game_name


async def test_db_schema(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(rank_id=None)

    game_statistics = await lobby_repository.create_game_statistics(user_id=user.id, game_name='Black Jokes')
    player_dto = dto_factories[PlayerStatisticDTO].build(
        game_name='Black Jokes',
        total_game=0,
        won_game=0,
    )
    assert player_dto.game_name == game_statistics.game_name

    assert (
        await fake_session.scalar(
            select(count(UserGameStatisticsORM.id)).where(
                # UserGameStatisticsORM.user_id == player_dto.user_id,
                UserGameStatisticsORM.game_name == player_dto.game_name,
                UserGameStatisticsORM.total_game == player_dto.total_game,
                UserGameStatisticsORM.won_game == player_dto.won_game,
            )
        )
        == 1
    )
