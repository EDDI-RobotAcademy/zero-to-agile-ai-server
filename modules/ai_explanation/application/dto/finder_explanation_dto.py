from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# [받을 데이터]
class ExplanationInput(BaseModel):
    # 1. 유저의 기준 (예산, 희망 지역 등)
    budget_monthly_max: Optional[int] = None
    budget_deposit_max: Optional[int] = None
    max_commute_min: Optional[int] = None

    # 2. 매물의 상태 (실제 월세, 실제 거리 등)
    house_monthly_rent: int
    house_deposit: int
    house_distance_min: float


# [줄 데이터]
class ReasonItem(BaseModel):
    code: str
    text: str
    evidence: Dict[str, Any]


class ExplanationResult(BaseModel):
    recommended_reasons: List[ReasonItem] = []  # 추천 이유 리스트
    reject_reasons: List[ReasonItem] = []  # 거절 사유 리스트