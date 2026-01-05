from fastapi import APIRouter

from modules.ai_explaination.adapter.input.web.request.recommendation_chatbot import (
    RecommendationChatbotRequest,
)
from modules.ai_explaination.adapter.input.web.response.recommendation_chatbot import (
    RecommendationChatbotResponse,
)
from modules.ai_explaination.application.usecase.explain_recommendation_usecase import (
    ExplainRecommendationUseCase,
)

router = APIRouter(prefix="/ai_explaination", tags=["ai_explaination"])

@router.post(
    "/recommendation",
    response_model=RecommendationChatbotResponse,
)
def explain_recommendation(
    request: RecommendationChatbotRequest,
) -> RecommendationChatbotResponse:
    usecase = ExplainRecommendationUseCase()
    return usecase.execute(request)