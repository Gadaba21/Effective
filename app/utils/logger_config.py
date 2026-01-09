import os
from pathlib import Path

from loguru import logger

Path('logs').mkdir(exist_ok=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, '..', '..', 'logs')

os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    'logs/user_lobby.log',
    rotation='10 MB',
    retention='10 days',
    compression='zip',
    level='DEBUG',
    filter=lambda record: record['extra'].get('user_lobby') is True,
)


user_lobby_logger = logger.bind(user_lobby=True)

__all__ = [
    'user_lobby_logger',
]
