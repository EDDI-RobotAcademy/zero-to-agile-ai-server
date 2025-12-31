from __future__ import annotations

from modules.finder_request.domain.finder_request import FinderRequest
from modules.student_house.application.port_in.recommend_student_house_port import (
    RecommendStudentHousePort,
)


class StudentHouseRecommendationAgent:
    """MQ에서 사용할 추천 에이전트."""

    def __init__(self, usecase: RecommendStudentHousePort):
        self.usecase = usecase

    def run(self, finder_request: FinderRequest | None) -> dict:
        """finder_request 기반 추천 결과를 반환한다."""
        if not finder_request:
            return {"request_id": None, "results": []}
        return self.usecase.execute(finder_request.finder_request_id)
