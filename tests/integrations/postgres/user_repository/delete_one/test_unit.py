from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(
        email='test@example.com',
        rank_id=None,
    )
    stmt = select(count(UserORM.id)).where(
        UserORM.id == user.id,
        UserORM.username == user.username,
        UserORM.email == user.email,
    )
    assert await fake_session.scalar(stmt) == 1
    await user_repository.delete_one(user_id=user.id)
    assert await fake_session.scalar(stmt) == 0
