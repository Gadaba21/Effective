from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.websockets import WebSocket

from app.utils.models import AppRequest


def postgres_engine_depend(request: AppRequest = None, websocket: WebSocket = None) -> AsyncEngine:  # type: ignore
    if websocket:
        return websocket.app.state.postgres_engine
    return request.app.state.postgres_engine


def redis_depend(websocket: WebSocket) -> AsyncEngine:
    return websocket.app.state.redis
