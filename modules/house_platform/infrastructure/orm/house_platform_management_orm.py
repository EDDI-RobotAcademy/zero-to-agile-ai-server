from sqlalchemy import BigInteger, Column, DateTime, Text, func

from infrastructure.db.postgres import Base


class HousePlatformManagementORM(Base):
    """관리비 포함/제외 테이블 ORM 매핑."""

    __tablename__ = "house_platform_management"

    house_platform_management_id = Column(
        BigInteger, primary_key=True, autoincrement=True
    )
    house_platform_id = Column(BigInteger, nullable=False)
    management_included = Column(Text, nullable=True)
    management_excluded = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )
