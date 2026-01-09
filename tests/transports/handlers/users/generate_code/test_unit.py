from unittest.mock import AsyncMock

from httpx import AsyncClient
from starlette import status

from app.services.code_service import CodeService
from app.transports.handlers.users.schemas import CodeDetail, GenerateCode, GenerateCodeResponse
from tests.conftest import ExplicitFastAPI
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
) -> None:
    code_service = AsyncMock(spec=CodeService)
    code_service.get_code_by_email.return_value = None
    code_service.create_code.return_value = dto_factories[GenerateCodeResponse].build()
    app.dependency_overrides[CodeService] = lambda: code_service
    result = await client.post(
        '/api/users/generate_code/',
        json=dto_factories[GenerateCode].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_201_CREATED
    assert code_service.create_code.await_count == 1
    assert code_service.get_code_by_email.await_count == 1
    assert code_service.delete_code.await_count == 0


async def test_generate_new_code(
    client: AsyncClient,
    app: ExplicitFastAPI,
    dto_factories: DTOFactoryDict,
) -> None:
    code_service = AsyncMock(spec=CodeService)
    code_service.get_code_by_email.return_value = dto_factories[CodeDetail].build()
    code_service.create_code.return_value = dto_factories[GenerateCodeResponse].build()
    app.dependency_overrides[CodeService] = lambda: code_service
    result = await client.post(
        '/api/users/generate_code/',
        json=dto_factories[GenerateCode].build().model_dump(mode='json'),
    )
    assert result.status_code == status.HTTP_201_CREATED
    assert code_service.get_code_by_email.await_count == 1
    assert code_service.delete_code.await_count == 1
    assert code_service.create_code.await_count == 1
