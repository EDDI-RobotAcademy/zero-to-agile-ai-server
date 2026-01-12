from sqlalchemy import Column, BigInteger, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class StudentRecommendationPriceObservationsORM(Base):
    __tablename__ = "student_recommendation_price_observations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # FeatureObservation과 연결될 house_id (FK 또는 Reference)
    house_platform_id = Column(BigInteger, nullable=False, index=True)
    recommendation_observation_id = Column(BigInteger, nullable=False, index=True)

    # ---------- Price 관측치 ----------
    가격_백분위 = Column(Float, nullable=False)
    가격_z점수 = Column(Float, nullable=False)
    예상_입주비용 = Column(Integer, nullable=False)
    월_비용_추정 = Column(Integer, nullable=False)
    가격_부담_비선형 = Column(Float, nullable=False)

    # ---------- 계산 시각 ----------
    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
