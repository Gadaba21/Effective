from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Path, Request, UploadFile, status
from jose import JWTError, jwt
from pydantic import EmailStr

from app.integrations.celery.tasks import send_confirmation_email_task
from app.services.code_service import CodeService
from app.services.exceptions import (
    CodeNotFoundService,
    EmailAlreadyExistsService,
    FileExtensionService,
    FileNotUploadService,
    InvalidIsActiveService,
    InvalidNewPasswordService,
    InvalidOldPasswordService,
    InvalidPasswordService,
    InvalidStatusService,
    MissCredentialsService,
    UserAlreadyActiveService,
    UsernameAlreadyExistsService,
    UserNotFoundService,
)
from app.services.user_service import UserService
from app.utils.config import get_env_settings
from app.utils.logger_config import user_lobby_logger

from .exceptions import (
    CodeNotFoundError,
    EmailAlreadyExistsError,
    FileExtensionError,
    FileNotUploadError,
    InvalidIsActiveError,
    InvalidNewPasswordError,
    InvalidOldPasswordError,
    InvalidPasswordError,
    InvalidStatusError,
    MissCredentialsError,
    UserAlreadyActiveError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from .schemas import (
    AccessEmail,
    AccessToken,
    AccessUpdatePasswordResponse,
    ActivateUser,
    GenerateCode,
    GenerateCodeResponse,
    LoginRequest,
    RecoveryPassword,
    RefreshForm,
    ResetPassword,
    TempUserCreate,
    TokenResponse,
    UpdatedUserResponse,
    UserCreate,
    UserCreateResponse,
    UserPublicResponse,
    UserResponse,
    UserTempResponse,
    UserUpdate,
)
from .utils import create_access_token, get_current_user, create_refresh_token

router_user = APIRouter(
    prefix='/api/users',
    tags=['users'],
)


@router_user.get(
    '/{user_id}/detail/',
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: Annotated[int, Path],
    user_service: Annotated[UserService, Depends()],
) -> UserPublicResponse:
    """Личный кабинет других пользователей"""
    try:
        user_lobby_logger.debug('Получена информация по незарегистрированному пользователю {}', user_id)
        return await user_service.get_user(user_id=user_id)
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: пользователь c id {} не найден.', user_id)
        raise UserNotFoundError


@router_user.get(
    '/personal_area/',
    status_code=status.HTTP_200_OK,
)
async def get_me_personal_area(
    user_service: Annotated[UserService, Depends()],
    current_user_id: Annotated[int, Depends(get_current_user)],
) -> UserResponse:
    """Личный кабинет зарегистрированных пользователей"""
    try:
        user_lobby_logger.debug('Получена информация по зарегистрированному пользователю {}', current_user_id)
        return await user_service.get_current_user(current_user_id)
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: пользователь c id {} не найден.', current_user_id)
        raise UserNotFoundError


@router_user.post(
    '/token/',
    status_code=status.HTTP_200_OK,
)
async def login(
    user_login_data: LoginRequest,
    user_service: Annotated[UserService, Depends()],
) -> TokenResponse:
    """Вход постоянных пользователей"""
    try:
        user_lobby_logger.debug('Пользователь c почтой {} осуществил вход', user_login_data.email)
        return await user_service.login_user(user_login_data)
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: пользователь c почтой {} не найден.', user_login_data.email)
        raise UserNotFoundError
    except InvalidStatusService:
        user_lobby_logger.error('Ошибка: Неправильный статус для авторизации по username.')
        raise InvalidStatusError
    except InvalidPasswordService:
        user_lobby_logger.error('Ошибка: Введен неверный пароль для пользователя.')
        raise InvalidPasswordError
    except MissCredentialsService:
        user_lobby_logger.error('Ошибка: Необходимо указать email и password.')
        raise MissCredentialsError
    except InvalidIsActiveService:
        user_lobby_logger.error('Ошибка: Пользователь не прошёл верификацию по email.')
        raise InvalidIsActiveError



@router_user.post(
    '/token/refresh/',
    status_code=status.HTTP_200_OK,
)
async def refresh(
    refresh_data: RefreshForm,
) -> AccessToken:
    """Обновление токена"""
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            get_env_settings().secret_key.get_secret_value(),
            algorithms=[get_env_settings().algorithm.get_secret_value()],
        )
        user_id: int | None = payload.get('user_id')
        if user_id is None:
            user_lobby_logger.error('Ошибка: Неверный refresh-токен.')
            raise HTTPException(status_code=401, detail='Неверный refresh-токен')
        access_token = create_access_token(data={'user_id': user_id})
        refresh_token = create_refresh_token(data={'user_id': user_id})
        user_lobby_logger.info('Токен обновлен')
        return AccessToken(access=access_token, refresh=refresh_token)
    except JWTError:
        user_lobby_logger.error('Ошибка: Неверный или истёкший refresh-токен.')
        raise HTTPException(status_code=401, detail='Неверный или истёкший refresh-токен')


