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

from fastapi import Depends
from modules.send_message.adapter.input.web.dependencies import get_send_message_repository
from modules.abang_user.adapter.input.web.dependencies import get_abang_user_repository
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort

def get_get_house_platform_usecase(
    repo: HousePlatformRepositoryPort = Depends(get_house_platform_repository),
    message_repo: SendMessageRepository = Depends(get_send_message_repository),
    user_repo: AbangUserRepositoryPort = Depends(get_abang_user_repository)
) -> GetHousePlatformUseCase:
    return GetHousePlatformUseCase(repo, message_repo, user_repo)

def get_update_house_platform_usecase() -> UpdateHousePlatformUseCase:
    return UpdateHousePlatformUseCase(get_house_platform_repository())

def get_delete_house_platform_usecase() -> DeleteHousePlatformUseCase:
    return DeleteHousePlatformUseCase(get_house_platform_repository())
