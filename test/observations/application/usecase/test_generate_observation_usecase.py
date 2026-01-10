import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from modules.observations.application.usecase.generate_student_recommendation_feature_observation_usecase import (
    GenerateStudentRecommendationFeatureObservationUseCase,
    HouseNotFoundError,
)
from modules.observations.domain.model.student_recommendation_feature_observation import StudentRecommendationFeatureObservation
from modules.observations.domain.value_objects.observation_notes import ObservationNotes
from modules.observations.domain.value_objects.distance_observation_features import DistanceObservationFeatures
from modules.observations.domain.value_objects.convenience_observation_features import ConvenienceObservationFeatures
from modules.observations.domain.value_objects.price_observation_features import PriceObservationFeatures
from modules.observations.domain.value_objects.risk_observation_features import RiskObservationFeatures
from modules.observations.domain.value_objects.observation_metadata import ObservationMetadata


# --------------------------
# Mock DTOs / Bundle
# --------------------------
class MockHouse:
    def __init__(self):
        self.deposit = 1000
        self.monthly_rent = 50
        self.manage_cost = 10
        self.is_banned = False
        self.floor_no = 3
        self.all_floors = 5
        self.lat_lng = {"lat": 37.5, "lng": 127.0}
        self.gu_nm = "강남구"
        self.snapshot_id = "snap-123"
        self.data_version = "house_v1"


class MockBundle:
    def __init__(self):
        self.house_platform = MockHouse()
        self.options = None  # 옵션 없으면 empty_convenience_raw 사용


# --------------------------
# Fixtures for ObservationRawAssembler
# --------------------------
@pytest.fixture
def mock_assembler_methods():
    with patch(
        "modules.observations.application.assembler.observation_raw_assembler.ObservationRawAssembler.build_price_raw",
        return_value={
            "price_percentile": 0.3,
            "price_zscore": 1.0,
            "expected_move_in_cost": 1000,
            "monthly_cost_estimate": 60,
            "nonlinear_price_burden": 0.5,
        }
    ), patch(
        "modules.observations.application.assembler.observation_raw_assembler.ObservationRawAssembler.build_risk_raw",
        return_value={
            "risk_event_count": 0,
            "risk_event_types": [],
            "risk_probability_est": 0.0,
            "risk_severity_score": 0.0,
            "risk_nonlinear_penalty": 0.0,
        }
    ), patch(
        "modules.observations.application.assembler.observation_raw_assembler.ObservationRawAssembler.empty_convenience_raw",
        return_value={
            "essential_option_coverage": 0.0,
            "convenience_score": 0.0,
        }
    ):
        yield


# --------------------------
# 테스트: 정상 흐름
# --------------------------
def test_execute_generates_observation(mock_assembler_methods):
    mock_obs_repo = MagicMock()
    mock_distance_usecase = MagicMock()
    mock_house_repo = MagicMock()
    mock_bundle = MockBundle()
    mock_house_repo.fetch_bundle_by_id.return_value = mock_bundle

    # save는 실제 VO 반환
    mock_obs_repo.save.side_effect = lambda x: x

    use_case = GenerateStudentRecommendationFeatureObservationUseCase(
        observation_repo=mock_obs_repo,
        distance_usecase=mock_distance_usecase,
        house_repo=mock_house_repo
    )

    observation = use_case.execute(1)

    # --------------------------
    # repo, house 호출 검증
    # --------------------------
    mock_house_repo.fetch_bundle_by_id.assert_called_once_with(1)
    mock_obs_repo.save.assert_called_once()
    mock_distance_usecase.execute.assert_called_once_with(
        recommendation_observation_id=observation.id,
        house_id=1
    )

    # --------------------------
    # VO 타입 검증
    # --------------------------
    assert isinstance(observation, StudentRecommendationFeatureObservation)

    # 기존
    assert isinstance(observation.가격_관측치, PriceObservationFeatures)
    assert observation.가격_관측치.가격_백분위 == 0.3

    # 수정
    assert isinstance(observation.가격_관측치, PriceObservationFeatures)
    assert observation.가격_관측치.가격_백분위 == 0.3
    assert observation.가격_관측치.가격_z점수 == 1.0
    assert observation.가격_관측치.월_비용_추정 == 60
    assert observation.가격_관측치.예상_입주비용 == 1000

    # 편의
    assert isinstance(observation.편의_관측치, ConvenienceObservationFeatures)
    assert observation.편의_관측치.필수_옵션_커버리지 == 0.0
    assert observation.편의_관측치.편의_점수 == 0.0

    # 위험
    assert isinstance(observation.위험_관측치, RiskObservationFeatures)

    # 메타데이터 & 관측 메모
    assert isinstance(observation.메타데이터, ObservationMetadata)
    assert isinstance(observation.관측_메모, ObservationNotes)


# 테스트: 집 없으면 예외
def test_execute_house_not_found_raises_error():
    mock_obs_repo = MagicMock()
    mock_distance_usecase = MagicMock()
    mock_house_repo = MagicMock()
    mock_house_repo.fetch_bundle_by_id.return_value = None

    use_case = GenerateStudentRecommendationFeatureObservationUseCase(
        observation_repo=mock_obs_repo,
        distance_usecase=mock_distance_usecase,
        house_repo=mock_house_repo
    )

    with pytest.raises(HouseNotFoundError):
        use_case.execute(999)
