from abc import ABC, abstractmethod
from typing import List

from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation


class DistanceObservationRepositoryPort(ABC):

    @abstractmethod
    def save_bulk(self, house_id: int, distances: List[DistanceFeatureObservation]):
        """매물 단위로 대학별 거리 observation bulk 저장"""
        pass
