from unittest.mock import AsyncMock

import pytest

from app.integrations.postgres.dtos.user_dto import UserByIdDTO
from app.integrations.postgres.exceptions import UserNotFoundPostgres
from app.services.exceptions import InvalidNewPasswordService, InvalidOldPasswordService, UserNotFoundService
from app.services.user_service import UserService
from app.transports.handlers.users.schemas import AccessResetPasswordResponse, ResetPassword
from tests.conftest_utils import DTOFactoryDict


async def test_nonexistent_user(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    mock_user_repository.get_one_by_id.side_effect = UserNotFoundPostgres
    with pytest.raises(UserNotFoundService):
        await fake_user_service.reset_password(
            reset_password_data=dto_factories[ResetPassword].build(
                new_password='Stringst1',
                old_password='Stringst1',
            ),
            user_id=1,
        )


async def test_happy_path(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    reset_password_data = dto_factories[ResetPassword].build(new_password='Stringst1')
    hash_password = fake_user_service.set_password(reset_password_data.old_password)
    expected_user = dto_factories[UserByIdDTO].build(
        email='test@example.com',
        hash_password=hash_password,
    )
    mock_user_repository.get_one_by_id.return_value = expected_user
    result = await fake_user_service.reset_password(
        reset_password_data=reset_password_data,
        user_id=expected_user.id,
    )
    assert result == AccessResetPasswordResponse(
        access='Пароль для пользователя был изменен!',
        username=expected_user.username,
        email=expected_user.email,
    )


async def test_invalid_old_password(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    hash_password = fake_user_service.set_password('Test123qwe')
    expected_user = dto_factories[UserByIdDTO].build(hash_password=hash_password)
    mock_user_repository.get_one_by_id.return_value = expected_user
    with pytest.raises(InvalidOldPasswordService):
        await fake_user_service.reset_password(
            reset_password_data=dto_factories[ResetPassword].build(old_password='Stringst1'), user_id=expected_user.id
        )


async def test_invalid_new_password(
    fake_user_service: UserService,
    mock_user_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    reset_password_data = dto_factories[ResetPassword].build(
        old_password='Stringst1',
        new_password='Stringst1',
    )
    hash_password = fake_user_service.set_password(reset_password_data.new_password)
    expected_user = dto_factories[UserByIdDTO].build(hash_password=hash_password)
    mock_user_repository.get_one_by_id.return_value = expected_user
    with pytest.raises(InvalidNewPasswordService):
        await fake_user_service.reset_password(
            reset_password_data=reset_password_data,
            user_id=expected_user.id,
        )
