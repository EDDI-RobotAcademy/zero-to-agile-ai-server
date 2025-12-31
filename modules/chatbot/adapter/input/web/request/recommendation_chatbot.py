from typing import List, Optional, Sequence, Union
from pydantic import BaseModel, Field

from modules.chatbot.domain.tone import ChatTone


class RecommendationItem(BaseModel):
    item_id: Union[int, str] = Field(..., description="매물 식별자")
    title: str = Field(..., description="매물 제목")
    address: str | None = Field(default=None, description="주소")
    room_type: str | None = Field(default=None, description="방 형태(원룸/투룸 등)")
    residence_type: str | None = Field(default=None, description="거주 형태(아파트/오피스텔 등)")
    deposit: int | None = Field(default=None, description="보증금")
    monthly_rent: int | None = Field(default=None, description="월세")
    manage_cost: int | None = Field(default=None, description="관리비")
    contract_area: float | None = Field(default=None, description="계약 면적")
    exclusive_area: float | None = Field(default=None, description="전용 면적")
    floor_no: int | None = Field(default=None, description="해당 층수")
    all_floors: int | None = Field(default=None, description="전체 층수")
    can_park: bool | None = Field(default=None, description="주차 가능 여부")
    has_elevator: bool | None = Field(default=None, description="엘리베이터 여부")
    built_in: Sequence[str] | None = Field(default=None, description="빌트인 옵션 목록")
    near_univ: bool | None = Field(default=None, description="대학 인접 여부")
    near_transport: bool | None = Field(default=None, description="대중교통 인접 여부")
    near_mart: bool | None = Field(default=None, description="편의점/마트 인접 여부")
    management_included: Sequence[str] | None = Field(default=None, description="관리비 포함 항목")
    management_excluded: Sequence[str] | None = Field(default=None, description="관리비 제외 항목")
    semantic_description: str | None = Field(default=None, description="매물 요약 설명문")
    reasons: List[str] = Field(default_factory=list, description="추천 이유 목록")


class RecommendationChatbotRequest(BaseModel):
    tone: ChatTone = Field(
        default=ChatTone.FORMAL,
        description="답변 말투 (기본: 존댓말)",
    )
    message: Optional[str] = Field(
        default=None,
        description="추가 조건: null일 경우 빈 문자열로 처리.",
    )
    recommendations: Optional[List[RecommendationItem]] = Field(
        default=None,
        description="추천된 매물 요약",
    )