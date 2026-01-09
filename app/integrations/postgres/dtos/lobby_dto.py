from datetime import datetime

from app.integrations.postgres.models import BaseDTO


class PlayerSchemaDTO(BaseDTO):
    """DTO схема для получения информации об игроках"""

    id: int
    name: str
    user_id: int | None
    room_id: int
    is_host: bool
    nickname_color: str
    is_disconnect: bool
    avatar: str | None
    is_vip: bool


class RoomSchemaDTO(BaseDTO):
    """DTO схема для получения информации об комнате"""

    id: int
    max_players: int
    started: bool
    password: str | None
    created_at: datetime
    afk_time: datetime
    title: str
    game_name: str
    players: list[PlayerSchemaDTO]
    is_private: bool


class RoomCreateDTO(BaseDTO):
    """DTO схема создание комнаты"""

    id: int
    max_players: int
    created_at: datetime
    title: str
    game_name: str
    is_private: bool


class RoomGameSchemaDTO(BaseDTO):
    """DTO для периодических задач"""

    id: int
    afk_time: datetime
    started: bool
    players: list[PlayerSchemaDTO]
