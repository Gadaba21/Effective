from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.user_service import UserService
from app.transports.handlers.users.exceptions import FileExtensionError, FileNotUploadError
from app.transports.handlers.users.schemas import UpdatedUserResponse
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_updated_user = dto_factories[UpdatedUserResponse].build()
    mock_user_service.upload_user_avatar.return_value = mock_updated_user
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    file_content = b'fake image content'
    file_name = 'avatar.png'
    result = await client.post('/api/users/1/upload_avatar/', files={'file': (file_name, file_content, 'image/png')})
    assert result.status_code == status.HTTP_200_OK
    assert result.json() == mock_updated_user.model_dump(mode='json')
    assert mock_user_service.upload_user_avatar.await_count == 1


async def test_invalid_file_extension(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.upload_user_avatar.side_effect = FileExtensionError
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    file_content = b'fake image content'
    file_name = 'document.pdf'
    result = await client.post(
        '/api/users/1/upload_avatar/', files={'file': (file_name, file_content, 'application/pdf')}
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_user_service.upload_user_avatar.await_count == 1


async def test_file_not_uploaded(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.upload_user_avatar.side_effect = FileNotUploadError
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    file_content = b'fake image content'
    file_name = 'avatar.png'
    result = await client.post('/api/users/1/upload_avatar/', files={'file': (file_name, file_content, 'image/png')})
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.upload_user_avatar.await_count == 1
