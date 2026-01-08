from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FinderRequestResponse(BaseModel):
    """
    요구서 응답 모델
    클라이언트에 반환되는 요구서 정보
    """
    finder_request_id: int = Field(..., description="요구서 ID")
    abang_user_id: int = Field(..., description="임차인 사용자 ID")
    preferred_region: Optional[str] = Field(None, description="선호 지역")
    price_type: Optional[str] = Field(None, description="가격 유형 (JEONSE, MONTHLY, MIXED)")
    max_deposit: Optional[int] = Field(None, description="최대 보증금")
    max_rent: Optional[int] = Field(None, description="최대 월세")
    status: str = Field(..., description="상태 (Y: 활성, N: 비활성)")
    house_type: Optional[str] = Field(None, description="주거 형태")
    additional_condition: Optional[str] = Field(None, description="추가 조건")
    university_name: Optional[str] = Field(None, description="대학교 이름")
    roomcount: Optional[str] = Field(None, description="방 개수")
    bathroomcount: Optional[str] = Field(None, description="욕실 개수")
    is_near: bool = Field(..., description="학교 근처 여부")
    aircon_yn: str = Field(..., description="에어컨 여부 (Y/N)")
    washer_yn: str = Field(..., description="세탁기 여부 (Y/N)")
    fridge_yn: str = Field(..., description="냉장고 여부 (Y/N)")
    max_building_age: int = Field(..., description="최대 건축 연한")
    created_at: Optional[datetime] = Field(None, description="생성 시각")
    updated_at: Optional[datetime] = Field(None, description="수정 시각")
    
    class Config:
        from_attributes = True
