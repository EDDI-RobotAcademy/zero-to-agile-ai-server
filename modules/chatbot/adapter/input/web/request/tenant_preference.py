from typing import Dict, Optional
from pydantic import BaseModel, Field

from modules.chatbot.domain.tone import ChatTone


class TenantPreferenceRequest(BaseModel):
    tone: ChatTone = Field(
        default=ChatTone.FORMAL,
        description="답변 말투 (기본: 존댓말)",
    )
    message: str = Field(..., description="사용자 요청 요약")
    preferences: Optional[Dict[str, str]] = Field(
        default=None,
        description="임차인 선호 조건",
    )