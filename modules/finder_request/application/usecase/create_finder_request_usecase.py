from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort
from modules.finder_request.application.dto.finder_request_dto import CreateFinderRequestDTO, FinderRequestDTO
from modules.finder_request.domain.finder_request import FinderRequest


class CreateFinderRequestUseCase:
    """
    임차인의 요구서 생성 유스케이스
    """
    
    def __init__(self, finder_request_repository: FinderRequestRepositoryPort):
        self.finder_request_repository = finder_request_repository
    
    def execute(self, dto: CreateFinderRequestDTO) -> FinderRequestDTO:
        """
        새로운 요구서를 생성합니다.
        
        Args:
            dto: 요구서 생성 정보
            
        Returns:
            생성된 요구서 정보
        """
        # 도메인 모델 생성
        finder_request = FinderRequest(
            abang_user_id=dto.abang_user_id,
            status="Y",  # 기본값: 활성
            finder_request_id=None,
            preferred_region=dto.preferred_region,
            price_type=dto.price_type,
            max_deposit=dto.max_deposit,
            max_rent=dto.max_rent,
            house_type=dto.house_type,
            additional_condition=dto.additional_condition,
            created_at=None,
            updated_at=None
        )
        
        # Repository를 통한 영속화
        created = self.finder_request_repository.create(finder_request)
        
        # 결과를 DTO로 변환하여 반환
        return FinderRequestDTO(
            finder_request_id=created.finder_request_id,
            abang_user_id=created.abang_user_id,
            status=created.status,
            preferred_region=created.preferred_region,
            price_type=created.price_type,
            max_deposit=created.max_deposit,
            max_rent=created.max_rent,
            house_type=created.house_type,
            additional_condition=created.additional_condition,
            created_at=created.created_at,
            updated_at=created.updated_at
        )
