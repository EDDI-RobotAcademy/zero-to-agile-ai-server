from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidatePool,
    StudentHouseDetail,
)


class StudentHouseSearchPort(ABC):
    """학생 추천 매물 검색 포트."""

    @abstractmethod
    def fetch_candidate_pool(
        self,
        preferred_region: str | None,
        price_type: str | None,
        max_deposit: int | None,
        max_rent: int | None,
        house_type: str | None,
        limit: int = 100,
    ) -> Sequence[StudentHouseCandidatePool]:
        """조건에 맞는 후보군을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_details(
        self, student_house_ids: Sequence[int]
    ) -> Sequence[StudentHouseDetail]:
        """추천 결과 조립용 상세 데이터를 반환한다."""
        raise NotImplementedError
