from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Sequence

from modules.risk_analysis_mock.application.dto.risk_score_dto import RiskScoreDTO
from modules.student_house.application.dto.student_house_dto import (
    StudentHouseScoreResult,
    StudentHouseScoreSource,
)


@dataclass(frozen=True)
class StudentHouseScoringPolicy:
    """학생 추천 점수 계산 정책.

    환경 변수로 기준/가중치를 조정할 수 있도록 설계했다.
    """

    price_base_rent: float
    price_penalty_per_unit: float
    weight_price: float
    weight_risk: float
    weight_option: float
    weight_base_total: float
    weight_distance: float
    threshold_risk: float
    threshold_price: float
    threshold_base_total: float
    distance_full_score_km: float
    distance_zero_score_km: float
    essential_options: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "StudentHouseScoringPolicy":
        """환경 변수를 기반으로 정책을 생성한다."""
        price_base = _get_float("STUDENT_HOUSE_PRICE_BASE_RENT", 50.0)
        price_penalty = _get_float(
            "STUDENT_HOUSE_PRICE_PENALTY_PER_UNIT", 2.0
        )
        weight_price = _get_float("STUDENT_HOUSE_WEIGHT_PRICE", 0.45)
        weight_risk = _get_float("STUDENT_HOUSE_WEIGHT_RISK", 0.35)
        weight_option = _get_float("STUDENT_HOUSE_WEIGHT_OPTION", 0.2)
        base_weight = _get_float("STUDENT_HOUSE_WEIGHT_BASE_TOTAL", 0.7)
        distance_weight = _get_float("STUDENT_HOUSE_WEIGHT_DISTANCE", 0.3)
        threshold_risk = _get_float("STUDENT_HOUSE_THRESHOLD_RISK", 70.0)
        threshold_price = _get_float("STUDENT_HOUSE_THRESHOLD_PRICE", 60.0)
        threshold_total = _get_float("STUDENT_HOUSE_THRESHOLD_BASE_TOTAL", 70.0)
        distance_full = _get_float(
            "STUDENT_HOUSE_DISTANCE_FULL_SCORE_KM", 0.5
        )
        distance_zero = _get_float(
            "STUDENT_HOUSE_DISTANCE_ZERO_SCORE_KM", 2.0
        )
        essentials = _get_list(
            "STUDENT_HOUSE_ESSENTIAL_OPTIONS", ["에어컨", "냉장고", "세탁기"]
        )

        weight_price, weight_risk, weight_option = _normalize_weights(
            (weight_price, weight_risk, weight_option),
            (0.45, 0.35, 0.2),
        )
        base_weight, distance_weight = _normalize_weights(
            (base_weight, distance_weight),
            (0.7, 0.3),
        )

        return cls(
            price_base_rent=price_base,
            price_penalty_per_unit=price_penalty,
            weight_price=weight_price,
            weight_risk=weight_risk,
            weight_option=weight_option,
            weight_base_total=base_weight,
            weight_distance=distance_weight,
            threshold_risk=threshold_risk,
            threshold_price=threshold_price,
            threshold_base_total=threshold_total,
            distance_full_score_km=distance_full,
            distance_zero_score_km=distance_zero,
            essential_options=tuple(essentials),
        )

    def calculate_scores(
        self, source: StudentHouseScoreSource, risk: RiskScoreDTO
    ) -> StudentHouseScoreResult:
        """스코어를 계산해 결과를 반환한다."""
        price_score = self.calculate_price_score(
            source.monthly_rent, source.manage_cost
        )
        option_score = self.calculate_option_score(source.built_in)
        risk_score = _clamp_score(risk.score)
        base_total = self.calculate_base_total_score(
            price_score, risk_score, option_score
        )
        is_recommended = self.is_recommended(
            price_score, risk_score, base_total
        )

        return StudentHouseScoreResult(
            house_platform_id=source.house_platform_id,
            price_score=price_score,
            option_score=option_score,
            risk_score=risk_score,
            base_total_score=base_total,
            is_student_recommended=is_recommended,
        )

    def calculate_price_score(
        self, monthly_rent: int | None, manage_cost: int | None
    ) -> float:
        """보증금 제외 월 부담 비용 기반 점수를 계산한다."""
        rent = float(monthly_rent or 0)
        manage = float(manage_cost or 0)
        current = rent + manage
        gap = max(0.0, current - self.price_base_rent)
        score = 100.0 - (gap * self.price_penalty_per_unit)
        return _clamp_score(score)

    def calculate_option_score(self, built_in: Sequence[str] | None) -> float:
        """필수 옵션 보유 비율을 점수로 환산한다."""
        essentials = {opt.strip().lower() for opt in self.essential_options if opt}
        if not essentials:
            return 0.0
        if not built_in:
            return 0.0
        normalized = {str(opt).strip().lower() for opt in built_in if opt}
        matched = essentials.intersection(normalized)
        score = (len(matched) / len(essentials)) * 100.0
        return _clamp_score(score)

    def calculate_base_total_score(
        self, price_score: float, risk_score: float, option_score: float
    ) -> float:
        """가격/리스크/옵션의 가중 합을 계산한다."""
        total = (
            price_score * self.weight_price
            + risk_score * self.weight_risk
            + option_score * self.weight_option
        )
        return round(_clamp_score(total), 1)

    def is_recommended(
        self, price_score: float, risk_score: float, base_total_score: float
    ) -> bool:
        """추천 여부를 판정한다."""
        return (
            risk_score >= self.threshold_risk
            and price_score >= self.threshold_price
            and base_total_score >= self.threshold_base_total
        )

    def calculate_distance_score(self, distance_km: float) -> float:
        """대학과의 거리를 점수로 환산한다."""
        if distance_km <= self.distance_full_score_km:
            return 100.0
        if distance_km >= self.distance_zero_score_km:
            return 0.0
        ratio = (distance_km - self.distance_full_score_km) / max(
            self.distance_zero_score_km - self.distance_full_score_km, 0.1
        )
        score = 100.0 - (ratio * 100.0)
        return _clamp_score(score)

    def calculate_total_score(
        self, base_total_score: float, distance_score: float
    ) -> float:
        """기본 점수와 거리 점수를 합쳐 최종 점수를 계산한다."""
        total = (
            base_total_score * self.weight_base_total
            + distance_score * self.weight_distance
        )
        return round(_clamp_score(total), 1)

    @staticmethod
    def calculate_distance_km(
        lat1: float, lng1: float, lat2: float, lng2: float
    ) -> float:
        """위도/경도로 직선 거리를 계산한다."""
        radius_km = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c


def _get_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_list(key: str, default: Sequence[str]) -> list[str]:
    raw = os.getenv(key)
    if not raw:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _normalize_weights(
    weights: Sequence[float], fallback: Sequence[float]
) -> tuple[float, ...]:
    total = sum(weights)
    if total <= 0:
        total = sum(fallback)
        if total <= 0:
            return tuple(0.0 for _ in weights)
        return tuple(value / total for value in fallback)
    return tuple(value / total for value in weights)


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, round(value, 1)))
