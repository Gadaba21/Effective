from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.integrations.postgres.dtos.user_dto import RankDetailDTO
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(users=[], name='валет', points_required=2)
    user = await orm_factories[UserORM].acreate(rank_id=rank.id)
    user_rank = await user_repository.get_rank(user_id=user.id)
    updated_user_rank = await fake_session.scalar(
        select(UserORM).where(UserORM.id == user.id).options(joinedload(UserORM.rank))
    )
    assert user_rank == RankDetailDTO.model_validate(user_rank)
    assert updated_user_rank.rank.id == rank.id


async def test_nonexistent_rank(
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(users=[], name='валет', points_required=2, id=1)

    user = await orm_factories[UserORM].acreate(rank_id=None)
    rank = await user_repository.get_rank(user_id=user.id)
    assert rank is None
