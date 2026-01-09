from typing import Annotated

from fastapi import Depends, File, UploadFile
from passlib.context import CryptContext
from pydantic import EmailStr

from app.integrations.postgres.dtos.user_dto import (
    RecoveryPasswordDTO,
    UserCreateDTO,
    UserTempCreateDTO,
    UserUpdatePartialDTO,
)
from app.integrations.postgres.exceptions import (
    EmailAlreadyExistsPostgres,
    UsernameAlreadyExistsPostgres,
    UserNotFoundPostgres,
)
from app.integrations.postgres.repositories.user_repository import UserRepository
from app.services.exceptions import (
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
from app.transports.handlers.users.exceptions import FileNotUploadError
from app.transports.handlers.users.schemas import (
    AccessResetPasswordResponse,
    AccessUpdatePasswordResponse,
    ActivateUser,
    LoginRequest,
    LoginTempRequest,
    PlayerStatisticResponse,
    RecoveryPassword,
    ResetPassword,
    TempUserCreate,
    TokenResponse,
    UpdatedUserResponse,
    UserAchievementsResponse,
    UserCreate,
    UserCreateResponse,
    UserPublicResponse,
    UserResponse,
    UserTempResponse,
    UserUpdate,
)
from app.transports.handlers.users.utils import create_access_token, create_refresh_token, resize_user_avatar

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends()],
    ) -> None:
        self._user_repository = user_repository

    async def get_user(
        self,
        user_id: int,
    ) -> UserPublicResponse:
        """Сервис по получению незарегистрированного пользователя"""
        try:
            user = await self._user_repository.get_one_with_rank_public(user_id=user_id)
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        achievements = await self._user_repository.get_user_achievements(user_id=user_id)
        return UserPublicResponse(
            **user.model_dump(),
            achievements=[UserAchievementsResponse(**achievement.model_dump()) for achievement in achievements],
        )

    async def get_current_user(
        self,
        user_id: int,
    ) -> UserResponse:
        """Сервис по получению зарегистрированного пользователя"""
        try:
            user = await self._user_repository.get_one_with_rank(user_id=user_id)
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        statistics = await self._user_repository.get_user_statistics(user_id=user_id)
        achievements = await self._user_repository.get_user_achievements(user_id=user_id)
        return UserResponse(
            **user.model_dump(),
            statistics=[PlayerStatisticResponse(**statistic.model_dump()) for statistic in statistics],
            achievements=[UserAchievementsResponse(**achievement.model_dump()) for achievement in achievements],
        )

    async def login_user(
        self,
        user_login_data: LoginRequest,
    ) -> TokenResponse:
        """Сервис для логина зарегистрированного пользователя"""
        if user_login_data.email and user_login_data.password:
            if not (
                user := await self._user_repository.get_one_by_email(
                    email=user_login_data.email,
                )
            ):
                raise UserNotFoundService
            if not self.check_password(user_login_data.password, user.hash_password):
                raise InvalidPasswordService
        else:
            raise MissCredentialsService
        if not user.status:
            raise InvalidStatusService
        if not user.is_active:
            raise InvalidIsActiveService
        access_token = create_access_token(data={'user_id': user.id})
        refresh_token = create_refresh_token(data={'user_id': user.id})
        return TokenResponse(access=access_token, refresh=refresh_token)


    async def create_user(
        self,
        user_data: UserCreate,
    ) -> UserCreateResponse:
        """Сервис для создания пользователя"""
        hash_password = self.set_password(user_data.password)
        try:
            user = await self._user_repository.add_one(
                UserCreateDTO(
                    **user_data.model_dump(),
                    status=True,
                    hash_password=hash_password,
                )
            )
        except EmailAlreadyExistsPostgres as exc:
            raise EmailAlreadyExistsService from exc
        except UsernameAlreadyExistsPostgres as exc:
            raise UsernameAlreadyExistsService from exc
        return UserCreateResponse(**user.model_dump())


    async def activate_user(
        self,
        access_email_data: EmailStr,
    ) -> ActivateUser:
        try:
            user = await self._user_repository.get_one_by_email(email=access_email_data)
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        if user.is_active:
            raise UserAlreadyActiveService
        await self._user_repository.activate_user(email=access_email_data)
        return ActivateUser(access='Ваш аккаунт был успешно активирован!')

    async def delete_user(
        self,
        user_id: int,
    ) -> None:
        """Сервис для создания удаление пользователя"""
        await self._user_repository.delete_one(user_id=user_id)

    async def update_user(
        self,
        user_update: UserUpdate,
        current_user_id: int,
    ) -> UpdatedUserResponse:
        """Сервис обновления информации о пользователе"""
        try:
            updated_user = await self._user_repository.update(
                user_id=current_user_id,
                user_update=UserUpdatePartialDTO(**user_update.model_dump()),
            )
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        except UsernameAlreadyExistsPostgres as exc:
            raise UsernameAlreadyExistsService from exc
        except EmailAlreadyExistsPostgres as exc:
            raise EmailAlreadyExistsService from exc
        return UpdatedUserResponse(**updated_user.model_dump())

    async def reset_password(
        self,
        reset_password_data: ResetPassword,
        user_id: int,
    ) -> AccessResetPasswordResponse:
        """Сервис обновления пароля пользователя"""
        try:
            user = await self._user_repository.get_one_by_id(user_id=user_id)
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        if not self.check_password(
            reset_password_data.old_password,
            user.hash_password,  # type: ignore
        ):
            raise InvalidOldPasswordService

        if self.check_password(
            reset_password_data.new_password,
            user.hash_password,  # type: ignore
        ):
            raise InvalidNewPasswordService

        new_hash_password = self.set_password(reset_password_data.new_password)
        try:
            await self._user_repository.update(
                user_id=user_id, user_update=UserUpdatePartialDTO(hash_password=new_hash_password)
            )
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        return AccessResetPasswordResponse(
            access='Пароль для пользователя был изменен!',
            username=user.username,
            email=user.email,
        )

    async def recovery_password(
        self,
        recovery_password_data: RecoveryPassword,
    ) -> AccessUpdatePasswordResponse:
        try:
            user = await self._user_repository.recovery_password(
                recovery_password_data=RecoveryPasswordDTO(
                    email=recovery_password_data.email,
                    hash_password=self.set_password(recovery_password_data.new_password),
                )
            )
        except UserNotFoundPostgres as exc:
            raise UserNotFoundService from exc
        return AccessUpdatePasswordResponse(
            access='Пароль для пользователя был изменен!',
            username=user.username,
        )

    @staticmethod
    def set_password(
        raw_password: str,
    ) -> str:
        """Функция для хеширования пароля"""
        return pwd_context.hash(raw_password)

    @staticmethod
    def check_password(
        raw_password: str,
        hash_password: str,
    ) -> bool:
        """Функция для проверки пароля"""
        return pwd_context.verify(raw_password, hash_password)

    async def upload_user_avatar(self, user_id: int, file: UploadFile = File(...)) -> UpdatedUserResponse:
        """Функция сохранения файла аватарки"""
        allowed_mime_types = {'image/jpeg', 'image/png', 'image/gif'}
        if file:
            if file.content_type not in allowed_mime_types:
                raise FileExtensionService

        try:
            contents = await file.read()

            # Изменяем размер аватарки, если он большой
            image = resize_user_avatar(max_size=200, contents=contents)
            if not file.filename:
                raise ValueError('Файл не имеет имени')

            new_filename = f'{user_id}_avatar.{file.filename.split(".")[-1]}'
            file_path = f'/media/avatar/{new_filename}'

            image.save(fp=file_path, quality=85)

            # сохранение пути в модуль пользователя
            updated_user = await self.update_user(user_update=UserUpdate(avatar=file_path), current_user_id=user_id)
            return updated_user

        except FileNotUploadService:
            raise FileNotUploadError
