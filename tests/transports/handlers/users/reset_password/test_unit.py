from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.code_service import CodeService
from app.services.exceptions import (
    CodeNotFoundService,
    InvalidNewPasswordService,
    InvalidOldPasswordService,
    UserNotFoundService,
)
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import AccessResetPasswordResponse, CodeDetail, ResetPassword
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.reset_password.return_value = dto_factories[AccessResetPasswordResponse].build()
    code_service = AsyncMock(spec=CodeService)
    code_service.get_code.return_value = dto_factories[CodeDetail].build()
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[CodeService] = lambda: code_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.post(
        '/api/users/reset_password/', json=dto_factories[ResetPassword].build().model_dump(mode='json')
    )
    assert result.status_code == status.HTTP_200_OK
    assert mock_user_service.reset_password.await_count == 1
    assert code_service.get_code.await_count == 1
    assert code_service.delete_code.await_count == 1


async def test_invalid_old_password(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.reset_password.side_effect = InvalidOldPasswordService
    code_service = AsyncMock(spec=CodeService)
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[CodeService] = lambda: code_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.post(
        '/api/users/reset_password/',
        json=dto_factories[ResetPassword]
        .build(
            new_password='Stringst1',
            old_password='Stringst1',
        )
        .model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_user_service.reset_password.await_count == 1
    assert code_service.get_code.await_count == 0
    assert code_service.delete_code.await_count == 0


async def test_invalid_new_password(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.reset_password.side_effect = InvalidNewPasswordService
    code_service = AsyncMock(spec=CodeService)
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[CodeService] = lambda: code_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.post(
        '/api/users/reset_password/', json=dto_factories[ResetPassword].build().model_dump(mode='json')
    )
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.reset_password.await_count == 1
    assert code_service.get_code.await_count == 0
    assert code_service.delete_code.await_count == 0


async def test_nonexistent_user(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.reset_password.side_effect = UserNotFoundService
    code_service = AsyncMock(spec=CodeService)
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[CodeService] = lambda: code_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.post(
        '/api/users/reset_password/', json=dto_factories[ResetPassword].build(new_password='qwee23444').model_dump(mode='json')
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_user_service.reset_password.await_count == 1
    assert code_service.get_code.await_count == 0
    assert code_service.delete_code.await_count == 0


async def test_nonexistent_code(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.reset_password.return_value = dto_factories[AccessResetPasswordResponse].build()
    code_service = AsyncMock(spec=CodeService)
    code_service.get_code.side_effect = CodeNotFoundService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[CodeService] = lambda: code_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.post(
        '/api/users/reset_password/', json=dto_factories[ResetPassword].build().model_dump(mode='json')
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_user_service.reset_password.await_count == 1
    assert code_service.get_code.await_count == 1
    assert code_service.delete_code.await_count == 0
