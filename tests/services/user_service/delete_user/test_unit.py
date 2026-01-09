from unittest.mock import AsyncMock

from app.services.user_service import UserService


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
) -> None:
    await fake_user_service.delete_user(user_id=1)
    assert mock_user_repository.delete_one.await_count == 1
