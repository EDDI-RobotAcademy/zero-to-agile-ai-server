from typing import List, Optional, Union, Sequence
from pydantic import BaseModel, Field
from modules.ai_explanation.domain.tone import ChatTone
# todo: 요청값 결과에 따라 수정 필요
# 매물 정보 (기존 RecommendationItem 재사용 또는 재정의)
class HouseItem(BaseModel):
    item_id: Union[int, str]
    title: str
    deposit: int
    monthly_rent: int
    # ... 필요한 필드들 ...

class FinderExplanationRequest(BaseModel):
    tone: ChatTone = Field(default=ChatTone.FORMAL, description="어조")
    message: Optional[str] = Field(default=None, description="추가 요청사항")
    recommendations: List[HouseItem] = Field(..., description="추천된 매물 목록")


    class RecommendedHouseItem(BaseModel):
        item_id: Union[int, str] = Field(..., description="매물 ID")
        title: str = Field(..., description="매물 이름")
        deposit: int = Field(..., description="보증금")
        monthly_rent: int = Field(..., description="월세")
        options: List[str] = Field(default=[], description="옵션 목록")
        distance_to_school: Optional[int] = Field(None, description="학교 통학 거리(분)")

    class FinderExplanationRequest(BaseModel):
        tone: ChatTone = Field(default=ChatTone.FORMAL, description="답변 어조")
        message: Optional[str] = Field(default=None, description="추가 요청 사항")

        # 추천된 매물 리스트 (보통 1개 또는 여러 개)
        recommendations: List[RecommendedHouseItem]