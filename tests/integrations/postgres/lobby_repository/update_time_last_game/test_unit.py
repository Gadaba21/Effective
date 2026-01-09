from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_update_time_last_game(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    assert await fake_session.scalar(select(count(RoomORM.id))) == 1

    await lobby_repository.update_time_last_game(room_id=room.id)
    room_orm = await fake_session.scalar(select(RoomORM).where(RoomORM.id == room.id))
    await fake_session.refresh(room)
    now = datetime.now(timezone.utc)
    time_diff = abs(room_orm.afk_time - now)

    assert time_diff < timedelta(seconds=2)
