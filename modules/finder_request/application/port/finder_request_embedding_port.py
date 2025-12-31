from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class FinderRequestEmbeddingPort(ABC):
    """finder_request 임베딩 저장소 포트."""

    @abstractmethod
    def upsert_embedding(
        self, finder_request_id: int, embedding: Iterable[float]
    ) -> None:
        """임베딩을 업서트한다."""
        raise NotImplementedError

    @abstractmethod
    def get_embedding(self, finder_request_id: int) -> list[float] | None:
        """요구서 임베딩을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def delete_embedding(self, finder_request_id: int) -> bool:
        """요구서 임베딩을 삭제한다."""
        raise NotImplementedError
