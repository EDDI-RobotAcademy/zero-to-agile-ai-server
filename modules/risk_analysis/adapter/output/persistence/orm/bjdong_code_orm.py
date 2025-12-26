"""
ORM model for bjdong_cd_mgm table (Korean legal dong code registry).

This table contains official legal dong codes used to query government APIs
like Building Ledger API and Real Transaction Price API.
"""

from sqlalchemy import Column, String
from infrastructure.db.postgres import Base


class BjdongCodeORM(Base):
    """
    ORM model for bjdong_cd_mgm table (Korean legal dong code registry).

    This table contains official legal dong codes used to query government APIs
    like Building Ledger API and Real Transaction Price API.
    """
    __tablename__ = "bjdong_cd_mgm"

    full_cd = Column(String(10), primary_key=True, comment="10-digit legal dong code")
    sido_nm = Column(String(50), nullable=False, comment="Sido name (e.g., 서울특별시)")
    sigungu_nm = Column(String(50), nullable=False, comment="Sigungu name (e.g., 강남구)")
    bjdong_nm = Column(String(50), nullable=False, comment="Legal dong name (e.g., 역삼동)")
    bjdong_full_nm = Column(String(200), nullable=True, comment="Full address")
    del_yn = Column(String(1), nullable=True, default="0", comment="Used flag: 1=used, 0=unused")
