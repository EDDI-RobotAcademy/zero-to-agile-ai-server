from sqlalchemy import Column, BigInteger, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class StudentRecommendationDistanceObservationORM(Base):
    __tablename__ = "student_recommendation_distance_observations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    recommendation_observation_id = Column(
        BigInteger,
        nullable=False,
        index=True
    )
    university_id = Column(BigInteger, nullable=False)     # FK

    학교까지_분 = Column(Float, nullable=False)
    거리_백분위 = Column(Float, nullable=False)
    거리_버킷 = Column(String(20), nullable=False)
    거리_비선형_점수 = Column(Float, nullable=False)

    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
