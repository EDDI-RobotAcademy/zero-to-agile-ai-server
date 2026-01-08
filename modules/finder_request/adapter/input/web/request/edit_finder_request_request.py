from pydantic import BaseModel, Field
from typing import Optional, Literal


class EditFinderRequestRequest(BaseModel):
    """
    요구서 수정 API 요청 모델
    """
    finder_request_id: int = Field(..., description="수정할 요구서 ID", gt=0)
    preferred_region: Optional[str] = Field(None, description="선호 지역", max_length=255)
    # ⭐ 가격 유형 (NULL 허용)
    price_type: Optional[Literal["JEONSE", "MONTHLY", "MIXED", "ETC"]] = Field(
        None,
        description="가격 유형 (JEONSE / MONTHLY / MIXED / ETC)"
    )
    max_deposit: Optional[int] = Field(None, description="최대 보증금")
    max_rent: Optional[int] = Field(None, description="최대 월세")
    house_type: Optional[str] = Field(None, description="주거 형태")
    additional_condition: Optional[str] = Field(None, description="추가 조건")
    university_name: Optional[str] = Field(None, description="대학교 이름", max_length=30)
    roomcount: Optional[str] = Field(None, description="방 개수")
    bathroomcount: Optional[str] = Field(None, description="욕실 개수")
    is_near: Optional[bool] = Field(None, description="학교 근처 여부")
    aircon_yn: Optional[Literal["Y", "N"]] = Field(None, description="에어컨 여부")
    washer_yn: Optional[Literal["Y", "N"]] = Field(None, description="세탁기 여부")
    fridge_yn: Optional[Literal["Y", "N"]] = Field(None, description="냉장고 여부")
    max_building_age: Optional[int] = Field(None, description="최대 건축 연한")
    # ⭐ 활성화 상태 (default = Y)
    status: Literal["Y", "N"] = Field(
        default="Y",
        description="활성화 상태 (Y: 활성, N: 비활성)",
        examples=["Y"]
    )
