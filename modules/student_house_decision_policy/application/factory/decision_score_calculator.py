from __future__ import annotations

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    ObservationScoreSource,
    StudentHouseScoreRecord,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)


class DecisionScoreCalculator:
    """관측 지표를 기반으로 점수를 계산한다."""

    def __init__(self, policy: DecisionPolicyConfig):
        self.policy = policy
        self._total_weights = _normalize_weights(
            (
                policy.weight_price,
                policy.weight_risk,
                policy.weight_option,
                policy.weight_distance,
            ),
            fallback=(0.35, 0.3, 0.2, 0.15),
        )
        self._price_weights = _normalize_weights(
            policy.price_feature_weights, fallback=(0.4, 0.3, 0.3)
        )
        self._option_weights = _normalize_weights(
            policy.option_feature_weights, fallback=(0.6, 0.4)
        )
        self._risk_weights = _normalize_weights(
            policy.risk_feature_weights, fallback=(0.4, 0.3, 0.3)
        )
        self._distance_weights = _normalize_weights(
            policy.distance_feature_weights, fallback=(0.4, 0.3, 0.3)
        )

    def calculate(
        self,
        source: ObservationScoreSource,
        observation_version: str,
        policy_version: str,
    ) -> StudentHouseScoreRecord:
        """관측치를 정책 점수로 변환한다."""
        price_score = self._calculate_price_score(source)
        option_score = self._calculate_option_score(source)
        risk_score = self._calculate_risk_score(source)
        distance_score = self._calculate_distance_score(source)

        base_total_score = self._combine_total_score(
            price_score, risk_score, option_score, distance_score
        )
        is_recommended = base_total_score >= self.policy.threshold_base_total

        return StudentHouseScoreRecord(
            house_platform_id=source.house_platform_id,
            snapshot_id=source.snapshot_id,
            price_score=price_score,
            option_score=option_score,
            risk_score=risk_score,
            distance_score=distance_score,
            base_total_score=base_total_score,
            is_student_recommended=is_recommended,
            observation_version=observation_version,
            policy_version=policy_version,
        )

    def _calculate_price_score(
        self, source: ObservationScoreSource
    ) -> float | None:
        """가격 관측치를 점수로 환산한다."""
        # 분포 내 위치(가격 percentile/zscore)는 낮을수록 유리하다.
        percentile_score = (
            (1.0 - _clamp01(source.price_percentile)) * 100.0
            if source.price_percentile is not None
            else None
        )
        zscore_score = (
            _zscore_to_score(
                source.price_zscore,
                self.policy.zscore_min,
                self.policy.zscore_max,
            )
            if source.price_zscore is not None
            else None
        )
        # 체감 가격 부담은 0~1 범위에서 낮을수록 유리하다.
        burden_score = (
            (1.0 - _clamp01(source.price_burden_nonlinear)) * 100.0
            if source.price_burden_nonlinear is not None
            else None
        )

        return _weighted_average(
            (
                (percentile_score, self._price_weights[0]),
                (zscore_score, self._price_weights[1]),
                (burden_score, self._price_weights[2]),
            )
        )

    def _calculate_option_score(
        self, source: ObservationScoreSource
    ) -> float | None:
        """편의/옵션 관측치를 점수로 환산한다."""
        coverage_score = (
            _ratio_to_score(source.essential_option_coverage)
            if source.essential_option_coverage is not None
            else None
        )
        convenience_score = (
            _ratio_to_score(source.convenience_score)
            if source.convenience_score is not None
            else None
        )
        # TODO: convenience_score 범위(0~1, 0~100) 정의가 확정되면 정규화 로직을 고정한다.
        return _weighted_average(
            (
                (coverage_score, self._option_weights[0]),
                (convenience_score, self._option_weights[1]),
            )
        )

    def _calculate_risk_score(
        self, source: ObservationScoreSource
    ) -> float | None:
        """리스크 관측치를 점수로 환산한다."""
        probability_score = (
            (1.0 - _clamp01(source.risk_probability_est)) * 100.0
            if source.risk_probability_est is not None
            else None
        )
        severity_score = (
            (1.0 - _clamp01(source.risk_severity_score)) * 100.0
            if source.risk_severity_score is not None
            else None
        )
        penalty_score = (
            (1.0 - _clamp01(source.risk_nonlinear_penalty)) * 100.0
            if source.risk_nonlinear_penalty is not None
            else None
        )
        # TODO: risk_severity_score가 0~1 스케일인지 확인 후 정규화 방식을 조정한다.
        return _weighted_average(
            (
                (probability_score, self._risk_weights[0]),
                (severity_score, self._risk_weights[1]),
                (penalty_score, self._risk_weights[2]),
            )
        )

    def _calculate_distance_score(
        self, source: ObservationScoreSource
    ) -> float | None:
        """거리 관측치를 점수로 환산한다."""
        time_score = _distance_time_to_score(
            source.distance_to_school_min,
            self.policy.distance_full_score_min,
            self.policy.distance_zero_score_min,
        )
        percentile_score = (
            1.0 - _clamp01(source.distance_percentile)
        ) * 100.0
        nonlinear_score = _ratio_to_score(source.distance_nonlinear_score)

        return _weighted_average(
            (
                (time_score, self._distance_weights[0]),
                (percentile_score, self._distance_weights[1]),
                (nonlinear_score, self._distance_weights[2]),
            )
        )

    def _combine_total_score(
        self,
        price_score: float | None,
        risk_score: float | None,
        option_score: float | None,
        distance_score: float | None,
    ) -> float:
        """누락된 항목은 제외하고 총점을 계산한다."""
        total = _weighted_average(
            (
                (price_score, self._total_weights[0]),
                (risk_score, self._total_weights[1]),
                (option_score, self._total_weights[2]),
                (distance_score, self._total_weights[3]),
            )
        )
        return total or 0.0


