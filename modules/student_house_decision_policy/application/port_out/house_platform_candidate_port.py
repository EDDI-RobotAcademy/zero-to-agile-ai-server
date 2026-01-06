from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidate,
    FilterCandidateCriteria,
)


class HousePlatformCandidateReadPort(ABC):
    """후보 조회 Port."""

    @abstractmethod
    def fetch_candidates(
        self, criteria: FilterCandidateCriteria, limit: int | None = None
    ) -> Sequence[FilterCandidate]:
        """조건에 맞는 후보를 조회한다."""
        raise NotImplementedError
