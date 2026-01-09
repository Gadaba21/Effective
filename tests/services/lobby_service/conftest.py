from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from app.integrations.postgres.repositories.settings_repository import SettingsRepository
from app.integrations.postgres.repositories.user_repository import UserRepository
from app.services.lobby_service import LobbyService


@pytest.fixture
def mock_lobby_repository() -> AsyncMock:
    return AsyncMock(spec=LobbyRepository)


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_settings_repository() -> AsyncMock:
    return AsyncMock(spec=SettingsRepository)


@pytest.fixture
def fake_lobby_service(
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    mock_settings_repository: AsyncMock,
) -> LobbyService:
    return LobbyService(lobby_repository=mock_lobby_repository,
                        user_repository=mock_user_repository,
                        settings_repository=mock_settings_repository)
