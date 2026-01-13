from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass(frozen=True)
class PriceFeatureObservation:
    id: Optional[int]

    house_platform_id: int
    recommendation_observation_id: Optional[int]  # 저장 전에는 None 가능

    가격_백분위: Optional[float]  # None 허용
    가격_z점수: Optional[float]  # None 허용
    예상_입주비용: int
    월_비용_추정: int
    가격_부담_비선형: float

    calculated_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self):
        if self.가격_백분위 is not None and not (0.0 <= self.가격_백분위 <= 1.0):
            raise ValueError(f"가격 백분위는 0 이상 1 이하이어야 합니다. 입력값: {self.가격_백분위}")

        # if self.가격_z점수 is not None and not (-10.0 <= self.가격_z점수 <= 10.0):
        #     raise ValueError(f"가격 z점수는 -10~10 사이여야 합니다. 입력값: {self.가격_z점수}")

        if self.예상_입주비용 < 0:
            raise ValueError(f"예상 입주비용은 0 이상이어야 합니다. 입력값: {self.예상_입주비용}")

        if self.월_비용_추정 < 0:
            raise ValueError(f"월 비용 추정은 0 이상이어야 합니다. 입력값: {self.월_비용_추정}")

        if self.가격_부담_비선형 < 0:
            raise ValueError(f"가격 부담 비선형 점수는 0 이상이어야 합니다. 입력값: {self.가격_부담_비선형}")

    @classmethod
    def from_raw(cls, raw: Dict) -> "PriceFeatureObservation":
        return cls(
            id=raw.get("id"),
            house_platform_id=raw["house_platform_id"],
            recommendation_observation_id=raw.get("recommendation_observation_id"),
            가격_백분위=raw.get("price_percentile"),
            가격_z점수=raw.get("price_zscore"),
            예상_입주비용=raw["expected_move_in_cost"],
            월_비용_추정=raw["monthly_cost_estimate"],
            가격_부담_비선형=raw.get("nonlinear_price_burden") or 0.0,
        )