def _normalize_weights(
    weights: tuple[float, ...], fallback: tuple[float, ...]
) -> tuple[float, ...]:
    total = sum(weights)
    if total <= 0:
        total = sum(fallback)
        if total <= 0:
            return tuple(0.0 for _ in weights)
        return tuple(value / total for value in fallback)
    return tuple(value / total for value in weights)


def _clamp01(value: float | None) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _ratio_to_score(value: float | None) -> float:
    """0~1 비율 값을 0~100 점수로 변환한다."""
    if value is None:
        return 0.0
    normalized = float(value)
    if normalized > 1.0:
        # TODO: 0~100 스케일로 들어오는 경우를 명확히 구분한다.
        normalized = normalized / 100.0
    return _clamp_score(normalized * 100.0)


def _zscore_to_score(zscore: float, min_z: float, max_z: float) -> float:
    """zscore를 0~100 점수로 변환한다(낮을수록 유리)."""
    if min_z >= max_z:
        return 50.0
    clamped = max(min_z, min(max_z, float(zscore)))
    score = (max_z - clamped) / (max_z - min_z) * 100.0
    # TODO: robust_z 또는 sigmoid 기반 점수 변환으로 개선한다.
    return _clamp_score(score)


def _distance_time_to_score(
    distance_min: float,
    full_score_min: float,
    zero_score_min: float,
) -> float:
    """도보 시간 기반 점수로 변환한다."""
    if distance_min <= full_score_min:
        return 100.0
    if distance_min >= zero_score_min:
        return 0.0
    ratio = (distance_min - full_score_min) / max(
        zero_score_min - full_score_min, 1.0
    )
    return _clamp_score(100.0 - (ratio * 100.0))


def _weighted_average(
    items: tuple[tuple[float | None, float], ...]
) -> float | None:
    """값이 없는 항목은 제외하고 가중 평균을 계산한다."""
    filtered = [(value, weight) for value, weight in items if value is not None]
    if not filtered:
        return None
    total_weight = sum(weight for _, weight in filtered)
    if total_weight <= 0:
        return None
    total = sum(value * weight for value, weight in filtered)
    return _clamp_score(total / total_weight)


def _clamp_score(value: float | None) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(100.0, round(float(value), 1)))
