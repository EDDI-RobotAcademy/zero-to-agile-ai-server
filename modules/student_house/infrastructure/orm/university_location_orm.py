from infrastructure.db.postgres import Base
from sqlalchemy import Column, Float, String


class UniversityLocationORM(Base):
    """대학 위치 정보를 조회하기 위한 테이블 매핑."""

    __tablename__ = "university_location"

    university_name = Column(String(50), primary_key=True)
    campus = Column(String(50), primary_key=True)
    region = Column(String(50), nullable=True)
    road_name_address = Column(String(50), nullable=True)
    jibun_address = Column(String(50), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
