from unittest.mock import AsyncMock

import pytest

from app.services.user_service import UserService


@pytest.fixture
def mock_user_service() -> AsyncMock:
    return AsyncMock(spec=UserService)
