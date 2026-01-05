from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from infrastructure.db.session_helper import open_session
from modules.finder_request.application.port.finder_request_embedding_port import (
    FinderRequestEmbeddingPort,
)
from modules.finder_request.infrastructure.orm.finder_request_embedding_orm import (
    FinderRequestEmbeddingORM,
)


class FinderRequestEmbeddingRepository(FinderRequestEmbeddingPort):
    """finder_request 임베딩 저장소 구현체."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session

    def upsert_embedding(
        self, finder_request_id: int, embedding: Iterable[float]
    ) -> None:
        """임베딩 벡터를 업서트한다."""
        session, generator = open_session(self._session_factory)
        try:
            existing = (
                session.query(FinderRequestEmbeddingORM)
                .filter(
                    FinderRequestEmbeddingORM.finder_request_id
                    == finder_request_id
                )
                .one_or_none()
            )
            vector = [float(x) for x in embedding]
            if existing:
                existing.embedding = vector
            else:
                session.add(
                    FinderRequestEmbeddingORM(
                        finder_request_id=finder_request_id,
                        embedding=vector,
                    )
                )
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def get_embedding(self, finder_request_id: int) -> list[float] | None:
        """요구서 임베딩을 조회한다."""
        session, generator = open_session(self._session_factory)
        try:
            row = (
                session.query(FinderRequestEmbeddingORM)
                .filter(
                    FinderRequestEmbeddingORM.finder_request_id
                    == finder_request_id
                )
                .one_or_none()
            )
            if not row or row.embedding is None:
                return None
            return [float(x) for x in row.embedding]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def delete_embedding(self, finder_request_id: int) -> bool:
        """요구서 임베딩을 삭제한다."""
        session, generator = open_session(self._session_factory)
        try:
            row = (
                session.query(FinderRequestEmbeddingORM)
                .filter(
                    FinderRequestEmbeddingORM.finder_request_id
                    == finder_request_id
                )
                .one_or_none()
            )
            if not row:
                return True
            session.delete(row)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            if generator:
                generator.close()
            else:
                session.close()
