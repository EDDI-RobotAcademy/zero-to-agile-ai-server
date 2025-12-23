from typing import Optional
from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort
from modules.finder_request.application.dto.finder_request_dto import FinderRequestDTO


class GetFinderRequestDetailUseCase:
    """
    임차인의 요구서 상세 조회 유스케이스
    """
    
    def __init__(self, finder_request_repository: FinderRequestRepositoryPort):
        self.finder_request_repository = finder_request_repository
    
    def execute(self, finder_request_id: int) -> Optional[FinderRequestDTO]:
        """
        특정 요구서의 상세 정보를 조회합니다.
        
        Args:
            finder_request_id: 요구서 ID
            
        Returns:
            요구서 상세 정보 또는 None
        """
        # Repository를 통한 조회
        finder_request = self.finder_request_repository.find_by_id(finder_request_id)
        
        # 요구서가 없으면 None 반환
        if not finder_request:
            return None
        
        # 도메인 모델 → DTO 변환
        return FinderRequestDTO(
            finder_request_id=finder_request.finder_request_id,
            abang_user_id=finder_request.abang_user_id,
            status=finder_request.status,
            preferred_region=finder_request.preferred_region,
            price_type=finder_request.price_type,
            max_deposit=finder_request.max_deposit,
            max_rent=finder_request.max_rent,
            house_type=finder_request.house_type,
            additional_condition=finder_request.additional_condition,
            created_at=finder_request.created_at,
            updated_at=finder_request.updated_at
        )
