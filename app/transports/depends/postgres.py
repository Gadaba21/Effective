from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session

from app.integrations.postgres.providers import session_factory_provide, session_provide
from app.transports.depends.app_scope import postgres_engine_depend


async def session_factory_depend(
    postgres_engine: Annotated[AsyncEngine, Depends(postgres_engine_depend)],
) -> AsyncGenerator[async_scoped_session[AsyncSession], None]:
    async with session_factory_provide(postgres_engine) as session_factory:
        yield session_factory


async def session_depend(
    session_factory: Annotated[async_scoped_session[AsyncSession], Depends(session_factory_depend)],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_provide(session_factory, mode='runtime') as session:
        yield session
