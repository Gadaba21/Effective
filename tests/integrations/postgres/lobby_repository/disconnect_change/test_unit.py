from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_disconnect_change(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=True)

    assert await fake_session.scalar(select(count(PlayerORM.id))) == 1

    await lobby_repository.disconnect_change(user_id=user.id, is_disconnect=True)
    player_orm = await fake_session.scalar(select(PlayerORM).where(PlayerORM.user_id == user.id))
    assert player_orm.is_disconnect is True

    await lobby_repository.disconnect_change(user_id=user.id, is_disconnect=False)
    player_orm = await fake_session.scalar(select(PlayerORM).where(PlayerORM.user_id == user.id))
    assert player_orm.is_disconnect is False
