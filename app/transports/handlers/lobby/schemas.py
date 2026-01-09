from datetime import datetime

from pydantic import BaseModel, Field

from app.transports.handlers.users.schemas import BaseSchema


class PlayerSchemaResponse(BaseModel):
    """Схема для игроков."""

    id: int
    name: str
    user_id: int | None
    room_id: int
    is_host: bool
    nickname_color: str
    is_disconnect: bool
    avatar: str | None
    is_vip: bool


class RoomCreateSchema(BaseModel):
    """Схема для создания комнаты."""

    title: str
    max_players: int = Field(..., ge=3, le=12)
    is_private: bool
    password: str | None


class RoomResponse(BaseSchema):
    """Схема для лобби"""

    id: int
    max_players: int
    created_at: datetime
    title: str
    game_name: str
    players: list[PlayerSchemaResponse]
    is_private: bool


class RoomCreateResponse(BaseSchema):
    """Схема для лобби"""

    id: int
    max_players: int
    created_at: datetime
    title: str
    game_name: str
    is_private: bool
    players: list[PlayerSchemaResponse]



class DeleteRoomSchema(BaseModel):
    """Схема для удаления комнат"""

    access: str


class JoinRoomSchema(BaseModel):
    """Схема для передачи пароля"""

    password: str | None

