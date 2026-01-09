import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.lobby_dto import PlayerSchemaDTO
from app.integrations.postgres.exceptions import PlayerNotFoundPostgres
from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest import dto_factories
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_get_player(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(
        rank_id=None,
    )
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    player = await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=False)
    assert await fake_session.scalar(select(count(PlayerORM.id))) == 1
    received_player = await lobby_repository.get_player(user_id=user.id)
    assert received_player == PlayerSchemaDTO.model_validate(player)
    assert received_player.user_id == user.id
    assert received_player.name == player.name


async def test_player_not_found(
    lobby_repository: LobbyRepository,
) -> None:
    with pytest.raises(PlayerNotFoundPostgres):
        await lobby_repository.get_player(user_id=1)
