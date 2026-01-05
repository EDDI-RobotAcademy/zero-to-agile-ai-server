from typing import List
from pydantic import BaseModel, Field

from modules.ai_explaination.adapter.input.web.request.recommendation_chatbot import (
    RecommendationItem,
)


class RecommendationResultResponse(BaseModel):
    recommendations: List[RecommendationItem] = Field(
        ..., description="추천된 매물 목록"
    )