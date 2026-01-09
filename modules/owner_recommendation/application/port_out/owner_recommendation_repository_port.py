from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from modules.owner_recommendation.application.dto.owner_recommendation_dto import (
    OwnerRecommendationRow,
)


class OwnerRecommendationRepositoryPort(ABC):
    """owner 추천 조회용 출력 포트."""

    @abstractmethod
    def fetch_recommendations(
        self, abang_user_id: int, rent_margin: int
    ) -> List[OwnerRecommendationRow]:
        raise NotImplementedError
