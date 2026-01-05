from infrastructure.db.postgres import Base
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, String, Text, func


class StudentHouseORM(Base):
    """대학생 추천 스코어를 저장하는 테이블 매핑."""

    __tablename__ = "student_house"

    student_house_id = Column(BigInteger, primary_key=True, autoincrement=True)
    house_platform_id = Column(
        BigInteger, ForeignKey("house_platform.house_platform_id"), unique=True, nullable=False, index=True
    )

    price_score = Column(Float, nullable=False)
    option_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    base_total_score = Column(Float, nullable=False, index=True)
    is_student_recommended = Column(Boolean, default=False, index=True)

    processing_status = Column(String(20), nullable=False, default="READY")
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
