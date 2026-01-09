from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import UpdatedUserDTO
from app.integrations.postgres.exceptions import (
    EmailAlreadyExistsPostgres,
    UsernameAlreadyExistsPostgres,
    UserNotFoundPostgres,
)
from app.services.exceptions import EmailAlreadyExistsService, UsernameAlreadyExistsService, UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UpdatedUserResponse, UserUpdate
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    expected_user = dto_factories[UpdatedUserDTO].build()
    mock_user_repository.update.return_value = expected_user
    result = await fake_user_service.update_user(
        user_update=dto_factories[UserUpdate].build(nickname_color='#FFFFFF'),
        current_user_id=1,
    )
    assert result == UpdatedUserResponse(**expected_user.model_dump())


async def test_username_already_exists(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.update.side_effect = UsernameAlreadyExistsPostgres
    with pytest.raises(UsernameAlreadyExistsService):
        await fake_user_service.update_user(
            user_update=dto_factories[UserUpdate].build(nickname_color='#FFFFFF'),
            current_user_id=1,
        )


async def test_nonexistent_user(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.update.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_user_service.update_user(
            user_update=dto_factories[UserUpdate].build(nickname_color='#FFFFFF'),
            current_user_id=1,
        )


async def test_email_already_exists(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.update.side_effect = EmailAlreadyExistsPostgres
    with pytest.raises(EmailAlreadyExistsService):
        await fake_user_service.update_user(
            user_update=dto_factories[UserUpdate].build(nickname_color='#FFFFFF'),
            current_user_id=1,
        )
