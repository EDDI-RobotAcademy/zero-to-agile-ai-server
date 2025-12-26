from __future__ import annotations

import asyncio
from typing import Sequence

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
from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidatePool,
    StudentHouseDetail,
)
from modules.student_house.application.port_in.recommend_student_house_port import (
    RecommendStudentHousePort,
)
from modules.student_house.application.port_out.student_house_embedding_search_port import (
    StudentHouseEmbeddingSearchPort,
)
from modules.student_house.application.port_out.student_house_search_port import (
    StudentHouseSearchPort,
)


class RecommendStudentHouseUseCase(RecommendStudentHousePort):
    """finder_request 기반 매물 추천 유스케이스."""

    def __init__(
        self,
        finder_request_repo: FinderRequestRepositoryPort,
        finder_request_embedding_repo: FinderRequestEmbeddingPort,
        search_repo: StudentHouseSearchPort,
        vector_repo: StudentHouseEmbeddingSearchPort,
        embedder,
    ):
        self.finder_request_repo = finder_request_repo
        self.finder_request_embedding_repo = finder_request_embedding_repo
        self.search_repo = search_repo
        self.vector_repo = vector_repo
        self.embedder = embedder

    def execute(self, finder_request_id: int) -> dict:
        """finder_request를 기반으로 추천 결과를 반환한다."""
        request = self.finder_request_repo.find_by_id(finder_request_id)
        if not request:
            return {
                "request_id": f"finder_request_{finder_request_id}",
                "query": {},
                "results": [],
            }

        candidates = self._fetch_candidates(request)
        if not candidates:
            return {
                "request_id": f"finder_request_{finder_request_id}",
                "query": self._build_query(request),
                "results": [],
            }

        embedding = self._get_request_embedding(request)
        if not embedding:
            return {
                "request_id": f"finder_request_{finder_request_id}",
                "query": self._build_query(request),
                "results": [],
            }

        candidate_ids = [item.student_house_id for item in candidates]
        hits = self.vector_repo.search_similar(
            embedding, candidate_ids, top_n=10
        )
        if not hits:
            return {
                "request_id": f"finder_request_{finder_request_id}",
                "query": self._build_query(request),
                "results": [],
            }

        details = self.search_repo.fetch_details([hit[0] for hit in hits])
        detail_map = {detail.student_house_id: detail for detail in details}

        results = []
        for rank, (student_house_id, distance) in enumerate(hits, start=1):
            detail = detail_map.get(student_house_id)
            if not detail:
                continue
            results.append(
                self._build_result(rank, distance, detail, request)
            )

        return {
            "request_id": f"finder_request_{finder_request_id}",
            "query": self._build_query(request),
            "results": results,
        }

    def _fetch_candidates(
        self, request: FinderRequest
    ) -> Sequence[StudentHouseCandidatePool]:
        """추천 후보군을 조회한다."""
        return self.search_repo.fetch_candidate_pool(
            preferred_region=request.preferred_region,
            price_type=request.price_type,
            max_deposit=request.max_deposit,
            max_rent=request.max_rent,
            house_type=request.house_type,
            limit=100,
        )

    def _get_request_embedding(self, request: FinderRequest) -> list[float] | None:
        """요구서 임베딩을 조회/생성한다."""
        embedding = self.finder_request_embedding_repo.get_embedding(
            request.finder_request_id
        )
        if embedding:
            return embedding

        text = build_finder_request_embedding_text(request)
        vectors = _run_async(self.embedder.embed_texts([text]))
        if not vectors:
            return None

        embedding = vectors[0]
        self.finder_request_embedding_repo.upsert_embedding(
            request.finder_request_id, embedding
        )
        return embedding

    def _build_result(
        self,
        rank: int,
        distance: float,
        detail: StudentHouseDetail,
        request: FinderRequest,
    ) -> dict:
        """추천 결과 단건을 구성한다."""
        score = max(0.0, round(1.0 - distance, 4))
        return {
            "rank": rank,
            "match": {
                "score": score,
                "score_type": "vector_similarity",
                "vector_distance": round(distance, 4),
            },
            "house": self._build_house(detail),
            "why_recommended": self._build_reasons(detail, request),
            "risk_flags": self._build_risk_flags(detail),
        }

    def _build_house(self, detail: StudentHouseDetail) -> dict:
        """house_platform 정보를 응답 형태로 변환한다."""
        house = _drop_none(
            {
                "house_platform_id": detail.house_platform_id,
                "domain_id": detail.domain_id,
                "rgst_no": detail.rgst_no,
                "title": detail.title,
                "sales_type": detail.sales_type,
                "deposit": detail.deposit,
                "monthly_rent": detail.monthly_rent,
                "manage_cost": detail.manage_cost,
                "room_type": detail.room_type,
                "residence_type": detail.residence_type,
                "contract_area": detail.contract_area,
                "exclusive_area": detail.exclusive_area,
                "floor": detail.floor_no,
                "all_floors": detail.all_floors,
                "address": detail.address,
                "lat_lng": detail.lat_lng,
                "can_park": detail.can_park,
                "has_elevator": detail.has_elevator,
                "image_urls": detail.image_urls,
                "built_in": detail.built_in,
                "near_univ": detail.near_univ,
                "near_transport": detail.near_transport,
                "near_mart": detail.near_mart,
                "management_included": detail.management_included,
                "management_excluded": detail.management_excluded,
                "created_at": detail.created_at,
                "updated_at": detail.updated_at,
            }
        )
        return house

    def _build_reasons(
        self, detail: StudentHouseDetail, request: FinderRequest
    ) -> list[str]:
        """추천 사유를 생성한다."""
        reasons: list[str] = []

        if (
            request.max_deposit is not None
            and detail.deposit is not None
            and detail.deposit <= request.max_deposit
        ):
            reasons.append("보증금 조건을 충족합니다.")
        if (
            request.max_rent is not None
            and detail.monthly_rent is not None
            and detail.monthly_rent <= request.max_rent
        ):
            reasons.append("월세 조건을 충족합니다.")
        additional = request.additional_condition or ""
        if "엘리베이터" in additional and detail.has_elevator:
            reasons.append("엘리베이터 조건을 충족합니다.")
        if "주차" in additional and detail.can_park:
            reasons.append("주차 가능 조건을 충족합니다.")
        if "역세권" in additional and detail.near_transport:
            reasons.append("역세권 조건을 충족합니다.")

        if not reasons:
            reasons.append("추천 점수가 높은 매물입니다.")

        return reasons[:3]

    # todo: 실제 리스크 도메인에서 risk message 를 받아와서 띄워주는 형식이 되어야 함
    def _build_risk_flags(self, detail: StudentHouseDetail) -> list[dict]:
        """리스크 플래그를 생성한다."""
        flags: list[dict] = []
        if detail.manage_cost is None:
            flags.append(
                {
                    "code": "MANAGE_COST_UNKNOWN",
                    "severity": "low",
                    "message": "관리비 정보가 확인되지 않습니다.",
                }
            )
        if not detail.management_included and not detail.management_excluded:
            flags.append(
                {
                    "code": "MANAGE_COST_UNCLEAR",
                    "severity": "low",
                    "message": "관리비 포함/제외 항목 확인이 필요합니다.",
                }
            )
        return flags

    def _build_query(self, request: FinderRequest) -> dict:
        """요청 정보를 응답용으로 정리한다."""
        return _drop_none(
            {
                "preferred_region": request.preferred_region,
                "price_type": request.price_type,
                "max_deposit": request.max_deposit,
                "max_rent": request.max_rent,
                "house_type": request.house_type,
                "additional_condition": request.additional_condition,
            }
        )

def _drop_none(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if value is not None}


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
