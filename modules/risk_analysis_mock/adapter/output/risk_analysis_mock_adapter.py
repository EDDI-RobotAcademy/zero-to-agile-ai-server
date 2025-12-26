from __future__ import annotations

from modules.risk_analysis_mock.application.dto.risk_score_dto import RiskScoreDTO
from modules.risk_analysis_mock.application.usecase.analyze_risk import (
    RiskAnalysisMockService,
)
from modules.student_house.application.port_out.risk_analysis_port import (
    RiskAnalysisPort,
)


class RiskAnalysisMockAdapter(RiskAnalysisPort):
    """student_house용 리스크 분석 mock 어댑터."""

    def __init__(self):
        self._service = RiskAnalysisMockService()

    async def analyze_risk(self, address: str | None, pnu: str | None) -> RiskScoreDTO:
        return await self._service.analyze_risk(address, pnu)
