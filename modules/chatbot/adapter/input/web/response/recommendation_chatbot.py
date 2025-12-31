from pydantic import BaseModel, Field


class RecommendationChatbotResponse(BaseModel):
    message: str = Field(..., description="챗봇 답변")