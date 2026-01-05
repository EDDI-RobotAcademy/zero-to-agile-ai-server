from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RiskScore:
    """리스크 점수 도메인 모델"""
    score: int
    factors: Dict[str, Any]
    summary: str


@dataclass
class PriceScore:
    """가격 적정성 점수 도메인 모델"""
    score: int
    comment: str
    metrics: Dict[str, Any]
