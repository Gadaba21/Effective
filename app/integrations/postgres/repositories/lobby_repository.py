from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.orm import selectinload

from app.integrations.postgres.dtos.lobby_dto import PlayerSchemaDTO, RoomCreateDTO, RoomSchemaDTO
from app.integrations.postgres.dtos.user_dto import AchievementDTO, PlayerStatisticDTO
from app.integrations.postgres.exceptions import (
    AchievementNotFoundPostgres,
    PlayerNotFoundPostgres,
    RoomNotFoundPostgres,
    TitleCreateRoomPostgres,
)
from app.integrations.postgres.orms.achievement_orm import AchievementORM

from app.integrations.postgres.orms.blacklis_orm import BlackListORM
from app.integrations.postgres.orms.games_achievements_orm import GameAchievementsORM
from app.integrations.postgres.orms.games_history_orm import GameHistoryORM
from app.integrations.postgres.orms.player_game_statistics_orm import UserGameStatisticsORM
from app.integrations.postgres.orms.player_orm import PlayerORM
from app.integrations.postgres.orms.room_orm import RoomORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.integrations.postgres.repositories.base_repository import BaseRepository
from app.transports.handlers.lobby.schemas import RoomCreateSchema
from app.utils.integrations.postgres.base_exception_handler import sqlalchemy_error_handle


