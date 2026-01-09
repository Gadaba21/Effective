from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_update_time_last_game(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(rank_id=None)
    assert await fake_session.scalar(select(count(UserORM.id))) == 1
    await user_repository.update_time_last_game(user_id=user.id)
    user_orm = await fake_session.scalar(select(UserORM).where(UserORM.id == user.id))

    await fake_session.refresh(user)
    now = datetime.now(timezone.utc)
    time_diff = abs(user_orm.time_last_game - now)

    assert time_diff < timedelta(seconds=2)
