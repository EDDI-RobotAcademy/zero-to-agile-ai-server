from abc import ABC, abstractmethod
from typing import List

from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation


class PriceObservationRepositoryPort(ABC):
    @abstractmethod
    def save_bulk(self, observations: List[PriceFeatureObservation]) -> None:
        """여러 PriceFeatureObservation을 DB에 저장"""

    @abstractmethod
    def save(self, observation: PriceFeatureObservation) -> PriceFeatureObservation:
        """단일 PriceFeatureObservation 저장 및 PK 반환"""
