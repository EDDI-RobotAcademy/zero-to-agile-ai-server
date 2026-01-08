from infrastructure.db.postgres import SessionLocal
from modules.send_message.adapter.output.persistence.send_message_repository_impl import SendMessageRepositoryImpl
from modules.send_message.application.usecase.create_send_message_usecase import CreateSendMessageUseCase
from modules.send_message.application.usecase.get_send_message_usecase import GetSendMessageUseCase
from modules.send_message.application.usecase.update_send_message_usecase import UpdateSendMessageUseCase
from modules.send_message.application.usecase.update_accept_status_usecase import UpdateAcceptStatusUseCase
from modules.send_message.application.usecase.get_accepted_proposals_usecase import GetAcceptedProposalsUseCase

# External Dependencies
from modules.abang_user.adapter.input.web.dependencies import get_abang_user_repository
from modules.house_platform.adapter.input.web.dependencies import get_house_platform_repository
from modules.finder_request.adapter.input.web.dependencies import get_finder_request_repository

# Repository Singleton
_send_message_repo = None

def get_send_message_repository():
    global _send_message_repo
    if _send_message_repo is None:
        _send_message_repo = SendMessageRepositoryImpl(SessionLocal)
    return _send_message_repo

# UseCases
def get_create_send_message_usecase():
    return CreateSendMessageUseCase(
        repository=get_send_message_repository(),
        user_repository=get_abang_user_repository(),
        house_repository=get_house_platform_repository(),
        finder_request_repository=get_finder_request_repository(SessionLocal) 
        # Note: get_finder_request_repository requires db_session_factory, 
        # usually passed by FastAPI Depends(get_db_session). 
        # Here we manually pass SessionLocal for factory construction if needed, 
        # OR we rely on FastAPI Depends injection in the router level if possible.
        # But get_create_send_message_usecase is usually called via Depends, 
        # so we should inject dependencies there too.
    )

# Better approach for dependencies injection in FastAPI:
from fastapi import Depends
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort
from modules.house_platform.application.port.output.house_platform_repository import HousePlatformRepository
from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository

def get_create_send_message_usecase_dep(
    repo=Depends(get_send_message_repository),
    user_repo=Depends(get_abang_user_repository), # This might return the Repo object directly or via Depends
    house_repo=Depends(get_house_platform_repository),
    finder_repo=Depends(get_finder_request_repository)
) -> CreateSendMessageUseCase:
    return CreateSendMessageUseCase(repo, user_repo, house_repo, finder_repo)

def get_get_send_message_usecase_dep(
    repo=Depends(get_send_message_repository)
) -> GetSendMessageUseCase:
    return GetSendMessageUseCase(repo)

def get_update_send_message_usecase_dep(
    repo=Depends(get_send_message_repository)
) -> UpdateSendMessageUseCase:
    return UpdateSendMessageUseCase(repo)

def get_update_accept_status_usecase_dep(
    repo=Depends(get_send_message_repository)
) -> UpdateAcceptStatusUseCase:
    return UpdateAcceptStatusUseCase(repo)

def get_get_accepted_proposals_usecase_dep(
    repo=Depends(get_send_message_repository),
    user_repo=Depends(get_abang_user_repository),
    house_repo=Depends(get_house_platform_repository),
    finder_repo=Depends(get_finder_request_repository)
) -> GetAcceptedProposalsUseCase:
    return GetAcceptedProposalsUseCase(repo, user_repo, house_repo, finder_repo)
