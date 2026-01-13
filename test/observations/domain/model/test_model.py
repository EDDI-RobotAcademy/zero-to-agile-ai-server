from datetime import datetime, timezone

from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation
from modules.observations.domain.model.student_recommendation_feature_observation import (
    StudentRecommendationFeatureObservation
)
from modules.observations.domain.value_objects.convenience_observation_features import ConvenienceObservationFeatures
from modules.observations.domain.value_objects.observation_metadata import ObservationMetadata
from modules.observations.domain.value_objects.observation_notes import ObservationNotes

from modules.observations.domain.value_objects.risk_observation_features import RiskObservationFeatures


def test_observation_creation():
    observation = StudentRecommendationFeatureObservation(
        id=None,
        house_platform_id=1,
        snapshot_id="snap-001",

        위험_관측치=RiskObservationFeatures(
            위험_사건_개수=1,
            위험_사건_유형=["flood"],
            위험_확률_추정=0.1,
            위험_심각도_점수=0.6,
            위험_비선형_패널티=0.2
        ),
        편의_관측치=ConvenienceObservationFeatures(
            필수_옵션_커버리지=0.9,
            편의_점수=0.85
        ),
        관측_메모=ObservationNotes.empty(),
        메타데이터=ObservationMetadata(
            관측치_버전="v1",
            원본_데이터_버전="raw-v1"
        ),
        calculated_at=datetime.now(timezone.utc)
    )

    # 검증
    assert observation.house_platform_id == 1
    assert observation.snapshot_id == "snap-001"

    assert observation.위험_관측치.위험_사건_개수 == 1
    assert observation.편의_관측치.편의_점수 == 0.85
    assert observation.메타데이터.관측치_버전 == "v1"
