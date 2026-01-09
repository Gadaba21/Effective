from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from app.integrations.postgres.dtos.lobby_dto import PlayerSchemaDTO
from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.rank_orm import RankORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.lobby_repository import LobbyRepository
from tests.conftest import dto_factories
from tests.conftest_utils import DTOFactoryDict, ORMFactoryDict


async def test_create_player(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(
        players=[],
        settings=None,
        settings_fm=None,
        blacklisted_players=[],
        game=None,
    )
    stmt = select(count(PlayerORM.id))
    assert await fake_session.scalar(stmt) == 0

    player = await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=True)
    user_stmt = select(UserORM).where(UserORM.id == user.id)
    result = await fake_session.execute(user_stmt)
    updated_user = result.scalars().one()

    assert updated_user.in_room is True
    assert player.user_id == user.id
    assert player.is_host is True


async def test_db_schema(
    fake_session: AsyncSession,
    lobby_repository: LobbyRepository,
    dto_factories: DTOFactoryDict,
    orm_factories: ORMFactoryDict,
) -> None:
    rank = await orm_factories[RankORM].acreate(
        users=[],
    )
    user = await orm_factories[UserORM].acreate(
        rank_id=rank.id,
    )
    room = await orm_factories[RoomORM].acreate(
        players=[],
        settings=None,
        settings_fm=None,
        blacklisted_players=[],
        game=None,
    )
    player = await lobby_repository.create_player(user_id=user.id, room_id=room.id, is_host=True)
    player_dto = dto_factories[PlayerSchemaDTO].build(
        user_id=user.id,
        room_id=room.id,
        is_host=True,
        name=user.username,
        nickname_color=user.nickname_color,
        avatar=user.avatar,
        is_vip=user.is_vip,
    )
    assert player_dto.user_id == player.user_id

    assert (
        await fake_session.scalar(
            select(count(PlayerORM.id)).where(
                PlayerORM.user_id == player_dto.user_id,
                PlayerORM.room_id == player_dto.room_id,
                PlayerORM.name == player_dto.name,
            )
        )
        == 1
    )
