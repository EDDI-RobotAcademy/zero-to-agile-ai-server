from pydantic import BaseModel, Field
from typing import Optional, Literal


class CreateFinderRequestRequest(BaseModel):
    """
    요구서 생성 API 요청 모델
    프론트엔드에서 받는 파라미터
    """
    preferred_region: Optional[str] = Field(None, description="선호 지역", max_length=255)
    # ⭐ 가격 유형 (NULL 허용)
    price_type: Optional[Literal["JEONSE", "MONTHLY", "MIXED", "ETC"]] = Field(None,description="가격 유형 (JEONSE / MONTHLY / MIXED / ETC)")
    max_deposit: Optional[int] = Field(None, description="최대 보증금")
    max_rent: Optional[int] = Field(None, description="최대 월세")
    house_type: Optional[str] = Field(None, description="주거 형태 (예: 원룸, 투룸, 오피스텔 등)")
    additional_condition: Optional[str] = Field(None, description="추가 조건")
    university_name: Optional[str] = Field(None, description="대학교 이름", max_length=30)
    roomcount: Optional[str] = Field(None, description="방 개수")
    bathroomcount: Optional[str] = Field(None, description="욕실 개수")
    is_near: bool = Field(default=False, description="학교 근처 여부")
    aircon_yn: Literal["Y", "N"] = Field(default="N", description="에어컨 여부")
    washer_yn: Literal["Y", "N"] = Field(default="N", description="세탁기 여부")
    fridge_yn: Literal["Y", "N"] = Field(default="N", description="냉장고 여부")
    max_building_age: int = Field(default=5, description="최대 건축 연한")
    # ⭐ 활성화 상태 (default = Y)
    status: Literal["Y", "N"] = Field(default="Y",description="활성화 상태 (Y: 활성, N: 비활성)",examples=["Y"])
