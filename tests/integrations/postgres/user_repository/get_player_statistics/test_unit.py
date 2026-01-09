from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import PlayerStatisticDTO
from app.integrations.postgres.orms.player_game_statistics_orm import UserGameStatisticsORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_get_user_statistics(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    stmt = select(count(UserGameStatisticsORM.user_id))
    user = await orm_factories[UserORM].acreate(
        rank_id=None,
    )
    assert await fake_session.scalar(stmt) == 0
    user_statistics = await orm_factories[UserGameStatisticsORM].acreate(game_name='test', user_id=user.id)
    assert await fake_session.scalar(stmt) == 1
    assert await user_repository.get_user_statistics(user_id=user_statistics.user_id) == [
        PlayerStatisticDTO.model_validate(user_statistics)
    ]


async def test_nonexistent_user(
    user_repository: UserRepository,
) -> None:
    assert await user_repository.get_user_statistics(user_id=1) == []


async def test_nonexistent_statistics(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    assert await fake_session.scalar(select(count(UserGameStatisticsORM.user_id))) == 0
    user = await orm_factories[UserORM].acreate(
        rank_id=None,
    )
    assert await user_repository.get_user_statistics(user_id=user.id) == []
