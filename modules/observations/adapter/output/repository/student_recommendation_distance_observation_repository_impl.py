from sqlalchemy import insert
from sqlalchemy.orm import Session
from typing import List

from modules.observations.application.port.distance_observation_repository_port import DistanceObservationRepositoryPort
from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation
from modules.observations.infrastructure.orm.student_recommendation_distance_feature_observations_orm import \
    StudentRecommendationDistanceObservationORM


class StudentRecommendationDistanceObservationRepository(DistanceObservationRepositoryPort):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save_bulk(self, distances: list[DistanceFeatureObservation]):
        if not distances:
            return

        # ORM 객체 -> dict 변환
        values = [
            {
                "house_id": d.house_platform_id,
                "recommendation_observation_id": d.recommendation_observation_id,
                "university_id": d.university_id,
                "학교까지_분": d.학교까지_분,
                "거리_백분위": d.거리_백분위,
                "거리_버킷": d.거리_버킷,
                "거리_비선형_점수": d.거리_비선형_점수,
                "calculated_at": d.calculated_at,
            }
            for d in distances
        ]

        stmt = insert(StudentRecommendationDistanceObservationORM).values(values)
        self.db_session.execute(stmt)
        self.db_session.commit()

    def get_bulk_by_house_platform_id(self, house_platform_id: int) -> List[DistanceFeatureObservation]:
        """매물 ID로 거리 관측치 목록 조회"""
        orms = self.db_session.query(StudentRecommendationDistanceObservationORM) \
            .filter(StudentRecommendationDistanceObservationORM.house_id == house_platform_id) \
            .all()

        return [
            DistanceFeatureObservation(
                id=o.id,
                house_platform_id=o.house_id,
                recommendation_observation_id=o.recommendation_observation_id,
                university_id=o.university_id,
                학교까지_분=o.학교까지_분,
                거리_백분위=o.거리_백분위,
                거리_버킷=o.거리_버킷,
                거리_비선형_점수=o.거리_비선형_점수,
                calculated_at=o.calculated_at,
            )
            for o in orms
        ]
