from abc import ABC, abstractmethod
from typing import List

from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation


class DistanceObservationRepositoryPort(ABC):

    @abstractmethod
    def save_bulk(self, distances: List[DistanceFeatureObservation]):
        """매물 단위로 대학별 거리 observation bulk 저장"""
        pass

    @abstractmethod
    def get_bulk_by_house_platform_id(self, house_platform_id: int) -> List[DistanceFeatureObservation]:
        """매물 ID로 거리 관측치 목록 조회"""
        pass
