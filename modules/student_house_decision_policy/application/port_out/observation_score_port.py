from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    ObservationScoreSource,
)


class ObservationScoreReadPort(ABC):
    """관측 저장소 조회 포트."""

    @abstractmethod
    def fetch_by_version(
        self, observation_version: str | None
    ) -> Sequence[ObservationScoreSource]:
        """관측 버전에 맞는 데이터를 조회한다."""
        raise NotImplementedError
