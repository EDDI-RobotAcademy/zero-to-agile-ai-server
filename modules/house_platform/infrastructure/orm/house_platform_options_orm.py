from sqlalchemy import BigInteger, Boolean, Column, Text
from sqlalchemy.dialects.postgresql import JSONB

from infrastructure.db.postgres import Base


class HousePlatformOptionORM(Base):
    """옵션 정규화 테이블 ORM 매핑."""

    __tablename__ = "house_platform_options"

    house_platform_options_id = Column(
        "house_platform_options_id", BigInteger, primary_key=True, autoincrement=True
    )
    house_platform_id = Column(BigInteger, nullable=False)
    built_in = Column("built_in", Text, nullable=True)
    near_univ = Column("near_univ", Boolean, nullable=True)
    near_transport = Column("near_transport", Boolean, nullable=True)
    near_mart = Column("near_mart", Boolean, nullable=True)
    nearby_pois = Column("nearby_pois", JSONB, nullable=True)
