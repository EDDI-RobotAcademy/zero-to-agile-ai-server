from typing import List, Optional, Union
from pydantic import BaseModel, Field

from modules.chatbot.domain.tone import ChatTone


class RecommendationItem(BaseModel):
    item_id: Union[int, str] = Field(..., description="매물 식별자")
    title: str = Field(..., description="매물 제목")
    reasons: List[str] = Field(default_factory=list, description="추천 이유 목록")


class RecommendationChatbotRequest(BaseModel):
    tone: ChatTone = Field(..., description="답변 말투")
    message: str = Field(..., description="사용자 질문 또는 요청")
    recommendations: Optional[List[RecommendationItem]] = Field(
        default=None,
        description="추천된 매물 요약",
    )