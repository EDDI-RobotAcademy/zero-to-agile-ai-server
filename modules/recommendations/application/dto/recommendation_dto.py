from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class RecommendStudentHouseCommand:
    """학생 매물 추천 요청 커맨드."""

    finder_request_id: int
    candidate_house_platform_ids: list[int]


@dataclass(frozen=True)
class RecommendStudentHouseMockCommand:
    """학생 매물 추천 임시 응답 요청 커맨드."""

    finder_request_id: int
    candidates: list[Any]


@dataclass
class RecommendStudentHouseResult:
    """추천 결과 응답 DTO."""

    finder_request_id: int
    generated_at: str
    status: str  # SUCCESS: 정상 응답, FAILED: 실패 응답
    detail: dict[str, Any] | None  # 실패 상세(활성화 전까지는 None)
    query_context: dict[str, Any]
    summary: dict[str, Any]
    recommended_top_k: list[dict[str, Any]]
    rejected_top_k: list[dict[str, Any]]


@dataclass(frozen=True)
class RecommendStudentHouseMockResponse:
    """추천 실패 시 임시 응답을 만든다."""

    finder_request_id: int
    recommended_top_k: list[dict[str, Any]]
    rejected_top_k: list[dict[str, Any]]
    query_context: dict[str, Any] | None = None

    def to_result(self) -> RecommendStudentHouseResult:
        """임시 응답을 결과 DTO로 변환한다."""
        query_context = self.query_context or {}
        return RecommendStudentHouseResult(
            finder_request_id=self.finder_request_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            status="FAILED",
            detail=None,
            query_context=query_context,
            summary={
                "total_candidates": len(self.recommended_top_k)
                + len(self.rejected_top_k),
                "recommended_count": len(self.recommended_top_k),
                "rejected_count": len(self.rejected_top_k),
                "top_k": len(self.recommended_top_k),
                "rejection_top_k": len(self.rejected_top_k),
            },
            recommended_top_k=self.recommended_top_k,
            rejected_top_k=self.rejected_top_k,
        )
