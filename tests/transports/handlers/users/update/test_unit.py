from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import EmailAlreadyExistsService, UsernameAlreadyExistsService, UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UpdatedUserResponse, UserUpdate
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.update_user.return_value = dto_factories[UpdatedUserResponse].build()
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.patch(
        '/api/users/update/',
        json=dto_factories[UserUpdate].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_200_OK
    assert mock_user_service.update_user.await_count == 1


async def test_nonexistent_user(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.update_user.side_effect = UserNotFoundService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.patch(
        '/api/users/update/',
        json=dto_factories[UserUpdate].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_user_service.update_user.await_count == 1


async def test_username_already_exists(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.update_user.side_effect = UsernameAlreadyExistsService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.patch(
        '/api/users/update/',
        json=dto_factories[UserUpdate].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.update_user.await_count == 1


async def test_email_already_exists(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.update_user.side_effect = EmailAlreadyExistsService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.patch(
        '/api/users/update/',
        json=dto_factories[UserUpdate].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.update_user.await_count == 1
