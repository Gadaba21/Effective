import asyncio
from collections import defaultdict
import json
from typing import Any

from redis import RedisError
from redis.asyncio import Redis, from_url

from app.utils.config import get_env_settings

DEFAULT_EXPIRE_SECONDS = 60 * 20
ROOM_EVENTS: dict[int, asyncio.Event] = defaultdict(asyncio.Event)


class RedisFacade:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @classmethod
    async def create(cls) -> 'RedisFacade':
        """Создаёт подключение к Redis и возвращает фасад."""
        settings = get_env_settings()
        redis_url = settings.celery_broker_url.get_secret_value()
        redis = await from_url(redis_url, decode_responses=True)
        return cls(redis)

    async def set_json(
        self,
        key: str,
        data: Any,
        expire: int = DEFAULT_EXPIRE_SECONDS,
    ) -> None:
        """Сохранить объект как JSON с TTL."""
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            await self._redis.set(name=key, value=json_data, ex=expire)
        except (TypeError, RedisError) as err:
            raise RuntimeError(f"Ошибка при сохранении JSON в Redis '{key}': {err}") from err

    async def get_json(self, key: str) -> dict[str, Any]:
        """
        Получить объект как JSON.
        """
        value = await self._redis.get(key)
        if value is None:
            return {}
        try:
            data = json.loads(value)
            return data
        except (json.JSONDecodeError, TypeError) as err:
            raise RuntimeError(f"Ошибка при чтении JSON из Redis '{key}': {err}") from err

    async def close(self) -> None:
        """Закрывает соединение с Redis."""
        await self._redis.close()

    async def get(self, key: str) -> Any:
        """Получить одиночное значение (String)."""
        return await self._redis.get(key)

    async def set(
        self,
        key: str,
        data: Any,
        expire: int = DEFAULT_EXPIRE_SECONDS,
    ) -> None:
        """Сохранить одиночное значение с TTL (по умолчанию 20 мин)."""
        await self._redis.set(name=key, value=data, ex=expire)

    async def set_list(
        self,
        key: str,
        values: list[Any],
        expire: int = DEFAULT_EXPIRE_SECONDS,
    ) -> None:
        """Перезаписать множество (Set) из списка."""
        if not values:
            await self._redis.delete(key)
            return
        await self._redis.delete(key)
        await self._redis.sadd(key, *values)
        await self._redis.expire(key, expire)

    async def get_list(self, key: str) -> list[Any]:
        """Получить множество (Set) как список."""
        members = await self._redis.smembers(key)
        return list(members)

    async def incr(self, key: str) -> int:
        """Инкрементировать числовое значение (увеличить на 1)."""
        try:
            value = await self._redis.incr(key)
            return int(value)
        except RedisError as err:
            raise RuntimeError(f"Ошибка при инкременте Redis-ключа '{key}': {err}") from err

    async def publish_ws_event(self, event: dict[str, Any]) -> None:
        """Публикация события в WebSocket channel"""
        msg = json.dumps(event, ensure_ascii=False)
        await self._redis.publish('ws_events', msg)

    async def update_json_dict(
        self,
        key: str,
        updates: dict[str, Any],
        expire: int = DEFAULT_EXPIRE_SECONDS,
    ) -> None:
        """Обновить словарь, добавляя/изменяя поля."""
        try:
            current_data = {}
            existing = await self._redis.get(key)
            if existing:
                current_data = json.loads(existing)
            current_data.update(updates)
            json_data = json.dumps(current_data, ensure_ascii=False)
            await self._redis.set(name=key, value=json_data, ex=expire)
        except (TypeError, RedisError, json.JSONDecodeError) as err:
            raise RuntimeError(f"Ошибка при обновлении словаря в Redis '{key}': {err}") from err

    async def clear_json_dict(self, key: str) -> None:
        """Очистить словарь (установить пустой dict)."""
        empty_dict: dict[str, Any] = {}
        await self.set_json(key, empty_dict)
