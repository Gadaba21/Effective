from urllib.parse import urlparse

from pydantic import BaseModel


class PostgresDSN(BaseModel):
    scheme: str
    user: str
    password: str
    host: str
    port: int
    database: str


def parse_postgres_dsn(dsn_str: str) -> PostgresDSN:
    parsed = urlparse(dsn_str)

    if not (parsed.username or parsed.password or parsed.hostname or parsed.port):
        msg = 'Invalid dsn_str.'
        raise ValueError(msg)

    return PostgresDSN(
        scheme=parsed.scheme,
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/'),
    )
