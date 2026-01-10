from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# [1] 사용자 의뢰 조건 (프론트엔드가 사용자가 입력한 값을 채워서 보냄)
class UserConstraints(BaseModel):
    budget_deposit_max: int = Field(..., description="최대 보증금")
    budget_monthly_max: int = Field(..., description="최대 월세")
    max_commute_min: int = Field(..., description="최대 통학 시간")
    must_have_options: List[str] = Field(default=[], description="필수 옵션")


# [2] 매물 분석 결과 (추천 API의 응답 중 'observation_summary' 부분)
class ObservationSummary(BaseModel):
    # JSON 구조 그대로 딕셔너리로 받음 (구조가 복잡하므로 Dict[str, Any]로 유연하게 처리 추천)
    price: Dict[str, Any]  # 예: {"monthly_cost_est": 60, "price_percentile": 0.22...}
    commute: Dict[str, Any]  # 예: {"distance_to_school_min": 18.2...}
    risk: Dict[str, Any]  # 예: {"risk_probability_est": 0.03...}
    options: Dict[str, Any]  # 예: {"essential_option_coverage": 1.0}


# [3] 매물 기본 정보 (추천 API의 응답 중 'raw' 부분)
class HouseRawData(BaseModel):
    title: str
    deposit: int
    monthly_rent: int
    address: str
    options: List[str] = []


# [Main] 최종 Request Body
class FinderExplanationRequest(BaseModel):
    # 추천/거절 여부 ("RECOMMENDED" or "REJECTED")
    decision_status: str

    # 사용자 조건
    user_constraints: UserConstraints

    # 추천된 매물 데이터
    house_raw: HouseRawData
    house_observation: ObservationSummary