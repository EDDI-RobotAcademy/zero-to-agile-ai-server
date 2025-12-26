from infrastructure.db.postgres import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, func


class FinderRequestEmbeddingORM(Base):
    """finder_request_embedding 테이블 ORM 매핑."""

    __tablename__ = "finder_request_embedding"

    finder_request_embedding_id = Column(
        BigInteger, primary_key=True, autoincrement=True
    )
    finder_request_id = Column(
        BigInteger, ForeignKey("finder_request.finder_request_id"), nullable=False
    )
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )
