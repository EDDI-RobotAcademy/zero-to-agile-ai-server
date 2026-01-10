from datetime import datetime, timezone
from math import radians, sin, atan2, sqrt, cos
from typing import List
import numpy as np
from modules.observations.application.port.distance_observation_repository_port import DistanceObservationRepositoryPort
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation
from modules.university.application.port.university_repository_port import UniversityRepositoryPort


class GenerateDistanceObservationUseCase:

    def __init__(
        self,
        distance_repo: DistanceObservationRepositoryPort,
        house_repo: HousePlatformRepositoryPort,
        university_repo: UniversityRepositoryPort,
    ):
        self.distance_repo = distance_repo
        self.house_repo = house_repo
        self.university_repo = university_repo

    def execute(self, recommendation_observation_id: int, house_id: int) -> None:
        bundle = self.house_repo.fetch_bundle_by_id(house_id)
        if not bundle or not bundle.house_platform or not bundle.house_platform.lat_lng:
            raise ValueError(f"House {house_id} missing location")

        house = bundle.house_platform
        universities = self.university_repo.get_university_locations()

        all_minutes = [
            self._calc_minutes(house.lat_lng, uni.lat, uni.lng)
            for uni in universities
        ]

        observations: List[DistanceFeatureObservation] = []

        for uni, minutes in zip(universities, all_minutes):
            observations.append(
                DistanceFeatureObservation(
                    id=None,
                    recommendation_observation_id=recommendation_observation_id,
                    university_id=uni.university_location_id,
                    학교까지_분=minutes,
                    거리_백분위=self._calc_percentile(minutes, all_minutes),
                    거리_버킷=self._calc_bucket(minutes),
                    거리_비선형_점수=self._calc_nonlinear_score(minutes),
                    calculated_at=datetime.now(timezone.utc),
                )
            )

        self.distance_repo.save_bulk(observations)

    # ---------- 계산 로직 ----------
    def _calc_minutes(self, house_latlng, uni_lat, uni_lng) -> float:
        lat1, lon1 = house_latlng["lat"], house_latlng["lng"]
        lat2, lon2 = uni_lat, uni_lng

        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        km = R * c

        return (km / 5) * 60  # 도보 5km/h

    def _calc_percentile(self, minutes: float, all_minutes: list[float]) -> float:
        arr = np.array(all_minutes)
        return float(np.sum(arr <= minutes) / len(arr))

    def _calc_bucket(self, minutes: float) -> str:
        if minutes < 10:
            return "0_10분"

        if minutes < 20:
            return "10_20분"

        if minutes < 30:
            return "20_30분"

        if minutes < 40:
            return "30_40분"

        return "40분_이상"

    def _calc_nonlinear_score(self, minutes: float) -> float:
        if minutes <= 20:
            return max(0.0, 1 - 0.01 * minutes)

        if minutes <= 30:
            return max(0.0, 0.8 - 0.02 * (minutes - 20))

        if minutes <= 40:
            return max(0.0, 0.6 - 0.03 * (minutes - 30))

        return 0.3
