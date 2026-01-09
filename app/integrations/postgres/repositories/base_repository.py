from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.transports.depends.postgres import session_depend


class BaseRepository:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(session_depend)] = None,  # type: ignore
    ) -> None:
        self._session: AsyncSession | None = session

    def set_session(self, session: AsyncSession) -> None:
        self._session = session
