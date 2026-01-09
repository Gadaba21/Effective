import dataclasses

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.requests import Request

from app.utils.config import AppSettings, EnvSettings


@dataclasses.dataclass
class LifeSpan:
    app_settings: AppSettings
    env_settings: EnvSettings
    postgres_engine: AsyncEngine
    redis: Redis


class AppRequest(Request):
    state: LifeSpan  # type: ignore[assignment]
