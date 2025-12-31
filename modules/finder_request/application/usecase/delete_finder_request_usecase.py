from modules.finder_request.application.port.finder_request_embedding_port import (
    FinderRequestEmbeddingPort,
)
from modules.finder_request.application.port.finder_request_repository_port import (
    FinderRequestRepositoryPort,
)


class DeleteFinderRequestUseCase:
    """
    임차인의 요구서 삭제 유스케이스 (hard delete - 실제 row 삭제)
    """
    
    def __init__(
        self,
        finder_request_repository: FinderRequestRepositoryPort,
        embedding_repository: FinderRequestEmbeddingPort,
    ):
        self.finder_request_repository = finder_request_repository
        self.embedding_repository = embedding_repository
    
    def execute(self, finder_request_id: int, abang_user_id: int) -> bool:
        """
        요구서를 삭제합니다 (hard delete - 실제 DB row 삭제).
        
        Args:
            finder_request_id: 삭제할 요구서 ID
            abang_user_id: 임차인 사용자 ID (권한 확인용)
            
        Returns:
            삭제 성공 여부
        """
        # 기존 요구서 조회 (권한 확인)
        existing = self.finder_request_repository.find_by_id(finder_request_id)
        
        if not existing:
            return False
        
        # 권한 확인 (본인의 요구서만 삭제 가능)
        if existing.abang_user_id != abang_user_id:
            return False
        
        # FK 제약을 피하기 위해 임베딩 먼저 삭제
        embedding_deleted = self.embedding_repository.delete_embedding(
            finder_request_id
        )
        if not embedding_deleted:
            return False

        # Repository를 통한 삭제
        return self.finder_request_repository.delete(finder_request_id)
