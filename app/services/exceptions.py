from app.services.base_exception_service import BaseExceptionService


class UserNotFoundService(BaseExceptionService):
    pass


class EmailAlreadyExistsService(BaseExceptionService):
    pass


class UsernameAlreadyExistsService(BaseExceptionService):
    pass


class InvalidPasswordService(BaseExceptionService):
    pass


class InvalidStatusService(BaseExceptionService):
    pass


class MissCredentialsService(BaseExceptionService):
    pass


class CodeNotFoundService(BaseExceptionService):
    pass



class InvalidOldPasswordService(BaseExceptionService):
    pass


class InvalidNewPasswordService(BaseExceptionService):
    pass


class UserInRoomService(BaseExceptionService):
    pass


class TitleCreateRoomService(BaseExceptionService):
    pass


class RoomNotFoundService(BaseExceptionService):
    pass


class NoSlotService(BaseExceptionService):
    pass


class PasswordRoomNotValidService(BaseExceptionService):
    pass


class BlackListService(BaseExceptionService):
    pass


class AchievementNotFoundService(BaseExceptionService):
    pass



class FileNotUploadService(BaseExceptionService):
    pass


class FileExtensionService(BaseExceptionService):
    pass


class InvalidIsActiveService(BaseExceptionService):
    pass


class UserAlreadyActiveService(BaseExceptionService):
    pass


class DeleteRoomNotAdminService(BaseExceptionService):
    pass
