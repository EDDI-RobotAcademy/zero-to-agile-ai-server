from __future__ import annotations

from abc import ABC, abstractmethod

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    RefreshStudentHouseScoreCommand,
    RefreshStudentHouseScoreResult,
)


class RefreshStudentHouseScorePort(ABC):
    """student_house 점수 갱신 입력 포트."""

    @abstractmethod
    def execute(
        self, command: RefreshStudentHouseScoreCommand
    ) -> RefreshStudentHouseScoreResult:
        """관측 버전에 맞춰 점수를 갱신한다."""
        raise NotImplementedError
