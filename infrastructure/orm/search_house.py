from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from infrastructure.db.postgres import Base


class SearchHouse(Base):
    """
    ORM Entity (Persistence model)
    - search_house 테이블에 대한 순수 매핑
    - 비즈니스 로직/메서드 넣지 않는다
    """
    __tablename__ = "search_house"

    search_house_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="추천 작업 단위 ID"
    )

    finder_request_id = Column(
        BigInteger,
        ForeignKey("finder_request.finder_request_id"),
        nullable=False,
        comment="유저가 작성한 매물 요청서 ID"
    )

    status = Column(
        String(20),
        nullable=False,
        comment="PENDING / QUEUED / PROCESSING / COMPLETED / FAILED"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    result_json = Column(JSON, nullable=True)
    completed_at = Column(DateTime, nullable=True)