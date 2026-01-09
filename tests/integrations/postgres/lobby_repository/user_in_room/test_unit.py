from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest_utils import ORMFactoryDict


async def test_in_room(
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

    assert await fake_session.scalar(select(count(UserORM.id))) == 1
    await lobby_repository.user_in_room(user_id=user.id, in_room=True)
    assert user.in_room is True
    await lobby_repository.user_in_room(user_id=user.id, in_room=False)
    assert user.in_room is False
