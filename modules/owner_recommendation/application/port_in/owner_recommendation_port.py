from __future__ import annotations

from abc import ABC, abstractmethod

from modules.owner_recommendation.application.dto.owner_recommendation_dto import (
    OwnerRecommendationResponse,
)


class OwnerRecommendationPort(ABC):
    """owner 추천 조회용 입력 포트."""

    @abstractmethod
    def execute(
        self, abang_user_id: int, rent_margin: int = 5
    ) -> OwnerRecommendationResponse:
        raise NotImplementedError
