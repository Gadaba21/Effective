from typing import Annotated

from fastapi import Depends

from app.integrations.postgres.exceptions import RoomNotFoundPostgres, UserNotFoundPostgres, TitleCreateRoomPostgres
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository

from app.integrations.postgres.repositories.user_repository import UserRepository
from app.services.exceptions import (
    UserInRoomService,
    UserNotFoundService, TitleCreateRoomService, RoomNotFoundService, NoSlotService, BlackListService,
    DeleteRoomNotAdminService,
)
from app.transports.handlers.lobby.exceptions import PasswordRoomNotValidError
from app.transports.handlers.lobby.schemas import (
    JoinRoomSchema,
    PlayerSchemaResponse,
    RoomCreateResponse,
    RoomCreateSchema,
    RoomResponse,
)
from app.utils.logger_config import user_lobby_logger


class LobbyService:
    def __init__(
        self,
        lobby_repository: Annotated[LobbyRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
    ) -> None:
        self._lobby_repository = lobby_repository
        self._user_repository = user_repository

    async def get_all_rooms(
        self,
    ) -> list[RoomResponse]:
        """Сервис получения всех комнат"""
        result = await self._lobby_repository.get_all_rooms()
        return [RoomResponse(**room.model_dump()) for room in result]

    async def create_room(self, room_data: RoomCreateSchema, current_user_id: int) -> RoomCreateResponse:
        """Сервис создания комнаты"""
        user_lobby_logger.info(f'Пользователь {current_user_id} создаёт комнату с данными: {room_data.model_dump()}')
        try:
            user = await self._user_repository.get_one_by_id(user_id=current_user_id)
        except UserNotFoundPostgres as exc:
            user_lobby_logger.error(f'Пользователь {current_user_id} не найден')
            raise UserNotFoundService from exc

        try:
            room = await self._lobby_repository.create_room(room_data=room_data)
        except TitleCreateRoomPostgres as exc:
            user_lobby_logger.error(f'Ошибка при создании комнаты: название {room_data.title} уже занято')
            raise TitleCreateRoomService from exc

        if user.in_room:
            user_lobby_logger.warning(f'Пользователь {current_user_id} уже находится в другой комнате')
            raise UserInRoomService

        player = await self._lobby_repository.create_player(room_id=room.id, user_id=current_user_id, is_host=True)
        user_lobby_logger.info(f'Комната {room.id} успешно создана пользователем {current_user_id}')
        return RoomCreateResponse(**room.model_dump(), players=[PlayerSchemaResponse(**player.model_dump())])

    async def join_lobby(
        self,
        join_data: JoinRoomSchema,
        room_id: int,
        user_id: int,
    ) -> RoomResponse:
        """Сервис входа в лобби"""
        user_lobby_logger.info(
            f'Пользователь {user_id} пытается войти в комнату {room_id} с паролем: {join_data.password or "None"}'
        )

        await self._lobby_repository.delete_player_except_current_room(user_id=user_id, room_id=room_id)

        try:
            user = await self._user_repository.get_one_by_id(user_id)
        except UserNotFoundPostgres as exc:
            user_lobby_logger.error(f'Пользователь {user_id} не найден')
            raise UserNotFoundService from exc

        if user.in_room:
            user_lobby_logger.warning(f'Пользователь {user_id} уже в другой комнате')
            raise UserInRoomService

        if not await self._lobby_repository.find_player(user_id=user_id):
            await self._lobby_repository.create_player(room_id=room_id, user_id=user_id, is_host=False)
            user_lobby_logger.info(f'Пользователь {user_id} добавлен в комнату {room_id}')

        try:
            room = await self._lobby_repository.get_one_room(room_id)
        except RoomNotFoundPostgres as exc:
            user_lobby_logger.error(f'Комната {room_id} не найдена')
            raise RoomNotFoundService from exc

        if len(room.players) > room.max_players:
            user_lobby_logger.warning(f'Комната {room_id} переполнена')
            raise NoSlotService

        if room.password and join_data.password != room.password:
            user_lobby_logger.warning(f'Неверный пароль для входа в комнату {room_id} пользователем {user_id}')
            raise PasswordRoomNotValidError

        if await self._lobby_repository.black_list(room_id=room_id, user_id=user_id):
            user_lobby_logger.warning(f'Пользователь {user_id} находится в чёрном списке комнаты {room_id}')
            raise BlackListService

        await self._lobby_repository.user_in_room(user_id=user_id, in_room=True)

        user_lobby_logger.info(f'Пользователь {user_id} успешно вошёл в комнату {room_id}')
        return RoomResponse(**room.model_dump())

    async def delete_lobby(
        self,
        room_id: int,
        user_id: int,
    ) -> None:
        try:
           user = await self._user_repository.get_one_by_id(user_id=user_id)
        except UserNotFoundPostgres as exc:
           user_lobby_logger.error(f'Пользователь {user_id} не найден')
           raise UserNotFoundService from exc
        if user.is_admin:
            await self._lobby_repository.delete_room(room_id=room_id)
        else:
            raise DeleteRoomNotAdminService
