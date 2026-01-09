from infrastructure.db.postgres import SessionLocal
from modules.house_platform.infrastructure.repository.house_platform_repository import HousePlatformRepository
from modules.house_platform.application.usecase.create_house_platform_usecase import CreateHousePlatformUseCase
from modules.house_platform.application.usecase.get_house_platform_usecase import GetHousePlatformUseCase
from modules.house_platform.application.usecase.update_house_platform_usecase import UpdateHousePlatformUseCase
from modules.house_platform.application.usecase.delete_house_platform_usecase import DeleteHousePlatformUseCase

# Repository Singleton
_house_platform_repo = None

def get_house_platform_repository():
    global _house_platform_repo
    if _house_platform_repo is None:
        _house_platform_repo = HousePlatformRepository(SessionLocal)
    return _house_platform_repo

# UseCase Dependencies
def get_create_house_platform_usecase() -> CreateHousePlatformUseCase:
    return CreateHousePlatformUseCase(get_house_platform_repository())

def get_get_house_platform_usecase() -> GetHousePlatformUseCase:
    return GetHousePlatformUseCase(get_house_platform_repository())

def get_update_house_platform_usecase() -> UpdateHousePlatformUseCase:
    return UpdateHousePlatformUseCase(get_house_platform_repository())

def get_delete_house_platform_usecase() -> DeleteHousePlatformUseCase:
    return DeleteHousePlatformUseCase(get_house_platform_repository())
