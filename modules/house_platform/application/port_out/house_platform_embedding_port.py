from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from modules.house_platform.application.dto.embedding_dto import (
    HousePlatformEmbeddingUpsert,
    HousePlatformSemanticSource,
)


class HousePlatformEmbeddingReadPort(ABC):
    """임베딩 대상 조회 포트."""

    @abstractmethod
    def fetch_all_sources(self) -> Sequence[HousePlatformSemanticSource]:
        """전체 매물 + 옵션 + 관리비 + 기존 설명을 조회한다."""
        raise NotImplementedError


class HousePlatformEmbeddingWritePort(ABC):
    """임베딩 저장 포트."""

    @abstractmethod
    def upsert_embeddings(self, items: Iterable[HousePlatformEmbeddingUpsert]) -> int:
        """임베딩을 업서트하고 저장 건수를 반환한다."""
        raise NotImplementedError
