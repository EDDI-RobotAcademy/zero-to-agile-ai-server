from typing import List
from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort
from modules.finder_request.application.dto.finder_request_dto import FinderRequestDTO


class ViewFinderRequestsUseCase:
    """
    임차인의 요구서 목록 조회 유스케이스
    """
    
    def __init__(self, finder_request_repository: FinderRequestRepositoryPort):
        self.finder_request_repository = finder_request_repository
    
    def execute(self, abang_user_id: int) -> List[FinderRequestDTO]:
        """
        특정 사용자의 요구서 목록을 조회합니다.
        
        Args:
            abang_user_id: 임차인 사용자 ID
            
        Returns:
            요구서 목록
        """
        # Repository를 통한 조회
        finder_requests = self.finder_request_repository.find_by_user_id(abang_user_id)
        
        # 도메인 모델 → DTO 변환
        return [
            FinderRequestDTO(
                finder_request_id=req.finder_request_id,
                abang_user_id=req.abang_user_id,
                status=req.status,
                preferred_region=req.preferred_region,
                price_type=req.price_type,
                max_deposit=req.max_deposit,
                max_rent=req.max_rent,
                house_type=req.house_type,
                additional_condition=req.additional_condition,
                created_at=req.created_at,
                updated_at=req.updated_at
            )
            for req in finder_requests
        ]
