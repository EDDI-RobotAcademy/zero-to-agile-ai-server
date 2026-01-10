from datetime import datetime, timezone

from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.observations.application.assembler.observation_raw_assembler import ObservationRawAssembler
from modules.observations.application.port.observation_repository_port import ObservationRepositoryPort
from modules.observations.application.usecase.generate_distance_observation_usecase import \
    GenerateDistanceObservationUseCase
from modules.observations.domain.model.student_recommendation_feature_observation import StudentRecommendationFeatureObservation
from modules.observations.domain.value_objects.convenience_observation_features import ConvenienceObservationFeatures
from modules.observations.domain.value_objects.distance_observation_features import DistanceObservationFeatures
from modules.observations.domain.value_objects.observation_metadata import ObservationMetadata
from modules.observations.domain.value_objects.observation_notes import ObservationNotes
from modules.observations.domain.value_objects.price_observation_features import PriceObservationFeatures
from modules.observations.domain.value_objects.risk_observation_features import RiskObservationFeatures


class HouseNotFoundError(Exception):
    def __init__(self, house_id: int):
        super().__init__(f"House with ID {house_id} not found.")


class GenerateStudentRecommendationFeatureObservationUseCase:

    def __init__(
        self,
        observation_repo: ObservationRepositoryPort,
        distance_usecase: GenerateDistanceObservationUseCase,
        house_repo: HousePlatformRepositoryPort,
    ):
        self.observation_repo = observation_repo
        self.distance_usecase = distance_usecase
        self.house_repo = house_repo

    def execute(self, house_id: int) -> StudentRecommendationFeatureObservation:
        bundle = self.house_repo.fetch_bundle_by_id(house_id)
        if not bundle or not bundle.house_platform:
            raise HouseNotFoundError(house_id)

        raw_house = bundle.house_platform

        # ---------- Feature 생성 ----------
        price = PriceObservationFeatures.from_raw(
            ObservationRawAssembler.build_price_raw(raw_house)
        )

        risk = RiskObservationFeatures.from_raw(
            ObservationRawAssembler.build_risk_raw(raw_house)
        )

        convenience = ConvenienceObservationFeatures.from_raw(
            ObservationRawAssembler.build_convenience_raw(bundle.options)
            if bundle.options
            else ObservationRawAssembler.empty_convenience_raw()
        )

        metadata = ObservationMetadata.from_raw(raw_house)

        feature = StudentRecommendationFeatureObservation(
            id=None,
            platform_id=house_id,
            snapshot_id=raw_house.snapshot_id,
            가격_관측치=price,
            위험_관측치=risk,
            편의_관측치=convenience,
            관측_메모=ObservationNotes.empty(),
            메타데이터=metadata,
            calculated_at=datetime.now(timezone.utc),
        )

        # ---------- 저장 & PK 확보 ----------
        saved_feature = self.observation_repo.save(feature)

        # ---------- Distance 생성 ----------
        self.distance_usecase.execute(
            recommendation_observation_id=saved_feature.id,
            house_id=house_id,
        )

        return saved_feature
