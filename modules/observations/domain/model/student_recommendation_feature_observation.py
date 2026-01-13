from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation
from modules.observations.domain.value_objects.convenience_observation_features import \
    ConvenienceObservationFeatures
from modules.observations.domain.value_objects.observation_metadata import ObservationMetadata
from modules.observations.domain.value_objects.observation_notes import ObservationNotes

from modules.observations.domain.value_objects.risk_observation_features import RiskObservationFeatures


@dataclass
class StudentRecommendationFeatureObservation:
    id: Optional[int]

    house_platform_id: int
    snapshot_id: str

    위험_관측치: RiskObservationFeatures
    편의_관측치: ConvenienceObservationFeatures

    관측_메모: ObservationNotes
    메타데이터: ObservationMetadata

    calculated_at: Optional[datetime] = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
