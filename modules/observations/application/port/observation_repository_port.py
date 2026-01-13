from abc import ABC, abstractmethod
from typing import Optional, List
from modules.observations.domain.model.student_recommendation_feature_observation import StudentRecommendationFeatureObservation

class ObservationRepositoryPort(ABC):

    @abstractmethod
    def find_latest_by_house_id(
        self, house_id: int
    ) -> Optional[StudentRecommendationFeatureObservation]:
        pass

    @abstractmethod
    def save(
        self, observation: StudentRecommendationFeatureObservation
    ) -> StudentRecommendationFeatureObservation:
        pass

    @abstractmethod
    def find_history(
        self, house_id: int
    ) -> List[StudentRecommendationFeatureObservation]:
        pass
