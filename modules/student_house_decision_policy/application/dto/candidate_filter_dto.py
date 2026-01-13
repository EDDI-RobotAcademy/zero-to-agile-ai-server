from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class FilterCandidateCommand:
    """후보 선별 요청."""

    finder_request_id: int


@dataclass
class FilterCandidateCriteria:
    """후보 선별 기준."""

    max_deposit_limit: int | None
    max_rent_limit: int | None
    budget_margin_ratio: float
    price_type: str | None = None
    preferred_region: str | None = None
    house_type: str | None = None
    additional_condition: str | None = None
    university_name: str | None = None
    is_near: bool = False


@dataclass
class FilterCandidate:
    """필터 조건을 통과한 후보."""

    house_platform_id: int
    snapshot_id: str | None
    deposit: int | None
    monthly_rent: int | None
    manage_cost: int | None


@dataclass
class FilterCandidateResult:
    """후보 선별 결과."""

    finder_request_id: int
    criteria: FilterCandidateCriteria
    candidates: Sequence[FilterCandidate] = field(default_factory=list)
    message: str | None = None


@dataclass
class ObservationPriceFeatures:
    """관측된 가격 관련 지표."""

    house_platform_id: int
    snapshot_id: str
    estimated_move_in_cost: int
    monthly_cost_est: int
    price_percentile: float
    price_zscore: float
    price_burden_nonlinear: float
