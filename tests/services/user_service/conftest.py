from io import BytesIO
import os
import shutil
from typing import Callable
from unittest.mock import AsyncMock

from PIL import Image
import pytest

from app.integrations.postgres.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def fake_user_service(
    mock_user_repository: AsyncMock,
) -> UserService:
    return UserService(user_repository=mock_user_repository)


@pytest.fixture
def create_mock_image() -> Callable[[str, str], AsyncMock]:
    def _create_mock_image(filename: str, format_: str = 'png') -> AsyncMock:
        img = Image.new('RGB', (200, 200), color='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format=format_)
        img_byte_arr.seek(0)
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=img_byte_arr.getvalue())
        mock_file.content_type = f'image/{format_}'
        mock_file.filename = filename
        return mock_file

    return _create_mock_image


@pytest.fixture(scope='module', autouse=True)
def setup_directory() -> None:
    temp_dir = '/media/avatar/'
    os.makedirs(temp_dir, exist_ok=True)
    yield
    shutil.rmtree(temp_dir, ignore_errors=True)
