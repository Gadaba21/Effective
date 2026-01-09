from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.games_history_orm import GameHistoryORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_create_history_game(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    players = [{'id': 1, 'name': 'PlayerOne', 'points': 10}, {'id': 2, 'name': 'PlayerTwo', 'points': 154}]
    stmt = select(count(GameHistoryORM.id))
    assert await fake_session.scalar(stmt) == 0
    await lobby_repository.create_history_game(game_name='Black Jokes', game_id=1, players=[players])
    assert await fake_session.scalar(stmt) == 1
    history_stmt = select(GameHistoryORM).where(GameHistoryORM.game_id == 1)
    result = await fake_session.execute(history_stmt)
    updated_history = result.scalars().one()

    assert updated_history.game_name == 'Black Jokes'
    assert updated_history.players == [players]
