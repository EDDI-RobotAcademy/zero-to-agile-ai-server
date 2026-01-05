from infrastructure.db.postgres import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, func


class StudentHouseEmbeddingORM(Base):
    """대학생 추천 매물 임베딩 테이블 매핑."""

    __tablename__ = "student_house_embedding"

    student_house_embedding_id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_house_id = Column(
        BigInteger, ForeignKey("student_house.student_house_id"), nullable=False, index=True
    )
    embedding = Column(Vector(1536), nullable=True)
    semantic_description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
