from __future__ import annotations

from modules.risk_analysis_mock.application.dto.risk_score_dto import RiskScoreDTO
from modules.student_house.application.dto.student_house_dto import (
    StudentHouseScoreResult,
    StudentHouseScoreSource,
)
from modules.student_house.application.factory.student_house_scoring_policy import (
    StudentHouseScoringPolicy,
)
from modules.student_house.application.port_in.calculate_student_house_port import (
    CalculateStudentHousePort,
)
from modules.student_house.application.port_out.house_platform_read_port import (
    HousePlatformReadPort,
)
from modules.student_house.application.port_out.risk_analysis_port import (
    RiskAnalysisPort,
)
from modules.student_house.application.port_out.student_house_repository_port import (
    StudentHouseRepositoryPort,
)


class CalculateStudentHouseService(CalculateStudentHousePort):
    """student_house 점수 계산과 저장을 담당한다."""

    def __init__(
        self,
        house_reader: HousePlatformReadPort,
        repository: StudentHouseRepositoryPort,
        risk_analyzer: RiskAnalysisPort,
        policy: StudentHouseScoringPolicy | None = None,
    ):
        self.house_reader = house_reader
        self.repository = repository
        self.risk_analyzer = risk_analyzer
        self.policy = policy or StudentHouseScoringPolicy.from_env()

    async def calculate_and_upsert_score(
        self, house_platform_id: int
    ) -> StudentHouseScoreResult | None:
        """house_platform 데이터를 기반으로 점수를 계산한다."""
        source = self.house_reader.get_house_detail(house_platform_id)
        if not source:
            self.repository.mark_failed(
                house_platform_id, "매물 정보를 찾을 수 없습니다."
            )
            return None

        try:
            risk = await self._analyze_risk(source)
            score = self.policy.calculate_scores(source, risk)
            self.repository.upsert_score(house_platform_id, score)
            return score
        except Exception as exc:
            self.repository.mark_failed(
                house_platform_id, f"점수 계산 실패: {exc}"
            )
            return None

    async def _analyze_risk(
        self, source: StudentHouseScoreSource
    ) -> RiskScoreDTO:
        """리스크 분석 포트를 호출한다."""
        return await self.risk_analyzer.analyze_risk(
            source.address, source.pnu_cd
        )
