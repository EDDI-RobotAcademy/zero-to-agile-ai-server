from __future__ import annotations

from abc import ABC, abstractmethod

from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCommand,
    FilterCandidateResult,
)


class FilterCandidatePort(ABC):
    """후보 선별 입력 포트."""

    @abstractmethod
    def execute(self, command: FilterCandidateCommand) -> FilterCandidateResult:
        """조건을 기준으로 후보를 선별한다."""
        raise NotImplementedError
