from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidate,
    StudentHouseCandidateQuery,
)


class GetStudentHouseCandidatesPort(ABC):
    """추천 후보군 조회 인터페이스."""

    @abstractmethod
    def get_high_score_candidates(
        self, query: StudentHouseCandidateQuery
    ) -> Sequence[StudentHouseCandidate]:
        """후보군을 조회해 반환한다."""
        raise NotImplementedError
