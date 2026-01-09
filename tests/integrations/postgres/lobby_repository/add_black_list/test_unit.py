from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.blacklis_orm import BlackListORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_add_black_list(
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

    room = await orm_factories[RoomORM].acreate(players=[], settings=None, blacklisted_players=[], game=None)
    assert await fake_session.scalar(select(count(BlackListORM.id))) == 0
    await lobby_repository.add_black_list(room_id=room.id, user_id=user.id)
    assert await fake_session.scalar(select(count(BlackListORM.id))) == 1

    blacklist_entry = await fake_session.scalar(select(BlackListORM))
    assert blacklist_entry.user_id == user.id
    assert blacklist_entry.room_id == room.id

    await fake_session.refresh(room, ['blacklisted_players'])
    assert room.blacklisted_players == [blacklist_entry]
