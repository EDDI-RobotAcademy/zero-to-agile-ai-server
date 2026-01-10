import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from modules.observations.domain.value_objects.convenience_observation_features import \
    ConvenienceObservationFeatures
from modules.observations.domain.value_objects.distance_observation_features import DistanceObservationFeatures
from modules.observations.domain.value_objects.observation_metadata import ObservationMetadata
from modules.observations.domain.value_objects.observation_notes import ObservationNotes
from modules.observations.domain.value_objects.price_observation_features import PriceObservationFeatures
from modules.observations.domain.value_objects.risk_observation_features import RiskObservationFeatures


@dataclass
class StudentRecommendationFeatureObservation:
    id: Optional[int]

    platform_id: int
    snapshot_id: str

    가격_관측치: PriceObservationFeatures
    위험_관측치: RiskObservationFeatures
    편의_관측치: ConvenienceObservationFeatures

    관측_메모: ObservationNotes
    메타데이터: ObservationMetadata

    calculated_at: Optional[datetime] = field(default_factory=datetime.now(timezone.utc))

    # @classmethod
    # def from_db_row(cls, row: dict) -> "StudentRecommendationFeatureObservation":
    #     """DB Row를 기반으로 Observation 생성"""
    #     return cls(
    #         platform_id=row["house_platform_id"],
    #         가격_관측치=PriceObservationFeatures(
    #             가격_백분위=row["percentile"],
    #             가격_z점수=row["zscore"],
    #             예상_입주비용=row["estimated_move_in_cost"],
    #             월_비용_추정=row["monthly_cost_est"],
    #             가격_부담_비선형=row["price_burden_nonlinear"]
    #         ),
    #         거리_관측치=DistanceObservationFeatures(
    #             학교까지_분=row["distance_to_school_min"],
    #             거리_백분위=row["distance_percentile"],
    #             거리_버킷=row["distance_bucket"],
    #             거리_비선형_점수=row["distance_nonlinear_score"]
    #         ),
    #         위험_관측치=RiskObservationFeatures(
    #             위험_사건_개수=row["risk_event_count"],
    #             위험_사건_유형=row["risk_event_types"],
    #             위험_확률_추정=row["risk_probability_est"],
    #             위험_심각도_점수=row["risk_severity_score"],
    #             위험_비선형_패널티=row["risk_nonlinear_penalty"]
    #         ),
    #         편의_관측치=ConvenienceObservationFeatures(
    #             필수_옵션_커버리지=row["essential_option_coverage"],
    #             편의_점수=row["convenience_score"]
    #         ),
    #         관측_메모=ObservationNotes(
    #             notes=row.get("observation_notes")
    #         ),
    #         메타데이터=ObservationMetadata(
    #             관측치_버전=row["observation_version"],
    #             원본_데이터_버전=row["source_data_version"]
    #         ),
    #         calculated_at=row.get("calculated_at")
    #     )
    #
    # def update_가격_관측치(self, 새_가격_관측치: PriceObservationFeatures):
    #     self.가격_관측치 = 새_가격_관측치
    #     self.calculated_at = datetime.now(timezone.utc)
    #
    # def update_거리_관측치(self, 새_거리_관측치: DistanceObservationFeatures):
    #     self.거리_관측치 = 새_거리_관측치
    #     self.calculated_at = datetime.now(timezone.utc)
    #
    # def update_위험_관측치(self, 새_위험_관측치: RiskObservationFeatures):
    #     self.위험_관측치 = 새_위험_관측치
    #     self.calculated_at = datetime.now(timezone.utc)
    #
    # def update_편의_관측치(self, 새_편의_관측치: ConvenienceObservationFeatures):
    #     self.편의_관측치 = 새_편의_관측치
    #     self.calculated_at = datetime.now(timezone.utc)
