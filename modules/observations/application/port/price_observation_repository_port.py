from abc import ABC, abstractmethod
from typing import List, Optional

from modules.observations.domain.model.price_feature_observation import PriceFeatureObservation


class PriceObservationRepositoryPort(ABC):
    @abstractmethod
    def save_bulk(self, observations: List[PriceFeatureObservation]) -> None:
        """여러 PriceFeatureObservation을 DB에 저장"""

    @abstractmethod
    def save(self, observation: PriceFeatureObservation) -> PriceFeatureObservation:
        """단일 PriceFeatureObservation 저장 및 PK 반환"""

    @abstractmethod
    def get_by_house_platform_id(self, house_platform_id: int) -> Optional[PriceFeatureObservation]:
        """매물 ID로 PriceFeatureObservation 조회 (최신)"""
