from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.services.exceptions import (
    UserInRoomService,
    UserNotFoundService, RoomNotFoundService, NoSlotService, PasswordRoomNotValidService, BlackListService,
    TitleCreateRoomService, DeleteRoomNotAdminService,
)
from app.services.lobby_service import LobbyService

from ..users.exceptions import UserNotFoundError
from ..users.utils import get_current_user
from .exceptions import (
    BlackListError,
    NoSlotError,
    PasswordRoomNotValidError,
    RoomNotFoundError,
    TitleCreateRoomError,
    UserInRoomError, DeleteRoomNotAdminError,
)
from .schemas import (
    JoinRoomSchema,
    RoomCreateResponse,
    RoomCreateSchema,
    RoomResponse,
)

router_lobby = APIRouter(
    prefix='/api/lobby',
    tags=['lobby'],
)


@router_lobby.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def list_lobby(
    lobby_service: Annotated[LobbyService, Depends()],
) -> list[RoomResponse]:
    """Получение списка комнат"""
    return await lobby_service.get_all_rooms()


@router_lobby.post(
    '/',
    response_model=RoomCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lobby(
    room_data: RoomCreateSchema,
    lobby_service: Annotated[LobbyService, Depends()],
    current_user_id: Annotated[int, Depends(get_current_user)],
) -> RoomCreateResponse:
    """Создание новой комнаты."""
    try:
        room = await lobby_service.create_room(room_data=room_data, current_user_id=current_user_id)
        return room
    except UserInRoomService:
        raise UserInRoomError
    except UserNotFoundService:
        raise UserNotFoundError
    except TitleCreateRoomService:
        raise TitleCreateRoomError


@router_lobby.post(
    '/{room_id}/join/',
    status_code=status.HTTP_200_OK,
)
async def join_lobby(
    room_id: int,
    join_data: JoinRoomSchema,
    current_user_id: Annotated[int, Depends(get_current_user)],
    lobby_service: Annotated[LobbyService, Depends()],
) -> None:
    """Вход пользователя в комнату."""

    try:
        await lobby_service.join_lobby(room_id=room_id, user_id=current_user_id, join_data=join_data)
    except UserInRoomService:
        raise UserInRoomError
    except UserNotFoundService:
        raise UserNotFoundError
    except RoomNotFoundService:
        raise RoomNotFoundError
    except NoSlotService:
        raise NoSlotError
    except PasswordRoomNotValidService:
        raise PasswordRoomNotValidError
    except BlackListService:
        raise BlackListError


@router_lobby.post(
    '/{room_id}/delete/',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lobby(
    room_id: int,
    current_user_id: Annotated[int, Depends(get_current_user)],
    lobby_service: Annotated[LobbyService, Depends()],
) -> None:
    """Удаление комнаты(только админ)."""
    try:
        await lobby_service.delete_lobby(room_id=room_id, user_id=current_user_id)
    except DeleteRoomNotAdminService:
        raise DeleteRoomNotAdminError
    except UserNotFoundService:
        raise UserNotFoundError

