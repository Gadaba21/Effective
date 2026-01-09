from typing import Annotated

from fastapi.params import Depends
from pydantic import EmailStr

from app.integrations.postgres.dtos.code_dto import AccessEmailDTO, CodeCreateDTO, CodeDetailDTO
from app.integrations.postgres.exceptions import CodeNotFoundPostgres
from app.integrations.postgres.repositories.code_repository import CodeRepository
from app.services.exceptions import CodeNotFoundService
from app.transports.handlers.users.schemas import AccessEmail, CodeDetail, GenerateCodeResponse
from app.transports.handlers.users.utils import generate_verification_code


class CodeService:
    def __init__(
        self,
        code_repository: Annotated[CodeRepository, Depends()],
    ) -> None:
        self._code_repository = code_repository

    async def create_code(
        self,
        email: EmailStr,
    ) -> GenerateCodeResponse:
        """Сервис по созданию кода"""
        code = generate_verification_code()
        await self._code_repository.add_one(CodeCreateDTO(code=code, email=email))
        return GenerateCodeResponse(access='Код был отправлен на вашу почту!')

    async def get_code(
        self,
        access_email_data: AccessEmail,
    ) -> CodeDetail:
        """Сервис по получению кода"""
        try:
            code_detail = await self._code_repository.get_one(AccessEmailDTO(**access_email_data.model_dump()))
        except CodeNotFoundPostgres as exc:
            raise CodeNotFoundService from exc
        return CodeDetail(**code_detail.model_dump())

    async def get_code_by_email(
        self,
        email: EmailStr,
    ) -> CodeDetail | None:
        """Сервис по поиску кода по почте"""
        if code := await self._code_repository.get_by_email(email):
            return CodeDetail(**code.model_dump())
        return None

    async def delete_code(
        self,
        delete_code_data: CodeDetail,
    ) -> None:
        """Сервис по удалению кода"""
        await self._code_repository.delete(CodeDetailDTO(**delete_code_data.model_dump()))
