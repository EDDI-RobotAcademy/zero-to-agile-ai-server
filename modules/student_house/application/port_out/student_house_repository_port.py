from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidateQuery,
    StudentHouseCandidateRaw,
    StudentHouseScoreResult,
)


class StudentHouseRepositoryPort(ABC):
    """student_house 저장소 인터페이스."""

    @abstractmethod
    def upsert_score(
        self, house_platform_id: int, score: StudentHouseScoreResult
    ) -> int:
        """스코어를 업서트하고 student_house_id를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def mark_failed(self, house_platform_id: int, reason: str) -> None:
        """실패 상태를 기록한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_candidates(
        self, query: StudentHouseCandidateQuery
    ) -> Sequence[StudentHouseCandidateRaw]:
        """추천 후보군 원본 데이터를 조회한다."""
        raise NotImplementedError
