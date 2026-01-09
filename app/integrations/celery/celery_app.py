from celery import Celery

from app.utils.config import get_env_settings

celery_app: Celery = Celery(
    'app',
    broker=get_env_settings().celery_broker_url.get_secret_value(),
    backend=get_env_settings().celery_result_backend.get_secret_value(),
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

