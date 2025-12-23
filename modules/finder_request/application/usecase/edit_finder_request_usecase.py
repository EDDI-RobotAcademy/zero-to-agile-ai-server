from typing import Optional
from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort
from modules.finder_request.application.dto.finder_request_dto import FinderRequestDTO
from modules.finder_request.domain.finder_request import FinderRequest


class EditFinderRequestUseCase:
    """
    임차인의 요구서 수정 유스케이스
    """
    
    def __init__(self, finder_request_repository: FinderRequestRepositoryPort):
        self.finder_request_repository = finder_request_repository
    
    def execute(
        self,
        finder_request_id: int,
        abang_user_id: int,
        preferred_region: Optional[str] = None,
        price_type: Optional[str] = None,
        max_deposit: Optional[int] = None,
        max_rent: Optional[int] = None,
        house_type: Optional[str] = None,
        additional_condition: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[FinderRequestDTO]:
        """
        요구서를 수정합니다.
        
        Args:
            finder_request_id: 수정할 요구서 ID
            abang_user_id: 임차인 사용자 ID (권한 확인용)
            preferred_region: 선호 지역 (선택)
            price_type: 가격 유형 (선택)
            max_deposit: 최대 보증금 (선택)
            max_rent: 최대 월세 (선택)
            house_type: 주거 형태 (선택)
            additional_condition: 추가 조건 (선택)
            status: 상태 (선택) - Y: 활성, N: 비활성
            
        Returns:
            수정된 요구서 정보 또는 None (존재하지 않거나 권한 없음)
        """
        # 기존 요구서 조회
        existing = self.finder_request_repository.find_by_id(finder_request_id)
        
        if not existing:
            return None
        
        # 권한 확인 (본인의 요구서만 수정 가능)
        if existing.abang_user_id != abang_user_id:
            return None
        
        # 도메인 모델 생성 (수정할 필드만 설정)
        finder_request = FinderRequest(
            finder_request_id=finder_request_id,
            abang_user_id=existing.abang_user_id,
            status=status if status is not None else existing.status,
            preferred_region=preferred_region if preferred_region is not None else existing.preferred_region,
            price_type=price_type if price_type is not None else existing.price_type,
            max_deposit=max_deposit if max_deposit is not None else existing.max_deposit,
            max_rent=max_rent if max_rent is not None else existing.max_rent,
            house_type=house_type if house_type is not None else existing.house_type,
            additional_condition=additional_condition if additional_condition is not None else existing.additional_condition
        )
        
        # Repository를 통한 업데이트
        updated = self.finder_request_repository.update(finder_request)
        
        if not updated:
            return None
        
        # DTO로 변환하여 반환
        return FinderRequestDTO(
            finder_request_id=updated.finder_request_id,
            abang_user_id=updated.abang_user_id,
            status=updated.status,
            preferred_region=updated.preferred_region,
            price_type=updated.price_type,
            max_deposit=updated.max_deposit,
            max_rent=updated.max_rent,
            house_type=updated.house_type,
            additional_condition=updated.additional_condition,
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )
