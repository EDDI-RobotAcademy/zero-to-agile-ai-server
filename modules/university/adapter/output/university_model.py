from sqlalchemy import BigInteger, Column, Float, String
from infrastructure.db.postgres import Base

class UniversityLocation(Base):
    __tablename__ = 'university_location'

    university_location_id = Column(
        BigInteger, primary_key=True, autoincrement=True
    )
    university_name = Column(String(50), nullable=False)
    campus = Column(String(50), nullable=False)
    region = Column(String(50))
    road_name_address = Column(String(50))
    jibun_address = Column(String(50))
    lat = Column(Float)
    lng = Column(Float)
