from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_change_password(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    assert await fake_session.scalar(select(count(RoomORM.id))) == 1
    room_orm = await fake_session.scalar(select(RoomORM).where(RoomORM.id == room.id))
    assert room.password == room_orm.password

    await lobby_repository.change_password(room_id=room.id, password='12344fgfg')
    room_orm = await fake_session.scalar(select(RoomORM).where(RoomORM.id == room.id))
    assert room_orm.password == '12344fgfg'
