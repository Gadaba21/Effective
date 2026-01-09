import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.repositories.lobby_repository import LobbyRepository


@pytest.fixture
def lobby_repository(fake_session: AsyncSession) -> LobbyRepository:
    return LobbyRepository(fake_session)
