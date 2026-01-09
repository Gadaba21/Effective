from pydantic import EmailStr
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.orm import joinedload, selectinload

from app.integrations.postgres.dtos.user_dto import (
    CreateRankDTO,
    PlayerStatisticDTO,
    RankDetailDTO,
    RecoveryPasswordDTO,
    UpdatedUserDTO,
    UserAchievementsDTO,
    UserByEmailDTO,
    UserByIdDTO,
    UserCreateDTO,
    UserDetailDTO,
    UserDTO,
    UserExpDTO,
    UserLoginResponseDTO,
    UserPublicDTO,
    UserTempCreateDTO,
    UserTempResponseDTO,
    UserUpdatePartialDTO,
)
from app.integrations.postgres.orms.games_achievements_orm import GameAchievementsORM
from app.integrations.postgres.orms.player_game_statistics_orm import UserGameStatisticsORM
from app.integrations.postgres.orms.user_orm import UserORM
from app.utils.integrations.postgres.base_exception_handler import sqlalchemy_error_handle

from ..exceptions import EmailAlreadyExistsPostgres, UsernameAlreadyExistsPostgres, UserNotFoundPostgres
from ..orms.achievement_orm import AchievementORM
from ..orms.rank_orm import RankORM
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями."""

    @sqlalchemy_error_handle
    async def get_one_by_id(
        self,
        user_id: int,
    ) -> UserByIdDTO:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self._session.execute(stmt)
        try:
            user = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        return UserByIdDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def get_one_by_username(
        self,
        username: str,
    ) -> UserLoginResponseDTO | None:
        stmt = select(UserORM).where(UserORM.username == username)
        result = await self._session.execute(stmt)
        user = result.scalars().first()
        return UserLoginResponseDTO.model_validate(user) if user else None

    @sqlalchemy_error_handle
    async def get_one_by_email(
        self,
        email: EmailStr,
    ) -> UserByEmailDTO:
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self._session.execute(stmt)
        try:
            user = result.scalars().one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        return UserByEmailDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def get_one_with_rank(
        self,
        user_id: int,
    ) -> UserDetailDTO:
        stmt = select(UserORM).options(joinedload(UserORM.rank)).where(UserORM.id == user_id)
        result = await self._session.execute(stmt)
        try:
            user = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        return UserDetailDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def get_one_with_rank_public(
        self,
        user_id: int,
    ) -> UserPublicDTO:
        stmt = select(UserORM).options(joinedload(UserORM.rank)).where(UserORM.id == user_id)
        result = await self._session.execute(stmt)
        try:
            user = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        return UserPublicDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def add_one(
        self,
        user_data: UserCreateDTO,
    ) -> UserDTO:
        user = UserORM(**user_data.model_dump())
        self._session.add(user)
        try:
            await self._session.flush()
            await self._session.refresh(user)
        except IntegrityError as exc:
            await self._session.rollback()
            if 'users_username_key' in exc.args[0]:
                raise UsernameAlreadyExistsPostgres
            if 'users_email_key' in exc.args[0]:
                raise EmailAlreadyExistsPostgres
        return UserDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def delete_one(
        self,
        user_id: int,
    ) -> None:
        stmt = update(UserORM).where(UserORM.id == user_id).values(is_active=False)
        await self._session.execute(stmt)


    @sqlalchemy_error_handle
    async def get_user_statistics(
        self,
        user_id: int,
    ) -> list[PlayerStatisticDTO]:
        stmt = select(UserGameStatisticsORM).where(UserGameStatisticsORM.user_id == user_id)
        result = await self._session.execute(stmt)
        return [PlayerStatisticDTO.model_validate(statistic) for statistic in result.scalars().all()]

    @sqlalchemy_error_handle
    async def get_user_achievements(
        self,
        user_id: int,
    ) -> list[UserAchievementsDTO]:
        stmt = (
            select(GameAchievementsORM)
            .where(GameAchievementsORM.user_id == user_id)
            .options(selectinload(GameAchievementsORM.achievement))
        )
        result = await self._session.execute(stmt)
        return [UserAchievementsDTO.model_validate(achievement) for achievement in result.scalars().all()]

    @sqlalchemy_error_handle
    async def update(
        self,
        user_id: int,
        user_update: UserUpdatePartialDTO,
        partial: bool = True,
    ) -> UpdatedUserDTO:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(**user_update.model_dump(exclude_none=partial))
            .returning(UserORM)
        )
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as exc:
            await self._session.rollback()
            if 'users_username_key' in exc.args[0]:
                raise UsernameAlreadyExistsPostgres
            if 'users_email_key' in exc.args[0]:
                raise EmailAlreadyExistsPostgres
            raise
        try:
            updated_user = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        await self._session.flush()
        return UpdatedUserDTO.model_validate(updated_user)

    @sqlalchemy_error_handle
    async def activate_user(
        self,
        email: EmailStr,
    ) -> None:
        stmt = update(UserORM).where(UserORM.email == email).values(is_active=True).returning(UserORM)
        result = await self._session.execute(stmt)
        try:
            result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc

    @sqlalchemy_error_handle
    async def recovery_password(
        self,
        recovery_password_data: RecoveryPasswordDTO,
    ) -> UserByEmailDTO:
        stmt = (
            update(UserORM)
            .where(UserORM.email == recovery_password_data.email)
            .values(hash_password=recovery_password_data.hash_password)
            .returning(UserORM)
        )
        result = await self._session.execute(stmt)
        try:
            user = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        return UserByEmailDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def update_exp(self, user_id: int, exp: int) -> UserExpDTO:
        stmt = update(UserORM).where(UserORM.id == user_id).values(exp=exp).returning(UserORM)
        result = await self._session.execute(stmt)
        try:
            user = result.scalar_one()
        except (NoResultFound, MultipleResultsFound) as exc:
            raise UserNotFoundPostgres from exc
        await self._session.flush()
        return UserExpDTO.model_validate(user)

    @sqlalchemy_error_handle
    async def update_rank(self, user_id: int, rank: int) -> None:
        stmt = update(UserORM).where(UserORM.id == user_id).values(rank_id=rank)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def get_next_rank(self, user_exp: int) -> RankDetailDTO | None:
        stmt = select(RankORM).where(RankORM.points_required > user_exp).order_by(RankORM.points_required).limit(1)
        result = await self._session.execute(stmt)
        rank = result.scalar_one_or_none()
        return RankDetailDTO.model_validate(rank) if rank else None

    @sqlalchemy_error_handle
    async def get_rank(self, user_id: int) -> RankDetailDTO | None:
        stmt = select(UserORM).where(UserORM.id == user_id).options(joinedload(UserORM.rank))
        result = await self._session.execute(stmt)
        user = result.unique().scalar_one_or_none()
        if not user or not user.rank:
            return None
        return RankDetailDTO.model_validate(user.rank)

    @sqlalchemy_error_handle
    async def delete_all_achievement(self) -> None:
        stmt = delete(AchievementORM)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def delete_all_ranks(self) -> None:
        stmt = delete(RankORM)
        await self._session.execute(stmt)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def create_rank(self, rank: CreateRankDTO) -> None:
        new_rank = RankORM(**rank.model_dump())
        self._session.add(new_rank)
        await self._session.flush()

    @sqlalchemy_error_handle
    async def update_time_last_game(self, user_id: int) -> None:
        stmt = update(UserORM).where(UserORM.id == user_id).values(time_last_game=func.now())
        await self._session.execute(stmt)
        await self._session.flush()
