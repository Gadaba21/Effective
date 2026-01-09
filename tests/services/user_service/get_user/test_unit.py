from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import UserAchievementsDTO, UserPublicDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UserAchievementsResponse, UserPublicResponse
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserPublicDTO].build()
    expected_achievements = [dto_factories[UserAchievementsDTO].build()]
    mock_user_repository.get_one_with_rank_public.return_value = expected_user
    mock_user_repository.get_user_achievements.return_value = expected_achievements
    result = await fake_user_service.get_user(user_id=1)
    assert result == UserPublicResponse(
        **expected_user.model_dump(),
        achievements=[UserAchievementsResponse(**achievement.model_dump()) for achievement in expected_achievements],
    )


async def test_nonexistent_user(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
) -> None:
    mock_user_repository.get_one_with_rank_public.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_user_service.get_user(user_id=1)


async def test_empty_achievements(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserPublicDTO].build()
    mock_user_repository.get_one_with_rank_public.return_value = expected_user
    mock_user_repository.get_user_achievements.return_value = []
    result = await fake_user_service.get_user(user_id=1)
    assert mock_user_repository.get_user_achievements.await_count == 1
    assert result == UserPublicResponse(**expected_user.model_dump(), achievements=[])
