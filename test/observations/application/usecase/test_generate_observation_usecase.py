import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from modules.observations.application.usecase.generate_student_recommendation_feature_observation_usecase import (
    GenerateStudentRecommendationFeatureObservationUseCase,
    HouseNotFoundError,
)
from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation
from modules.observations.domain.value_objects.convenience_observation_features import ConvenienceObservationFeatures
from modules.observations.domain.value_objects.risk_observation_features import RiskObservationFeatures
from modules.observations.domain.value_objects.observation_metadata import ObservationMetadata
from modules.observations.domain.value_objects.observation_notes import ObservationNotes
from modules.observations.domain.model.student_recommendation_feature_observation import StudentRecommendationFeatureObservation


# --------------------------
# Mock DTOs / Bundle
# --------------------------
class MockHouse:
    def __init__(self):
        self.id = 1
        self.snapshot_id = "snap-123"
        self.deposit = 1000
        self.monthly_rent = 50
        self.manage_cost = 10
        self.is_banned = False
        self.floor_no = 3
        self.all_floors = 5
        self.lat_lng = {"lat": 37.5, "lng": 127.0}
        self.gu_nm = "강남구"
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
            "id": None,
            "house_platform_id": 1,
            "recommendation_observation_id": 123,
            "price_percentile": 0.3,
            "price_zscore": 1.0,
            "expected_move_in_cost": 1000,
            "monthly_cost_estimate": 60,
            "nonlinear_price_burden": 0.5,
        }
    ), patch(
        "modules.observations.application.assembler.observation_raw_assembler.ObservationRawAssembler.build_risk_raw",
        return_value={
            "risk_event_count": 2,
            "risk_event_types": ["fire", "flood"],
            "risk_probability_est": 0.2,
            "risk_severity_score": 0.3,
            "risk_nonlinear_penalty": 0.1,
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
    # Repository / UseCase Mock
    mock_obs_repo = MagicMock()
    mock_distance_usecase = MagicMock()
    mock_house_repo = MagicMock()
    mock_bundle = MockBundle()
    mock_house_repo.fetch_bundle_by_id.return_value = mock_bundle

    # save는 VO 그대로 반환
    mock_obs_repo.save.side_effect = lambda x: x

    use_case = GenerateStudentRecommendationFeatureObservationUseCase(
        observation_repo=mock_obs_repo,
        distance_usecase=mock_distance_usecase,
        house_repo=mock_house_repo,
    )

    observation: StudentRecommendationFeatureObservation = use_case.execute(1)

    # --------------------
    # Assertions
    # --------------------
    # House ID / Snapshot
    assert observation.house_platform_id == mock_bundle.house_platform.id
    assert observation.snapshot_id == mock_bundle.house_platform.snapshot_id

    # Risk VO
    risk_vo = observation.위험_관측치
    assert isinstance(risk_vo, RiskObservationFeatures)
    assert risk_vo.위험_사건_개수 == 2
    assert risk_vo.위험_사건_유형 == ["fire", "flood"]
    assert 0.0 <= risk_vo.위험_확률_추정 <= 1.0

    # Convenience VO
    convenience_vo = observation.편의_관측치
    assert isinstance(convenience_vo, ConvenienceObservationFeatures)
    assert convenience_vo.편의_점수 == 0.0

    # Notes & Metadata
    notes_vo = observation.관측_메모
    metadata_vo = observation.메타데이터
    assert isinstance(notes_vo, ObservationNotes)
    assert isinstance(metadata_vo, ObservationMetadata)
    assert metadata_vo.원본_데이터_버전 == mock_bundle.house_platform.data_version

    # Calculated timestamp
    assert observation.calculated_at <= datetime.now(timezone.utc)

    # Price Feature VO
    price_vo = PriceFeatureObservation.from_raw({
        "id": None,
        "house_platform_id": mock_bundle.house_platform.id,
        "recommendation_observation_id": 123,
        "price_percentile": 0.5,
        "price_zscore": 0.0,
        "expected_move_in_cost": 1000,
        "monthly_cost_estimate": 60,
        "nonlinear_price_burden": 0.5,
    })
    assert isinstance(price_vo, PriceFeatureObservation)
    assert price_vo.가격_백분위 == 0.5


# --------------------------
# 테스트: 집 없으면 예외
# --------------------------
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
