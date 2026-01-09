import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.postgres.repositories.user_repository import UserRepository


@pytest.fixture
def user_repository(fake_session: AsyncSession) -> UserRepository:
    return UserRepository(fake_session)
