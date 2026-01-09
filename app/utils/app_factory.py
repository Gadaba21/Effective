from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from redis.asyncio import Redis
from sqladmin import Admin
from app.integrations.postgres.providers import postgres_engine_provide
from app.integrations.redis.config import async_redis_context
from app.integrations.sqladmin.models.code_admin import CodeAdmin
from app.integrations.sqladmin.models.room_admin import RoomAdmin
from app.integrations.sqladmin.models.user_admin import UserAdmin
from app.transports.handlers.admins.sqladmin_authentication import AdminAuth
from app.transports.handlers.lobby.routes import router_lobby
from app.transports.handlers.users.routes import router_user
from app.utils.config import AppSettings, get_app_settings, get_env_settings



class AppFactory:
    @classmethod
    @asynccontextmanager
    async def redis_manager(
        cls,
    ) -> AsyncGenerator[Redis]:
        async with async_redis_context() as redis:
            yield redis


    @classmethod
    def _setup_cors(
        cls,
        app: FastAPI,
    ) -> None:
        """Настройка CORS middleware с кастомными параметрами."""
        origins = get_env_settings().allowed_origins.get_secret_value()
        valid_origins = [origin.strip() for origin in origins.split(',')]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=valid_origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=[
                'Content-Disposition',
                'X-Total-Count',
                'X-Error-Message',
            ],
            max_age=600,
        )

    @classmethod
    def make(
        cls,
        app_settings: AppSettings,
    ) -> FastAPI:
        app = FastAPI(
            debug=app_settings.debug,
            version=app_settings.version,
            title=app_settings.app_name,
            lifespan=cls.lifespan,
        )
        cls._setup_cors(app)
        cls.include_routers(app)
        return app

    @classmethod
    def include_routers(
        cls,
        app: FastAPI,
    ) -> None:
        app.include_router(router_user)
        app.include_router(router_lobby)

    @classmethod
    @asynccontextmanager
    async def lifespan(
        cls,
        app: FastAPI,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Главный lifespan приложения."""
        async with (
            cls.redis_manager() as redis,
            postgres_engine_provide(get_env_settings().postgres_dsn.get_secret_value()) as engine,
        ):
            app.state.redis = redis
            app.state.postgres_engine = engine
            admin_auth = AdminAuth(secret_key=get_env_settings().secret_key.get_secret_value())
            admin = Admin(app=app, engine=engine, authentication_backend=admin_auth)
            cls.include_admin_routers(admin)

            yield {
                'app_settings': get_app_settings(),
                'env_settings': get_env_settings(),
                'redis': redis,
                'postgres_engine': engine,
            }

    @classmethod
    def include_admin_routers(
        cls,
        admin: Admin,
    ) -> None:
        admin.add_view(RoomAdmin)
        admin.add_view(UserAdmin)
        admin.add_view(CodeAdmin)

