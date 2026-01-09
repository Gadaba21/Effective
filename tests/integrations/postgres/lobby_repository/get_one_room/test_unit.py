import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.lobby_dto import RoomSchemaDTO
from app.integrations.postgres.exceptions import RoomNotFoundPostgres
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_get_one_room(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    assert await fake_session.scalar(select(count(RoomORM.id))) == 0

    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    assert await fake_session.scalar(select(count(RoomORM.id))) == 1
    assert await lobby_repository.get_one_room(room_id=room.id) == RoomSchemaDTO.model_validate(room)


async def test_room_not_found(
    lobby_repository: LobbyRepository,
) -> None:
    with pytest.raises(RoomNotFoundPostgres):
        await lobby_repository.get_one_room(room_id=1)
