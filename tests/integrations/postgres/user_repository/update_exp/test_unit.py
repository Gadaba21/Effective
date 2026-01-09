import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.dtos.user_dto import UserExpDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    user = await orm_factories[UserORM].acreate(rank_id=None, exp=0)
    updated_user_exp = await user_repository.update_exp(user_id=user.id, exp=2)
    updated_user = await fake_session.scalar(select(UserORM).where(UserORM.id == user.id))
    assert updated_user_exp == UserExpDTO.model_validate(user)
    assert updated_user_exp.exp == updated_user.exp == 2


async def test_nonexistent_user(
    user_repository: UserRepository,
) -> None:
    with pytest.raises(UserNotFoundPostgres):
        await user_repository.update_exp(user_id=1, exp=2)
