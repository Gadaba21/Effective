from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


@asynccontextmanager
async def postgres_engine_provide(
    postgres_dsn: str,
) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(postgres_dsn)
    yield engine
    await engine.dispose()


@asynccontextmanager
async def session_factory_provide(
    engine: AsyncEngine,
) -> AsyncGenerator[async_scoped_session[AsyncSession]]:
    scoped_session = async_scoped_session(
        async_sessionmaker(
            bind=engine,
            autoflush=True,
            expire_on_commit=False,
        ),
        scopefunc=current_task,
    )
    try:
        yield scoped_session
    finally:
        await scoped_session.remove()


@asynccontextmanager
async def session_provide(
    session_factory: async_scoped_session[AsyncSession],
    mode: Literal['runtime', 'test'],
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        if mode == 'runtime':
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
        else:
            try:
                yield session
            finally:
                await session.rollback()
