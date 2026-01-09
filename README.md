# Тестовое задание для Effective

## Доступные API

Пользователи:
В данном проекте реализованна регистрация, для того чтобы подтвердить регистрацию, необходимо ввести код подтверждения на почту.
Мягкое удаление пользователя, без удаления из бд.
Есть личный кабинет.
Лобби:
Смотреть доступные комнаты могут все посетители сайта
Авторизованные пользователи могут создавать комнаты.
Удалять комнаты может только администратор.
Пользователь может присоединиться к комнате

## Виртуальное окружение.

В качестве виртуального окружения было принято использовать `uv`.  

### Команды для использования uv

`pip install uv` - установка  
`uv venv --python 3.11` - создание виртуального окружения  
`source .venv/Scripts/activate` - активация (стандартная)  
`uv sync` - синхронизация зависимостей  
`uv sync --dev` - синхронизация зависимостей включая dev
`uv sync --all-groups` - синхронизация зависимостей включая все группы
`uv run uvicorn app.main:app --reload` - проверка запуска приложения  
`uv add <название библиотеки>` - установка новой библиотеки


## Ссылки

Документация API игры: http://localhost:8000/docs


### Docker команды для запуска контейнеров

`docker compose -f .docker/local/docker-compose.yaml --env-file .docker/local/docker-compose-variables.env up -d --remove-orphans --build` - запуск контейнеров для локальной разработки

## Команды для миграции

Сначала создаем миграции

`alembic revision --autogenerate -m "Описание изменений"`


Применяем их

`alembic upgrade head`


## Скрипты для заполнения бд

### Скрипт для заполнения достижений
`python -m app.integrations.postgres.loading_data.achievement --db-url postgresql+asyncpg://postgres:postgres@localhost:15432/postgres --file app/integrations/postgres/loading_data/data/achievement.xlsx`

### Скрипт для заполнения ранга
`python -m app.integrations.postgres.loading_data.rank --db-url postgresql+asyncpg://postgres:postgres@localhost:15432/postgres --file app/integrations/postgres/loading_data/data/rank.xlsx`


