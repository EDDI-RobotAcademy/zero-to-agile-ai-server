from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.house_platform.application.dto.embedding_dto import (
    EmbedRequest,
    EmbedResult,
)


class EmbeddingPort(ABC):
    """임베딩 모델 호출 인터페이스."""

    @abstractmethod
    def is_dummy(self) -> bool:
        """더미 모드 여부를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    async def embed(self, requests: Sequence[EmbedRequest]) -> Sequence[EmbedResult]:
        """텍스트 목록을 임베딩 벡터로 변환한다."""
        raise NotImplementedError
