from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import ActivateUser
from app.transports.handlers.users.utils import EmailService, create_token_for_confirm_email
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_return = ActivateUser(access='Ваш аккаунт был успешно активирован!')
    mock_user_service.activate_user.return_value = expected_return
    email_service = AsyncMock(spec=EmailService)
    token_mock = create_token_for_confirm_email(data={'email': 'test@mail.com'})

    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[EmailService] = lambda: email_service

    result = await client.get(
        f'/api/users/create/access_email/{token_mock}/',
    )

    assert result.status_code == status.HTTP_200_OK
    assert mock_user_service.activate_user.await_count == 1
    assert result.json() == expected_return.model_dump()


async def test_invalid_token(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    invalid_token = 'invalid_token'
    app.dependency_overrides[UserService] = lambda: mock_user_service

    result = await client.get(
        f'/api/users/create/access_email/{invalid_token}/',
    )

    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json() == {'detail': 'Неверный или истёкший токен подтверждения.'}


async def test_nonexistent_user(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.activate_user.side_effect = UserNotFoundService
    token_mock = create_token_for_confirm_email(data={'email': 'test@mail.com'})

    app.dependency_overrides[UserService] = lambda: mock_user_service

    result = await client.get(
        f'/api/users/create/access_email/{token_mock}/',
    )

    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_user_service.activate_user.await_count == 1
