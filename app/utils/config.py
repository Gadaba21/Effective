from functools import lru_cache

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseModel):
    app_name: str = 'Tower empire'
    version: str = '1.0'
    debug: bool = True


class EnvSettings(
    BaseSettings,
    env_file='.env',
):
    postgres_dsn: SecretStr
    secret_key: SecretStr
    algorithm: SecretStr
    su_username: SecretStr
    su_password: SecretStr
    smtp_server: SecretStr
    smtp_username: SecretStr
    smtp_password: SecretStr
    celery_broker_url: SecretStr
    celery_result_backend: SecretStr
    redis_host: SecretStr
    redis_port: SecretStr
    redis_db: SecretStr
    redis_password: SecretStr
    postgres_main: SecretStr
    allowed_origins: SecretStr


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache
def get_env_settings() -> EnvSettings:
    return EnvSettings()
