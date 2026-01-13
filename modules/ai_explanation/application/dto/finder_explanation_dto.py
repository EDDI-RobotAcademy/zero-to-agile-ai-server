from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ==========================================
# [Input] Request & Observation 구조 매핑
# ==========================================

# User Constraints
class UserConstraintsInput(BaseModel):
    budget_deposit_max: Optional[int] = Field(None, description="최대 보증금")
    budget_monthly_max: Optional[int] = Field(None, description="최대 월세")
    max_commute_min: Optional[int] = Field(None, description="최대 통학 시간")

# 매물 추천 결과 - Price
class ObservationPriceInput(BaseModel):
    monthly_cost_est: float = Field(..., description="월 비용 추정치")
    price_percentile: float = Field(..., description="가격 백분위 (0.0~1.0)")
    price_zscore: Optional[float] = None
    price_burden_nonlinear: Optional[float] = None
    estimated_move_in_cost: Optional[float] = Field(None, description="예상 입주 비용")

# 매물 추천 결과 - Commute
class ObservationCommuteInput(BaseModel):
    distance_to_school_min: float = Field(..., description="학교 통학 시간(분)")
    distance_bucket: Optional[str] = None
    distance_percentile: Optional[float] = None
    distance_nonlinear_score: Optional[float] = None

class ObservationSummaryInput(BaseModel):
    price: ObservationPriceInput
    commute: ObservationCommuteInput
    # risk, options 등은 설명 대상에서 제외되므로 생략 가능 (또는 Dict로 받음)

# UseCase에 전달될 객체
class ExplanationInput(BaseModel):
    user_constraints: UserConstraintsInput
    observation_summary: ObservationSummaryInput

# ==========================================
# [Output] 결과 데이터 (Text & Evidence)
# ==========================================

class ReasonItem(BaseModel):
    code: Optional[str] = None     # Null 허용
    text: str                      # 사용자에게 보여줄 ai 설명 텍스트
    evidence: Dict[str, Any]       # 근거 데이터 (Price, Commute 관련)

class ExplanationResult(BaseModel):
    recommended_reasons: List[ReasonItem] = Field(default_factory=list)
    reject_reasons: List[ReasonItem] = Field(default_factory=list)