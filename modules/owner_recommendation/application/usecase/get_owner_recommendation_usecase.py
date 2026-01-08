from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from modules.owner_recommendation.application.dto.owner_recommendation_dto import (
    HousePlatformSummaryResponse,
    MatchedFinderRequestResponse,
    OwnerRecommendationItemResponse,
    OwnerRecommendationResponse,
    OwnerRecommendationRow,
)
from modules.owner_recommendation.application.port_in.owner_recommendation_port import (
    OwnerRecommendationPort,
)
from modules.owner_recommendation.application.port_out.owner_recommendation_repository_port import (
    OwnerRecommendationRepositoryPort,
)


class GetOwnerRecommendationUseCase(OwnerRecommendationPort):
    """owner 보유 매물 기반 추천 유스케이스."""

    def __init__(self, repository: OwnerRecommendationRepositoryPort):
        self.repository = repository

    def execute(
        self, abang_user_id: int, rent_margin: int = 5
    ) -> OwnerRecommendationResponse:
        rows = self.repository.fetch_recommendations(
            abang_user_id=abang_user_id,
            rent_margin=rent_margin,
        )

        grouped: Dict[int, List[OwnerRecommendationRow]] = defaultdict(list)
        for row in rows:
            grouped[row.house_platform_id].append(row)

        results: List[OwnerRecommendationItemResponse] = []
        total_matched_requests = 0

        for house_platform_id, items in grouped.items():
            first = items[0]
            house = HousePlatformSummaryResponse(
                house_platform_id=house_platform_id,
                title=first.house_title,
                address=first.house_address,
                sales_type=first.house_sales_type,
                residence_type=first.house_residence_type,
                monthly_rent=first.house_monthly_rent,
                deposit=first.house_deposit,
                room_type=first.house_room_type,
                gu_nm=first.house_gu_nm,
                dong_nm=first.house_dong_nm,
            )

            matched_requests = [
                MatchedFinderRequestResponse(
                    finder_request_id=item.finder_request_id,
                    abang_user_id=item.finder_abang_user_id,
                    price_type=item.finder_price_type,
                    house_type=item.finder_house_type,
                    max_rent=item.finder_max_rent,
                    preferred_region=item.finder_preferred_region,
                )
                for item in items
            ]
            total_matched_requests += len(matched_requests)

            results.append(
                OwnerRecommendationItemResponse(
                    house_platform=house,
                    matched_finder_requests=matched_requests,
                )
            )

        return OwnerRecommendationResponse(
            abang_user_id=abang_user_id,
            rent_margin=rent_margin,
            total_recommended_houses=len(results),
            total_matched_requests=total_matched_requests,
            results=results,
        )
