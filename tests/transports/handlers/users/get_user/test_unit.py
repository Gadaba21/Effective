from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UserPublicResponse
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_user_service: AsyncMock,
) -> None:
    mock_user_service.get_user.return_value = dto_factories[UserPublicResponse].build()
    app.dependency_overrides[UserService] = lambda: mock_user_service
    result = await client.get(
        f'/api/users/1/detail/',
    )
    assert result.status_code == status.HTTP_200_OK
    assert mock_user_service.get_user.await_count == 1


async def test_nonexistent_user(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
) -> None:
    mock_user_service.get_user.side_effect = UserNotFoundService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    result = await client.get(
        f'/api/users/1/detail/',
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_user_service.get_user.await_count == 1