@router_user.post(
    '/create/',
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request,
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends()],
) -> UserCreateResponse:
    """Создание пользователя"""
    try:
        user = await user_service.create_user(user_data)
        user_lobby_logger.debug('Создан пользователь с почтой {}', user.email)
    except EmailAlreadyExistsService as exc:
        user_lobby_logger.error('Ошибка: Пользователь с email {} уже существует.', user_data.email)
        raise EmailAlreadyExistsError from exc
    except UsernameAlreadyExistsService as exc:
        user_lobby_logger.error('Ошибка: Пользователь с username {} уже существует.', user_data.username)
        raise UsernameAlreadyExistsError from exc

    send_confirmation_email_task.delay(user.email, str(request.url))
    user_lobby_logger.info(
        'Задача на отправку ссылки для подтверждения почты запущена. Email: {}',
        user.email,
    )
    return user

@router_user.get(
    '/create/access_email/{token}/',
    status_code=status.HTTP_200_OK,
)
async def access_email(
    token: Annotated[str, Path],
    user_service: Annotated[UserService, Depends()],
) -> ActivateUser:
    """Подтверждение почты"""
    try:
        payload = jwt.decode(
            token,
            get_env_settings().secret_key.get_secret_value(),
            algorithms=[get_env_settings().algorithm.get_secret_value()],
        )
        email: EmailStr | None = payload.get('email')
        if email is None:
            user_lobby_logger.error('Ошибка: Неверный email.')
            raise HTTPException(status_code=401, detail='Неверный email.')
        user_lobby_logger.info('Email получен.')
    except JWTError:
        user_lobby_logger.error('Ошибка: Неверный или истёкший токен подтверждения.')
        raise HTTPException(status_code=401, detail='Неверный или истёкший токен подтверждения.')
    try:
        response = await user_service.activate_user(email)
        user_lobby_logger.debug('Аккаунт {} активирован', email)
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: пользователь с почтой {} не найден.', email)
        raise UserNotFoundError
    except UserAlreadyActiveService:
        user_lobby_logger.error('Ошибка: пользователь с почтой {} Уже активирован!', email)
        raise UserAlreadyActiveError
    return response


@router_user.patch(
    '/update/',
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_update: UserUpdate,
    current_user_id: Annotated[int, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends()],
) -> UpdatedUserResponse:
    """Изменения информации о пользователе"""
    try:
        user_lobby_logger.info('Изменение информации о пользователе {}', user_update.username)
        return await user_service.update_user(user_update, current_user_id)
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: пользователь {} не найден.', user_update.username)
        raise UserNotFoundError
    except UsernameAlreadyExistsService:
        user_lobby_logger.error('Ошибка: Пользователь с username {} уже существует.', user_update.username)
        raise UsernameAlreadyExistsError
    except EmailAlreadyExistsService:
        user_lobby_logger.error('Ошибка: Пользователь с email {} уже существует.', user_update.email)
        raise EmailAlreadyExistsError


@router_user.delete(
    '/delete/',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: Annotated[int, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends()],
) -> None:
    """Удаление почты"""
    user_lobby_logger.info('Удаление пользователя с id {}', user_id)
    await user_service.delete_user(user_id)


