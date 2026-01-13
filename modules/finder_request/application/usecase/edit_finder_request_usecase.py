from __future__ import annotations

import asyncio
from typing import Optional

from modules.finder_request.application.dto.finder_request_dto import (
    FinderRequestDTO,
)
from modules.finder_request.application.factory.finder_request_embedding_factory import (
    build_finder_request_embedding_text,
)
from modules.finder_request.application.port.finder_request_embedding_port import (
    FinderRequestEmbeddingPort,
)
from modules.finder_request.application.port.finder_request_repository_port import (
    FinderRequestRepositoryPort,
)
from modules.finder_request.domain.finder_request import FinderRequest


class EditFinderRequestUseCase:
    """
    임차인의 요구서 수정 유스케이스
    """
    
    def __init__(
        self,
        finder_request_repository: FinderRequestRepositoryPort,
        embedding_repository: FinderRequestEmbeddingPort | None = None,
        embedder=None,
    ):
        self.finder_request_repository = finder_request_repository
        self.embedding_repository = embedding_repository
        self.embedder = embedder
    
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
        university_name: Optional[str] = None,
        roomcount: Optional[str] = None,
        bathroomcount: Optional[str] = None,
        is_near: Optional[bool] = None,
        aircon_yn: Optional[str] = None,
        washer_yn: Optional[str] = None,
        fridge_yn: Optional[str] = None,
        max_building_age: Optional[int] = None,
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
            university_name: 대학교 이름 (선택)
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
            additional_condition=additional_condition if additional_condition is not None else existing.additional_condition,
            university_name=university_name if university_name is not None else existing.university_name,
            roomcount=roomcount if roomcount is not None else existing.roomcount,
            bathroomcount=bathroomcount if bathroomcount is not None else existing.bathroomcount,
            is_near=is_near if is_near is not None else existing.is_near,
            aircon_yn=aircon_yn if aircon_yn is not None else existing.aircon_yn,
            washer_yn=washer_yn if washer_yn is not None else existing.washer_yn,
            fridge_yn=fridge_yn if fridge_yn is not None else existing.fridge_yn,
            max_building_age=max_building_age if max_building_age is not None else existing.max_building_age
        )
        
        # Repository를 통한 업데이트
        updated = self.finder_request_repository.update(finder_request)
        
        if not updated:
            return None

        self._upsert_embedding(updated)
        
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
            university_name=updated.university_name,
            roomcount=updated.roomcount,
            bathroomcount=updated.bathroomcount,
            is_near=updated.is_near,
            aircon_yn=updated.aircon_yn,
            washer_yn=updated.washer_yn,
            fridge_yn=updated.fridge_yn,
            max_building_age=updated.max_building_age,
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )

    def _upsert_embedding(self, request: FinderRequest) -> None:
        """요구서 임베딩을 저장한다."""
        if not self.embedding_repository or not self.embedder:
            return
        text = build_finder_request_embedding_text(request)
        embedding = _run_async(self.embedder.embed_texts([text]))
        if embedding:
            self.embedding_repository.upsert_embedding(
                request.finder_request_id, embedding[0]
            )


def _run_async(coro):
    """동기 컨텍스트에서 코루틴을 실행한다."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    return asyncio.run(coro)
