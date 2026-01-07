"""
건축물대장 정보를 저장하는 ORM 모델
"""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from infrastructure.orm import Base


class HouseBldrgst(Base):
    """
    건축물대장 테이블

    PNU 기반으로 건축물대장 정보를 저장
    """

    __tablename__ = "house_bldrgst"
    __table_args__ = {"sqlite_autoincrement": True}

    # Primary Key
    pnu_id = Column(String(19), primary_key=True, nullable=False, comment="PNU 필지번호 (19자리)")

    # 건축물대장 핵심 필드
    violation_yn = Column(String(1), nullable=True, comment="위반 건축물 여부 (Y/N)")
    main_use_name = Column(String(100), nullable=True, comment="주용도코드명")
    approval_date = Column(String(8), nullable=True, comment="사용승인일 (YYYYMMDD)")
    seismic_yn = Column(String(1), nullable=True, comment="내진 설계 여부 (Y/N)")

    # 메타 정보
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="생성일시")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="수정일시"
    )
