from sqlalchemy import BigInteger, Column, ForeignKey, String

from infrastructure.db.postgres import Base


class HousePlatformOptionORM(Base):
    """옵션 정규화 테이블 ORM 매핑."""

    __tablename__ = "house_platform_options"

    house_platform_options_id = Column(
        "house_platform_options_id", BigInteger, primary_key=True, autoincrement=True
    )
    house_platform_id = Column(
        BigInteger, ForeignKey("house_platform.house_platform_id"), nullable=False
    )
    option = Column("options", String(50), nullable=True)
