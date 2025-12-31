from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from infrastructure.db.session_helper import open_session
from modules.student_house.application.port_out.student_house_embedding_search_port import (
    StudentHouseEmbeddingSearchPort,
)


class StudentHouseEmbeddingSearchRepository(StudentHouseEmbeddingSearchPort):
    """student_house_embedding 벡터 검색 저장소."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session

    def search_similar(
        self,
        query_vector: Iterable[float],
        candidate_ids: Sequence[int],
        top_n: int = 10,
    ) -> Sequence[tuple[int, float]]:
        """후보군 내에서 유사도를 검색한다."""
        if not candidate_ids:
            return []
        session, generator = open_session(self._session_factory)
        try:
            vec = [float(x) for x in query_vector]
            sql = text(
                """
                SELECT student_house_id,
                       embedding <=> (:vec)::vector AS distance
                FROM student_house_embedding
                WHERE embedding IS NOT NULL
                  AND student_house_id = ANY(:ids)
                ORDER BY distance ASC
                LIMIT :limit
                """
            )
            rows = session.execute(
                sql,
                {"vec": vec, "ids": list(candidate_ids), "limit": top_n},
            ).fetchall()
            return [(int(row[0]), float(row[1])) for row in rows]
        finally:
            if generator:
                generator.close()
            else:
                session.close()
