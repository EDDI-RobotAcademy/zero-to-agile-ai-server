from __future__ import annotations

from abc import ABC, abstractmethod

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseEmbeddingResult,
)


class GenerateStudentHouseEmbeddingsPort(ABC):
    """student_house 임베딩 생성 인터페이스."""

    @abstractmethod
    async def execute(
        self, batch_size: int, concurrency: int
    ) -> StudentHouseEmbeddingResult:
        """전체 student_house 임베딩을 생성/저장한다."""
        raise NotImplementedError
