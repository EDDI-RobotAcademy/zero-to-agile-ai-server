from sqlalchemy import Column, String, Float
from infrastructure.db.postgres import Base

class UniversityLocation(Base):
    __tablename__ = 'university_location'

    university_name = Column(String(50), primary_key=True)
    campus = Column(String(50), primary_key=True)
    region = Column(String(50))
    road_name_address = Column(String(50))
    jibun_address = Column(String(50))
    lat = Column(Float)
    lng = Column(Float)
