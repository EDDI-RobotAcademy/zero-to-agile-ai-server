from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionPolicyConfig:
    """스코어 정책(가중치/임계값/버전)을 관리한다."""

    weight_price: float = 0.35
    weight_risk: float = 0.3
    weight_option: float = 0.2
    weight_distance: float = 0.15
    threshold_base_total: float = 50.0
    top_k: int = 10
    policy_version: str = "v1"

    price_feature_weights: tuple[float, float, float] = (0.4, 0.3, 0.3)
    option_feature_weights: tuple[float, float] = (0.6, 0.4)
    risk_feature_weights: tuple[float, float, float] = (0.4, 0.3, 0.3)
    distance_feature_weights: tuple[float, float, float] = (0.4, 0.3, 0.3)

    zscore_min: float = -3.0
    zscore_max: float = 3.0
    distance_full_score_min: float = 10.0
    distance_zero_score_min: float = 60.0
