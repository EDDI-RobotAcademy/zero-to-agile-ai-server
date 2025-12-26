from infrastructure.db.postgres import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, func


class HousePlatformEmbeddingORM(Base):
    """house_platform_embedding 테이블 ORM 매핑."""

    __tablename__ = "house_platform_embedding"

    house_platform_embedding_id = Column(
        BigInteger, primary_key=True, index=True, autoincrement=True
    )
    house_platform_id = Column(
        BigInteger,
        ForeignKey("house_platform.house_platform_id"),
        nullable=False,
        index=True,
    )
    semantic_description = Column("semantic_description", Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )
