from sqladmin import ModelView

from app.integrations.postgres.orms.room_orm import RoomORM


class RoomAdmin(ModelView, model=RoomORM):
    name = 'Игры: Комната'
    name_plural = 'Игры: Комнаты'
    icon = 'fa-solid fa-rocket'

    column_list = [
        RoomORM.id,
        RoomORM.title,
        RoomORM.is_private,
        RoomORM.password,
        RoomORM.game_name,
        RoomORM.max_players,
        RoomORM.created_at,
        RoomORM.started,
        RoomORM.players,
        RoomORM.blacklisted_players,

    ]
    column_searchable_list = [RoomORM.title]
    column_sortable_list = [
        RoomORM.started,
        RoomORM.created_at,
    ]