@router_user.post(
    '/generate_code/',
    status_code=status.HTTP_201_CREATED,
)
async def generate_code(
    generate_code_data: GenerateCode,
    code_service: Annotated[CodeService, Depends()],
) -> GenerateCodeResponse:
    """Генерация кода"""
    old_code = await code_service.get_code_by_email(generate_code_data.email)
    user_lobby_logger.info('Поиск кода по почте: {}', generate_code_data.email)
    if old_code:
        user_lobby_logger.info('Найден старый код')
        await code_service.delete_code(old_code)
        user_lobby_logger.info('Старый код удален')
    user_lobby_logger.info('Создается и отправляется новый код на почту {}', generate_code_data.email)
    return await code_service.create_code(email=generate_code_data.email)


@router_user.post(
    '/reset_password/',
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    reset_password_data: ResetPassword,
    user_id: Annotated[int, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends()],
    code_service: Annotated[CodeService, Depends()],
) -> AccessUpdatePasswordResponse:
    """Обновление пароля"""
    try:
        response_reset_password = await user_service.reset_password(
            reset_password_data=reset_password_data,
            user_id=user_id,
        )
        user_lobby_logger.debug('Пароль для пользователя был изменен')
    except InvalidOldPasswordService:
        user_lobby_logger.error('Ошибка: Неверно введен старый пароль.')
        raise InvalidOldPasswordError
    except InvalidNewPasswordService:
        user_lobby_logger.error('Ошибка: Старый и новый пароли совпадают.')
        raise InvalidNewPasswordError
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: Пользователь c id {} не найден.', user_id)
        raise UserNotFoundError
    try:
        code = await code_service.get_code(
            AccessEmail(
                code=reset_password_data.code,
                email=response_reset_password.email,
            ),
        )
        user_lobby_logger.info('Код подтверждения смены пароля найден')
    except CodeNotFoundService:
        user_lobby_logger.error('Ошибка: Код подтверждения смены пароля не найден.')
        raise CodeNotFoundError
    await code_service.delete_code(code)
    user_lobby_logger.info('Код подтверждения смены пароля удален')
    return AccessUpdatePasswordResponse(**response_reset_password.model_dump())


@router_user.post(
    '/recovery_password/',
    status_code=status.HTTP_200_OK,
)
async def recovery_password(
    recovery_password_data: RecoveryPassword,
    user_service: Annotated[UserService, Depends()],
    code_service: Annotated[CodeService, Depends()],
) -> AccessUpdatePasswordResponse:
    """Восстановление пароля"""
    try:
        code = await code_service.get_code(
            AccessEmail(
                email=recovery_password_data.email,
                code=recovery_password_data.code,
            ),
        )
        user_lobby_logger.info('Код подтверждения восстановления пароля найден')
    except CodeNotFoundService:
        user_lobby_logger.error('Ошибка: Код подтверждения восстановления пароля не найден.')
        raise CodeNotFoundError
    try:
        access_response = await user_service.recovery_password(recovery_password_data)
        user_lobby_logger.debug('Пароль изменен')
    except UserNotFoundService:
        user_lobby_logger.error('Ошибка: Пользователь c почтой {} не найден.', recovery_password_data.email)
        raise UserNotFoundError
    await code_service.delete_code(code)
    user_lobby_logger.info('Код подтверждения восстановления пароля удален')
    return access_response


@router_user.post(
    '/{user_id}/upload_avatar/',
    status_code=status.HTTP_200_OK,
)
async def upload_user_avatar(
    user_service: Annotated[UserService, Depends()],
    user_id: int,
    file: UploadFile = File(...),
) -> UpdatedUserResponse:
    """Загрузка файла с аватаркой"""
    try:
        user_lobby_logger.info('Сохраняем файл {}', file.filename)
        updated_user = await user_service.upload_user_avatar(user_id=user_id, file=file)

        user_lobby_logger.info(
            'Файл сохранен. Информация по пользователю {} c аватаркой {} обновлена',
            updated_user.username,
            updated_user.avatar,
        )
        return updated_user
    except FileExtensionService:
        user_lobby_logger.error('Ошибка: Недопустимый тип файла. Разрешены только JPEG, PNG, GIF.')
        raise FileExtensionError
    except FileNotUploadService:
        user_lobby_logger.error('Ошибка: Файл не загружен.')
        raise FileNotUploadError
