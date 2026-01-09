from fastapi import status

from app.transports.handlers.base_exception_handlers import BaseExceptionTransport


class EmailAlreadyExistsError(BaseExceptionTransport):
    detail = 'Пользователь с таким email уже существует.'
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class UsernameAlreadyExistsError(BaseExceptionTransport):
    detail = 'Пользователь с таким username уже существует.'
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class InvalidPasswordError(BaseExceptionTransport):
    detail = 'Введен неверный пароль для пользователя.'
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class InvalidStatusError(BaseExceptionTransport):
    detail = 'Неправильный статус для авторизации по username.'
    status_code = status.HTTP_400_BAD_REQUEST


class MissCredentialsError(BaseExceptionTransport):
    detail = 'Необходимо указать email и password.'
    status_code = status.HTTP_400_BAD_REQUEST


class UserNotFoundError(BaseExceptionTransport):
    detail = 'Пользователь не найден.'
    status_code = status.HTTP_404_NOT_FOUND


class CodeNotFoundError(BaseExceptionTransport):
    detail = 'Код не найден.'
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidOldPasswordError(BaseExceptionTransport):
    detail = 'Неверно введен старый пароль.'
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidNewPasswordError(BaseExceptionTransport):
    detail = 'Старый и новый пароли совпадают. Введите другой.'
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class FileExtensionError(BaseExceptionTransport):
    detail = 'Недопустимый тип файла. Разрешены только JPEG, PNG, GIF'
    status_code = status.HTTP_400_BAD_REQUEST


class FileNotUploadError(BaseExceptionTransport):
    detail = 'Файл не передан'
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class InvalidIsActiveError(BaseExceptionTransport):
    detail = 'Для авторизации требуется подтверждение почты по ссылке в письме.'
    status_code = status.HTTP_403_FORBIDDEN


class UserAlreadyActiveError(BaseExceptionTransport):
    detail = 'Ваш аккаунт уже активирован. Наслаждайтесь игрой!'
    status_code = status.HTTP_406_NOT_ACCEPTABLE
