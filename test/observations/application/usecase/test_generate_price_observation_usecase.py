# test/observations/application/usecase/test_generate_price_observation_usecase.py
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from modules.observations.application.usecase.generate_price_observation_usecase import GeneratePriceObservationUseCase
from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation


def test_generate_price_observation_with_mock():
    # 테스트용 데이터 (정수)
    house_prices = {
        1: 1000,
        2: 1100,  # z-score가 0이 안되도록 조정
        3: 1200,
    }
    recommendation_observation_id = 42
    house_id = 2

    # Mock Repository
    mock_repo = MagicMock()
    mock_repo.save = MagicMock(return_value=None)

    # UseCase 생성
    usecase = GeneratePriceObservationUseCase(
        price_repo=mock_repo,
        house_prices=house_prices
    )

    # Execute
    obs = usecase.execute(
        recommendation_observation_id=recommendation_observation_id,
        house_platform_id=house_id
    )

    # Assertions
    mock_repo.save.assert_called_once()

    saved_obs = mock_repo.save.call_args[0][0]
    assert isinstance(saved_obs, PriceFeatureObservation)
    assert saved_obs.recommendation_observation_id == recommendation_observation_id
    assert 0.0 <= saved_obs.가격_백분위 <= 1.0
    assert -10 <= saved_obs.가격_z점수 <= 10  # <- 완화
    assert saved_obs.예상_입주비용 == house_prices[house_id]
    assert saved_obs.월_비용_추정 == int(house_prices[house_id] / 100)
    assert saved_obs.가격_부담_비선형 in [1.0, 0.8, 0.6, 0.3]
    assert isinstance(saved_obs.calculated_at, datetime)
