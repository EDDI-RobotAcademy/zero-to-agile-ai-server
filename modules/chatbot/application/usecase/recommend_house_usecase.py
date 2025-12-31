from typing import List

from modules.chatbot.adapter.input.web.request.recommendation_chatbot import (
    RecommendationItem,
)
from modules.chatbot.adapter.input.web.request.tenant_preference import (
    TenantPreferenceRequest,
)
from modules.chatbot.adapter.input.web.response.recommendation_result import (
    RecommendationResultResponse,
)


class RecommendHouseUseCase:
    def execute(
        self,
        request: TenantPreferenceRequest,
    ) -> RecommendationResultResponse:
        recommendations = self._build_recommendations(request)
        return RecommendationResultResponse(recommendations=recommendations)

    def _build_recommendations(
        self,
        request: TenantPreferenceRequest,
    ) -> List[RecommendationItem]:
        preference_summary = self._format_preferences(request)
        return [
            RecommendationItem(
                item_id="sample-1",
                title="추천 매물",
                reasons=[
                    request.message or "",
                    preference_summary,
                ],
            )
        ]

    def _format_preferences(self, request: TenantPreferenceRequest) -> str:
        if not request.preferences:
            return "선호 조건이 제공되지 않았습니다"

        formatted_pairs = [
            f"{key}: {value}"
            for key, value in request.preferences.items()
        ]
        return ", ".join(formatted_pairs)