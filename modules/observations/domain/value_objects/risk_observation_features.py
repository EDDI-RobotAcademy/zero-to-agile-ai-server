from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass(frozen=True)
class RiskObservationFeatures:
    위험_사건_개수: int
    위험_사건_유형: List[str]
    위험_확률_추정: float
    위험_심각도_점수: float
    위험_비선형_패널티: float

    def __post_init__(self):
        if self.위험_사건_개수 < 0:
            raise ValueError(f"위험 사건 개수는 0 이상이어야 합니다. 입력값: {self.위험_사건_개수}")

        if not all(isinstance(t, str) and t for t in self.위험_사건_유형):
            raise ValueError(f"위험 사건 유형은 비어 있지 않은 문자열 리스트여야 합니다. 입력값: {self.위험_사건_유형}")

        if not (0.0 <= self.위험_확률_추정 <= 1.0):
            raise ValueError(f"위험 확률 추정은 0 이상 1 이하이어야 합니다. 입력값: {self.위험_확률_추정}")

        if self.위험_심각도_점수 < 0:
            raise ValueError(f"위험 심각도 점수는 0 이상이어야 합니다. 입력값: {self.위험_심각도_점수}")

        if self.위험_비선형_패널티 < 0:
            raise ValueError(f"위험 비선형 패널티는 0 이상이어야 합니다. 입력값: {self.위험_비선형_패널티}")

    @classmethod
    def from_raw(cls, raw: Dict) -> "RiskObservationFeatures":
        # 테스트용/미완성 데이터 처리: 없으면 기본값
        return cls(
            위험_사건_개수=raw.get("risk_event_count", 0),
            위험_사건_유형=raw.get("risk_event_types", []),
            위험_확률_추정=raw.get("risk_probability_est", 0.0),
            위험_심각도_점수=raw.get("risk_severity_score", 0.0),
            위험_비선형_패널티=raw.get("risk_nonlinear_penalty", 0.0),
        )
