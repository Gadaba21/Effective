from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.orms.blacklis_orm import BlackListORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_black_list(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )

    room = await orm_factories[RoomORM].acreate(
        players=[],
        settings=None,
        settings_fm=None,
        blacklisted_players=[],
        game=None,
    )
    await orm_factories[BlackListORM].acreate(room_id=room.id, user_id=user.id, room=room)

    blacklist_entry = await lobby_repository.black_list(room_id=room.id, user_id=user.id)

    assert blacklist_entry is True


async def test_black_list_empty(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    user1 = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(
        players=[],
        settings=None,
        settings_fm=None,
        blacklisted_players=[],
        game=None,
    )
    await orm_factories[BlackListORM].acreate(room_id=room.id, user_id=user1.id, room=room)

    blacklist_entry = await lobby_repository.black_list(room_id=room.id, user_id=user.id)
    assert blacklist_entry is False
