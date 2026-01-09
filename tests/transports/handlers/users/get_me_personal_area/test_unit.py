from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UserResponse
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_user_service: AsyncMock,
) -> None:
    mock_user_service.get_current_user.return_value = dto_factories[UserResponse].build()
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 123
    result = await client.get(
        f'/api/users/personal_area/',
    )
    assert result.status_code == status.HTTP_200_OK
    assert mock_user_service.get_current_user.await_count == 1


async def test_nonexistent_user(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
) -> None:
    mock_user_service.get_current_user.side_effect = UserNotFoundService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 123
    result = await client.get(
        f'/api/users/personal_area/',
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_user_service.get_current_user.await_count == 1