class LobbyRepository(BaseRepository):
    """Репозиторий для работы с лобби."""

    @sqlalchemy_error_handle
    async def get_one_room(self, room_id: int) -> RoomSchemaDTO:
        stmt = select(RoomORM).where(RoomORM.id == room_id).options(selectinload(RoomORM.players))
        result = await self._session.execute(stmt)
        try:
            room = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise RoomNotFoundPostgres from exc
        return RoomSchemaDTO.model_validate(room)

    @sqlalchemy_error_handle
    async def get_all_rooms(
        self,
    ) -> list[RoomSchemaDTO]:
        stmt = select(RoomORM).options(selectinload(RoomORM.players))
        result = await self._session.execute(stmt)
        return [RoomSchemaDTO.model_validate(room) for room in result.scalars().all()]

    @sqlalchemy_error_handle
    async def get_player(
        self,
        user_id: int,
    ) -> PlayerSchemaDTO:
        stmt = select(PlayerORM).where(PlayerORM.user_id == user_id)
        result = await self._session.execute(stmt)
        try:
            player = result.scalars().one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise PlayerNotFoundPostgres from exc
        return PlayerSchemaDTO.model_validate(player)

    @sqlalchemy_error_handle
    async def find_player(
        self,
        user_id: int,
    ) -> PlayerSchemaDTO | None:
        stmt = select(PlayerORM).where(PlayerORM.user_id == user_id)
        result = await self._session.execute(stmt)
        player = result.scalars().first()
        return PlayerSchemaDTO.model_validate(player) if player else None

    @sqlalchemy_error_handle
    async def get_all_player(
        self,
        room_id: int,
    ) -> list[PlayerSchemaDTO]:
        stmt = select(PlayerORM).where(PlayerORM.room_id == room_id).order_by(PlayerORM.id)
        result = await self._session.execute(stmt)
        return [PlayerSchemaDTO.model_validate(player) for player in result.scalars().all()]

    @sqlalchemy_error_handle
    async def get_all_player_in_room(
        self,
        room_id: int,
    ) -> list[PlayerSchemaDTO]:
        stmt = select(PlayerORM).where(PlayerORM.room_id == room_id, PlayerORM.is_disconnect == False)
        result = await self._session.execute(stmt)
        return [PlayerSchemaDTO.model_validate(player) for player in result.scalars().all()]

    @sqlalchemy_error_handle
    async def create_room(
        self,
        room_data: RoomCreateSchema,
    ) -> RoomCreateDTO:
        room = RoomORM(**room_data.model_dump(exclude_unset=True))
        if room_data.password:
            room.is_private = True
            room.password = room_data.password
        self._session.add(room)
        try:
            await self._session.flush()
            await self._session.refresh(room)
        except IntegrityError as exc:
            await self._session.rollback()
            if 'rooms_title_key' in exc.args[0]:
                raise TitleCreateRoomPostgres
        return RoomCreateDTO.model_validate(room)

    @sqlalchemy_error_handle
    async def create_player(
        self,
        user_id: int,
        room_id: int,
        is_host: bool,
    ) -> PlayerSchemaDTO:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalars().one()
        player = PlayerORM(
            name=user.username,
            user_id=user_id,
            room_id=room_id,
            nickname_color=user.nickname_color,
            avatar=user.avatar,
            is_vip=user.is_vip,
            is_host=is_host,
        )
        user.in_room = True
        self._session.add(player)
        await self._session.flush()
        await self._session.refresh(player)
        return PlayerSchemaDTO.model_validate(player)

    @sqlalchemy_error_handle
    async def user_in_room(self, user_id: int, in_room: bool) -> None:
        stmt = update(UserORM).where(UserORM.id == user_id).values(in_room=in_room)
        await self._session.execute(stmt)
        await self._session.flush()


    @sqlalchemy_error_handle
    async def delete_room(
        self,
        room_id: int,
    ) -> None:
        stmt = delete(RoomORM).where(RoomORM.id == room_id)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def black_list(self, user_id: int, room_id: int) -> bool | None:
        stmt = select(BlackListORM).where(BlackListORM.room_id == room_id, BlackListORM.user_id == user_id)
        result = await self._session.execute(stmt)
        blacklist_entry = result.scalars().first()
        return blacklist_entry is not None

    @sqlalchemy_error_handle
    async def add_black_list(
        self,
        user_id: int,
        room_id: int,
    ) -> None:
        blacklist = BlackListORM(user_id=user_id, room_id=room_id)
        self._session.add(blacklist)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def disconnect_change(self, user_id: int, is_disconnect: bool) -> None:
        stmt = update(PlayerORM).where(PlayerORM.user_id == user_id).values(is_disconnect=is_disconnect)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def disconnect_check(self, user_id: int, room_id: int) -> bool:
        stmt = select(PlayerORM).where(PlayerORM.user_id == user_id, PlayerORM.room_id == room_id)
        result = await self._session.execute(stmt)
        player = result.scalars().first()
        return player.is_disconnect if player else True

    @sqlalchemy_error_handle
    async def delete_player(
        self,
        user_id: int,
    ) -> None:
        stmt = delete(PlayerORM).where(PlayerORM.user_id == user_id)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def delete_player_except_current_room(
        self,
        user_id: int,
        room_id: int,
    ) -> None:
        stmt = delete(PlayerORM).where(PlayerORM.user_id == user_id).where(PlayerORM.room_id != room_id)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def is_host(
        self,
        user_id: int,
    ) -> PlayerSchemaDTO | None:
        stmt = select(PlayerORM).where(PlayerORM.user_id == user_id, PlayerORM.is_host == True)
        result = await self._session.execute(stmt)
        player = result.scalars().first()
        return PlayerSchemaDTO.model_validate(player) if player else None

    @sqlalchemy_error_handle
    async def change_host(self, player_id: int, is_host: bool) -> None:
        stmt = update(PlayerORM).where(PlayerORM.id == player_id).values(is_host=is_host)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def change_private(self, room_id: int, is_private: bool) -> None:
        stmt = update(RoomORM).where(RoomORM.id == room_id).values(is_private=is_private)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def change_password(self, room_id: int, password: str) -> None:
        stmt = update(RoomORM).where(RoomORM.id == room_id).values(password=password)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def change_max_players(self, room_id: int, max_players: int) -> None:
        stmt = update(RoomORM).where(RoomORM.id == room_id).values(max_players=max_players)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def game_started(self, room_id: int, started: bool) -> None:
        stmt = update(RoomORM).where(RoomORM.id == room_id).values(started=started)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def update_time_last_game(self, room_id: int) -> None:
        stmt = update(RoomORM).where(RoomORM.id == room_id).values(afk_time=func.now())
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def create_history_game(
        self,
        game_name: str,
        game_id: int,
        players: dict[str, int],
    ) -> None:
        history = GameHistoryORM(game_name=game_name, game_id=game_id, players=players)
        self._session.add(history)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def update_game_statistic(self, win_game: int, total_game: int, statistic_id: int) -> None:
        stmt = (
            update(UserGameStatisticsORM)
            .where(UserGameStatisticsORM.id == statistic_id)
            .values(won_game=win_game, total_game=total_game)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def get_achievement(self, name_achievement: str) -> AchievementDTO:
        stmt = select(AchievementORM).where(AchievementORM.name == name_achievement)
        result = await self._session.execute(stmt)
        try:
            achievement = result.scalars().one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise AchievementNotFoundPostgres from exc
        return AchievementDTO.model_validate(achievement)

    @sqlalchemy_error_handle
    async def create_game_achievement(self, user_id: int, achievement_id: int, game_name: str) -> None:
        achievement = GameAchievementsORM(user_id=user_id, achievement_id=achievement_id, game_name=game_name)
        self._session.add(achievement)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def create_game_statistics(
        self,
        user_id: int,
        game_name: str,
    ) -> PlayerStatisticDTO:
        player_statistic = UserGameStatisticsORM(game_name=game_name, user_id=user_id)
        self._session.add(player_statistic)
        await self._session.flush()
        await self._session.refresh(player_statistic)
        return PlayerStatisticDTO.model_validate(player_statistic)

    @sqlalchemy_error_handle
    async def get_game_statistics(self, user_id: int) -> PlayerStatisticDTO | None:
        stmt = select(UserGameStatisticsORM).where(UserGameStatisticsORM.user_id == user_id)
        result = await self._session.execute(stmt)
        statistics = result.scalars().first()
        return PlayerStatisticDTO.model_validate(statistics) if statistics else None

    @sqlalchemy_error_handle
    async def get_player_by_id(
        self,
        player_id: int,
    ) -> PlayerSchemaDTO:
        stmt = select(PlayerORM).where(PlayerORM.id == player_id)
        result = await self._session.execute(stmt)
        try:
            player = result.scalars().one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise PlayerNotFoundPostgres from exc
        return PlayerSchemaDTO.model_validate(player)


    @sqlalchemy_error_handle
    async def delete_player_by_id(
        self,
        player_id: int,
    ) -> None:
        stmt = delete(PlayerORM).where(PlayerORM.id == player_id)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def get_player_by_id(
        self,
        player_id: int,
    ) -> PlayerSchemaDTO:
        stmt = select(PlayerORM).where(PlayerORM.id == player_id)
        result = await self._session.execute(stmt)
        try:
            player = result.scalars().one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise PlayerNotFoundPostgres from exc
        return PlayerSchemaDTO.model_validate(player)
