from sqlalchemy import insert
from sqlalchemy.orm import Session

from modules.observations.application.port.distance_observation_repository_port import DistanceObservationRepositoryPort
from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation


class StudentRecommendationDistanceObservationRepository(DistanceObservationRepositoryPort):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save_bulk(self, house_id: int, distances: list[DistanceFeatureObservation]):
        if not distances:
            return

        # ORM 객체 -> dict 변환
        values = [
            {
                "house_id": house_id,
                "university_id": d.university_id,
                "학교까지_분": d.학교까지_분,
                "거리_백분위": d.거리_백분위,
                "거리_버킷": d.거리_버킷,
                "거리_비선형_점수": d.거리_비선형_점수,
                "calculated_at": d.calculated_at,
            }
            for d in distances
        ]

        stmt = insert(DistanceFeatureObservation).values(values)
        self.db_session.execute(stmt)
        self.db_session.commit()
