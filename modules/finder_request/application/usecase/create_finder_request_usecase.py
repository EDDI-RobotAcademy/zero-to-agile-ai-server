from __future__ import annotations

import asyncio

from modules.finder_request.application.dto.finder_request_dto import (
    CreateFinderRequestDTO,
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


class CreateFinderRequestUseCase:
    """
    임차인의 요구서 생성 유스케이스
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
            university_name=dto.university_name,
            roomcount=dto.roomcount,
            bathroomcount=dto.bathroomcount,
            is_near=dto.is_near,
            aircon_yn=dto.aircon_yn,
            washer_yn=dto.washer_yn,
            fridge_yn=dto.fridge_yn,
            max_building_age=dto.max_building_age,
            created_at=None,
            updated_at=None
        )
        
        # Repository를 통한 영속화
        created = self.finder_request_repository.create(finder_request)

        # self._upsert_embedding(created)
        
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
            university_name=created.university_name,
            roomcount=created.roomcount,
            bathroomcount=created.bathroomcount,
            is_near=created.is_near,
            aircon_yn=created.aircon_yn,
            washer_yn=created.washer_yn,
            fridge_yn=created.fridge_yn,
            max_building_age=created.max_building_age,
            created_at=created.created_at,
            updated_at=created.updated_at
        )

    # def _upsert_embedding(self, request: FinderRequest) -> None:
    #     """요구서 임베딩을 저장한다."""
    #     if not self.embedding_repository or not self.embedder:
    #         return
    #     text = build_finder_request_embedding_text(request)
    #     embedding = _run_async(self.embedder.embed_texts([text]))
    #     if embedding:
    #         self.embedding_repository.upsert_embedding(
    #             request.finder_request_id, embedding[0]
    #         )


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
