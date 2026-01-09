import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.exceptions import PlayerNotFoundPostgres
from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest import dto_factories
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_disconnect_check(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    player = await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=True)

    assert await fake_session.scalar(select(count(PlayerORM.id))) == 1

    is_disconnect = await lobby_repository.disconnect_check(user_id=user.id, room_id=room.id)
    assert player.is_disconnect == is_disconnect
