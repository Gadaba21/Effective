from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.dtos.user_dto import RankDetailDTO
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.repositories.user_repository import UserRepository
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_happy_path(
    fake_session: AsyncSession,
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(users=[], name='валет', points_required=2)
    rank1 = await orm_factories[RankORM].acreate(users=[], name='король', points_required=4)
    rank2 = await orm_factories[RankORM].acreate(users=[], name='туз', points_required=6)
    next_rank = await user_repository.get_next_rank(user_exp=3)
    updated_next_rank = await fake_session.scalar(select(RankORM).where(RankORM.id == rank1.id))
    assert next_rank == RankDetailDTO.model_validate(next_rank)
    assert updated_next_rank.id == next_rank.id
    assert updated_next_rank.name != rank2.name
    assert updated_next_rank.points_required != rank.points_required


async def test_nonexistent_rank(
    user_repository: UserRepository,
    orm_factories: ORMFactoryDict,
    dto_factories: DTOFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(users=[], name='валет', points_required=2)
    rank1 = await orm_factories[RankORM].acreate(users=[], name='король', points_required=4)

    next_rank = await user_repository.get_next_rank(user_exp=4)
    assert next_rank is None

    next_rank = await user_repository.get_next_rank(user_exp=5)
    assert next_rank is None
