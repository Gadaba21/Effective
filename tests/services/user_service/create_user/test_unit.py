from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import UserDTO
from app.integrations.postgres.exceptions import EmailAlreadyExistsPostgres, UsernameAlreadyExistsPostgres
from app.services.exceptions import EmailAlreadyExistsService, UsernameAlreadyExistsService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import UserCreate, UserCreateResponse
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    password_raw = 'stringst1'
    expected_user = dto_factories[UserDTO].build()
    mock_user_repository.add_one.return_value = expected_user
    result = await fake_user_service.create_user(
        user_data=dto_factories[UserCreate].build(
            password=password_raw,
            password_2=password_raw,
        )
    )
    assert result == UserCreateResponse(**expected_user.model_dump())


async def test_email_already_exists(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    password_raw = 'stringst1'
    mock_user_repository.add_one.side_effect = EmailAlreadyExistsPostgres
    with pytest.raises(EmailAlreadyExistsService):
        await fake_user_service.create_user(
            user_data=dto_factories[UserCreate].build(
                password=password_raw,
                password_2=password_raw,
            )
        )


async def test_username_already_exists(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    password_raw = 'stringst1'
    mock_user_repository.add_one.side_effect = UsernameAlreadyExistsPostgres
    with pytest.raises(UsernameAlreadyExistsService):
        await fake_user_service.create_user(
            user_data=dto_factories[UserCreate].build(
                password=password_raw,
                password_2=password_raw,
            )
        )
