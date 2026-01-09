from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.exceptions import (
    BlackListService,
    NoSlotService,
    PasswordRoomNotValidService,
    RoomNotFoundService,
    UserInRoomService,
    UserNotFoundService,
)
from app.services.lobby_service import LobbyService
from app.transports.handlers.lobby.schemas import JoinRoomSchema, RoomResponse
from app.transports.handlers.users.utils import get_current_user
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.return_value = dto_factories[RoomResponse].build()
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    app.dependency_overrides[get_current_user] = lambda: 1
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_200_OK
    assert mock_lobby_service.join_lobby.await_count == 1


async def test_user_in_room(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.side_effect = UserInRoomService
    app.dependency_overrides[get_current_user] = lambda: 1
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_lobby_service.join_lobby.await_count == 1


async def test_user_not_found(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.side_effect = UserNotFoundService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_lobby_service.join_lobby.await_count == 1


async def test_room_not_found(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.side_effect = RoomNotFoundService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert mock_lobby_service.join_lobby.await_count == 1


async def test_no_slot(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.side_effect = NoSlotService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_lobby_service.join_lobby.await_count == 1


async def test_password_room_no_valid(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.side_effect = PasswordRoomNotValidService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_lobby_service.join_lobby.await_count == 1


async def test_black_list(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
    mock_lobby_service: AsyncMock,
) -> None:
    mock_lobby_service.join_lobby.side_effect = BlackListService
    app.dependency_overrides[get_current_user] = lambda: 123
    app.dependency_overrides[LobbyService] = lambda: mock_lobby_service
    result = await client.post(
        f'/api/lobby/1/join/',
        json=dto_factories[JoinRoomSchema].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert mock_lobby_service.join_lobby.await_count == 1
