from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy.sql import func
from infrastructure.db.postgres import Base


class FinderRequest(Base):
    """
    ORM Entity (Persistence Model)
    - SQLAlchemy가 인식하는 DB 테이블 매핑
    해인님 로직이랑 안 섞이려고 따로 만듦. domain > orm으로 분리
    """
    __tablename__ = "finder_request"

    finder_request_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())