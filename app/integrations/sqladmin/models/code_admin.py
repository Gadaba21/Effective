from sqladmin import ModelView

from app.integrations.postgres.orms.code_orm import CodeORM


class CodeAdmin(ModelView, model=CodeORM):
    """
    Админ-панель для кодов восстановления.
    """

    name = 'Код'
    name_plural = 'Аккаунт: Коды восстановления'
    icon = 'fa-solid fa-code'

    column_list = [
        CodeORM.email,
        CodeORM.code,
    ]
    column_searchable_list = [CodeORM.email]
