from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import UsernameAlreadyExistsService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import TempUserCreate, UserTempResponse
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.create_temp_user.return_value = dto_factories[UserTempResponse].build()
    app.dependency_overrides[UserService] = lambda: mock_user_service
    result = await client.post(
        '/api/users/create_temp/',
        json=dto_factories[TempUserCreate].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_201_CREATED
    assert mock_user_service.create_temp_user.await_count == 1


async def test_username_already_exists(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_service.create_temp_user.side_effect = UsernameAlreadyExistsService
    app.dependency_overrides[UserService] = lambda: mock_user_service
    result = await client.post(
        '/api/users/create_temp/',
        json=dto_factories[TempUserCreate].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert mock_user_service.create_temp_user.await_count == 1
