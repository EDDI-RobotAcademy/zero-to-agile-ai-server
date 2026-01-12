from fastapi import Depends

from infrastructure.db.postgres import SessionLocal, get_db_session
from modules.send_message.adapter.output.persistence.send_message_repository_impl import SendMessageRepositoryImpl
from modules.send_message.application.usecase.create_send_message_usecase import CreateSendMessageUseCase
from modules.send_message.application.usecase.get_send_message_usecase import GetSendMessageUseCase
from modules.send_message.application.usecase.update_send_message_usecase import UpdateSendMessageUseCase
from modules.send_message.application.usecase.update_accept_status_usecase import UpdateAcceptStatusUseCase
from modules.send_message.application.usecase.get_accepted_proposals_usecase import GetAcceptedProposalsUseCase

from modules.abang_user.adapter.output.abang_user_repository import (
    AbangUserRepository,
)
from modules.finder_request.adapter.output.repository.finder_request_repository import (
    FinderRequestRepository,
)
from modules.house_platform.infrastructure.repository.house_platform_repository import (
    HousePlatformRepository,
)

# 저장소 싱글톤
_send_message_repo = None

def get_send_message_repository():
    global _send_message_repo
    if _send_message_repo is None:
        _send_message_repo = SendMessageRepositoryImpl(SessionLocal)
    return _send_message_repo

def get_abang_user_repository():
    return AbangUserRepository(SessionLocal)

def get_house_platform_repository():
    return HousePlatformRepository(SessionLocal)

def get_finder_request_repository(
    db_session=Depends(get_db_session),
):
    return FinderRequestRepository(db_session)

# 유스케이스
def get_create_send_message_usecase():
    return CreateSendMessageUseCase(
        repository=get_send_message_repository(),
        user_repository=get_abang_user_repository(),
        house_repository=get_house_platform_repository(),
        finder_request_repository=get_finder_request_repository(
            SessionLocal()
        ),
    )

# FastAPI 의존성 주입용 함수

def get_create_send_message_usecase_dep(
    repo=Depends(get_send_message_repository),
    user_repo=Depends(get_abang_user_repository),
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