import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Generator
from typing import cast

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
import pytest

from app.utils.app_factory import AppFactory
from app.utils.config import EnvSettings, get_app_settings
from tests.conftest_utils import DTOFactoryDict


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def fake_env_settings(postgres_test_dsn: str) -> EnvSettings:
    return EnvSettings(postgres_dsn=SecretStr(postgres_test_dsn))


@pytest.fixture(scope='session')
def postgres_test_dsn() -> str:
    return 'postgresql+asyncpg://postgres:postgres@localhost:5431/test_db_black_jokes'


@pytest.fixture
async def dto_factories() -> DTOFactoryDict:
    return DTOFactoryDict()


class ExplicitFastAPI(FastAPI):
    dependency_overrides: dict


@pytest.fixture
def app() -> ExplicitFastAPI:
    service = AppFactory.make(
        app_settings=get_app_settings(),
    )
    return cast(ExplicitFastAPI, service)


@pytest.fixture
async def client(
    app: ExplicitFastAPI,
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://_testing_',
    ) as client:
        yield client
