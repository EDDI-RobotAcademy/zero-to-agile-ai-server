from sqlalchemy import Column, Integer, BigInteger, Float, String, DateTime, Text, ARRAY, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class StudentRecommendationFeatureObservationORM(Base):
    __tablename__ = "student_recommendation_feature_observations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 매물 식별
    house_platform_id = Column(BigInteger, primary_key=True, nullable=False)
    snapshot_id = Column(String, nullable=False)

    # 위험 관련
    risk_event_count = Column(Integer, nullable=False)
    risk_event_types = Column(ARRAY(Text), nullable=False)
    risk_probability_est = Column(Float, nullable=False)
    risk_severity_score = Column(Float, nullable=False)
    risk_nonlinear_penalty = Column(Float, nullable=False)

    # 편의 관련
    essential_option_coverage = Column(Float, nullable=False)
    convenience_score = Column(Float, nullable=False)

    # 메모 및 버전
    observation_notes = Column(JSON, nullable=True)
    observation_version = Column(String(20), nullable=False)
    source_data_version = Column(String(20), nullable=False)

    # 생성/계산 시간
    calculated_at = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
