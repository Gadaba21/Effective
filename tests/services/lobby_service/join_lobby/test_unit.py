from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.lobby_dto import RoomSchemaDTO
from app.integrations.postgres.dtos.user_dto import UserByIdDTO
from app.integrations.postgres.exceptions import RoomNotFoundPostgres, UserNotFoundPostgres
from app.services.exceptions import (
    BlackListService,
    NoSlotService,
    RoomNotFoundService,
    UserInRoomService,
    UserNotFoundService,
)
from app.services.lobby_service import LobbyService
from app.transports.handlers.lobby.exceptions import PasswordRoomNotValidError
from app.transports.handlers.lobby.schemas import JoinRoomSchema, RoomResponse
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    lobby = dto_factories[RoomSchemaDTO].build()
    mock_lobby_repository.get_one_room.return_value = lobby
    mock_lobby_repository.black_list.return_value = False
    result = await fake_lobby_service.join_lobby(
        join_data=JoinRoomSchema(password=lobby.password), user_id=user.id, room_id=lobby.id
    )

    assert result == RoomResponse(**lobby.model_dump())


async def test_user_not_found(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.get_one_by_id.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_lobby_service.join_lobby(join_data=JoinRoomSchema(password=None), user_id=1, room_id=1)

    assert mock_lobby_repository.user_in_room.await_count == 0
    assert mock_lobby_repository.find_player.await_count == 0
    assert mock_lobby_repository.get_one_room.await_count == 0
    mock_user_repository.get_one_by_id.assert_awaited_once_with(1)


async def test_user_in_room(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=True)
    mock_user_repository.get_one_by_id.return_value = user
    with pytest.raises(UserInRoomService):
        await fake_lobby_service.join_lobby(join_data=JoinRoomSchema(password=None), user_id=user.id, room_id=1)
    assert mock_lobby_repository.user_in_room.await_count == 0


async def test_room_not_found(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    mock_lobby_repository.get_one_room.side_effect = RoomNotFoundPostgres
    with pytest.raises(RoomNotFoundService):
        await fake_lobby_service.join_lobby(join_data=JoinRoomSchema(password=None), user_id=user.id, room_id=1)

    assert mock_lobby_repository.user_in_room.await_count == 0


async def test_no_slot(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    lobby = dto_factories[RoomSchemaDTO].build(
        max_players=2,
        players=[{'id': 1, 'name': 'Player1'}, {'id': 2, 'name': 'Player2'}, {'id': 3, 'name': 'Player3'}],
    )
    mock_lobby_repository.get_one_room.return_value = lobby
    with pytest.raises(NoSlotService):
        await fake_lobby_service.join_lobby(
            join_data=JoinRoomSchema(password=lobby.password), user_id=user.id, room_id=lobby.id
        )
    assert mock_lobby_repository.user_in_room.await_count == 0


async def test_equals_slot(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    lobby = dto_factories[RoomSchemaDTO].build(
        max_players=2,
        players=[{'id': 1, 'name': 'Player1'}, {'id': 2, 'name': 'Player2'}],
    )
    mock_lobby_repository.get_one_room.return_value = lobby
    mock_lobby_repository.black_list.return_value = False
    result = await fake_lobby_service.join_lobby(
        join_data=JoinRoomSchema(password=lobby.password), user_id=user.id, room_id=lobby.id
    )

    assert result == RoomResponse(**lobby.model_dump())
    assert mock_lobby_repository.user_in_room.await_count == 1


async def test_password_room_not_valid_error(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    lobby = dto_factories[RoomSchemaDTO].build(password='1254')
    mock_lobby_repository.get_one_room.return_value = lobby
    with pytest.raises(PasswordRoomNotValidError):
        await fake_lobby_service.join_lobby(
            join_data=JoinRoomSchema(password='fjgkldfjgk'), user_id=user.id, room_id=lobby.id
        )

    assert mock_lobby_repository.user_in_room.await_count == 0


async def test_black_list(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    user = dto_factories[UserByIdDTO].build(in_room=False)
    mock_user_repository.get_one_by_id.return_value = user
    lobby = dto_factories[RoomSchemaDTO].build()
    mock_lobby_repository.get_one_room.return_value = lobby
    mock_lobby_repository.black_list.return_value = True
    with pytest.raises(BlackListService):
        await fake_lobby_service.join_lobby(
            join_data=JoinRoomSchema(password=lobby.password), user_id=user.id, room_id=lobby.id
        )
    assert mock_lobby_repository.user_in_room.await_count == 0
