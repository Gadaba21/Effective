from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import UserByEmailDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import AccessUpdatePasswordResponse, RecoveryPassword
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserByEmailDTO].build()
    mock_user_repository.recovery_password.return_value = expected_user
    result = await fake_user_service.recovery_password(
        recovery_password_data=dto_factories[RecoveryPassword].build(),
    )
    assert result == AccessUpdatePasswordResponse(
        access='Пароль для пользователя был изменен!',
        username=expected_user.username,
    )


async def test_nonexistent_user(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.recovery_password.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_user_service.recovery_password(
            recovery_password_data=dto_factories[RecoveryPassword].build(),
        )
