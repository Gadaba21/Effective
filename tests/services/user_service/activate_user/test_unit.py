from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import UserByEmailDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.services.exceptions import UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import AccessEmail, ActivateUser
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UserByEmailDTO].build(is_active=False)
    mock_user_repository.get_one_by_email.return_value = expected_user
    result = await fake_user_service.activate_user(access_email_data=dto_factories[AccessEmail].build())
    assert mock_user_repository.get_one_by_email.await_count == 1
    assert mock_user_repository.activate_user.await_count == 1
    assert result == ActivateUser(access='Ваш аккаунт был успешно активирован!')


async def test_nonexistent_user(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.get_one_by_email.side_effect = UserNotFoundPostgres
    mock_user_repository.activate_user.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_user_service.activate_user(access_email_data=dto_factories[AccessEmail].build())
    assert mock_user_repository.get_one_by_email.await_count == 1
    assert mock_user_repository.activate_user.await_count == 0
