from starlette import status

from app.transports.handlers.base_exception_handlers import BaseExceptionTransport


class RoomNotFoundError(BaseExceptionTransport):
    detail = 'Комната не найдена.'
    status_code = status.HTTP_404_NOT_FOUND


class UserInRoomError(BaseExceptionTransport):
    detail = 'Вы уже находитесь в комнате'
    status_code = status.HTTP_400_BAD_REQUEST


class TitleCreateRoomError(BaseExceptionTransport):
    detail = 'Такое название комнаты уже используется'
    status_code = status.HTTP_400_BAD_REQUEST


class NoSlotError(BaseExceptionTransport):
    detail = 'Свободных мест больше нет!'
    status_code = status.HTTP_400_BAD_REQUEST


class PasswordRoomNotValidError(BaseExceptionTransport):
    detail = 'Пароль неверный'
    status_code = status.HTTP_400_BAD_REQUEST


class BlackListError(BaseExceptionTransport):
    detail = 'Вы не можете зайти в данную комнату'
    status_code = status.HTTP_400_BAD_REQUEST


class DeleteRoomNotAdminError(BaseExceptionTransport):
    detail = 'Вы не являетесь админом'
    status_code = status.HTTP_403_FORBIDDEN