from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    StudentHouseScoreQuery,
    StudentHouseScoreRecord,
    StudentHouseScoreSummary,
)


class StudentHouseScorePort(ABC):
    """student_house 점수 저장/조회 포트."""

    @abstractmethod
    def upsert_score(self, score: StudentHouseScoreRecord) -> int:
        """점수 레코드를 업서트한다."""
        raise NotImplementedError

    @abstractmethod
    def mark_failed(self, house_platform_id: int, reason: str) -> None:
        """점수 계산 실패 상태를 기록한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_top_k(
        self, query: StudentHouseScoreQuery
    ) -> Sequence[StudentHouseScoreSummary]:
        """추천 후보 상위 K를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_by_house_platform_ids(
        self,
        house_platform_ids: Sequence[int],
        policy_version: str | None = None,
    ) -> Sequence[StudentHouseScoreSummary]:
        """매물 ID 목록으로 점수 요약을 조회한다."""
        raise NotImplementedError
