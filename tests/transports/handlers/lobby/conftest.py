from unittest.mock import AsyncMock

import pytest

from app.services.lobby_service import LobbyService


@pytest.fixture
def mock_lobby_service() -> AsyncMock:
    return AsyncMock(spec=LobbyService)
