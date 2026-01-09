import os
from unittest.mock import AsyncMock

import pytest

from app.services.exceptions import FileExtensionService
from app.services.user_service import UserService
from app.transports.handlers.users.exceptions import FileNotUploadError
from app.transports.handlers.users.schemas import UpdatedUserResponse
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
    create_mock_image: AsyncMock,
) -> None:
    expected_user = dto_factories[UpdatedUserResponse].build()
    mock_user_repository.update.return_value = expected_user
    mock_file = create_mock_image('avatar.png')

    result = await fake_user_service.upload_user_avatar(user_id=1, file=mock_file)
    assert result == expected_user
    assert os.path.exists('/media/avatar/1_avatar.png')


async def test_invalid_file_extension(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_file = AsyncMock()
    mock_file.content_type = 'application/pdf'

    with pytest.raises(FileExtensionService):
        await fake_user_service.upload_user_avatar(user_id=1, file=mock_file)


async def test_file_not_uploaded(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
    create_mock_image: AsyncMock,
) -> None:
    mock_user_repository.update.side_effect = FileNotUploadError
    mock_file = create_mock_image('avatar.png')

    with pytest.raises(FileNotUploadError):
        await fake_user_service.upload_user_avatar(user_id=1, file=mock_file)


async def test_file_without_name(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
    create_mock_image: AsyncMock,
) -> None:
    mock_file = create_mock_image('')  # не указываем имя файла

    with pytest.raises(ValueError, match='Файл не имеет имени'):
        await fake_user_service.upload_user_avatar(user_id=1, file=mock_file)
