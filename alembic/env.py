import asyncio
from logging.config import fileConfig
import os

from sqlalchemy.engine import Connection

from alembic import context
from app.integrations.postgres.orms.baseorm import BaseORM
from app.integrations.postgres.providers import postgres_engine_provide
from app.utils.config import get_env_settings

config = context.config

fileConfig('alembic.ini')

target_metadata = BaseORM.metadata


async def run_migrations_online(postgres_dsn: str) -> None:
    async with (
        postgres_engine_provide(postgres_dsn) as connectable,
        connectable.connect() as connection,
    ):
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=target_metadata.schema,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations() -> None:
    if 'PYTEST_CURRENT_TEST' in os.environ:
        postgres_dsn = 'postgresql+asyncpg://postgres:postgres@localhost:5431/test_db_black_jokes'
    else:
        postgres_dsn = get_env_settings().postgres_dsn.get_secret_value()
    asyncio.run(run_migrations_online(postgres_dsn))


if context.is_offline_mode():
    msg = 'Offline mode is not supported for async migrations'
    raise NotImplementedError(msg)
else:
    run_migrations()
