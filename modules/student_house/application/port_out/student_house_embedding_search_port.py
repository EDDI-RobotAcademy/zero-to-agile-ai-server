from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence


class StudentHouseEmbeddingSearchPort(ABC):
    """student_house 임베딩 검색 포트."""

    @abstractmethod
    def search_similar(
        self,
        query_vector: Iterable[float],
        candidate_ids: Sequence[int],
        top_n: int = 10,
    ) -> Sequence[tuple[int, float]]:
        """후보군 내 유사도 검색을 수행한다."""
        raise NotImplementedError
