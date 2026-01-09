from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.lobby_dto import RoomSchemaDTO
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_get_all_rooms(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    assert await fake_session.scalar(select(count(RoomORM.id))) == 0
    room1 = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    room2 = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)

    result = await fake_session.execute(select(RoomORM))
    rooms_from_db = result.scalars().all()
    assert await fake_session.scalar(select(count(RoomORM.id))) == 2
    assert await lobby_repository.get_all_rooms() == [RoomSchemaDTO.model_validate(room) for room in rooms_from_db]


async def test_get_all_rooms_zero(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    assert await fake_session.scalar(select(count(RoomORM.id))) == 0
    result = await fake_session.execute(select(RoomORM))
    rooms_from_db = result.scalars().all()
    assert await fake_session.scalar(select(count(RoomORM.id))) == 0
    assert await lobby_repository.get_all_rooms() == [RoomSchemaDTO.model_validate(room) for room in rooms_from_db]
    assert await lobby_repository.get_all_rooms() == []
