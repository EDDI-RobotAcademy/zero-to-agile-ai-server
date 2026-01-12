import pytest
from dataclasses import dataclass
from datetime import datetime, timezone

from modules.observations.application.usecase.generate_price_observation_usecase import (
    GeneratePriceObservationUseCase,
)
from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation


# ---------- Fake Repository ----------
class FakePriceObservationRepository:
    """UseCase와 동일 시그니처: save 메서드"""
    def __init__(self):
        self.called = False
        self.saved_observation = None

    def save(self, observation: PriceFeatureObservation):
        self.called = True
        self.saved_observation = observation


# ---------- Test ----------
def test_generate_price_observation_usecase():
    # given
    house_prices = {
        101: 500_000,  # house_platform_id -> price
        102: 800_000,
        103: 1_200_000,
    }

    price_repo = FakePriceObservationRepository()
    usecase = GeneratePriceObservationUseCase(price_repo, house_prices)

    recommendation_observation_id = 999
    house_platform_id = 102

    # when
    observation = usecase.execute(
        recommendation_observation_id=recommendation_observation_id,
        house_platform_id=house_platform_id
    )

    # then
    assert price_repo.called is True
    saved = price_repo.saved_observation
    assert saved is not None

    # ---------- FK 필수 값 검증 ----------
    assert saved.recommendation_observation_id == recommendation_observation_id
    assert saved.house_platform_id == house_platform_id
    assert saved.id is None  # 새로 생성된 observation

    # ---------- 계산 값 검증 ----------
    assert 0.0 <= saved.가격_백분위 <= 1.0
    assert -10.0 <= saved.가격_z점수 <= 10.0
    assert saved.예상_입주비용 >= 0
    assert saved.월_비용_추정 >= 0
    assert 0.0 <= saved.가격_부담_비선형 <= 1.0
    assert saved.calculated_at is not None
