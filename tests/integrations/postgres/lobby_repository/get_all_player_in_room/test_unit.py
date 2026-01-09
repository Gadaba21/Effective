from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.lobby_dto import PlayerSchemaDTO
from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest import dto_factories
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_get_all_player_in_room_successfully(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user_1 = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    user_2 = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    await lobby_repository.create_player(user_id=user_2.id, room_id=room.id, is_host=True)
    await lobby_repository.create_player(user_id=user_1.id, room_id=room.id, is_host=False)

    assert await fake_session.scalar(select(count(PlayerORM.id))) == 2
    result = await fake_session.execute(select(PlayerORM).where(PlayerORM.room_id == room.id))
    players_from_db = result.scalars().all()

    received_player = await lobby_repository.get_all_player_in_room(room_id=room.id)
    assert len(received_player) == 2
    assert received_player == [PlayerSchemaDTO.model_validate(player) for player in players_from_db]

    await lobby_repository.disconnect_change(user_id=user_1.id, is_disconnect=True)
    received_player = await lobby_repository.get_all_player_in_room(room_id=room.id)
    assert len(received_player) == 1


async def test_get_all_player_in_room_zero(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=True)
    await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=False)
    assert await fake_session.scalar(select(count(PlayerORM.id))) == 2
    await lobby_repository.disconnect_change(user_id=user.id, is_disconnect=True)

    received_player = await lobby_repository.get_all_player_in_room(room_id=room.id)
    assert received_player == []
