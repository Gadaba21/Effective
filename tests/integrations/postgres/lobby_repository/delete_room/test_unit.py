from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_delete_room(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    room1 = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    room2 = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    assert await fake_session.scalar(select(count(RoomORM.id))) == 2
    await lobby_repository.delete_room(room_id=room1.id)
    assert await fake_session.scalar(select(count(RoomORM.id))) == 1
    room = await fake_session.scalar(select(RoomORM))
    assert room.id == room2.id
