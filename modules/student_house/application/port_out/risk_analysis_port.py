from __future__ import annotations

from abc import ABC, abstractmethod

from modules.risk_analysis_mock.application.dto.risk_score_dto import RiskScoreDTO


class RiskAnalysisPort(ABC):
    """리스크 분석 인터페이스."""

    @abstractmethod
    async def analyze_risk(self, address: str | None, pnu: str | None) -> RiskScoreDTO:
        """주소/PNU 기반 리스크 점수를 반환한다."""
        raise NotImplementedError
