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

    house_platform_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="매물 PK",
    )
    title = Column(Text, nullable=True, comment="매물 제목")
    address = Column(Text, nullable=True, comment="매물 주소")
    deposit = Column(BigInteger, nullable=True, comment="보증금")
    abang_user_id = Column(
        BigInteger,
        nullable=False,
        server_default=text("-1"),
        comment="등록 사용자 ID",
    )
    created_at = Column(
        DateTime, server_default=func.now(), nullable=True, comment="게시 시각"
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="최종 수정 시각",
    )
    registered_at = Column(DateTime, nullable=True, comment="등록 시각")
    domain_id = Column(
        Integer, server_default=text("1"), nullable=True, comment="도메인 ID"
    )
    rgst_no = Column(String(50), nullable=True, comment="원본 등록 번호")
    snapshot_id = Column(String(64), nullable=True, comment="스냅샷 ID")
    pnu_cd = Column(Text, nullable=True, comment="PNU 코드")
    is_banned = Column(
        Boolean, server_default=text("false"), nullable=True, comment="차단 여부"
    )
    sales_type = Column(String(20), nullable=True, comment="거래 유형")
    monthly_rent = Column(BigInteger, nullable=True, comment="월세")
    room_type = Column(String(20), nullable=True, comment="방 유형")
    residence_type = Column(String(50), nullable=True, comment="주거 유형")
    contract_area = Column(Numeric(10, 2), nullable=True, comment="계약 면적")
    exclusive_area = Column(Numeric(10, 2), nullable=True, comment="전용 면적")
    floor_no = Column(Integer, nullable=True, comment="해당 층")
    all_floors = Column(Integer, nullable=True, comment="총 층수")
    lat_lng = Column(JSONB, nullable=True, comment="위경도")
    manage_cost = Column(BigInteger, nullable=True, comment="관리비(만원)")
    can_park = Column(Boolean, nullable=True, comment="주차 가능")
    has_elevator = Column(Boolean, nullable=True, comment="엘리베이터 여부")
    image_urls = Column(Text, nullable=True, comment="이미지 URL 목록")
    gu_nm = Column(String(10), nullable=True, comment="구 이름")
    dong_nm = Column(String(10), nullable=True, comment="동 이름")
