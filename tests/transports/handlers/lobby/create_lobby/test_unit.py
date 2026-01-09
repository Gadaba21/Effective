from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import TitleCreateRoomService, UserInRoomService, UserNotFoundService
from app.services.lobby_service import LobbyService
from app.transports.handlers.lobby.schemas import RoomCreateResponse, RoomCreateSchema
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.create_room.return_value = dto_factories[RoomCreateResponse].build()
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/',
        json=dto_factories[RoomCreateSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_201_CREATED
    assert mock_lobby_service.create_room.await_count == 1


async def test_user_in_room(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.create_room.side_effect = UserInRoomService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/',
        json=dto_factories[RoomCreateSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_lobby_service.create_room.await_count == 1


async def test_user_not_found(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.create_room.side_effect = UserNotFoundService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/',
        json=dto_factories[RoomCreateSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_lobby_service.create_room.await_count == 1


async def test_title_create_room(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.create_room.side_effect = TitleCreateRoomService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/',
        json=dto_factories[RoomCreateSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_lobby_service.create_room.await_count == 1
