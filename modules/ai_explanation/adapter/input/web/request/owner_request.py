from typing import Dict, Optional
from pydantic import BaseModel, Field

from modules.ai_explanation.domain.tone import ChatTone

# todo: 요청값 결과에 따라 수정 필요
class OwnerExplanationRequest(BaseModel):
    tone: ChatTone = Field(
        default=ChatTone.FORMAL,
        description="답변 말투 (기본: 존댓말)",
    )
    message: Optional[str] = Field(
        default=None,
        description="추가 조건: null일 경우 빈 문자열로 처리.",
    )
    preferences: Optional[Dict[str, str]] = Field(
        default=None,
        description="임차인 선호 조건",
    )