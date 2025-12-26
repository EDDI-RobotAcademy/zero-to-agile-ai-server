from __future__ import annotations

from abc import ABC, abstractmethod

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseScoreSource,
)


class HousePlatformReadPort(ABC):
    """house_platform 원본 조회 포트."""

    @abstractmethod
    def get_house_detail(
        self, house_platform_id: int
    ) -> StudentHouseScoreSource | None:
        """house_platform 단건 데이터를 반환한다."""
        raise NotImplementedError
