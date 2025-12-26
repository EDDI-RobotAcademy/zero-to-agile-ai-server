from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseEmbeddingUpsert,
    StudentHouseSemanticSource,
)


class StudentHouseEmbeddingReadPort(ABC):
    """임베딩 대상 조회 포트."""

    @abstractmethod
    def fetch_all_sources(self) -> Sequence[StudentHouseSemanticSource]:
        """임베딩에 필요한 조인 데이터를 조회한다."""
        raise NotImplementedError


class StudentHouseEmbeddingWritePort(ABC):
    """임베딩 저장 포트."""

    @abstractmethod
    def upsert_embeddings(self, items: Iterable[StudentHouseEmbeddingUpsert]) -> int:
        """임베딩을 업서트하고 저장 건수를 반환한다."""
        raise NotImplementedError
