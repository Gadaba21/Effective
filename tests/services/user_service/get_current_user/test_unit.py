from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import PlayerStatisticDTO, UserAchievementsDTO, UserDetailDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import PlayerStatisticResponse, UserAchievementsResponse, UserResponse
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserDetailDTO].build()
    expected_statistics = [dto_factories[PlayerStatisticDTO].build()]
    expected_achievements = [dto_factories[UserAchievementsDTO].build()]
    mock_user_repository.get_one_with_rank.return_value = expected_user
    mock_user_repository.get_user_statistics.return_value = expected_statistics
    mock_user_repository.get_user_achievements.return_value = expected_achievements
    result = await fake_user_service.get_current_user(user_id=1)
    assert result == UserResponse(
        **expected_user.model_dump(),
        statistics=[PlayerStatisticResponse(**statistic.model_dump()) for statistic in expected_statistics],
        achievements=[UserAchievementsResponse(**achievement.model_dump()) for achievement in expected_achievements],
    )


async def test_nonexistent_user(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
) -> None:
    mock_user_repository.get_one_with_rank.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_user_service.get_current_user(user_id=1)


async def test_empty_statistics(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserDetailDTO].build()
    expected_statistics = []
    expected_achievements = [dto_factories[UserAchievementsDTO].build()]
    mock_user_repository.get_one_with_rank.return_value = expected_user
    mock_user_repository.get_user_statistics.return_value = expected_statistics
    mock_user_repository.get_user_achievements.return_value = expected_achievements
    result = await fake_user_service.get_current_user(user_id=1)
    assert result == UserResponse(
        **expected_user.model_dump(),
        statistics=[],
        achievements=[UserAchievementsResponse(**achievement.model_dump()) for achievement in expected_achievements],
    )


async def test_empty_achievements(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserDetailDTO].build()
    expected_statistics = [dto_factories[PlayerStatisticDTO].build()]
    expected_achievements = []
    mock_user_repository.get_one_with_rank.return_value = expected_user
    mock_user_repository.get_user_statistics.return_value = expected_statistics
    mock_user_repository.get_user_achievements.return_value = expected_achievements
    result = await fake_user_service.get_current_user(user_id=1)
    assert result == UserResponse(
        **expected_user.model_dump(),
        statistics=[PlayerStatisticResponse(**statistic.model_dump()) for statistic in expected_statistics],
        achievements=[],
    )
