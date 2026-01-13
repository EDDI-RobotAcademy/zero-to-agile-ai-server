from typing import Optional
from pydantic import BaseModel, Field
from modules.ai_explanation.domain.tone import ChatTone


# [1] 임대인 건물 정보
class OwnerHouseData(BaseModel):
    house_platform_id: int = Field(..., description="매물 ID")
    title: str = Field(..., description="매물 이름")
    address: str = Field(..., description="주소")
    sales_type: str = Field(..., description="판매 유형 (예: MONTHLY)")
    residence_type: str = Field(..., description="주거 형태 (예: ONE_ROOM)")
    monthly_rent: int = Field(..., description="월세")
    deposit: int = Field(..., description="보증금")
    room_type: str = Field(..., description="방 종류 (예: OPEN)")
    gu_nm: str = Field(..., description="자치구 명 (예: 관악구)")  # 지역 매칭 로직에 필요
    dong_nm: str = Field(..., description="법정동 명 (예: 신림동)")  # 지역 매칭 로직에 필요


# [2] 세입자 후보 정보
class MatchedFinderRequestData(BaseModel):
    finder_request_id: int
    abang_user_id: int = Field(..., description="세입자 유저 ID")
    price_type: str = Field(..., description="선호 거래 유형 (MONTHLY 등)")
    house_type: str = Field(..., description="선호 주거 형태")
    max_rent: int = Field(..., description="최대 월세 예산")
    preferred_region: str = Field(..., description="선호 지역")


# 최종 요청 Body
class OwnerExplanationRequest(BaseModel):
    tone: ChatTone = Field(default=ChatTone.FORMAL)

    owner_house: OwnerHouseData

    finders: MatchedFinderRequestData