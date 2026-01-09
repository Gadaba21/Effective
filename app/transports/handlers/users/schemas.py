from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core.core_schema import ValidationInfo


class BaseSchema(BaseModel):
    """Базовый класс для схем"""

    model_config = ConfigDict(from_attributes=True)


class PlayerStatisticResponse(BaseSchema):
    """Схема статистики"""

    id: int
    game_name: str
    total_game: int
    won_game: int


class AchievementResponse(BaseSchema):
    """Схема достижений"""

    name: str
    desc: str


class RankResponse(BaseSchema):
    name: str


class UserAchievementsResponse(BaseSchema):
    """Схема представления достижений"""

    achievement: AchievementResponse
    game_name: str
    receiving_cond: datetime | None


class UserResponse(BaseSchema):
    """Схема представления пользователя"""

    id: int
    username: str
    email: EmailStr | None
    date_joined: datetime
    avatar: str | None
    dracoins: int
    is_vip: bool
    its_vip_time: datetime | None
    exp: int = 0
    rank: RankResponse | None
    is_active: bool
    nickname_color: str
    statistics: list[PlayerStatisticResponse]
    achievements: list[UserAchievementsResponse]


class UserPublicResponse(BaseSchema):
    """Схема представления пользователя другим пользователям"""

    username: str
    avatar: str | None
    rank: RankResponse | None
    date_joined: datetime
    nickname_color: str
    achievements: list[UserAchievementsResponse]


class GenerateCode(BaseModel):
    """Схема кода доступа"""

    email: EmailStr


class AccessEmail(BaseModel):
    """Схема подтверждения почты"""

    code: str = Field(..., max_length=10)
    email: EmailStr


class RefreshForm(BaseModel):
    """Схема для refresh токена"""

    refresh_token: str = Field(..., alias='refresh')


class UserCreate(BaseModel):
    """Схема создания пользователя"""

    username: str = Field(..., max_length=15, min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_2: str = Field(..., min_length=8)

    @field_validator('password_2')
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return v

    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_а-яА-ЯёЁ]+$', v):
            raise ValueError('Имя пользователя может содержать только буквы, цифры и подчеркивания')
        return v

    @field_validator('email')
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Некорректный email')
        return v

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать минимум 8 символов, буквы и цифры')
        return v


class TempUserCreate(BaseModel):
    """Схема создания временного пользователя"""

    username: str = Field(..., max_length=15, min_length=3)

    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9 @#$%^&!?;:\\+=></*()_-]+$', v):
            raise ValueError('Имя пользователя может содержать только буквы, цифры и подчеркивания')
        return v


class UserUpdate(BaseModel):
    """Схема обновления информации о пользователе"""

    username: str | None = Field(None, max_length=15, min_length=3)
    email: EmailStr | None = None
    avatar: str | None = None
    nickname_color: str | None = None

    @field_validator('nickname_color')
    def validate_nickname_color(cls, v: str) -> str:
        if not v:
            return v
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Цвет должен быть в формате #RRGGBB')
        return v


class ResetPassword(BaseModel):
    """Схема изменения пароля пользователя"""

    old_password: str
    new_password: str = Field(..., min_length=8)
    code: str = Field(..., max_length=10)

    @field_validator('new_password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать минимум 8 символов, буквы и цифры')
        return v


class RecoveryPassword(BaseModel):
    """Схема восстановления пароля пользователя"""

    email: EmailStr
    new_password: str = Field(..., min_length=8)
    code: str = Field(..., max_length=10)

    @field_validator('new_password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать минимум 8 символов, буквы и цифры')
        return v


class LoginRequest(BaseModel):
    """Схема ответа на вход"""

    email: EmailStr
    password: str


class LoginTempRequest(BaseModel):
    """Схема ответа на вход временных пользователей"""

    username: str


class UserCreateResponse(BaseModel):
    """Схема ответа на регистрацию пользователей"""

    email: EmailStr


class UserTempResponse(BaseModel):
    """Схема ответа на регистрацию временных пользователей"""

    username: str


class TokenResponse(BaseModel):
    """Схема ответа на вход"""

    access: str
    refresh: str


class AccessToken(BaseModel):
    """Модель, представляющая токен доступа."""

    access: str
    refresh: str


class ActivateUser(BaseModel):
    """Модель для запроса активации пользователя."""

    access: str


class CodeDetail(BaseModel):
    """Модель с деталями верификационного кода."""

    code: str
    email: EmailStr


class GenerateCodeResponse(BaseModel):
    """Модель ответа на генерацию кода."""

    access: str


class AccessResetPasswordResponse(BaseModel):
    """Модель ответа для доступа к сбросу пароля."""

    access: str
    username: str
    email: EmailStr


class AccessUpdatePasswordResponse(BaseModel):
    """Модель ответа на обновление пароля."""

    access: str
    username: str


class UpdatedUserResponse(BaseModel):
    """Модель ответа с обновлёнными данными пользователя."""

    username: str
    email: EmailStr | None
    avatar: str | None
    nickname_color: str
