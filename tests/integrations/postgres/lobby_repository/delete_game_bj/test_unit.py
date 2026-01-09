from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.black_jokes.gameBJ_orm import GameBJORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_delete_game_bj(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    game = GameBJORM(
        name='Test Game',
        room_id=room.id,
    )
    fake_session.add(game)
    await fake_session.flush()
    await fake_session.refresh(game)
    assert await fake_session.scalar(select(count(GameBJORM.id))) == 1
    await lobby_repository.delete_game_bj(room_id=room.id)
    assert await fake_session.scalar(select(count(GameBJORM.id))) == 0
