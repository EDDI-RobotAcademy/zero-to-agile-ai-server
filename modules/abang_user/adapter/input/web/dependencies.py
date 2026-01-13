from infrastructure.db.postgres import SessionLocal
from modules.abang_user.adapter.output.abang_user_repository import AbangUserRepository
from modules.abang_user.application.usecase.get_user_phone_usecase import GetUserPhoneUseCase
from modules.abang_user.application.usecase.update_user_usecase import UpdateUserUseCase

# Repository Singletons
_abang_user_repo = None

def get_abang_user_repository():
    global _abang_user_repo
    if _abang_user_repo is None:
        _abang_user_repo = AbangUserRepository(SessionLocal)
    return _abang_user_repo

# UseCase Dependencies
def get_get_user_phone_usecase() -> GetUserPhoneUseCase:
    return GetUserPhoneUseCase(get_abang_user_repository())

def get_update_user_usecase() -> UpdateUserUseCase:
    return UpdateUserUseCase(get_abang_user_repository())
