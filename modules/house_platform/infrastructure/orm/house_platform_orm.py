from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

from infrastructure.db.postgres import Base


class HousePlatformORM(Base):
    """house_platform 테이블 ORM 매핑."""

    __tablename__ = "house_platform"

    house_platform_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    deposit = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )
    domain_id = Column(Integer, server_default=text("1"), nullable=True)
    rgst_no = Column(String(50), nullable=True)
    pnu_cd = Column(BigInteger, nullable=True)
    sales_type = Column(String(20), nullable=True)
    monthly_rent = Column(BigInteger, nullable=True)
    room_type = Column(String(20), nullable=True)
    contract_area = Column(Numeric(10, 2), nullable=True)
    exclusive_area = Column(Numeric(10, 2), nullable=True)
    floor_no = Column(Integer, nullable=True)
    all_floors = Column(Integer, nullable=True)
    lat_lng = Column(JSONB, nullable=True)
    manage_cost = Column(BigInteger, nullable=True)
    can_park = Column(Boolean, nullable=True)
    has_elevator = Column(Boolean, nullable=True)
    image_urls = Column(Text, nullable=True)
