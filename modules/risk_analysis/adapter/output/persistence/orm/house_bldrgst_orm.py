"""
ORM model for house_bldrgst table (Risk Analysis Results).

This table stores building analysis results linked to house_platform.
We only use three columns: house_platform_id, address, total_score.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey
from infrastructure.db.postgres import Base


class HouseBldrgstORM(Base):
    """
    ORM model for house_bldrgst table (Risk Analysis Results).

    Stores building analysis results for properties in house_platform table.
    Only maps essential columns for risk analysis storage.
    """
    __tablename__ = "house_bldrgst"

    house_bldrgst_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key for house_bldrgst table"
    )
    house_platform_id = Column(
        BigInteger,
        ForeignKey("house_platform.house_platform_id"),
        nullable=True,
        comment="FK to house_platform table"
    )
    address = Column(
        Text,
        nullable=True,
        comment="Full address from house_platform"
    )
    total_score = Column(
        BigInteger,
        nullable=True,
        comment="Total risk score (0-100)"
    )
