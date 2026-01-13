from __future__ import annotations

from dataclasses import dataclass

from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)


@dataclass
class RefreshStudentHouseScoreCommand:
    """스코어 갱신 요청."""

    observation_version: str | None = None
    policy: DecisionPolicyConfig | None = None


@dataclass
class ObservationScoreSource:
    """관측 저장소에서 가져온 원본 지표."""

    house_platform_id: int
    snapshot_id: str | None
    observation_version: str | None
    price_percentile: float | None
    price_zscore: float | None
    price_burden_nonlinear: float | None
    estimated_move_in_cost: int
    monthly_cost_est: int
    essential_option_coverage: float | None
    convenience_score: float | None
    risk_probability_est: float | None
    risk_severity_score: float | None
    risk_nonlinear_penalty: float | None
    distance_to_school_min: float
    distance_percentile: float
    distance_nonlinear_score: float


@dataclass
class StudentHouseScoreRecord:
    """student_house 테이블에 저장할 점수 레코드."""

    house_platform_id: int
    snapshot_id: str
    price_score: float
    option_score: float
    risk_score: float
    distance_score: float
    base_total_score: float
    is_student_recommended: bool
    observation_version: str
    policy_version: str


@dataclass
class StudentHouseScoreQuery:
    """추천 후보 조회 조건."""

    observation_version: str | None
    policy_version: str | None
    threshold_base_total: float
    limit: int


@dataclass
class StudentHouseScoreSummary:
    """추천 후보 요약."""

    house_platform_id: int
    base_total_score: float
    price_score: float
    option_score: float
    risk_score: float
    distance_score: float
    observation_version: str | None
    policy_version: str | None


@dataclass
class RefreshStudentHouseScoreResult:
    """스코어 갱신 결과."""

    observation_version: str
    policy_version: str
    total_observations: int
    processed_count: int
    failed_count: int
