from app.integrations.postgres.base_exception import BasePostgresError


class UserNotFoundPostgres(BasePostgresError):
    pass


class UsernameAlreadyExistsPostgres(BasePostgresError):
    pass


class EmailAlreadyExistsPostgres(BasePostgresError):
    pass


class CodeNotFoundPostgres(BasePostgresError):
    pass


class RoomNotFoundPostgres(BasePostgresError):
    pass


class TitleCreateRoomPostgres(BasePostgresError):
    pass


class PlayerNotFoundPostgres(BasePostgresError):
    pass


class AchievementNotFoundPostgres(BasePostgresError):
    pass

