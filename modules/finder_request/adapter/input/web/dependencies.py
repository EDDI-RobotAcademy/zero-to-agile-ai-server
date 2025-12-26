from fastapi import Depends
from infrastructure.db.postgres import get_db_session
from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository
from modules.finder_request.application.usecase.create_finder_request_usecase import CreateFinderRequestUseCase
from modules.finder_request.application.usecase.view_finder_requests_usecase import ViewFinderRequestsUseCase
from modules.finder_request.application.usecase.get_finder_request_detail_usecase import GetFinderRequestDetailUseCase
from modules.finder_request.application.usecase.edit_finder_request_usecase import EditFinderRequestUseCase
from modules.finder_request.application.usecase.delete_finder_request_usecase import DeleteFinderRequestUseCase


def get_finder_request_repository(db_session_factory=Depends(get_db_session)):
    """FinderRequest Repository 인스턴스 생성"""
    return FinderRequestRepository(db_session_factory)


def get_create_finder_request_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository)
) -> CreateFinderRequestUseCase:
    """CreateFinderRequest UseCase 인스턴스 생성"""
    return CreateFinderRequestUseCase(repository)


def get_view_finder_requests_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository)
) -> ViewFinderRequestsUseCase:
    """ViewFinderRequests UseCase 인스턴스 생성"""
    return ViewFinderRequestsUseCase(repository)


def get_finder_request_detail_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository)
) -> GetFinderRequestDetailUseCase:
    """GetFinderRequestDetail UseCase 인스턴스 생성"""
    return GetFinderRequestDetailUseCase(repository)


def get_edit_finder_request_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository)
) -> EditFinderRequestUseCase:
    """EditFinderRequest UseCase 인스턴스 생성"""
    return EditFinderRequestUseCase(repository)


def get_delete_finder_request_usecase(
    repository: FinderRequestRepository = Depends(get_finder_request_repository)
) -> DeleteFinderRequestUseCase:
    """DeleteFinderRequest UseCase 인스턴스 생성"""
    return DeleteFinderRequestUseCase(repository)
