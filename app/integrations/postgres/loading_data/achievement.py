import argparse
import asyncio
from pathlib import Path
import sys

import pandas as pd
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.integrations.postgres.repositories.user_repository import UserRepository

# чтобы видеть project_root и правильно импортировать app.*
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from app.integrations.postgres.dtos.game_bj_dto import AchievementCreateBJDTO
from app.integrations.postgres.orms.baseorm import BaseORM


class CreateAchievement:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def reset_achievement(self, file_path: str) -> None:
        """Удаляет старые карты и импортирует новые из Excel"""
        # удаляем все старые записи
        await self._user_repository.delete_all_achievement()

        # читаем Excel
        df = pd.read_excel(file_path)

        # приведение типов
        df = df.rename(
            columns={
                'name': 'name',
                'desc': 'desc',
            }
        )

        # сохраняем построчно
        for i, row in df.iterrows():
            validated = AchievementCreateBJDTO(
                name=row['name'],
                desc=row['desc'],
            )
            await self._user_repository.create_achievement(validated)


async def run_import(db_url: str, file_path: str) -> None:
    engine = create_async_engine(db_url, echo=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    # создаём таблицы, если их ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session=session)
        creator = CreateAchievement(user_repository=repo)
        await creator.reset_achievement(file_path=file_path)
        await session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Импорт карт из Excel в БД (с очисткой старых)')
    parser.add_argument(
        '--db-url',
        type=str,
        required=True,
        help='URL подключения к БД, например: postgresql+asyncpg://postgres:postgres@localhost:15432/postgres',
    )
    parser.add_argument('--file', type=str, required=True, help='Путь к Excel-файлу')

    args = parser.parse_args()

    asyncio.run(run_import(db_url=args.db_url, file_path=args.file))
