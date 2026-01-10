from datetime import datetime, timezone
from math import radians, sin, atan2, sqrt, cos
from typing import List
import numpy as np
from modules.observations.application.port.distance_observation_repository_port import DistanceObservationRepositoryPort
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation
from modules.university.application.port.university_repository_port import UniversityRepositoryPort
from modules.observations.domain.value_objects.distance_observation_features import DistanceObservationFeatures


class GenerateDistanceObservationUseCase:

    def __init__(
        self,
        distance_observation_repo: DistanceObservationRepositoryPort,
        raw_house_repo: HousePlatformRepositoryPort,
        university_repo: UniversityRepositoryPort,
    ):
        self.distance_observation_repo = distance_observation_repo
        self.raw_house_repo = raw_house_repo
        self.university_repo = university_repo

    def execute(self, house_id: int):
        bundle = self.raw_house_repo.fetch_bundle_by_id(house_id)
        if not bundle or not bundle.house_platform or not bundle.house_platform.lat_lng:
            raise Exception(f"House {house_id} not found or missing lat_lng")

        raw_house = bundle.house_platform
        universities = self.university_repo.get_university_locations()  # 614개 대학

        # 모든 대학까지 거리 계산
        all_minutes = [self._calc_minutes(raw_house, uni) for uni in universities]

        distances: List[DistanceFeatureObservation] = []
        for university, minutes in zip(universities, all_minutes):
            percentile = self._calc_percentile(minutes, all_minutes)
            bucket = self._calc_bucket(minutes)
            nonlinear_score = self._calc_nonlinear_score(minutes)

            distances.append(
                DistanceFeatureObservation(
                    university_id=university.university_location_id,
                    학교까지_분=minutes,
                    거리_백분위=percentile,
                    거리_버킷=bucket,
                    거리_비선형_점수=nonlinear_score,
                    calculated_at=datetime.now(timezone.utc),
                )
            )

        self.distance_observation_repo.save_bulk(house_id, distances)

    def _calc_minutes(self, house, uni):
        """
        Haversine formula를 사용한 도보 예상 시간 계산
        house.lat_lng와 uni.lat/lng 사용
        """
        lat1, lon1 = house.lat_lng["lat"], house.lat_lng["lng"]
        lat2, lon2 = uni.lat, uni.lng

        R = 6371  # 지구 반지름 km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        km = R * c

        walking_speed_kmh = 5  # km/h
        minutes = (km / walking_speed_kmh) * 60
        return minutes

    def _calc_percentile(self, minutes: float, all_minutes: list) -> float:
        all_minutes = np.array(all_minutes)
        percentile = np.sum(all_minutes <= minutes) / len(all_minutes)
        return percentile  # 0~1 범위

    def _calc_bucket(self, minutes: float) -> str:
        if minutes < 10:
            return "0_10분"
        elif minutes < 20:
            return "10_20분"
        elif minutes < 30:
            return "20_30분"
        elif minutes < 40:
            return "30_40분"
        else:
            return "40분_이상"

    def _calc_nonlinear_score(self, minutes: float) -> float:
        if minutes <= 20:
            return 1 - 0.01 * minutes
        elif minutes <= 30:
            return 0.8 - 0.02 * (minutes - 20)
        elif minutes <= 40:
            return 0.6 - 0.03 * (minutes - 30)
        else:
            return 0.3
