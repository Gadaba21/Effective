from unittest.mock import AsyncMock

from app.integrations.postgres.dtos.lobby_dto import RoomSchemaDTO
from app.services.lobby_service import LobbyService
from app.transports.handlers.lobby.schemas import RoomResponse
from tests.conftest_utils import DTOFactoryDict


async def test_happy_path(
    fake_lobby_service: LobbyService,
    mock_lobby_repository: AsyncMock,
    dto_factories: DTOFactoryDict,
) -> None:
    lobbies = [dto_factories[RoomSchemaDTO].build()]
    mock_lobby_repository.get_all_rooms.return_value = lobbies
    result = await fake_lobby_service.get_all_rooms()
    assert result == [RoomResponse(**room.model_dump()) for room in result]
