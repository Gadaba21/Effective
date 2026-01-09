import asyncio
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session

from app.integrations.postgres.providers import postgres_engine_provide, session_factory_provide, session_provide
from app.utils.config import EnvSettings
from tests.conftest_utils import ORMFactoryDict
from tests.integrations.postgres.conftest_utils import docker_container_manager


@pytest.fixture(scope='session')
async def fake_engine(fake_env_settings: EnvSettings) -> AsyncGenerator[AsyncEngine]:
    with docker_container_manager(fake_env_settings.postgres_dsn.get_secret_value()):
        process = await asyncio.create_subprocess_exec(
            'alembic', 'upgrade', 'head', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            pytest.fail(f'Миграции не применились: {stderr.decode()}')

        async with postgres_engine_provide(fake_env_settings.postgres_dsn.get_secret_value()) as engine:
            yield engine


@pytest.fixture
async def fake_session_factory(
    fake_engine: AsyncEngine,
) -> AsyncGenerator[async_scoped_session[AsyncSession]]:
    async with session_factory_provide(fake_engine) as session_factory:
        yield session_factory


@pytest.fixture
async def fake_session(
    fake_session_factory: AbstractAsyncContextManager[async_scoped_session[AsyncSession]],
) -> AsyncGenerator[async_scoped_session[AsyncSession]]:
    async with session_provide(fake_session_factory, mode='test') as session:
        yield session


@pytest.fixture
async def orm_factories(fake_session: AsyncSession) -> ORMFactoryDict:
    return ORMFactoryDict(fake_session)
