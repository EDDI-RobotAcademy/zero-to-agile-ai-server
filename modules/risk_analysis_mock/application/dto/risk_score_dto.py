from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskScoreDTO:
    """리스크 분석 결과 DTO."""

    score: float
    level: str
    reason: str | None = None
