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
    # ⭐ 활성화 상태 (default = Y)
    status: Literal["Y", "N"] = Field(
        default="Y",
        description="활성화 상태 (Y: 활성, N: 비활성)",
        examples=["Y"]
    )
