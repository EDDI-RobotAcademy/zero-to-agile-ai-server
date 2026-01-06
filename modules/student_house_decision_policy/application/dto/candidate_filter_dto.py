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


@dataclass
class FilterCandidate:
    """필터 조건을 통과한 후보."""

    house_platform_id: int
    deposit: int
    monthly_rent: int | None
    manage_cost: int | None


@dataclass
class FilterCandidateResult:
    """후보 선별 결과."""

    finder_request_id: int
    criteria: FilterCandidateCriteria
    candidates: Sequence[FilterCandidate] = field(default_factory=list)
    message: str | None = None
