from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.user_service import UserService
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    mock_user_service: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.delete(
        '/api/users/delete/',
    )
    assert result.status_code == status.HTTP_204_NO_CONTENT
    assert mock_user_service.delete_user.await_count == 1
