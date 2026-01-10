from __future__ import annotations

from abc import ABC, abstractmethod

from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseCommand,
    RecommendStudentHouseResult,
)


class RecommendStudentHousePort(ABC):
    """학생 매물 추천 유스케이스 포트."""

    @abstractmethod
    def execute(
        self, command: RecommendStudentHouseCommand
    ) -> RecommendStudentHouseResult | None:
        """추천 결과를 생성한다."""
        raise NotImplementedError
