from sqladmin import ModelView

from app.integrations.postgres.orms.user_orm import UserORM


class UserAdmin(ModelView, model=UserORM):
    name = 'Игры: Пользователь'
    name_plural = 'Игры: Пользователи'
    icon = 'fa-solid fa-user'

    column_list = [
        UserORM.id,
        UserORM.username,
        UserORM.email,
        UserORM.exp,
        UserORM.rank,
        UserORM.status,
        UserORM.date_joined,
        UserORM.is_vip,
        UserORM.its_vip_time,
        UserORM.dracoins,
        UserORM.is_active,
        UserORM.in_room,
    ]
    form_excluded_columns = [
        UserORM.hash_password,
        UserORM.avatar,
    ]
    column_searchable_list = [
        UserORM.username,
        UserORM.email,
    ]
    column_sortable_list = [
        UserORM.username,
        UserORM.email,
    ]
