from datetime import datetime, timezone
from typing import Dict

import numpy as np

from modules.observations.application.port.price_observation_repository_port import PriceObservationRepositoryPort
from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation


class GeneratePriceObservationUseCase:
    """
    house_platform_id 단위로 PriceFeatureObservation 생성
    - 가격 백분위, z-score, 예상 입주비용, 월 비용 추정, 비선형 가격 부담 계산
    """

    def __init__(self, price_repo: PriceObservationRepositoryPort, house_prices: Dict[int, int]):
        """
        house_prices: dict[house_platform_id -> 가격 데이터]
        """
        self.price_repo = price_repo
        self.house_prices = house_prices

    def execute(self, recommendation_observation_id: int, house_platform_id: int) -> PriceFeatureObservation:
        if house_platform_id not in self.house_prices:
            raise ValueError(f"House {house_platform_id} has no price data")

        price = self.house_prices[house_platform_id]
        all_prices = np.array(list(self.house_prices.values()))

        # ---------- 백분위 & z-score ----------
        price_percentile = float(np.sum(all_prices <= price) / len(all_prices))
        mean = float(np.mean(all_prices))
        std = float(np.std(all_prices))
        price_zscore = float((price - mean) / std) if std > 0 else 0.0
        # TODO: zscore 범위 정책이 확정되면 보정 방식을 조정한다.
        # price_zscore = max(-10.0, min(10.0, price_zscore))

        # ---------- 예상 비용 계산 (예시: deposit + 월세) ----------
        expected_move_in_cost = price  # 예시: deposit = price
        monthly_cost_estimate = int(price / 100)  # 예시: 월비 = price / 100

        # ---------- 비선형 부담 점수 ----------
        if price_zscore <= 0:
            nonlinear_price_burden = 1.0
        elif price_zscore <= 1:
            nonlinear_price_burden = 0.8
        elif price_zscore <= 2:
            nonlinear_price_burden = 0.6
        else:
            nonlinear_price_burden = 0.3

        # ---------- Observation 생성 ----------
        observation = PriceFeatureObservation(
            id=None,
            house_platform_id=house_platform_id,
            recommendation_observation_id=recommendation_observation_id,
            가격_백분위=price_percentile,
            가격_z점수=price_zscore,
            예상_입주비용=expected_move_in_cost,
            월_비용_추정=monthly_cost_estimate,
            가격_부담_비선형=nonlinear_price_burden,
            calculated_at=datetime.now(timezone.utc),
        )

        self.price_repo.save(observation)
        return observation
