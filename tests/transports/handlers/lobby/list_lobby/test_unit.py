from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.lobby_service import LobbyService
from app.transports.handlers.lobby.schemas import RoomResponse
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.get_all_rooms.return_value = [dto_factories[RoomResponse].build()]
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.get(
        f'/api/lobby/',
    )
    assert result.status_code == status.HTTP_200_OK
    assert mock_lobby_service.get_all_rooms.await_count == 1
