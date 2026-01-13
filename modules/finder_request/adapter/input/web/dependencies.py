from fastapi import Depends
from infrastructure.db.postgres import get_db_session
from infrastructure.external.embedding_agent import OpenAIEmbeddingAgent
from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository
from modules.finder_request.infrastructure.repository.finder_request_embedding_repository import (
    FinderRequestEmbeddingRepository,
)
from modules.finder_request.application.usecase.create_finder_request_usecase import CreateFinderRequestUseCase
from modules.finder_request.application.usecase.view_finder_requests_usecase import ViewFinderRequestsUseCase
from modules.finder_request.application.usecase.get_finder_request_detail_usecase import GetFinderRequestDetailUseCase
from modules.finder_request.application.usecase.edit_finder_request_usecase import EditFinderRequestUseCase
from modules.finder_request.application.usecase.delete_finder_request_usecase import DeleteFinderRequestUseCase


def get_finder_request_repository(db_session_factory=Depends(get_db_session)):
    """FinderRequest Repository 인스턴스 생성"""
    return FinderRequestRepository(db_session_factory)


def get_finder_request_embedding_repository():
    """FinderRequest 임베딩 저장소 인스턴스 생성"""
    return FinderRequestEmbeddingRepository()


def get_embedding_agent():
    """임베딩 에이전트 인스턴스 생성"""
    return OpenAIEmbeddingAgent()


def get_create_finder_request_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository),
    embedding_repository: FinderRequestEmbeddingRepository = Depends(
        get_finder_request_embedding_repository
    ),
    embedder: OpenAIEmbeddingAgent = Depends(get_embedding_agent),
) -> CreateFinderRequestUseCase:
    """CreateFinderRequest UseCase 인스턴스 생성"""
    return CreateFinderRequestUseCase(repository, embedding_repository, embedder)


def get_view_finder_requests_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository)
) -> ViewFinderRequestsUseCase:
    """ViewFinderRequests UseCase 인스턴스 생성"""
    return ViewFinderRequestsUseCase(repository)


from modules.send_message.adapter.input.web.dependencies import get_send_message_repository
from modules.abang_user.adapter.input.web.dependencies import get_abang_user_repository
from modules.send_message.application.port.output.send_message_repository import SendMessageRepository
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort

def get_finder_request_detail_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository),
    message_repo: SendMessageRepository = Depends(get_send_message_repository),
    user_repo: AbangUserRepositoryPort = Depends(get_abang_user_repository)
) -> GetFinderRequestDetailUseCase:
    """GetFinderRequestDetail UseCase 인스턴스 생성"""
    return GetFinderRequestDetailUseCase(repository, message_repo, user_repo)


def get_edit_finder_request_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository),
    embedding_repository: FinderRequestEmbeddingRepository = Depends(
        get_finder_request_embedding_repository
    ),
    embedder: OpenAIEmbeddingAgent = Depends(get_embedding_agent),
) -> EditFinderRequestUseCase:
    """EditFinderRequest UseCase 인스턴스 생성"""
    return EditFinderRequestUseCase(repository, embedding_repository, embedder)


def get_delete_finder_request_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository),
    embedding_repository: FinderRequestEmbeddingRepository = Depends(
        get_finder_request_embedding_repository
    ),
) -> DeleteFinderRequestUseCase:
    """DeleteFinderRequest UseCase 인스턴스 생성"""
    return DeleteFinderRequestUseCase(repository, embedding_repository)
