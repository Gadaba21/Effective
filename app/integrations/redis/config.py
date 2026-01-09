from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from redis.asyncio import Redis

from app.utils.config import get_env_settings


@asynccontextmanager
async def async_redis_context() -> AsyncGenerator[Redis, None]:
    env = get_env_settings()
    redis = Redis(
        host=env.redis_host.get_secret_value(),
        port=int(env.redis_port.get_secret_value()),
        db=int(env.redis_db.get_secret_value()),
        password=None,
        decode_responses=True,
        socket_timeout=5,
        socket_keepalive=True,
    )
    try:
        yield redis
    finally:
        await redis.close()
