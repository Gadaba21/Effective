from pydantic import EmailStr

from app.integrations.postgres.models import BaseDTO


class BaseCodeDTO(BaseDTO):
    """Базовая DTO схема для отправки кода"""

    code: str
    email: EmailStr


class CodeCreateDTO(BaseCodeDTO):
    """DTO схема для создания кода"""

    pass


class AccessEmailDTO(BaseCodeDTO):
    """DTO схема для подтверждения почты"""

    pass


class CodeDetailDTO(BaseCodeDTO):
    """DTO схема для получения информации о коде"""

    pass
