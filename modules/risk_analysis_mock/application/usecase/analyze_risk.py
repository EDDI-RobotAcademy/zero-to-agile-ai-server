from __future__ import annotations

import hashlib

from modules.risk_analysis_mock.application.dto.risk_score_dto import RiskScoreDTO


class RiskAnalysisMockService:
    """리스크 분석 mock 서비스."""

    async def analyze_risk(self, address: str | None, pnu: str | None) -> RiskScoreDTO:
        """주소/PNU를 기반으로 고정된 mock 점수를 만든다."""
        seed = f"{address or ''}|{pnu or ''}".encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()
        score = 60 + (int(digest[:2], 16) % 41)
        level = "SAFE" if score >= 80 else "WARN" if score >= 70 else "DANGER"
        reason = "mock 분석 결과"
        return RiskScoreDTO(score=score, level=level, reason=reason)
