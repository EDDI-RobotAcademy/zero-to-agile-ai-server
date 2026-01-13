from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func, Boolean
from infrastructure.db.postgres import Base


class FinderRequestModel(Base):
    """
    finder_request 테이블 ORM 모델
    임차인의 매물 요구 조건을 저장
    """
    __tablename__ = "finder_request"

    finder_request_id = Column(BigInteger, primary_key=True, autoincrement=True)
    abang_user_id = Column(Integer, nullable=False)
    preferred_region = Column(String(255), nullable=True)
    price_type = Column(String(20), nullable=True)  # JEONSE, MONTHLY, MIXED
    max_deposit = Column(BigInteger, nullable=True)
    max_rent = Column(BigInteger, nullable=True)
    status = Column(String(1), nullable=False, default="Y")  # Y: 활성, N: 비활성
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    house_type = Column(String, nullable=True)
    additional_condition = Column(String, nullable=True)
    university_name = Column(String(30), nullable=True)
    roomcount = Column(String, nullable=True)
    bathroomcount = Column(String, nullable=True)
    is_near = Column(Boolean, nullable=True, default=False)
    aircon_yn = Column(String(1), nullable=False, default="N")
    washer_yn = Column(String(1), nullable=False, default="N")
    fridge_yn = Column(String(1), nullable=False, default="N")
    max_building_age = Column(Integer, nullable=False, default=5)
