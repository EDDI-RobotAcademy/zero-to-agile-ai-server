from typing import List, Optional
from pydantic import BaseModel, Field


class AiResponse(BaseModel):
    """
    AI 설명 공통 응답 모델
    임차인(Finder)과 임대인(Owner) 모두 이 포맷을 사용
    """
    message: str = Field(
        ...,
        description="AI가 생성한 전체 설명 텍스트 (인사말 + 본문 포함)",
        examples=["안녕하세요! 이 매물은 학교와 도보 5분 거리라 추천해요."]
    )

    key_points: Optional[List[str]] = Field(
        default=None,
        description="핵심 요약 3줄 (리스트 형태)"
    )