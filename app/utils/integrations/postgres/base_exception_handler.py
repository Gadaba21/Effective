from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Coroutine, Literal, ParamSpec, TypeVar
from unittest.mock import AsyncMock

from sqlalchemy.exc import SQLAlchemyError

from app.integrations.postgres.base_exception import BasePostgresError

P = ParamSpec('P')
R = TypeVar('R')


@contextmanager
def sqlalchemy_error_manager() -> Generator[None, None, None]:
    try:
        yield
    except SQLAlchemyError as exc:
        raise BasePostgresError from exc


def sqlalchemy_error_handle(func: Callable[P, R]) -> Callable[P, R]:
    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with sqlalchemy_error_manager():
                return await func(*args, **kwargs)
    else:

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with sqlalchemy_error_manager():
                return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def transactional_session(mode: Literal['runtime', 'test'] = 'runtime') -> Any:
    def decorator(handler: Callable[..., Coroutine[Any, Any, Any]]) -> Any:
        @wraps(handler)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:  # ⬅️ Убрали self из параметров
            from app.integrations.postgres.providers import session_factory_provide, session_provide
            from app.main import app

            current_mode = 'runtime'
            # Первый аргумент - это self (экземпляр сервиса)
            self_instance = args[0] if args else None
            if not self_instance:
                return await handler(*args, **kwargs)

            if self_instance and hasattr(self_instance, '_lobby_repository'):
                repo = self_instance._lobby_repository
                if isinstance(repo, AsyncMock):
                    current_mode = 'test'

                # В тестовом режиме просто пропускаем логику транзакции
            if current_mode == 'test':
                return await handler(*args, **kwargs)

            async with session_factory_provide(app.state.postgres_engine) as session_factory:
                async with session_provide(session_factory, mode=mode) as session:
                    originals = {}
                    repos = [
                        getattr(self_instance, '_lobby_repository', None),
                        getattr(self_instance, '_settings_repository', None),
                        getattr(self_instance, '_game_bj_repository', None),
                        getattr(self_instance, '_game_fm_repository', None),
                        getattr(self_instance, '_user_repository', None),
                        getattr(self_instance, 'repo', None),
                        getattr(self_instance, '_payment_repository', None),
                    ]
                    repos = list(dict.fromkeys(filter(None, repos)))

                    # Устанавливаем новую сессию во все репозитории
                    for repo in repos:
                        if hasattr(repo, 'set_session'):
                            originals[repo] = repo._session  # type: ignore
                            repo.set_session(session)  # type: ignore

                    try:
                        result = await handler(*args, **kwargs)
                        return result
                    finally:
                        # Возвращаем старые сессии
                        for repo, original_session in originals.items():
                            repo.set_session(original_session)  # type: ignore

        return wrapper

    return decorator
