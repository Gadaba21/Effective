from collections.abc import Generator
from contextlib import contextmanager
import time

import docker
from docker.models.containers import Container

from app.utils.parse_postgres_dsn import parse_postgres_dsn


def start_test_db(
    postgres_user: str,
    postgres_password: str,
    postgres_db: str,
    timeout: int = 30,
) -> Container:
    client = docker.from_env()
    container = client.containers.run(
        'postgres:16-alpine',
        name='test_postgres',
        environment={
            'POSTGRES_USER': postgres_user,
            'POSTGRES_PASSWORD': postgres_password,
            'POSTGRES_DB': postgres_db,
        },
        ports={'5432/tcp': 5431},
        detach=True,
        remove=True,
        healthcheck={
            'test': ['CMD-SHELL', f'pg_isready -U {postgres_user} -d {postgres_db}'],
            'interval': int(5e8),
            'timeout': int(5e8),
            'retries': 30,
        },
    )

    start_time = time.time()
    while time.time() - start_time < timeout:
        container.reload()
        if container.attrs.get('State', {}).get('Health', {}).get('Status') == 'healthy':
            return container
        time.sleep(1)

    msg = 'Ошибка при запуске контейнера'

    raise ValueError(msg)


@contextmanager
def docker_container_manager(postgres_dsn: str) -> Generator[Container]:
    parsed_dsn = parse_postgres_dsn(postgres_dsn)
    container = start_test_db(
        postgres_user=parsed_dsn.user,
        postgres_password=parsed_dsn.password,
        postgres_db=parsed_dsn.database,
    )
    try:
        yield container
    finally:
        container.stop()
