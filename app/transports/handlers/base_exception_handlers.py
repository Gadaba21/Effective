from fastapi import HTTPException
from starlette import status


class BaseExceptionTransport(HTTPException):
    detail: str = 'Internal server error'
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )
