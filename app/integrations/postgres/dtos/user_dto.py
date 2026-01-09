from datetime import datetime

from pydantic import EmailStr

from ..models import BaseDTO


class RankDTO(BaseDTO):
    name: str


class UserDetailDTO(BaseDTO):
    """DTO для пользователя с полной информацией."""

    id: int
    username: str
    email: EmailStr | None
    hash_password: str | None
    date_joined: datetime
    avatar: str | None
    dracoins: int
    is_vip: bool
    its_vip_time: datetime | None
    exp: int
    rank: RankDTO | None
    is_active: bool
    status: bool
    nickname_color: str
    in_room: bool


class DeleteUserDTO(BaseDTO):
    id: int
    time_last_game: datetime


class UserByIdDTO(BaseDTO):
    id: int
    username: str
    email: EmailStr | None
    hash_password: str | None
    in_room: bool
    is_admin: bool


class UserByEmailDTO(BaseDTO):
    id: int
    username: str
    hash_password: str
    status: bool
    is_active: bool


class UserDTO(BaseDTO):
    """DTO для пользователя."""

    email: EmailStr


class UserPublicDTO(BaseDTO):
    """DTO для публичной информации о пользователе."""

    username: str
    avatar: str | None
    rank: RankDTO | None
    date_joined: datetime
    nickname_color: str


class UserCreateDTO(BaseDTO):
    """DTO для создания пользователей."""

    username: str
    email: EmailStr
    hash_password: str
    status: bool


class UserTempCreateDTO(BaseDTO):
    """DTO для создания временных пользователей."""

    username: str
    status: bool


class UserTempResponseDTO(BaseDTO):
    """DTO для информации о временных пользователей."""

    username: str


class UserLoginResponseDTO(BaseDTO):
    """DTO для ответа на вход не зарегистрированного пользователей."""

    id: int
    status: bool


class UserUpdatePartialDTO(BaseDTO):
    """DTO для изменения информации о пользователе."""

    username: str | None = None
    email: EmailStr | None = None
    avatar: str | None = None
    hash_password: str | None = None
    nickname_color: str | None = None


class UpdatedUserDTO(BaseDTO):
    """DTO для изменения информации о пользователе."""

    username: str
    email: EmailStr | None
    avatar: str | None
    nickname_color: str


class PlayerStatisticDTO(BaseDTO):
    """DTO для получения информации о статистики пользователя."""

    id: int
    game_name: str
    total_game: int
    won_game: int


class AchievementDTO(BaseDTO):
    """DTO о достижениях."""

    id: int
    name: str
    desc: str


class UserAchievementsDTO(BaseDTO):
    """DTO для получения информации о достижениях пользователя."""

    achievement: AchievementDTO
    game_name: str
    receiving_cond: datetime | None


class UserSchemaDTO(BaseDTO):
    id: int
    username: str
    nickname_color: str | None = None
    avatar: str | None = None


class RecoveryPasswordDTO(BaseDTO):
    email: EmailStr
    hash_password: str


class RankDetailDTO(BaseDTO):
    """DTO для ранга."""

    id: int
    name: str
    points_required: int



class UserExpDTO(BaseDTO):
    id: int
    exp: int


class CreateRankDTO(BaseDTO):
    """DTO для создания ранга"""

    name: str
    points_required: int
