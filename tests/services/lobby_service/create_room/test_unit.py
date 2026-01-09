from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.lobby_dto import PlayerSchemaDTO, RoomCreateDTO
from app.integrations.postgres.dtos.user_dto import UserByIdDTO
from app.integrations.postgres.exceptions import TitleCreateRoomPostgres, UserNotFoundPostgres
from app.services.exceptions import TitleCreateRoomService, UserInRoomService, UserNotFoundService
from app.services.lobby_service import LobbyService
from app.transports.handlers.lobby.schemas import PlayerSchemaResponse, RoomCreateResponse, RoomCreateSchema
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    lobby = dto_factories[RoomCreateDTO].build()
    mock_lobby_repository.create_room.return_value = lobby
    player = dto_factories[PlayerSchemaDTO].build()
    mock_lobby_repository.create_player.return_value = player
    result = await fake_lobby_service.create_room(
        room_data=dto_factories[RoomCreateSchema].build(), current_user_id=user.id
    )
    assert result == RoomCreateResponse(**lobby.model_dump(), players=[PlayerSchemaResponse(**player.model_dump())])


async def test_user_not_found(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.get_one_by_id.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_lobby_service.create_room(room_data=dto_factories[RoomCreateSchema].build(), current_user_id=1)

    mock_user_repository.get_one_by_id.assert_awaited_once_with(user_id=1)
    assert mock_lobby_repository.create_room.await_count == 0
    assert mock_lobby_repository.create_player.await_count == 0


async def test_title_create_room(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    mock_lobby_repository.create_room.side_effect = TitleCreateRoomPostgres
    room_data = dto_factories[RoomCreateSchema].build()
    with pytest.raises(TitleCreateRoomService):
        await fake_lobby_service.create_room(room_data=room_data, current_user_id=user.id)

    mock_lobby_repository.create_room.assert_awaited_once_with(room_data=room_data)
    assert mock_lobby_repository.create_player.await_count == 0


async def test_user_in_room(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=True)
    mock_user_repository.get_one_by_id.return_value = user
    room_data = dto_factories[RoomCreateSchema].build()
    with pytest.raises(UserInRoomService):
        await fake_lobby_service.create_room(room_data=room_data, current_user_id=user.id)

    assert mock_lobby_repository.create_player.await_count == 0
    mock_lobby_repository.create_room.assert_awaited_once_with(room_data=room_data)
