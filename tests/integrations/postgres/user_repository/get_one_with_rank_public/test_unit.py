import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import UserPublicDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import ORMFactoryDict


async def test_target_user_with_rank(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    assert await fake_session.scalar(select(count(UserORM.id))) == 0
    user = await orm_factories[UserORM].acreate(
        email='test@example.com',
        rank_id=rank.id,
    )
    assert await fake_session.scalar(select(count(UserORM.id))) == 1
    assert await fake_session.scalar(select(count(RankORM.id))) == 1
    assert rank.id == user.rank_id
    assert await user_repository.get_one_with_rank_public(user_id=user.id) == UserPublicDTO.model_validate(user)


async def test_target_user_without_rank(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    assert await fake_session.scalar(select(count(UserORM.id))) == 0
    user = await orm_factories[UserORM].acreate(
        email='test@example.com',
        rank=None,
        rank_id=None,
    )
    assert await fake_session.scalar(select(count(UserORM.id))) == 1
    assert await fake_session.scalar(select(count(RankORM.id))) == 0
    assert user.rank_id is None
    assert await user_repository.get_one_with_rank_public(user_id=user.id) == UserPublicDTO.model_validate(user)


async def test_nonexistent_user(
    user_repository: UserRepository,
) -> None:
    with pytest.raises(UserNotFoundPostgres):
        await user_repository.get_one_with_rank_public(user_id=1)
