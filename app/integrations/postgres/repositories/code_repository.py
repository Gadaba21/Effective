from pydantic import EmailStr
from sqlalchemy import delete, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.integrations.postgres.dtos.code_dto import AccessEmailDTO, CodeCreateDTO, CodeDetailDTO
from app.integrations.postgres.exceptions import CodeNotFoundPostgres
from app.integrations.postgres.orms.code_orm import CodeORM
from app.integrations.postgres.repositories.base_repository import BaseRepository
from app.utils.integrations.postgres.base_exception_handler import sqlalchemy_error_handle


class CodeRepository(BaseRepository):
    @sqlalchemy_error_handle
    async def add_one(
        self,
        code_data: CodeCreateDTO,
    ) -> None:
        code = CodeORM(**code_data.model_dump())
        self._session.add(code)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def get_one(
        self,
        access_email_data: AccessEmailDTO,
    ) -> CodeDetailDTO:
        stmt = (
            select(CodeORM)
            .where(CodeORM.email == access_email_data.email)
            .where(CodeORM.code == access_email_data.code)
        )
        result = await self._session.execute(stmt)
        try:
            code = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise CodeNotFoundPostgres from exc
        return CodeDetailDTO.model_validate(code)

    @sqlalchemy_error_handle
    async def get_by_email(
        self,
        email: EmailStr,
    ) -> CodeDetailDTO | None:
        stmt = select(CodeORM).where(CodeORM.email == email)
        result = await self._session.execute(stmt)
        code = result.first()
        return CodeDetailDTO.model_validate(code) if code else None

    @sqlalchemy_error_handle
    async def delete(
        self,
        delete_code_data: CodeDetailDTO,
    ) -> None:
        stmt = (
            delete(CodeORM).where(CodeORM.email == delete_code_data.email).where(CodeORM.code == delete_code_data.code)
        )
        await self._session.execute(stmt)
