import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.user_dto import AchievementDTO
from app.integrations.postgres.exceptions import AchievementNotFoundPostgres
from app.integrations.postgres.orms.achievement_orm import AchievementORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest import dto_factories
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_get_achievement(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    achievement = await orm_factories[AchievementORM].acreate()
    assert await fake_session.scalar(select(count(AchievementORM.id))) == 1
    received_achievement = await lobby_repository.get_achievement(name_achievement=achievement.name)
    assert received_achievement == AchievementDTO.model_validate(achievement)
    assert received_achievement.desc == achievement.desc
    assert received_achievement.name == achievement.name


async def test_achievement_not_found(
    lobby_repository: LobbyRepository,
) -> None:
    with pytest.raises(AchievementNotFoundPostgres):
        await lobby_repository.get_achievement(name_achievement='fgffg')
