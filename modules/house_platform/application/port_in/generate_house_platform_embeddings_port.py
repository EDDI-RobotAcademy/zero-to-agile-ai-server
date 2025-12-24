from __future__ import annotations

from abc import ABC, abstractmethod

from modules.house_platform.application.dto.embedding_dto import (
    HousePlatformEmbeddingResult,
)


class GenerateHousePlatformEmbeddingsPort(ABC):
    """전체 매물 임베딩 생성 유스케이스 인터페이스."""

    @abstractmethod
    async def execute(
        self, batch_size: int, concurrency: int
    ) -> HousePlatformEmbeddingResult:
        """전체 매물 임베딩을 생성/저장한다."""
        raise NotImplementedError
