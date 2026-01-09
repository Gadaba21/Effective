from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.black_jokes.gameBJ_orm import GameBJORM
from app.integrations.postgres.orms.black_jokes.playerBJ_orm import PlayerBJORM
from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_player_bj_disconnected(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    room = await orm_factories[RoomORM].acreate(
        players=[],
        settings=None,
        settings_fm=None,
        blacklisted_players=[],
        game=None,
    )
    game = await orm_factories[GameBJORM].acreate(
        room_id=room.id,
        players=[],
        name='Test Game',
    )
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    player = await orm_factories[PlayerORM].acreate(
        name='Test Player',
        user_id=user.id,
        room_id=room.id,
    )
    player_bj = await orm_factories[PlayerBJORM].acreate(
        name='Test',
        user_id=user.id,
        game_id=game.id,
        player_id=player.id,
    )

    assert await fake_session.scalar(select(count(PlayerBJORM.id))) == 1

    await lobby_repository.player_bj_disconnected(user_id=user.id, is_disconnect=True)
    player_orm = await fake_session.scalar(select(PlayerBJORM).where(PlayerBJORM.user_id == user.id))
    assert player_orm.is_disconnect is True

    await lobby_repository.player_bj_disconnected(user_id=user.id, is_disconnect=False)
    player_orm = await fake_session.scalar(select(PlayerBJORM).where(PlayerBJORM.user_id == user.id))
    assert player_orm.is_disconnect is False
