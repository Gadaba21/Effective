import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.exceptions import TitleCreateRoomPostgres
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from app.transports.handlers.lobby.schemas import RoomCreateSchema
from tests.conftest import dto_factories
from tests.conftest_utils import DTOFactoryDict


async def test_create_room(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    stmt = select(count(RoomORM.id))
    assert await fake_session.scalar(stmt) == 0
    await lobby_repository.create_room(room_data=dto_factories[RoomCreateSchema].build())
    assert await fake_session.scalar(stmt) == 1


async def test_creation_schema(
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    room_data = dto_factories[RoomCreateSchema].build()
    room = await lobby_repository.create_room(room_data=room_data)
    assert room.title == room_data.title
    assert room.max_players == room_data.max_players
    assert room.game_name == 'Идет выбор'


async def test_db_schema(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    room_data = dto_factories[RoomCreateSchema].build(
        title='test',
        password='123',
        max_players=3,
        is_private=True,
    )
    await lobby_repository.create_room(room_data=room_data)
    assert (
        await fake_session.scalar(
            select(count(RoomORM.id)).where(
                RoomORM.title == room_data.title,
                RoomORM.max_players == room_data.max_players,
                RoomORM.password == room_data.password,
                RoomORM.is_private == room_data.is_private,
            )
        )
        == 1
    )


async def test_creation_username_already_exists(
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
) -> None:
    room_data_1 = dto_factories[RoomCreateSchema].build()
    room_data_2 = dto_factories[RoomCreateSchema].build(title=room_data_1.title)
    await lobby_repository.create_room(room_data=room_data_1)
    with pytest.raises(TitleCreateRoomPostgres):
        await lobby_repository.create_room(room_data=room_data_2)
