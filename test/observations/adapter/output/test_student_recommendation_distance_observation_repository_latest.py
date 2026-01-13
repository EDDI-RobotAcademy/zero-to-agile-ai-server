from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.observations.adapter.output.repository.student_recommendation_distance_observation_repository_impl import (
    StudentRecommendationDistanceObservationRepository,
)
from modules.observations.infrastructure.orm.student_recommendation_distance_feature_observations_orm import (
    StudentRecommendationDistanceObservationORM,
)


def test_get_bulk_by_house_platform_id_returns_latest_per_university():
    """대학별 최신 관측치만 반환되는지 확인한다."""
    engine = create_engine("sqlite:///:memory:")
    StudentRecommendationDistanceObservationORM.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        rows = [
            StudentRecommendationDistanceObservationORM(
                id=1,
                house_id=1,
                recommendation_observation_id=1,
                university_id=1,
                학교까지_분=12.0,
                거리_백분위=0.2,
                거리_버킷="10_20분",
                거리_비선형_점수=0.8,
                calculated_at=base_time,
            ),
            StudentRecommendationDistanceObservationORM(
                id=2,
                house_id=1,
                recommendation_observation_id=2,
                university_id=1,
                학교까지_분=15.0,
                거리_백분위=0.4,
                거리_버킷="10_20분",
                거리_비선형_점수=0.7,
                calculated_at=base_time + timedelta(minutes=5),
            ),
            StudentRecommendationDistanceObservationORM(
                id=3,
                house_id=1,
                recommendation_observation_id=3,
                university_id=2,
                학교까지_분=25.0,
                거리_백분위=0.6,
                거리_버킷="20_30분",
                거리_비선형_점수=0.5,
                calculated_at=base_time + timedelta(minutes=10),
            ),
            StudentRecommendationDistanceObservationORM(
                id=4,
                house_id=1,
                recommendation_observation_id=4,
                university_id=2,
                학교까지_분=30.0,
                거리_백분위=0.7,
                거리_버킷="30_40분",
                거리_비선형_점수=0.4,
                calculated_at=base_time,
            ),
            StudentRecommendationDistanceObservationORM(
                id=5,
                house_id=2,
                recommendation_observation_id=5,
                university_id=1,
                학교까지_분=40.0,
                거리_백분위=0.9,
                거리_버킷="40분_이상",
                거리_비선형_점수=0.3,
                calculated_at=base_time + timedelta(minutes=20),
            ),
        ]
        session.add_all(rows)
        session.commit()

        repo = StudentRecommendationDistanceObservationRepository(session)
        results = repo.get_bulk_by_house_platform_id(1)

        assert len(results) == 2
        result_map = {item.university_id: item for item in results}
        assert result_map[1].학교까지_분 == 15.0
        assert result_map[2].학교까지_분 == 25.0
    finally:
        session.close()
