from __future__ import annotations

from abc import ABC, abstractmethod


class RecommendStudentHousePort(ABC):
    """finder_request 기반 추천 인터페이스."""

    @abstractmethod
    def execute(self, finder_request_id: int) -> dict:
        """추천 결과를 반환한다."""
        raise NotImplementedError
