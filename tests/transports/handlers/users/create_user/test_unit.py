from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import EmailAlreadyExistsService, UsernameAlreadyExistsService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UserCreate, UserCreateResponse
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    raw_password = 'Stringst1'
    mock_user_service.create_user.return_value = dto_factories[UserCreateResponse].build()
    app.dependency_overrides[UserService] = lambda: mock_user_service
    with patch('app.integrations.celery.tasks.send_confirmation_email_task.delay') as mock_send_email_task:
        result = await client.post(
            '/api/users/create/',
            json=dto_factories[UserCreate]
            .build(
                password=raw_password,
                password_2=raw_password,
            )
            .model_dump(mode='json'),
        )
    assert result.status_code == status.HTTP_201_CREATED
    assert mock_user_service.create_user.await_count == 1
    mock_send_email_task.assert_called_once_with(result.json()['email'], result.url)


async def test_email_already_exists(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    raw_password = 'Stringst1'
    mock_user_service.create_user.side_effect = EmailAlreadyExistsService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    result = await client.post(
        '/api/users/create/',
        json=dto_factories[UserCreate]
        .build(
            password=raw_password,
            password_2=raw_password,
        )
        .model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.create_user.await_count == 1


async def test_username_already_exists(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    raw_password = 'Stringst1'
    mock_user_service.create_user.side_effect = UsernameAlreadyExistsService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    result = await client.post(
        '/api/users/create/',
        json=dto_factories[UserCreate]
        .build(
            password=raw_password,
            password_2=raw_password,
        )
        .model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.create_user.await_count == 1
