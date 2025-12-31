from __future__ import annotations

from abc import ABC, abstractmethod

from modules.student_house.application.dto.student_house_dto import StudentHouseScoreResult


class CalculateStudentHousePort(ABC):
    """student_house 점수 계산/저장 인터페이스."""

    @abstractmethod
    async def calculate_and_upsert_score(
        self, house_platform_id: int
    ) -> StudentHouseScoreResult | None:
        """house_platform_id 기반으로 점수 계산 후 저장한다."""
        raise NotImplementedError
